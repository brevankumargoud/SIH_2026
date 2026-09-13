from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import uuid

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None

class TokenPayload(BaseModel):
    sub: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    roles: list[str] = []

    class Config:
        from_attributes = True
