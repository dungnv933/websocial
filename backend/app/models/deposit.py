"""
Deposit model for SMM Panel
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Deposit(Base):
    """Deposit model for user deposits"""
    
    __tablename__ = "deposits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    method = Column(String(50), default="bank_transfer", nullable=False)
    bank_name = Column(String(100), default="ACB", nullable=False)
    transaction_id = Column(String(200), nullable=True)
    status = Column(String(20), default="pending", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="deposits")
    
    def __repr__(self):
        return "<Deposit(id={}, user_id={}, amount={}, status='{}')>".format(
            self.id, self.user_id, self.amount, self.status
        )

