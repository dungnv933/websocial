"""
Service schemas for SMM Panel
"""
from pydantic import BaseModel
from typing import Optional


class ServiceResponse(BaseModel):
    """Service response schema"""
    id: int
    name: str
    category: str
    rate: float
    min_quantity: int
    max_quantity: int
    provider: str
    description: Optional[str] = None
    status: str
    
    class Config:
        orm_mode = True


class ServiceCreate(BaseModel):
    """Service creation schema"""
    name: str
    category: str
    rate: float
    min_quantity: int
    max_quantity: int
    provider: str
    provider_service_id: str
    description: Optional[str] = None
    status: str = "active"


class ServiceUpdate(BaseModel):
    """Service update schema"""
    name: Optional[str] = None
    category: Optional[str] = None
    rate: Optional[float] = None
    min_quantity: Optional[int] = None
    max_quantity: Optional[int] = None
    provider: Optional[str] = None
    provider_service_id: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

