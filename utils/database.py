from models.message import db,Message
from models.participant import User
from models.conversation import Conversation
from datetime import datetime

def get_or_create_conversation(user1_id, user2_id):
    """
    Get existing conversation between two users or create a new one.
    Always ensures user1_id < user2_id.
    """
    # Ensure user1_id < user2_id
    if user1_id > user2_id:
        user1_id, user2_id = user2_id, user1_id
    
    # Try to find existing conversation
    conversation = Conversation.query.filter_by(
        user1_id=user1_id,
        user2_id=user2_id
    ).first()
    
    # Create if doesn't exist
    if not conversation:
        conversation = Conversation(
            user1_id=user1_id,
            user2_id=user2_id
        )
        db.session.add(conversation)
        db.session.commit()
        print(f"📝 Created new conversation between {user1_id} and {user2_id}")
    
    return conversation


def save_message(conversation_id, sender_id, content):
    """
    Save a new message to the database.
    """
    message = Message(
        conversation_id=conversation_id,
        sender_id=sender_id,
        content=content,
        sent_at=datetime.utcnow()
    )
    
    db.session.add(message)
    
    # Update conversation's updated_at timestamp
    conversation = Conversation.query.get(conversation_id)
    if conversation:
        conversation.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return message


def mark_message_delivered(message_id):
    """
    Mark a message as delivered.
    """
    message = Message.query.get(message_id)
    if message and not message.delivered_at:
        message.delivered_at = datetime.utcnow()
        db.session.commit()
        return True
    return False