"""
Admin API endpoints for SMM Panel
"""
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.database import get_db
from app.models.user import User
from app.models.order import Order
from app.models.service import Service
from app.models.deposit import Deposit
from app.models.transaction import Transaction
from app.schemas.user import UserUpdate
from app.schemas.service import ServiceCreate, ServiceUpdate
from app.dependencies import get_current_user, get_admin_user

router = APIRouter()




@router.get("/users")
async def get_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    status_filter: str = Query(None),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all users with pagination and filters
    """
    query = db.query(User)
    
    if search:
        query = query.filter(
            (User.username.contains(search)) | 
            (User.email.contains(search))
        )
    
    if status_filter:
        query = query.filter(User.status == status_filter)
    
    total = query.count()
    offset = (page - 1) * per_page
    users = query.offset(offset).limit(per_page).all()
    
    return {
        "users": users,
        "total": total,
        "page": page,
        "per_page": per_page
    }


@router.put("/users/{user_id}/balance")
async def update_user_balance(
    user_id: int,
    balance_change: float,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Add or subtract user balance
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    old_balance = user.balance
    user.balance += balance_change
    
    if user.balance < 0:
        user.balance = 0
    
    # Create transaction record
    transaction = Transaction(
        user_id=user.id,
        type="deposit" if balance_change > 0 else "order",
        amount=balance_change,
        balance_before=old_balance,
        balance_after=user.balance,
        description="Admin balance adjustment"
    )
    
    db.add(transaction)
    db.commit()
    
    return {"message": "Balance updated successfully", "new_balance": user.balance}


@router.put("/users/{user_id}/ban")
async def ban_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Ban or unban user
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.status = "banned" if user.status == "active" else "active"
    db.commit()
    
    return {"message": "User status updated", "status": user.status}


@router.get("/orders")
async def get_orders(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status_filter: str = Query(None),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all orders with pagination and filters
    """
    query = db.query(Order)
    
    if status_filter:
        query = query.filter(Order.status == status_filter)
    
    total = query.count()
    offset = (page - 1) * per_page
    orders = query.offset(offset).limit(per_page).all()
    
    return {
        "orders": orders,
        "total": total,
        "page": page,
        "per_page": per_page
    }


@router.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    new_status: str,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update order status
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    order.status = new_status
    db.commit()
    
    return {"message": "Order status updated", "status": new_status}


@router.get("/services")
async def get_services(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all services
    """
    services = db.query(Service).all()
    return services


@router.post("/services")
async def create_service(
    service_data: ServiceCreate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create new service
    """
    new_service = Service(**service_data.dict())
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    
    return new_service


@router.put("/services/{service_id}")
async def update_service(
    service_id: int,
    service_data: ServiceUpdate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update service
    """
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    for field, value in service_data.dict(exclude_unset=True).items():
        setattr(service, field, value)
    
    db.commit()
    db.refresh(service)
    
    return service


@router.get("/deposits")
async def get_deposits(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status_filter: str = Query(None),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all deposits with pagination and filters
    """
    query = db.query(Deposit)
    
    if status_filter:
        query = query.filter(Deposit.status == status_filter)
    
    total = query.count()
    offset = (page - 1) * per_page
    deposits = query.offset(offset).limit(per_page).all()
    
    return {
        "deposits": deposits,
        "total": total,
        "page": page,
        "per_page": per_page
    }


@router.put("/deposits/{deposit_id}/approve")
async def approve_deposit(
    deposit_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Approve deposit manually
    """
    deposit = db.query(Deposit).filter(Deposit.id == deposit_id).first()
    if not deposit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit not found"
        )
    
    if deposit.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deposit is not pending"
        )
    
    # Update deposit status
    deposit.status = "approved"
    
    # Add balance to user
    user = db.query(User).filter(User.id == deposit.user_id).first()
    if user:
        user.balance += deposit.amount
        
        # Create transaction record
        transaction = Transaction(
            user_id=user.id,
            type="deposit",
            amount=deposit.amount,
            balance_before=user.balance - deposit.amount,
            balance_after=user.balance,
            description="Manual deposit approval"
        )
        
        db.add(transaction)
        db.commit()
    
    return {"message": "Deposit approved successfully"}
