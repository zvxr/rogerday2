import os
import json
import redis.asyncio as redis
from typing import Optional, Any
from app.logger import get_logger

logger = get_logger("cache")


class RedisCache:
    """Redis cache client for storing Claude summaries"""
    
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.client: Optional[redis.Redis] = None
        self.cache_minutes = int(os.getenv("ANTHROPIC_SUMMARY_CACHE_MINUTES", "60"))
        
        logger.info(f"Redis cache initialized with URL: {self.redis_url}")
        logger.info(f"Cache TTL set to {self.cache_minutes} minutes")
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.client = redis.from_url(self.redis_url, decode_responses=True)
            await self.client.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            self.client = None
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()
            logger.info("Disconnected from Redis")
    
    def _generate_cache_key(self, user_id: str, patient_id: int, form_id: int) -> str:
        """Generate a unique cache key for a summary"""
        return f"summary:{user_id}:{patient_id}:{form_id}"
    
    async def get_summary(self, user_id: str, patient_id: int, form_id: int) -> Optional[dict]:
        """Get a cached summary"""
        if not self.client:
            logger.warning("Redis client not available")
            return None
        
        try:
            cache_key = self._generate_cache_key(user_id, patient_id, form_id)
            cached_data = await self.client.get(cache_key)
            
            if cached_data:
                logger.info(f"Cache hit for key: {cache_key}")
                return json.loads(cached_data)
            else:
                logger.info(f"Cache miss for key: {cache_key}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting cached summary: {str(e)}")
            return None
    
    async def set_summary(self, user_id: str, patient_id: int, form_id: int, summary_data: dict) -> bool:
        """Cache a summary"""
        if not self.client:
            logger.warning("Redis client not available")
            return False
        
        try:
            cache_key = self._generate_cache_key(user_id, patient_id, form_id)
            cache_value = json.dumps(summary_data)
            
            # Set with TTL in seconds
            ttl_seconds = self.cache_minutes * 60
            await self.client.setex(cache_key, ttl_seconds, cache_value)
            
            logger.info(f"Cached summary for key: {cache_key} with TTL: {self.cache_minutes} minutes")
            return True
            
        except Exception as e:
            logger.error(f"Error caching summary: {str(e)}")
            return False
    
    async def delete_summary(self, user_id: str, patient_id: int, form_id: int) -> bool:
        """Delete a cached summary"""
        if not self.client:
            logger.warning("Redis client not available")
            return False
        
        try:
            cache_key = self._generate_cache_key(user_id, patient_id, form_id)
            result = await self.client.delete(cache_key)
            
            if result:
                logger.info(f"Deleted cached summary for key: {cache_key}")
            else:
                logger.info(f"No cached summary found to delete for key: {cache_key}")
            
            return bool(result)
            
        except Exception as e:
            logger.error(f"Error deleting cached summary: {str(e)}")
            return False


# Global cache instance
cache_client = None


async def get_cache_client() -> RedisCache:
    """Get or create cache client instance"""
    global cache_client
    if cache_client is None:
        cache_client = RedisCache()
        await cache_client.connect()
    return cache_client


async def close_cache_client():
    """Close the cache client connection"""
    global cache_client
    if cache_client:
        await cache_client.disconnect()
        cache_client = None 