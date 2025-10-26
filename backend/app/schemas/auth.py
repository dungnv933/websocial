"""
Authentication schemas for SMM Panel
"""
from pydantic import BaseModel
from typing import Optional


class UserRegister(BaseModel):
    """User registration schema"""
    username: str
    email: str
    password: str
    referral_code: Optional[str] = None


class UserLogin(BaseModel):
    """User login schema"""
    username: str
    password: str


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data schema"""
    username: Optional[str] = None


class UserResponse(BaseModel):
    """User response schema"""
    id: int
    username: str
    email: str
    balance: float
    total_spent: float
    tier_level: int
    tier_name: str
    tier_discount: float
    referral_code: str
    status: str
    created_at: str
    
    class Config:
        orm_mode = True
