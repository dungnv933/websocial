"""
BUMX API client for SMM Panel
"""
import httpx
import logging
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class BUMXClient:
    """BUMX API client"""
    
    def __init__(self):
        self.api_key = settings.bumx_api_key
        self.base_url = settings.bumx_api_url
        self.headers = {
            "Authorization": "Bearer {}".format(self.api_key),
            "Content-Type": "application/json"
        }
    
    async def create_order(self, service_id: str, link: str, quantity: int) -> Dict[str, Any]:
        """
        Create order with BUMX API
        
        Args:
            service_id: BUMX service ID
            link: Target link
            quantity: Order quantity
            
        Returns:
            API response with order details
        """
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "service": service_id,
                    "link": link,
                    "quantity": quantity
                }
                
                response = await client.post(
                    "{}/services/order".format(self.base_url),
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info("BUMX order created successfully: {}".format(result))
                    return result
                else:
                    logger.error("BUMX API error: {} - {}".format(response.status_code, response.text))
                    raise Exception("BUMX API error: {}".format(response.status_code))
                    
        except httpx.TimeoutException:
            logger.error("BUMX API timeout")
            raise Exception("BUMX API timeout")
        except Exception as e:
            logger.error("BUMX API error: {}".format(str(e)))
            raise
    
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        Get order status from BUMX API
        
        Args:
            order_id: BUMX order ID
            
        Returns:
            Order status information
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "{}/orders/{}".format(self.base_url, order_id),
                    headers=self.headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error("BUMX API error: {} - {}".format(response.status_code, response.text))
                    raise Exception("BUMX API error: {}".format(response.status_code))
                    
        except httpx.TimeoutException:
            logger.error("BUMX API timeout")
            raise Exception("BUMX API timeout")
        except Exception as e:
            logger.error("BUMX API error: {}".format(str(e)))
            raise
    
    async def get_services(self) -> Dict[str, Any]:
        """
        Get available services from BUMX API
        
        Returns:
            List of available services
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "{}/services".format(self.base_url),
                    headers=self.headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error("BUMX API error: {} - {}".format(response.status_code, response.text))
                    raise Exception("BUMX API error: {}".format(response.status_code))
                    
        except httpx.TimeoutException:
            logger.error("BUMX API timeout")
            raise Exception("BUMX API timeout")
        except Exception as e:
            logger.error("BUMX API error: {}".format(str(e)))
            raise

