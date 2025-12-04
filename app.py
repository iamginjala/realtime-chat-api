from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from utils.jwt_helper import decode_token
from datetime import datetime
from config import Config
from models import db, User, Conversation, Message

from utils.database import get_or_create_conversation, save_message, mark_message_delivered


socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Initialize database
    db.init_app(app)
    
    # Initialize SocketIO
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Create tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables created")
    
    @app.route('/health')
    def health():
        return {'status': 'ok', 'database': 'connected'}
    
    return app

active_users = {}

@socketio.on('connect')
def handle_connect(auth):
    try:
        token = auth.get('token')
        if not token:
            print('❌ Connection rejected: No token provided')
            return False
        
        payload = decode_token(token)
        user_id = payload.get('user_id')

        active_users[user_id] = request.sid # type: ignore
        
        print(f"✅ User {user_id} connected with socket {request.sid}") # type: ignore
        
        emit('authenticated', {'user_id': user_id, 'message': 'Authentication successful'})
        
        return True
        
    except Exception as e:
        print(f"❌ Connection rejected: {str(e)}")
        return False

@socketio.on('disconnect')
def handle_disconnect():
    user_id = None
    for uid, sid in active_users.items():
        if sid == request.sid: # type: ignore
            user_id = uid
            break
    
    if user_id:
        del active_users[user_id]
        print(f"👋 User {user_id} disconnected")

@socketio.on('ping')
def handle_ping():
    emit('pong', {'timestamp': datetime.now().isoformat()})
@socketio.on('send_message')
def handle_send_message(data):
    """
    Handle incoming message from client.
    Expected data: {
        'to_user_id': int,
        'content': str
    }
    """
    try:
        # Get sender info from JWT (already validated in connect)
        sender_id = None
        for uid, sid in active_users.items():
            if sid == request.sid: # type: ignore
                sender_id = uid
                break
        
        if not sender_id:
            emit('error', {'message': 'User not authenticated'})
            return
        
        to_user_id = data.get('to_user_id')
        content = data.get('content')
        
        if not to_user_id or not content:
            emit('error', {'message': 'Missing to_user_id or content'})
            return
        
        # Get or create conversation
        conversation = get_or_create_conversation(sender_id, to_user_id)
        
        # Save message to database
        message = save_message(conversation.id, sender_id, content)
        
        # Confirm to sender
        emit('message_sent', {
            'message_id': message.id,
            'conversation_id': conversation.id,
            'status': 'sent',
            'sent_at': message.sent_at.isoformat()
        })
        
        print(f"✉️ Message {message.id} from {sender_id} to {to_user_id}: {content[:50]}")
        
        # Deliver to recipient if online
        recipient_socket_id = active_users.get(to_user_id)
        if recipient_socket_id:
            socketio.emit('new_message', {
                'message_id': message.id,
                'conversation_id': conversation.id,
                'from_user_id': sender_id,
                'content': content,
                'sent_at': message.sent_at.isoformat()
            }, to=recipient_socket_id)
            
            # Mark as delivered
            mark_message_delivered(message.id)
            
            # Notify sender about delivery
            emit('message_delivered', {
                'message_id': message.id,
                'delivered_at': datetime.utcnow().isoformat()
            })
            
            print(f"✅ Message {message.id} delivered to user {to_user_id}")
        else:
            print(f"📭 User {to_user_id} is offline. Message queued.")
    
    except Exception as e:
        print(f"❌ Error sending message: {str(e)}")
        emit('error', {'message': f'Failed to send message: {str(e)}'})



if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=True)