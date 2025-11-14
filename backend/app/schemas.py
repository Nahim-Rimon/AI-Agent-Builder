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
        orm_mode = True

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

class AgentOut(BaseModel):
    id: int
    name: str
    role: Optional[str]
    goal: Optional[str]
    model_name: str
    temperature: float
    max_tokens: int
    class Config:
        orm_mode = True

class ChatMessageCreate(BaseModel):
    message: str

class ChatMessageOut(BaseModel):
    id: int
    sender: str
    message: str
    created_at: datetime
    class Config:
        orm_mode = True
