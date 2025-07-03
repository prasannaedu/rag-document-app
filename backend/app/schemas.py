from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Dict, Any

class DocumentCreate(BaseModel):
    filename: str
    original_filename: str
    content: str
    doc_metadata: Dict[str, Any]

class DocumentResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    original_filename: str
    content: str
    doc_metadata: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True  

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @validator('password')
    def password_length(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class QueryRequest(BaseModel):
    query: str  