import jwt
from datetime import datetime, timedelta
from config import Config

secret = Config.SECRET_KEY
def generate_token(user_id,email):
    payload = {
    'user_id': user_id,
    'email': email,
    'exp': datetime.utcnow() + timedelta(hours=Config.EXPIRES_IN_HOURS), # What should go here?
    'iat': datetime.utcnow()   # What should go here?
}
    token = jwt.encode(payload,secret,algorithm="HS256")

    return token

def decode_token(token):
    try:
        decoded = jwt.decode(token, secret, algorithms=['HS256'])
        return {'user_id': decoded['user_id'], 'email': decoded['email']}
    except jwt.ExpiredSignatureError:
        raise Exception('Token has expired')
    except jwt.InvalidTokenError:
        raise Exception('Invalid token')