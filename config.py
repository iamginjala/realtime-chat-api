import os
from dotenv import load_dotenv

load_dotenv()


SECRET_KEY = os.getenv('SECRET_KEY','dev-secret-key-please-change-in-production')
EXPIRATION =int(os.getenv('EXPIRES_IN_HOURS',24))

DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://chatuser:chatpassword@localhost:5432/realtime_chat'
)
