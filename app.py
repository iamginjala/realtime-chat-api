from flask import Flask, render_template,request
from flask_socketio import SocketIO, disconnect, emit
from flask_cors import CORS
from utils.jwt_helper import decode_token
from datetime import datetime

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['SECRET_KEY'] = 'some secret'
    socketio.init_app(app, cors_allowed_origins="*")

    @app.route('/health')
    def health():
        return {'status': 'ok'}
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

if __name__ == '__main__':
    app = create_app()
    socketio.run(app)