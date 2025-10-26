"""
Order schemas for SMM Panel
"""
from pydantic import BaseModel
from typing import Optional


class OrderCreate(BaseModel):
    """Order creation schema"""
    service_id: int
    link: str
    quantity: int


class OrderResponse(BaseModel):
    """Order response schema"""
    id: int
    user_id: int
    service_id: int
    service_name: str
    link: str
    quantity: int
    charge: float
    start_count: Optional[int] = None
    remains: Optional[int] = None
    status: str
    bumx_order_id: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None
    
    class Config:
        orm_mode = True


class OrderStatusUpdate(BaseModel):
    """Order status update schema"""
    status: str


class OrderListResponse(BaseModel):
    """Order list response schema"""
    orders: list
    total: int
    page: int
    per_page: int

