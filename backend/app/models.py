from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    agents = relationship('Agent', back_populates='owner')

class Agent(Base):
    __tablename__ = 'agents'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    role = Column(String)
    goal = Column(Text)
    model_name = Column(String, default='gpt-4-turbo')
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=1024)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship('User', back_populates='agents')
    chats = relationship('ChatMessage', back_populates='agent', cascade='all, delete')

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey('agents.id'))
    sender = Column(String)  # 'user' or 'agent'
    message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    agent = relationship('Agent', back_populates='chats')
