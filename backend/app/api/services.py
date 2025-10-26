"""
Services API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.models.user import User
from app.schemas.service import ServicesResponse, ServiceResponse
from app.utils.bumx_client import get_bumx_client, BUMXClient
from app.utils.redis_client import get_redis_client, RedisClient
from app.dependencies import get_current_active_user

router = APIRouter()


@router.get("/", response_model=ServicesResponse)
async def get_services(
    category: Optional[str] = Query(None, description="Filter by category"),
    current_user: User = Depends(get_current_active_user),
    bumx_client: BUMXClient = Depends(get_bumx_client),
    redis_client: RedisClient = Depends(get_redis_client)
):
    """
    Lấy danh sách services từ BUMX API với Redis caching
    """
    try:
        # Kiểm tra cache trước
        cache_key = f"services:{category or 'all'}"
        cached_services = await redis_client.get(cache_key)
        
        if cached_services:
            return ServicesResponse(
                services=cached_services,
                total=len(cached_services),
                category=category
            )
        
        # Lấy từ BUMX API
        services_data = await bumx_client.get_services()
        
        # Convert sang ServiceResponse
        services = []
        for service_data in services_data:
            service = ServiceResponse(
                service=service_data.get("service"),
                name=service_data.get("name"),
                type=service_data.get("type"),
                category=service_data.get("category"),
                rate=service_data.get("rate"),
                min=service_data.get("min"),
                max=service_data.get("max"),
                description=service_data.get("description")
            )
            services.append(service)
        
        # Filter theo category nếu có
        if category:
            services = [s for s in services if s.category.lower() == category.lower()]
        
        # Cache kết quả (1 giờ)
        await redis_client.set(cache_key, [s.dict() for s in services], ttl=3600)
        
        return ServicesResponse(
            services=services,
            total=len(services),
            category=category
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy danh sách services: {str(e)}"
        )


@router.get("/categories")
async def get_service_categories(
    current_user: User = Depends(get_current_active_user),
    bumx_client: BUMXClient = Depends(get_bumx_client),
    redis_client: RedisClient = Depends(get_redis_client)
):
    """
    Lấy danh sách categories có sẵn
    """
    try:
        # Kiểm tra cache
        cache_key = "service_categories"
        cached_categories = await redis_client.get(cache_key)
        
        if cached_categories:
            return {"categories": cached_categories, "total": len(cached_categories)}
        
        # Lấy từ BUMX API
        services_data = await bumx_client.get_services()
        
        # Extract categories
        categories = list(set(s.get("category", "").lower() for s in services_data if s.get("category")))
        categories.sort()
        
        # Cache kết quả (1 giờ)
        await redis_client.set(cache_key, categories, ttl=3600)
        
        return {"categories": categories, "total": len(categories)}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy danh sách categories: {str(e)}"
        )