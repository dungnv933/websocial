"""
Transaction model cho SMM Panel
"""

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from sqlalchemy import String, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class TransactionType(str, Enum):
    """
    Transaction type enumeration
    """
    DEPOSIT = "deposit"
    ORDER_PAYMENT = "order_payment"
    REFUND = "refund"


class Transaction(Base):
    """
    Transaction model - Quản lý giao dịch tài chính
    """
    __tablename__ = "transactions"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Foreign keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Transaction information
    type: Mapped[TransactionType] = mapped_column(
        String(50),
        nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False
    )
    
    # Balance tracking
    balance_before: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False
    )
    balance_after: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False
    )
    
    # Description
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="transactions")
    
    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, type={self.type}, amount={self.amount})>"
    
    @property
    def is_credit(self) -> bool:
        """
        Kiểm tra xem transaction có phải credit không
        """
        return self.type in [TransactionType.DEPOSIT, TransactionType.REFUND]
    
    @property
    def is_debit(self) -> bool:
        """
        Kiểm tra xem transaction có phải debit không
        """
        return self.type == TransactionType.ORDER_PAYMENT