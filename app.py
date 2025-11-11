from flask import Flask,request
from flask_socketio import SocketIO, emit, disconnect
from flask_cors import CORS

from utils.jwt_helper import generate_token,validate_token
from config import SECRET_KEY

from datetime import datetime

# app = Flask(__name__)
# app.config['SECRET_KEY'] = SECRET_KEY



socketio = SocketIO(cors_allowed_origins="*",async_mode='eventlet')

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    CORS(app)
    socketio.init_app(app)

    from utils.database import init_db
    with app.app_context():
         init_db()
    return app

active_users = {}
socket_to_user = {}

@socketio.on('connect')
def handle_connect():
        token = request.args.get('token')
        payload = validate_token(token)
        socket_id = request.sid # type: ignore

        if not payload :
            print(f'unauthorized connection Attempt')
            disconnect()
            return
        user_id = payload['user_id']
        active_users[user_id] = socket_id # type: ignore
        socket_to_user[socket_id] = user_id

        print(f"user {user_id} connected with socket {socket_id}")
        emit('connected',{'message':f'welcome user {user_id}'})

@socketio.on('disconnect')
def handle_discconect():
    socket_id = request.sid #type: ignore
    user_id = socket_to_user.get(socket_id)

    if user_id :
        del active_users[user_id]
        del socket_to_user[socket_id]

        print(f"user {user_id} disconnected")
    
@socketio.on('ping')
def handle_ping(data):
    socket_id = request.sid #type: ignore
    user_id = socket_to_user.get(socket_id)
    if not user_id:
        print("⚠️ Received ping from unknown socket")
        return

    print(f"user {user_id} sent ping: {data}")

    emit('pong',{'response': data,'timestamp':datetime.utcnow().isoformat()})
    
    
if __name__ == "__main__":
    app = create_app()
    print("🚀 Starting Socket.IO server...")
    print(f"📡 Server running on http://localhost:5000")
    print(f"🔐 JWT authentication enabled")
    socketio.run(app,debug=True,host='0.0.0.0',port=5000)
    







