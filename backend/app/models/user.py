"""
User model for SMM Panel
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """User model with tier system and referral support"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    balance = Column(Float, default=0.0, nullable=False)
    total_spent = Column(Float, default=0.0, nullable=False)
    
    # Tier system
    tier_level = Column(Integer, default=1, nullable=False)
    tier_name = Column(String(20), default="Cấp 1", nullable=False)
    tier_discount = Column(Float, default=0.0, nullable=False)
    
    # Referral system
    referral_code = Column(String(20), unique=True, index=True, nullable=False)
    referred_by_code = Column(String(20), nullable=True)
    
    # Status
    status = Column(String(20), default="active", nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    orders = relationship("Order", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    deposits = relationship("Deposit", back_populates="user")
    
    def __repr__(self):
        return "<User(username='{}', email='{}', tier='{}')>".format(
            self.username, self.email, self.tier_name
        )
