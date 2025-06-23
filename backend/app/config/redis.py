"""
Redis Configuration
Redis配置管理 - [redis][config]
"""

import redis.asyncio as redis
from typing import Optional
import asyncio

from app.config.settings import app_config_get_settings

settings = app_config_get_settings()

class RedisClient:
    """
    Redis客户端类
    [redis][client]
    """
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
    
    async def redis_client_get(self) -> redis.Redis:
        """
        获取Redis客户端
        [redis][client][get]
        """
        if self._client is None:
            self._client = redis.from_url(
                settings.REDIS_URL,
                password=settings.REDIS_PASSWORD or None,
                db=settings.REDIS_DB,
                encoding="utf-8",
                decode_responses=True,
                retry_on_timeout=True,
                socket_keepalive=True,
                socket_keepalive_options={},
            )
        return self._client
    
    async def redis_connection_test(self) -> bool:
        """
        测试Redis连接
        [redis][connection][test]
        """
        try:
            client = await self.redis_client_get()
            await client.ping()
            return True
        except Exception as e:
            print(f"Redis connection failed: {e}")
            return False
    
    async def redis_client_close(self):
        """
        关闭Redis客户端
        [redis][client][close]
        """
        if self._client:
            await self._client.aclose()
            self._client = None

# 全局Redis客户端实例
redis_client_instance = RedisClient()

async def redis_client_get_global() -> redis.Redis:
    """
    获取全局Redis客户端
    [redis][client][get_global]
    """
    return await redis_client_instance.redis_client_get()

async def redis_cache_set(key: str, value: str, expire: int = 3600) -> bool:
    """
    设置缓存
    [redis][cache][set]
    """
    try:
        client = await redis_client_get_global()
        await client.setex(key, expire, value)
        return True
    except Exception:
        return False

async def redis_cache_get(key: str) -> Optional[str]:
    """
    获取缓存
    [redis][cache][get]
    """
    try:
        client = await redis_client_get_global()
        return await client.get(key)
    except Exception:
        return None

async def redis_cache_delete(key: str) -> bool:
    """
    删除缓存
    [redis][cache][delete]
    """
    try:
        client = await redis_client_get_global()
        await client.delete(key)
        return True
    except Exception:
        return False

async def redis_cache_exists(key: str) -> bool:
    """
    检查缓存是否存在
    [redis][cache][exists]
    """
    try:
        client = await redis_client_get_global()
        return await client.exists(key) > 0
    except Exception:
        return False