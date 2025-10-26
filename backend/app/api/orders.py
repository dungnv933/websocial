"""
Orders API endpoints
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models.user import User
from app.models.order import Order, OrderStatus
from app.models.transaction import Transaction, TransactionType
from app.schemas.order import OrderCreate, OrderResponse, OrderHistoryResponse
from app.utils.bumx_client import get_bumx_client, BUMXClient
from app.dependencies import get_current_active_user

router = APIRouter()


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    bumx_client: BUMXClient = Depends(get_bumx_client)
):
    """
    Tạo order mới
    """
    try:
        # Lấy thông tin service để tính giá (mock - trong thực tế sẽ lấy từ BUMX API)
        service_rate = 0.01  # $0.01 per unit (mock)
        total_price = Decimal(str(service_rate * order_data.quantity))
        
        # Kiểm tra balance
        if current_user.balance < total_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Số dư không đủ để tạo order"
            )
        
        # Tạo order
        order = Order(
            user_id=current_user.id,
            service_id=order_data.service_id,
            service_name=f"Service {order_data.service_id}",  # Mock name
            link=order_data.link,
            quantity=order_data.quantity,
            price=total_price,
            status=OrderStatus.PENDING
        )
        
        db.add(order)
        await db.flush()  # Để lấy order ID
        
        # Tạo transaction để trừ tiền
        transaction = Transaction(
            user_id=current_user.id,
            type=TransactionType.ORDER_PAYMENT,
            amount=total_price,
            balance_before=current_user.balance,
            balance_after=current_user.balance - total_price,
            description=f"Thanh toán order {order.id}"
        )
        
        # Cập nhật balance user
        current_user.balance -= total_price
        
        db.add(transaction)
        await db.commit()
        await db.refresh(order)
        
        # Gửi order đến BUMX API (async)
        try:
            bumx_response = await bumx_client.create_order(
                service_id=order_data.service_id,
                link=order_data.link,
                quantity=order_data.quantity
            )
            
            # Cập nhật BUMX order ID
            order.bumx_order_id = bumx_response.get("order")
            order.status = OrderStatus.PROCESSING
            
            await db.commit()
            
        except Exception as e:
            # Log error nhưng không fail order
            print(f"BUMX API error: {e}")
        
        return order
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo order: {str(e)}"
        )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy chi tiết order
    """
    try:
        result = await db.execute(
            select(Order).where(
                Order.id == order_id,
                Order.user_id == current_user.id
            )
        )
        order = result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order không tồn tại"
            )
        
        return order
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy chi tiết order: {str(e)}"
        )


@router.get("/history", response_model=OrderHistoryResponse)
async def get_order_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy lịch sử orders của user với phân trang
    """
    try:
        # Tính offset
        offset = (page - 1) * per_page
        
        # Query orders
        query = select(Order).where(Order.user_id == current_user.id).order_by(desc(Order.created_at))
        
        # Count total
        count_query = select(Order).where(Order.user_id == current_user.id)
        total_result = await db.execute(count_query)
        total = len(total_result.scalars().all())
        
        # Pagination
        query = query.offset(offset).limit(per_page)
        result = await db.execute(query)
        orders = result.scalars().all()
        
        # Tính total pages
        total_pages = (total + per_page - 1) // per_page
        
        return OrderHistoryResponse(
            orders=orders,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy lịch sử orders: {str(e)}"
        )