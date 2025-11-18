from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class AgentCreate(BaseModel):
    name: str
    role: Optional[str] = ''
    goal: Optional[str] = ''
    model_name: Optional[str] = 'gpt-4-turbo'
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1024
    top_p: Optional[float] = 1.0
    top_k: Optional[int] = 50
    api_key: Optional[str] = None
    provider: Optional[str] = 'openai'

class AgentOut(BaseModel):
    id: int
    name: str
    role: Optional[str]
    goal: Optional[str]
    model_name: str
    temperature: float
    max_tokens: int
    top_p: Optional[float]
    top_k: Optional[int]
    provider: Optional[str]
    class Config:
        from_attributes = True

class ChatMessageCreate(BaseModel):
    message: str
    api_key: Optional[str] = None

class ChatMessageOut(BaseModel):
    id: int
    sender: str
    message: str
    created_at: datetime
    class Config:
        from_attributes = True
