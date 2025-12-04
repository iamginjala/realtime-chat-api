import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret')
    EXPIRES_IN_HOURS = int(os.getenv('EXPIRES_IN_HOURS', 24))

    DB_USER = os.getenv('DB_USER', 'chatuser')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'chatpassword')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'realtime_chat')
    
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False