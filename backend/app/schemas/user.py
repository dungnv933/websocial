"""
User Pydantic schemas
"""

import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, EmailStr, validator


class UserBase(BaseModel):
    """
    Base user schema
    """
    email: EmailStr


class UserCreate(UserBase):
    """
    Schema để tạo user mới
    """
    password: str
    
    @validator("password")
    def validate_password(cls, v: str) -> str:
        """
        Validate password strength
        """
        if len(v) < 8:
            raise ValueError("Mật khẩu phải có ít nhất 8 ký tự")
        return v


class UserLogin(BaseModel):
    """
    Schema để login
    """
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """
    Schema response cho user
    """
    id: uuid.UUID
    balance: Decimal
    total_spent: Decimal
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: float,
            datetime: lambda v: v.isoformat()
        }


class TokenResponse(BaseModel):
    """
    Schema response cho JWT token
    """
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse