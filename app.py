from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from utils.jwt_helper import decode_token
from datetime import datetime
from config import Config
from models import db, User, Conversation, Message
from functools import wraps
from flask import jsonify
from utils.database import get_or_create_conversation, save_message, mark_message_delivered,get_undelivered_messages,get_conversation_messages,mark_messages_as_read


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

    @app.route('/api/conversations', methods=['GET'])
    @jwt_required
    def get_conversations(user_id):
        """
        Get all conversations for the authenticated user
        """
        try:
            conversations = Conversation.query.filter(
                (Conversation.user1_id == user_id) | (Conversation.user2_id == user_id)
            ).all()
            result = []

            for conv in conversations:
                other_user_id = conv.user2_id if conv.user1_id == user_id else conv.user1_id
                last_message = Message.query.filter_by(
                    conversation_id=conv.id
                ).order_by(Message.sent_at.desc()).first()

                unread_count = Message.query.filter(
                    Message.conversation_id == conv.id,
                    Message.sender_id != user_id,
                    Message.read_at.is_(None)
                ).count()

                conv_data = {
                    'conversation_id': conv.id,
                    'other_user_id': other_user_id,
                    'last_message': None,
                    'unread_count': unread_count,
                    'updated_at': conv.updated_at.isoformat()
                }

                if last_message:
                    conv_data['last_message'] = {
                        'content': last_message.content,
                        'sent_at': last_message.sent_at.isoformat(),
                        'sender_id': last_message.sender_id
                    }
                result.append(conv_data)
            return jsonify({'conversations': result}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/messages', methods=['GET'])
    @jwt_required
    def get_messages(user_id):
        """
        Get message history for a conversation with pagination.
        Query params: conversation_id,limit,offset
        """
        try:
            conversation_id = request.args.get('conversation_id', type=int)
            limit = request.args.get('limit', default=50, type=int)
            offset = request.args.get('offset', default=0, type=int)

            if not conversation_id:
                return jsonify({'error': 'conversation_id is required'}), 400

            # Check if user is part of this conversation
            conversation = Conversation.query.filter(
                Conversation.id == conversation_id,
                ((Conversation.user1_id == user_id) | (Conversation.user2_id == user_id))
            ).first()

            if not conversation:
                return jsonify({'error': 'Conversation not found or access denied'}), 404

            # Get messages
            messages, total = get_conversation_messages(conversation_id, limit, offset)

            # Convert messages to dict
            messages_data = [msg.to_dict() for msg in messages]

            # Calculate has_more
            has_more = (offset + limit) < total

            return jsonify({
                'messages': messages_data,
                'total': total,
                'has_more': has_more
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/messages/read', methods=['POST'])
    @jwt_required
    def mark_read(user_id):
        """
        Mark all unread messages in a conversation as read.
        Query params: conversation_id
        """
        try:
            conversation_id = request.args.get('conversation_id', type=int)
            if not conversation_id:
                return jsonify({'error': 'conversation_id is required'}), 400

            # Check if user is part of this conversation
            conversation = Conversation.query.filter(
                Conversation.id == conversation_id,
                ((Conversation.user1_id == user_id) | (Conversation.user2_id == user_id))
            ).first()

            if not conversation:
                return jsonify({'error': 'Conversation not found or access denied'}), 404

            count = mark_messages_as_read(conversation_id, user_id)

            return jsonify({
                'success': True,
                'messages_marked': count
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500 



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

        if not user_id:
            print('❌ Connection rejected: Invalid token')
            return False

        active_users[user_id] = request.sid # type: ignore

        # Deliver undelivered messages
        undelivered = get_undelivered_messages(user_id)
        if undelivered:
            print(f"📬 Delivering {len(undelivered)} queued messages to user {user_id}")
            for message in undelivered:
                emit('new_message', {
                    'message_id': message.id,
                    'conversation_id': message.conversation_id,
                    'from_user_id': message.sender_id,
                    'content': message.content,
                    'sent_at': message.sent_at.isoformat()
                })
                mark_message_delivered(message.id)

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

def jwt_required(f):
    """Decorator to require JWT authentication for REST endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No Authorization Header'}), 401

        try:
            token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
            payload = decode_token(token)

            if not payload:
                return jsonify({'error': 'Invalid token'}), 401

            return f(user_id=payload.get('user_id'), *args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 401
    return decorated_function


if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=True)