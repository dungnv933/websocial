"""
User schemas for SMM Panel
"""
from pydantic import BaseModel
from typing import List, Optional


class TierInfo(BaseModel):
    """Tier information schema"""
    tier_level: int
    tier_name: str
    tier_discount: float
    total_spent: float
    next_tier_spent: Optional[float] = None


class ReferralInfo(BaseModel):
    """Referral information schema"""
    referral_code: str
    referred_users: int
    total_earnings: float


class ReferredUser(BaseModel):
    """Referred user schema"""
    username: str
    email: str
    total_spent: float
    commission_earned: float
    created_at: str


class ReferralResponse(BaseModel):
    """Referral response schema"""
    referral_info: ReferralInfo
    referred_users: List[ReferredUser]


class BalanceResponse(BaseModel):
    """Balance response schema"""
    balance: float
    total_spent: float


class UserUpdate(BaseModel):
    """User update schema for admin"""
    balance: Optional[float] = None
    status: Optional[str] = None

