import httpx
import os
from typing import Optional, Dict, Any

LIKEVIET_API_BASE = "https://likeviet.vn/api/v2"
LIKEVIET_API_KEY = os.getenv("LIKEVIET_API_KEY", "c827f930b6fbe6dc726f5ed7429b31b7")

class LikevietService:
    """Service for Likeviet API interactions"""
    
    def __init__(self):
        self.base_url = LIKEVIET_API_BASE
        self.api_key = LIKEVIET_API_KEY
    
    async def get_services(self) -> Dict[str, Any]:
        """Get available services from Likeviet"""
        async with httpx.AsyncClient() as client:
            payload = {
                "key": self.api_key,
                "action": "services"
            }
            try:
                response = await client.post(
                    self.base_url,
                    data=payload,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                return {"error": f"Request failed: {str(e)}"}
            except Exception as e:
                return {"error": f"Unexpected error: {str(e)}"}
    
    async def create_order(self, service_id: int, link: str, quantity: int) -> Dict[str, Any]:
        """Create new order for social media engagement"""
        async with httpx.AsyncClient() as client:
            payload = {
                "key": self.api_key,
                "action": "add",
                "service": service_id,
                "link": link,
                "quantity": quantity
            }
            try:
                response = await client.post(
                    self.base_url,
                    data=payload,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                return {"error": f"Request failed: {str(e)}"}
            except Exception as e:
                return {"error": f"Unexpected error: {str(e)}"}
    
    async def check_order_status(self, order_id: int) -> Dict[str, Any]:
        """Check order status"""
        async with httpx.AsyncClient() as client:
            payload = {
                "key": self.api_key,
                "action": "status",
                "order": order_id
            }
            try:
                response = await client.post(
                    self.base_url,
                    data=payload,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                return {"error": f"Request failed: {str(e)}"}
            except Exception as e:
                return {"error": f"Unexpected error: {str(e)}"}
    
    async def get_balance(self) -> Dict[str, Any]:
        """Get account balance"""
        async with httpx.AsyncClient() as client:
            payload = {
                "key": self.api_key,
                "action": "balance"
            }
            try:
                response = await client.post(
                    self.base_url,
                    data=payload,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                return {"error": f"Request failed: {str(e)}"}
            except Exception as e:
                return {"error": f"Unexpected error: {str(e)}"}

# Initialize service
likeviet_service = LikevietService()


import os
from typing import Optional, Dict, Any

LIKEVIET_API_BASE = "https://likeviet.vn/api/v2"
LIKEVIET_API_KEY = os.getenv("LIKEVIET_API_KEY", "c827f930b6fbe6dc726f5ed7429b31b7")

class LikevietService:
    """Service for Likeviet API interactions"""
    
    def __init__(self):
        self.base_url = LIKEVIET_API_BASE
        self.api_key = LIKEVIET_API_KEY
    
    async def get_services(self) -> Dict[str, Any]:
        """Get available services from Likeviet"""
        async with httpx.AsyncClient() as client:
            payload = {
                "key": self.api_key,
                "action": "services"
            }
            try:
                response = await client.post(
                    self.base_url,
                    data=payload,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                return {"error": f"Request failed: {str(e)}"}
            except Exception as e:
                return {"error": f"Unexpected error: {str(e)}"}
    
    async def create_order(self, service_id: int, link: str, quantity: int) -> Dict[str, Any]:
        """Create new order for social media engagement"""
        async with httpx.AsyncClient() as client:
            payload = {
                "key": self.api_key,
                "action": "add",
                "service": service_id,
                "link": link,
                "quantity": quantity
            }
            try:
                response = await client.post(
                    self.base_url,
                    data=payload,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                return {"error": f"Request failed: {str(e)}"}
            except Exception as e:
                return {"error": f"Unexpected error: {str(e)}"}
    
    async def check_order_status(self, order_id: int) -> Dict[str, Any]:
        """Check order status"""
        async with httpx.AsyncClient() as client:
            payload = {
                "key": self.api_key,
                "action": "status",
                "order": order_id
            }
            try:
                response = await client.post(
                    self.base_url,
                    data=payload,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                return {"error": f"Request failed: {str(e)}"}
            except Exception as e:
                return {"error": f"Unexpected error: {str(e)}"}
    
    async def get_balance(self) -> Dict[str, Any]:
        """Get account balance"""
        async with httpx.AsyncClient() as client:
            payload = {
                "key": self.api_key,
                "action": "balance"
            }
            try:
                response = await client.post(
                    self.base_url,
                    data=payload,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                return {"error": f"Request failed: {str(e)}"}
            except Exception as e:
                return {"error": f"Unexpected error: {str(e)}"}

# Initialize service
likeviet_service = LikevietService()



