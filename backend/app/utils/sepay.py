"""
Sepay webhook handler for SMM Panel
"""
import hashlib
import hmac
import logging
from typing import Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)


class SepayWebhook:
    """Sepay webhook handler"""
    
    def __init__(self):
        self.secret = settings.sepay_secret
    
    def verify_signature(self, payload: str, signature: str) -> bool:
        """
        Verify Sepay webhook signature
        
        Args:
            payload: Raw payload string
            signature: Signature from headers
            
        Returns:
            True if signature is valid
        """
        try:
            expected_signature = hmac.new(
                self.secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error("Signature verification error: {}".format(str(e)))
            return False
    
    def parse_webhook_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Sepay webhook data
        
        Args:
            data: Webhook payload data
            
        Returns:
            Parsed deposit information
        """
        try:
            return {
                "amount": float(data.get("amount", 0)),
                "transaction_id": data.get("transaction_id", ""),
                "bank_name": data.get("bank_name", "ACB"),
                "status": data.get("status", "pending"),
                "user_id": data.get("user_id"),
                "deposit_id": data.get("deposit_id")
            }
        except Exception as e:
            logger.error("Webhook data parsing error: {}".format(str(e)))
            raise
    
    def process_deposit(self, deposit_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process deposit from webhook
        
        Args:
            deposit_data: Parsed deposit data
            
        Returns:
            Processing result
        """
        try:
            # This would typically update database
            # For now, just log the processing
            logger.info("Processing deposit: {}".format(deposit_data))
            
            return {
                "success": True,
                "message": "Deposit processed successfully",
                "deposit_id": deposit_data.get("deposit_id")
            }
        except Exception as e:
            logger.error("Deposit processing error: {}".format(str(e)))
            return {
                "success": False,
                "message": "Deposit processing failed",
                "error": str(e)
            }

