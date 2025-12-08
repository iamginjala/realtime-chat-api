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

def get_undelivered_messages(user_id: int) -> list[Message]:
    """
    Get all undelivered messages for a user.
    Returns messages where the user is a participant but message hasn't been delivered.
    """
    # Find all conversations where user is a participant
    conversations = Conversation.query.filter(
        (Conversation.user1_id == user_id) | (Conversation.user2_id == user_id)
    ).all()

    if not conversations:
        return []

    # Get conversation IDs
    c_ids = [c.id for c in conversations]

    # Find undelivered messages
    undelivered = Message.query.filter(
        Message.conversation_id.in_(c_ids),
        Message.sender_id != user_id,
        Message.delivered_at.is_(None)
    ).order_by(Message.sent_at).all()

    return undelivered

def get_conversation_messages(conversation_id: int, limit: int = 50,offset: int = 0):
    """ Get messages from a conversation with pagination.
        Returns messages ordered by sent_at (newest first).
    """
    messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.sent_at.desc()).limit(limit).offset(offset).all()

    total = Message.query.filter_by(conversation_id=conversation_id).count()

    return messages,total

def mark_messages_as_read(conversation_id: int, user_id: int) -> int:
    """
    Mark all unread messages in a conversation as read for the given user.
    Returns the number of messages marked as read.
    """
    # Find all unread messages in this conversation that were NOT sent by the user
    unread_messages = Message.query.filter(
        Message.conversation_id == conversation_id,
        Message.sender_id != user_id,
        Message.read_at.is_(None)
    ).all()

    # Mark them as read
    count = 0
    for message in unread_messages:
        message.read_at = datetime.utcnow()
        count += 1

    if count > 0:
        db.session.commit()

    return count