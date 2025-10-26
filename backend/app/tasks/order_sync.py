"""
Background task for syncing order status with BUMX API
"""
import asyncio
import logging
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.order import Order
from app.utils.bumx import BUMXClient
from app.utils.telegram import TelegramBot

logger = logging.getLogger(__name__)


async def sync_order_status(order_id: int):
    """
    Sync order status with BUMX API
    
    Args:
        order_id: Order ID to sync
    """
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order or not order.bumx_order_id:
            return
        
        # Get status from BUMX API
        bumx_client = BUMXClient()
        bumx_status = await bumx_client.get_order_status(order.bumx_order_id)
        
        # Update order status
        new_status = bumx_status.get("status", order.status)
        if new_status != order.status:
            order.status = new_status
            db.commit()
            
            # Send Telegram notification
            telegram_bot = TelegramBot()
            if new_status == "completed":
                await telegram_bot.notify_order_completed(
                    order.id,
                    order.user.username,
                    order.service.name
                )
            elif new_status == "cancelled":
                await telegram_bot.notify_order_failed(
                    order.id,
                    order.user.username,
                    order.service.name,
                    "Order cancelled"
                )
            
            logger.info("Order {} status updated to {}".format(order_id, new_status))
    
    except Exception as e:
        logger.error("Error syncing order {}: {}".format(order_id, str(e)))
    finally:
        db.close()


async def sync_all_pending_orders():
    """
    Sync all pending orders with BUMX API
    """
    db = SessionLocal()
    try:
        pending_orders = db.query(Order).filter(
            Order.status.in_(["pending", "processing"])
        ).all()
        
        for order in pending_orders:
            await sync_order_status(order.id)
            await asyncio.sleep(1)  # Rate limiting
    
    except Exception as e:
        logger.error("Error syncing pending orders: {}".format(str(e)))
    finally:
        db.close()


async def start_order_sync_task():
    """
    Start background task for order sync
    """
    while True:
        try:
            await sync_all_pending_orders()
            await asyncio.sleep(300)  # Sync every 5 minutes
        except Exception as e:
            logger.error("Order sync task error: {}".format(str(e)))
            await asyncio.sleep(60)  # Wait 1 minute before retry

