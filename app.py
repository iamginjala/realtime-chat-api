from flask import Flask,render_template
from flask_socketio import SocketIO

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'some secret'
    socketio.init_app(app)

    @app.route('/health')
    def health():
        return {'status': 'ok'}
    return app

@socketio.on('connect')
def handle_connect():
    print('client connected ')
@socketio.on('disconnect')
def handle_disconnect():
    print('client disconnected')
if __name__ == '__main__':
    app = create_app()
    socketio.run(app)