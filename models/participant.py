from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from utils.database import Base

class ConversationParticipant(Base):
    __tablename__ = 'conversation_participants'
    id = Column(Integer,primary_key=True)
    conversation_id = Column(Integer,ForeignKey('conversations.id',ondelete='CASCADE'),nullable=False)
    user_id = Column(Integer,nullable=False,index=True)
    joined_at = Column(DateTime(timezone=True),server_default=func.now())
    last_read_at = Column(DateTime(timezone=True),server_default=func.now())

    conversation = relationship("Conversation", back_populates="participants")
    
    __table_args__ = (
        UniqueConstraint('conversation_id', 'user_id', name='unique_conversation_user'),
    )