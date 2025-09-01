import redis.asyncio as redis
import json
from typing import Optional, Any
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class RedisClient:
    """Redis client wrapper for caching operations"""
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or settings.REDIS_URL
        self.redis = None
    
    async def connect(self):
        """Connect to Redis"""
        if self.redis is None:
            self.redis = redis.from_url(self.redis_url)
            logger.info("Connected to Redis")
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
            self.redis = None
            logger.info("Disconnected from Redis")
    
    async def set(self, key: str, value: str, expire: int = 3600) -> None:
        """Set key-value pair with expiration"""
        await self.connect()
        await self.redis.set(key, value, ex=expire)
        logger.debug(f"Set cache key: {key}")
    
    async def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        await self.connect()
        value = await self.redis.get(key)
        if value:
            logger.debug(f"Cache hit for key: {key}")
        else:
            logger.debug(f"Cache miss for key: {key}")
        return value
    
    async def delete(self, key: str) -> None:
        """Delete key"""
        await self.connect()
        await self.redis.delete(key)
        logger.debug(f"Deleted cache key: {key}")
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        await self.connect()
        return await self.redis.exists(key) > 0
    
    async def health_check(self) -> bool:
        """Check Redis health"""
        try:
            await self.connect()
            await self.redis.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {str(e)}")
            return False

# Global Redis client instance
redis_client = RedisClient()
