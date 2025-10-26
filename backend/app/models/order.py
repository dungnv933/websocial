"""
Order model for SMM Panel
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Order(Base):
    """Order model for SMM orders"""
    
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    link = Column(String(500), nullable=False)
    quantity = Column(Integer, nullable=False)
    charge = Column(Float, nullable=False)
    start_count = Column(Integer, nullable=True)
    remains = Column(Integer, nullable=True)
    status = Column(String(20), default="pending", nullable=False)
    bumx_order_id = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="orders")
    service = relationship("Service", back_populates="orders")
    
    def __repr__(self):
        return "<Order(id={}, user_id={}, service_id={}, status='{}')>".format(
            self.id, self.user_id, self.service_id, self.status
        )

