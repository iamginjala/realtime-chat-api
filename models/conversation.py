from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Conversation(db.Model):
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade='all, delete-orphan')
    user1 = db.relationship('User', foreign_keys=[user1_id])
    user2 = db.relationship('User', foreign_keys=[user2_id])
    
    # Ensure user1_id < user2_id to prevent duplicates
    __table_args__ = (
        db.CheckConstraint('user1_id < user2_id', name='user_order_check'),
        db.UniqueConstraint('user1_id', 'user2_id', name='unique_conversation'),
    )
    
    def __repr__(self):
        return f'<Conversation {self.id}: {self.user1_id} <-> {self.user2_id}>'