"""
Shared database instance for all models.
"""
from flask_sqlalchemy import SQLAlchemy

# Single shared db instance
db = SQLAlchemy()
