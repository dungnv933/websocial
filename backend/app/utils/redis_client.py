"""
Redis client cho caching
"""

import json
import logging
from typing import Optional, Any
import redis.asyncio as redis

from app.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Redis client để cache data
    """
    
    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self.client: Optional[redis.Redis] = None
    
    async def connect(self):
        """
        Kết nối đến Redis
        """
        try:
            self.client = redis.from_url(self.redis_url, decode_responses=True)
            await self.client.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """
        Ngắt kết nối Redis
        """
        if self.client:
            await self.client.close()
            logger.info("Disconnected from Redis")
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Lấy data từ cache
        """
        if not self.client:
            await self.connect()
        
        try:
            data = await self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Lưu data vào cache với TTL
        """
        if not self.client:
            await self.connect()
        
        try:
            data = json.dumps(value)
            await self.client.setex(key, ttl, data)
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Xóa data từ cache
        """
        if not self.client:
            await self.connect()
        
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Kiểm tra key có tồn tại không
        """
        if not self.client:
            await self.connect()
        
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False


# Global Redis client instance
redis_client = RedisClient()


async def get_redis_client() -> RedisClient:
    """
    Dependency để lấy Redis client
    """
    return redis_client
