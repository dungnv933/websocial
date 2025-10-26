"""
Payment API endpoints for SMM Panel
"""
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.database import get_db
from app.models.deposit import Deposit
from app.models.user import User
from app.models.transaction import Transaction
from app.utils.sepay import SepayWebhook
from app.utils.telegram import TelegramBot
from app.dependencies import get_current_user

router = APIRouter()


@router.post("/deposit")
async def create_deposit(
    amount: float,
    method: str = "bank_transfer",
    bank_name: str = "ACB",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create deposit request
    """
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be greater than 0"
        )
    
    # Create deposit record
    new_deposit = Deposit(
        user_id=current_user.id,
        amount=amount,
        method=method,
        bank_name=bank_name,
        status="pending"
    )
    
    db.add(new_deposit)
    db.commit()
    db.refresh(new_deposit)
    
    return {
        "deposit_id": new_deposit.id,
        "amount": amount,
        "method": method,
        "bank_name": bank_name,
        "status": "pending",
        "message": "Deposit request created. Please transfer to bank account."
    }


@router.post("/sepay/webhook")
async def sepay_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Sepay webhook for deposit confirmation
    """
    # Get raw body and signature
    body = await request.body()
    signature = request.headers.get("X-Sepay-Signature", "")
    
    # Verify signature
    sepay_webhook = SepayWebhook()
    if not sepay_webhook.verify_signature(body.decode(), signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )
    
    # Parse webhook data
    import json
    webhook_data = json.loads(body.decode())
    deposit_data = sepay_webhook.parse_webhook_data(webhook_data)
    
    # Find deposit
    deposit = db.query(Deposit).filter(
        Deposit.id == deposit_data.get("deposit_id"),
        Deposit.status == "pending"
    ).first()
    
    if not deposit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit not found"
        )
    
    # Update deposit status
    deposit.status = "approved"
    deposit.transaction_id = deposit_data.get("transaction_id")
    
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
            description="Deposit via {} - {}".format(deposit.bank_name, deposit.transaction_id)
        )
        
        db.add(transaction)
        db.commit()
        
        # Send Telegram notification
        try:
            telegram_bot = TelegramBot()
            await telegram_bot.notify_deposit_approved(user.username, deposit.amount)
        except Exception as e:
            # Log error but don't fail the deposit
            print("Telegram notification failed: {}".format(str(e)))
    
    return {"status": "success", "message": "Deposit processed successfully"}
