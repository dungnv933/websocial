"""
Order API endpoints for SMM Panel
"""
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.database import get_db
from app.models.order import Order
from app.models.service import Service
from app.models.user import User
from app.models.transaction import Transaction
from app.schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate
from app.utils.tier import calculate_discounted_price
from app.utils.bumx import BUMXClient
from app.utils.telegram import TelegramBot
from app.dependencies import get_current_user

router = APIRouter()


@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new order
    """
    # Get service
    service = db.query(Service).filter(Service.id == order_data.service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    if service.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service is not active"
        )
    
    # Validate quantity
    if order_data.quantity < service.min_quantity or order_data.quantity > service.max_quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be between {} and {}".format(service.min_quantity, service.max_quantity)
        )
    
    # Calculate price
    original_price = (service.rate * order_data.quantity) / 1000
    discounted_price = calculate_discounted_price(original_price, current_user.tier_discount)
    
    # Check user balance
    if current_user.balance < discounted_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance"
        )
    
    try:
        # Create order with BUMX API
        bumx_client = BUMXClient()
        bumx_response = await bumx_client.create_order(
            service.provider_service_id,
            order_data.link,
            order_data.quantity
        )
        
        # Create order in database
        new_order = Order(
            user_id=current_user.id,
            service_id=service.id,
            link=order_data.link,
            quantity=order_data.quantity,
            charge=discounted_price,
            status="processing",
            bumx_order_id=bumx_response.get("order_id")
        )
        
        db.add(new_order)
        
        # Deduct balance
        current_user.balance -= discounted_price
        current_user.total_spent += discounted_price
        
        # Update tier if needed
        new_tier_level, new_tier_name, new_tier_discount = calculate_tier(current_user.total_spent)
        if new_tier_level != current_user.tier_level:
            current_user.tier_level = new_tier_level
            current_user.tier_name = new_tier_name
            current_user.tier_discount = new_tier_discount
        
        # Create transaction record
        transaction = Transaction(
            user_id=current_user.id,
            type="order",
            amount=-discounted_price,
            balance_before=current_user.balance + discounted_price,
            balance_after=current_user.balance,
            description="Order for {} - {} quantity".format(service.name, order_data.quantity)
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(new_order)
        
        # Send Telegram notification
        try:
            telegram_bot = TelegramBot()
            await telegram_bot.notify_new_order(
                new_order.id,
                current_user.username,
                service.name,
                discounted_price
            )
        except Exception as e:
            # Log error but don't fail the order
            print("Telegram notification failed: {}".format(str(e)))
        
        return new_order
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create order: {}".format(str(e))
        )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific order by ID
    """
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order


@router.get("/", response_model=list)
async def get_orders(
    status_filter: str = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user orders with optional status filter
    """
    query = db.query(Order).filter(Order.user_id == current_user.id)
    
    if status_filter:
        query = query.filter(Order.status == status_filter)
    
    orders = query.order_by(Order.created_at.desc()).all()
    return orders
