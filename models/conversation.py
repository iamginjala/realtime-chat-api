from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from utils.database import Base

class Conversation(Base):
    __tablename__= 'conversations'
    id = Column(Integer,primary_key=True,index=True)
    type = Column(String(20),default='direct',nullable=False)
    created_at = Column(DateTime(timezone=True),server_default=func.now())

    participants = relationship("ConversationParticipant", back_populates="conversation")
    messages = relationship("Message", back_populates="conversation")