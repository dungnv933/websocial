"""
Telegram bot utilities for SMM Panel
"""
import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot for notifications"""
    
    def __init__(self):
        self.bot_token = settings.telegram_bot_token
        self.chat_id = settings.telegram_chat_id
    
    async def send_message(self, message: str) -> bool:
        """
        Send message to Telegram chat
        
        Args:
            message: Message to send
            
        Returns:
            True if message sent successfully
        """
        try:
            # For now, just log the message
            # In production, you would use python-telegram-bot library
            logger.info("Telegram notification: {}".format(message))
            return True
        except Exception as e:
            logger.error("Telegram send error: {}".format(str(e)))
            return False
    
    async def notify_new_order(self, order_id: int, username: str, service_name: str, amount: float) -> bool:
        """
        Send new order notification
        
        Args:
            order_id: Order ID
            username: Username
            service_name: Service name
            amount: Order amount
            
        Returns:
            True if notification sent successfully
        """
        message = "🆕 New Order\nOrder ID: {}\nUser: {}\nService: {}\nAmount: {:,} VND".format(
            order_id, username, service_name, amount
        )
        return await self.send_message(message)
    
    async def notify_deposit_approved(self, username: str, amount: float) -> bool:
        """
        Send deposit approved notification
        
        Args:
            username: Username
            amount: Deposit amount
            
        Returns:
            True if notification sent successfully
        """
        message = "💰 Deposit Approved\nUser: {}\nAmount: {:,} VND".format(username, amount)
        return await self.send_message(message)
    
    async def notify_order_completed(self, order_id: int, username: str, service_name: str) -> bool:
        """
        Send order completed notification
        
        Args:
            order_id: Order ID
            username: Username
            service_name: Service name
            
        Returns:
            True if notification sent successfully
        """
        message = "✅ Order Completed\nOrder ID: {}\nUser: {}\nService: {}".format(
            order_id, username, service_name
        )
        return await self.send_message(message)
    
    async def notify_order_failed(self, order_id: int, username: str, service_name: str, reason: str) -> bool:
        """
        Send order failed notification
        
        Args:
            order_id: Order ID
            username: Username
            service_name: Service name
            reason: Failure reason
            
        Returns:
            True if notification sent successfully
        """
        message = "❌ Order Failed\nOrder ID: {}\nUser: {}\nService: {}\nReason: {}".format(
            order_id, username, service_name, reason
        )
        return await self.send_message(message)

