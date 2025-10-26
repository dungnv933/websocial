"""
Service API endpoints for SMM Panel
"""
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.database import get_db
from app.models.service import Service
from app.schemas.service import ServiceResponse, ServiceCreate, ServiceUpdate

router = APIRouter()


@router.get("/", response_model=list)
async def get_services(
    category: str = Query(None, description="Filter by category"),
    db: Session = Depends(get_db)
):
    """
    Get available services, optionally filtered by category
    """
    query = db.query(Service).filter(Service.status == "active")
    
    if category:
        query = query.filter(Service.category == category)
    
    services = query.all()
    return services


@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(service_id: int, db: Session = Depends(get_db)):
    """
    Get specific service by ID
    """
    service = db.query(Service).filter(Service.id == service_id).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    return service
