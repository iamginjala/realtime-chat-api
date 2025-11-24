import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret')
    EXPIRES_IN_HOURS = int(os.getenv('EXPIRES_IN_HOURS', 24))