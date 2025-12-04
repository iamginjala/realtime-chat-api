from models import db, User, Conversation, Message
from datetime import datetime
from typing import Optional

def get_or_create_conversation(user1_id: int, user2_id: int) -> Conversation:
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
            user1_id=user1_id, # type: ignore
            user2_id=user2_id # type: ignore
        )
        db.session.add(conversation)
        db.session.commit()
        print(f"📝 Created new conversation between {user1_id} and {user2_id}")
    
    return conversation


def save_message(conversation_id: int, sender_id: int, content: str) -> Message:
    """
    Save a new message to the database.
    """
    message = Message(
        conversation_id=conversation_id, # type: ignore
        sender_id=sender_id, # type: ignore
        content=content, # type: ignore
        sent_at=datetime.utcnow() # type: ignore
    )
    
    db.session.add(message)
    
    # Update conversation's updated_at timestamp
    conversation = Conversation.query.get(conversation_id)
    if conversation:
        conversation.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return message


def mark_message_delivered(message_id: int) -> bool:
    """
    Mark a message as delivered.
    """
    message = Message.query.get(message_id)
    if message and not message.delivered_at:
        message.delivered_at = datetime.utcnow()
        db.session.commit()
        return True
    return False