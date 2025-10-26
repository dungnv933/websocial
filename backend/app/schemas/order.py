"""
Order Pydantic schemas
"""

import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, validator
from app.models.order import OrderStatus


class OrderCreate(BaseModel):
    """
    Schema để tạo order mới
    """
    service_id: int
    link: str
    quantity: int
    
    @validator("link")
    def validate_link(cls, v: str) -> str:
        """
        Validate link format
        """
        if not v.startswith(("http://", "https://")):
            raise ValueError("Link phải bắt đầu bằng http:// hoặc https://")
        return v
    
    @validator("quantity")
    def validate_quantity(cls, v: int) -> int:
        """
        Validate quantity
        """
        if v <= 0:
            raise ValueError("Số lượng phải lớn hơn 0")
        if v > 1000000:
            raise ValueError("Số lượng không được vượt quá 1,000,000")
        return v


class OrderResponse(BaseModel):
    """
    Schema response cho order
    """
    id: uuid.UUID
    user_id: uuid.UUID
    service_id: int
    service_name: str
    link: str
    quantity: int
    price: Decimal
    status: OrderStatus
    bumx_order_id: str
    created_at: datetime
    completed_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: float,
            datetime: lambda v: v.isoformat()
        }


class OrderHistoryResponse(BaseModel):
    """
    Schema response cho order history
    """
    orders: list[OrderResponse]
    total: int
    page: int
    per_page: int
    total_pages: int