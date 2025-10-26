"""
User API endpoints for SMM Panel
"""
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.database import get_db
from app.models.user import User
from app.models.transaction import Transaction
from app.schemas.user import TierInfo, ReferralResponse, BalanceResponse, UserUpdate
from app.utils.tier import calculate_tier, get_next_tier_info
from app.dependencies import get_current_user

router = APIRouter()


@router.get("/tier", response_model=TierInfo)
async def get_user_tier(current_user: User = Depends(get_current_user)):
    """
    Get current user tier information
    """
    next_tier_info = get_next_tier_info(current_user.tier_level, current_user.total_spent)
    
    return TierInfo(
        tier_level=current_user.tier_level,
        tier_name=current_user.tier_name,
        tier_discount=current_user.tier_discount,
        total_spent=current_user.total_spent,
        next_tier_spent=next_tier_info.get("next_tier_spent")
    )


@router.get("/balance", response_model=BalanceResponse)
async def get_user_balance(current_user: User = Depends(get_current_user)):
    """
    Get current user balance
    """
    return BalanceResponse(
        balance=current_user.balance,
        total_spent=current_user.total_spent
    )


@router.get("/referrals", response_model=ReferralResponse)
async def get_user_referrals(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get user referrals and earnings
    """
    # Get referred users
    referred_users = db.query(User).filter(User.referred_by_code == current_user.referral_code).all()
    
    # Calculate total earnings from referrals (5% commission)
    total_earnings = 0
    referred_users_data = []
    
    for user in referred_users:
        commission_earned = user.total_spent * 0.05  # 5% commission
        total_earnings += commission_earned
        
        referred_users_data.append({
            "username": user.username,
            "email": user.email,
            "total_spent": user.total_spent,
            "commission_earned": commission_earned,
            "created_at": user.created_at.isoformat()
        })
    
    return ReferralResponse(
        referral_info={
            "referral_code": current_user.referral_code,
            "referred_users": len(referred_users),
            "total_earnings": total_earnings
        },
        referred_users=referred_users_data
    )


@router.get("/orders")
async def get_user_orders(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user orders with pagination
    """
    from app.models.order import Order
    from app.models.service import Service
    
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get orders with service information
    orders_query = db.query(Order, Service).join(Service).filter(Order.user_id == current_user.id)
    total = orders_query.count()
    
    orders = orders_query.offset(offset).limit(per_page).all()
    
    # Format response
    orders_data = []
    for order, service in orders:
        orders_data.append({
            "id": order.id,
            "service_name": service.name,
            "link": order.link,
            "quantity": order.quantity,
            "charge": order.charge,
            "status": order.status,
            "created_at": order.created_at.isoformat(),
            "updated_at": order.updated_at.isoformat() if order.updated_at else None
        })
    
    return {
        "orders": orders_data,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }


@router.get("/transactions")
async def get_user_transactions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user transactions with pagination
    """
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get transactions
    transactions_query = db.query(Transaction).filter(Transaction.user_id == current_user.id)
    total = transactions_query.count()
    
    transactions = transactions_query.order_by(Transaction.created_at.desc()).offset(offset).limit(per_page).all()
    
    # Format response
    transactions_data = []
    for transaction in transactions:
        transactions_data.append({
            "id": transaction.id,
            "type": transaction.type,
            "amount": transaction.amount,
            "balance_before": transaction.balance_before,
            "balance_after": transaction.balance_after,
            "description": transaction.description,
            "created_at": transaction.created_at.isoformat()
        })
    
    return {
        "transactions": transactions_data,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }
