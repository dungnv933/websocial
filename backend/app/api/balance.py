"""
Balance API endpoints
"""

from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.transaction import Transaction, TransactionType
from app.schemas.service import BalanceResponse, DepositRequest
from app.dependencies import get_current_active_user

router = APIRouter()


@router.get("/", response_model=BalanceResponse)
async def get_balance(
    current_user: User = Depends(get_current_active_user)
):
    """
    Lấy số dư hiện tại của user
    """
    return BalanceResponse(
        balance=float(current_user.balance),
        currency="USD"
    )


@router.post("/deposit")
async def deposit_balance(
    deposit_data: DepositRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Nạp tiền vào tài khoản (mock implementation)
    """
    try:
        amount = Decimal(str(deposit_data.amount))
        
        # Tạo transaction
        transaction = Transaction(
            user_id=current_user.id,
            type=TransactionType.DEPOSIT,
            amount=amount,
            balance_before=current_user.balance,
            balance_after=current_user.balance + amount,
            description=f"Nạp tiền ${amount}"
        )
        
        # Cập nhật balance
        current_user.add_balance(amount)
        
        db.add(transaction)
        await db.commit()
        
        return {
            "message": f"Nạp tiền thành công ${amount}",
            "new_balance": float(current_user.balance),
            "transaction_id": str(transaction.id)
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi nạp tiền: {str(e)}"
        )


@router.get("/transactions")
async def get_transaction_history(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy lịch sử giao dịch của user
    """
    try:
        result = await db.execute(
            select(Transaction)
            .where(Transaction.user_id == current_user.id)
            .order_by(Transaction.created_at.desc())
            .limit(50)
        )
        transactions = result.scalars().all()
        
        return {
            "transactions": [
                {
                    "id": str(t.id),
                    "type": t.type.value,
                    "amount": float(t.amount),
                    "balance_before": float(t.balance_before),
                    "balance_after": float(t.balance_after),
                    "description": t.description,
                    "created_at": t.created_at.isoformat()
                }
                for t in transactions
            ],
            "total": len(transactions)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy lịch sử giao dịch: {str(e)}"
        )
