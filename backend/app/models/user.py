"""
User model cho SMM Panel
"""

import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, DateTime, Boolean, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    """
    User model - Quản lý thông tin người dùng
    """
    __tablename__ = "users"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Thông tin cơ bản
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Balance và spending
    balance: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        default=Decimal('0.00'),
        nullable=False
    )
    total_spent: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        default=Decimal('0.00'),
        nullable=False
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, balance={self.balance})>"
    
    def add_balance(self, amount: Decimal) -> None:
        """
        Thêm balance cho user
        """
        self.balance += amount
    
    def deduct_balance(self, amount: Decimal) -> bool:
        """
        Trừ balance của user
        Returns True nếu thành công, False nếu không đủ balance
        """
        if self.balance >= amount:
            self.balance -= amount
            self.total_spent += amount
            return True
        return False