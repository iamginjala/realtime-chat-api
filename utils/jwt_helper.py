import jwt
from config import SECRET_KEY,EXPIRATION
from datetime import datetime,timedelta

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=EXPIRATION),  # Expiry # type: ignore
        'iat': datetime.utcnow()  # Issued at (optional but useful)
    }

    token = jwt.encode(payload,SECRET_KEY,algorithm='HS256')

    return token

def validate_token(token):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
