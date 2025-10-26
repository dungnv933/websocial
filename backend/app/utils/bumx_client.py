"""
BUMX API Client cho SMM Panel
HTTP client để gọi BUMX API với retry logic và caching
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import httpx
import json

from app.config import settings

logger = logging.getLogger(__name__)


class BUMXAPIError(Exception):
    """
    Custom exception cho BUMX API errors
    """
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class BUMXClient:
    """
    BUMX API Client để gọi các services
    """
    
    def __init__(self):
        self.base_url = settings.BUMX_API_URL
        self.api_key = settings.BUMX_API_KEY
        self.timeout = 30.0
        self.max_retries = 3
        self.retry_delay = 1.0
    
    async def _make_request(
        self,
        endpoint: str,
        data: Optional[Dict] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Thực hiện HTTP request đến BUMX API với retry logic
        """
        url = f"{self.base_url}{endpoint}"
        
        # Prepare headers
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "SMM-Panel-Backend/1.0.0"
        }
        
        # Prepare data
        request_data = {"key": self.api_key}
        if data:
            request_data.update(data)
        
        try:
            logger.info(f"Making request to BUMX API: {url}")
            logger.debug(f"Request data: {request_data}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, data=request_data, headers=headers)
                
                logger.info(f"BUMX API response status: {response.status_code}")
                
                if response.status_code >= 400:
                    error_msg = f"BUMX API error: HTTP {response.status_code}"
                    logger.error(error_msg)
                    raise BUMXAPIError(
                        message=error_msg,
                        status_code=response.status_code
                    )
                
                response_data = response.json()
                logger.debug(f"BUMX API response: {response_data}")
                
                return response_data
                
        except httpx.TimeoutException:
            logger.error(f"BUMX API timeout: {url}")
            if retry_count < self.max_retries:
                logger.info(f"Retrying request (attempt {retry_count + 1}/{self.max_retries})")
                await asyncio.sleep(self.retry_delay * (retry_count + 1))
                return await self._make_request(endpoint, data, retry_count + 1)
            else:
                raise BUMXAPIError("BUMX API timeout after max retries")
                
        except httpx.RequestError as e:
            logger.error(f"BUMX API request error: {e}")
            if retry_count < self.max_retries:
                logger.info(f"Retrying request (attempt {retry_count + 1}/{self.max_retries})")
                await asyncio.sleep(self.retry_delay * (retry_count + 1))
                return await self._make_request(endpoint, data, retry_count + 1)
            else:
                raise BUMXAPIError(f"BUMX API request error: {str(e)}")
                
        except json.JSONDecodeError as e:
            logger.error(f"BUMX API JSON decode error: {e}")
            raise BUMXAPIError(f"Invalid JSON response: {str(e)}")
                
        except Exception as e:
            logger.error(f"BUMX API unexpected error: {e}")
            raise BUMXAPIError(f"Unexpected error: {str(e)}")
    
    async def get_services(self) -> List[Dict[str, Any]]:
        """
        Lấy danh sách services từ BUMX API
        """
        try:
            response = await self._make_request("/services")
            return response
        except BUMXAPIError:
            raise
        except Exception as e:
            logger.error(f"Error getting services: {e}")
            raise BUMXAPIError(f"Failed to get services: {str(e)}")
    
    async def create_order(
        self,
        service_id: int,
        link: str,
        quantity: int
    ) -> Dict[str, Any]:
        """
        Tạo order mới trên BUMX API
        """
        order_data = {
            "service": service_id,
            "link": link,
            "quantity": quantity
        }
        
        try:
            response = await self._make_request("/order", data=order_data)
            return response
        except BUMXAPIError:
            raise
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            raise BUMXAPIError(f"Failed to create order: {str(e)}")
    
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        Lấy trạng thái order từ BUMX API
        """
        try:
            response = await self._make_request("/order", data={"order": order_id})
            return response
        except BUMXAPIError:
            raise
        except Exception as e:
            logger.error(f"Error getting order status: {e}")
            raise BUMXAPIError(f"Failed to get order status: {str(e)}")
    
    async def get_balance(self) -> Dict[str, Any]:
        """
        Lấy balance từ BUMX API
        """
        try:
            response = await self._make_request("/balance")
            return response
        except BUMXAPIError:
            raise
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            raise BUMXAPIError(f"Failed to get balance: {str(e)}")


async def get_bumx_client() -> BUMXClient:
    """
    Dependency để lấy BUMX client
    """
    return BUMXClient()