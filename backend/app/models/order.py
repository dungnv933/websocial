"""
Order model cho SMM Panel
"""

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from sqlalchemy import String, DateTime, Integer, Numeric, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class OrderStatus(str, Enum):
    """
    Order status enumeration
    """
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Order(Base):
    """
    Order model - Quản lý đơn hàng SMM services
    """
    __tablename__ = "orders"
    
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
    
    # Order information
    service_id: Mapped[int] = mapped_column(Integer, nullable=False)
    service_name: Mapped[str] = mapped_column(String(255), nullable=False)
    link: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False
    )
    
    # Status
    status: Mapped[OrderStatus] = mapped_column(
        String(50),
        default=OrderStatus.PENDING,
        nullable=False
    )
    
    # BUMX integration
    bumx_order_id: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="orders")
    
    def __repr__(self) -> str:
        return f"<Order(id={self.id}, service_id={self.service_id}, status={self.status})>"
    
    @property
    def is_completed(self) -> bool:
        """
        Kiểm tra xem order đã hoàn thành chưa
        """
        return self.status == OrderStatus.COMPLETED
    
    @property
    def is_active(self) -> bool:
        """
        Kiểm tra xem order có đang active không
        """
        return self.status in [OrderStatus.PENDING, OrderStatus.PROCESSING]