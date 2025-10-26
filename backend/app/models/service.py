"""
Service model for SMM Panel
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Service(Base):
    """Service model for SMM services"""
    
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)  # facebook, instagram, tiktok, youtube, shopee
    rate = Column(Float, nullable=False)  # price per 1000
    min_quantity = Column(Integer, nullable=False)
    max_quantity = Column(Integer, nullable=False)
    provider = Column(String(100), nullable=False)
    provider_service_id = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="active", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    orders = relationship("Order", back_populates="service")
    
    def __repr__(self):
        return "<Service(name='{}', category='{}', rate={})>".format(
            self.name, self.category, self.rate
        )
