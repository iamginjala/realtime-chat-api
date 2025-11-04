import os
from dotenv import load_dotenv

load_dotenv()


SECRET_KEY = os.getenv('SECRET_KEY','dev-secret-key-please-change-in-production')
EXPIRATION =int(os.getenv('EXPIRES_IN_HOURS',24))