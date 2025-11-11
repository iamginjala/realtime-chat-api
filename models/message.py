from sqlalchemy import Column, Integer, String, DateTime,ForeignKey,Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from utils.database import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer,primary_key=True)
    conversation_id = Column(Integer,ForeignKey('conversations.id',ondelete='CASCADE'),nullable=False,index=True)
    content = Column(Text, nullable=False) 
    sender_id = Column(Integer,nullable=False)
    sent_at = Column(DateTime(timezone=True),server_default=func.now())
    delivered_at = Column(DateTime(timezone=True),nullable=True)
    read_at = Column(DateTime(timezone=True),nullable=True)

    conversation = relationship("Conversation",back_populates="messages")