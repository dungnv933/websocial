"""
Service Pydantic schemas
"""

from typing import List, Optional
from pydantic import BaseModel


class ServiceResponse(BaseModel):
    """
    Schema response cho service từ BUMX API
    """
    service: int
    name: str
    type: str
    category: str
    rate: float
    min: int
    max: int
    description: Optional[str] = None
    
    class Config:
        from_attributes = True


class ServicesResponse(BaseModel):
    """
    Schema response cho danh sách services
    """
    services: List[ServiceResponse]
    total: int
    category: Optional[str] = None


class BalanceResponse(BaseModel):
    """
    Schema response cho balance
    """
    balance: float
    currency: str = "USD"


class DepositRequest(BaseModel):
    """
    Schema request cho deposit
    """
    amount: float
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.amount <= 0:
            raise ValueError("Số tiền phải lớn hơn 0")


class PromotionResponse(BaseModel):
    """
    Schema response cho promotion
    """
    id: str
    name: str
    description: str
    discount_percentage: int
    min_amount: Optional[float] = None
    max_discount: Optional[float] = None
    is_active: bool = True
