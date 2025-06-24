"""
Cache Configuration Module
缓存配置模块 - [core][cache_config]
"""

import asyncio
import json
import hashlib
from typing import Optional, Any, Union, Dict
from datetime import timedelta
import redis.asyncio as redis
import logging

from app.config.settings import app_config_get_settings
from app.core.logging_config import get_logger

logger = get_logger("app.core.cache_config")


class CacheManager:
    """
    缓存管理器
    [core][cache_config][cache_manager]
    """
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.memory_cache: Dict[str, Any] = {}
        self.use_redis = True
        
    async def cache_manager_initialize(self):
        """
        初始化缓存管理器
        [core][cache_config][cache_manager][initialize]
        """
        try:
            settings = app_config_get_settings()
            self.redis_client = redis.from_url(settings.REDIS_URL)
            
            # 测试Redis连接
            await self.redis_client.ping()
            self.use_redis = True
            logger.info("Cache manager initialized with Redis backend")
            
        except Exception as e:
            logger.warning(f"Redis connection failed, falling back to memory cache: {str(e)}")
            self.use_redis = False
            self.redis_client = None
    
    def _cache_manager_generate_key(self, key: str, namespace: str = "default") -> str:
        """
        生成缓存键
        [core][cache_config][cache_manager][generate_key]
        """
        return f"datasay:cache:{namespace}:{key}"
    
    def _cache_manager_serialize_value(self, value: Any) -> str:
        """
        序列化缓存值
        [core][cache_config][cache_manager][serialize_value]
        """
        try:
            return json.dumps(value, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(value)
    
    def _cache_manager_deserialize_value(self, value: str) -> Any:
        """
        反序列化缓存值
        [core][cache_config][cache_manager][deserialize_value]
        """
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    async def cache_manager_set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        namespace: str = "default"
    ) -> bool:
        """
        设置缓存值
        [core][cache_config][cache_manager][set]
        """
        cache_key = self._cache_manager_generate_key(key, namespace)
        serialized_value = self._cache_manager_serialize_value(value)
        
        try:
            if self.use_redis and self.redis_client:
                if ttl:
                    await self.redis_client.setex(cache_key, ttl, serialized_value)
                else:
                    await self.redis_client.set(cache_key, serialized_value)
            else:
                # 内存缓存
                self.memory_cache[cache_key] = {
                    "value": serialized_value,
                    "ttl": ttl,
                    "created_at": asyncio.get_event_loop().time()
                }
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set cache key {cache_key}: {str(e)}")
            return False
    
    async def cache_manager_get(
        self, 
        key: str, 
        namespace: str = "default"
    ) -> Optional[Any]:
        """
        获取缓存值
        [core][cache_config][cache_manager][get]
        """
        cache_key = self._cache_manager_generate_key(key, namespace)
        
        try:
            if self.use_redis and self.redis_client:
                value = await self.redis_client.get(cache_key)
                if value:
                    return self._cache_manager_deserialize_value(value.decode('utf-8'))
            else:
                # 内存缓存
                if cache_key in self.memory_cache:
                    cache_data = self.memory_cache[cache_key]
                    
                    # 检查TTL
                    if cache_data["ttl"]:
                        current_time = asyncio.get_event_loop().time()
                        if current_time - cache_data["created_at"] > cache_data["ttl"]:
                            del self.memory_cache[cache_key]
                            return None
                    
                    return self._cache_manager_deserialize_value(cache_data["value"])
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get cache key {cache_key}: {str(e)}")
            return None
    
    async def cache_manager_delete(
        self, 
        key: str, 
        namespace: str = "default"
    ) -> bool:
        """
        删除缓存值
        [core][cache_config][cache_manager][delete]
        """
        cache_key = self._cache_manager_generate_key(key, namespace)
        
        try:
            if self.use_redis and self.redis_client:
                await self.redis_client.delete(cache_key)
            else:
                self.memory_cache.pop(cache_key, None)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete cache key {cache_key}: {str(e)}")
            return False
    
    async def cache_manager_exists(
        self, 
        key: str, 
        namespace: str = "default"
    ) -> bool:
        """
        检查缓存键是否存在
        [core][cache_config][cache_manager][exists]
        """
        cache_key = self._cache_manager_generate_key(key, namespace)
        
        try:
            if self.use_redis and self.redis_client:
                return bool(await self.redis_client.exists(cache_key))
            else:
                return cache_key in self.memory_cache
                
        except Exception as e:
            logger.error(f"Failed to check cache key existence {cache_key}: {str(e)}")
            return False
    
    async def cache_manager_clear_namespace(self, namespace: str = "default") -> bool:
        """
        清空指定命名空间的缓存
        [core][cache_config][cache_manager][clear_namespace]
        """
        try:
            if self.use_redis and self.redis_client:
                pattern = f"datasay:cache:{namespace}:*"
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
            else:
                # 内存缓存
                pattern = f"datasay:cache:{namespace}:"
                keys_to_delete = [key for key in self.memory_cache.keys() if key.startswith(pattern)]
                for key in keys_to_delete:
                    del self.memory_cache[key]
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear namespace {namespace}: {str(e)}")
            return False
    
    async def cache_manager_get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        [core][cache_config][cache_manager][get_stats]
        """
        stats = {
            "backend": "redis" if self.use_redis else "memory",
            "connected": False,
            "total_keys": 0
        }
        
        try:
            if self.use_redis and self.redis_client:
                info = await self.redis_client.info()
                stats["connected"] = True
                stats["total_keys"] = info.get("db0", {}).get("keys", 0)
                stats["memory_usage"] = info.get("used_memory_human", "N/A")
            else:
                stats["connected"] = True
                stats["total_keys"] = len(self.memory_cache)
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {str(e)}")
        
        return stats


# 全局缓存管理器实例
cache_manager = CacheManager()


def cache_key_generate(prefix: str, *args, **kwargs) -> str:
    """
    生成缓存键的辅助函数
    [core][cache_config][cache_key_generate]
    """
    # 创建唯一的键
    key_parts = [prefix]
    
    # 添加位置参数
    for arg in args:
        key_parts.append(str(arg))
    
    # 添加关键字参数（按键排序确保一致性）
    if kwargs:
        sorted_kwargs = sorted(kwargs.items())
        for k, v in sorted_kwargs:
            key_parts.append(f"{k}:{v}")
    
    # 组合并生成哈希
    key_string = ":".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


class cached:
    """
    缓存装饰器
    [core][cache_config][cached]
    """
    
    def __init__(
        self, 
        ttl: Optional[int] = 3600,
        namespace: str = "function",
        key_prefix: str = ""
    ):
        self.ttl = ttl
        self.namespace = namespace
        self.key_prefix = key_prefix
    
    def __call__(self, func):
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            func_name = f"{func.__module__}.{func.__name__}"
            cache_key = cache_key_generate(
                self.key_prefix or func_name,
                *args,
                **kwargs
            )
            
            # 尝试从缓存获取
            cached_result = await cache_manager.cache_manager_get(
                cache_key, 
                self.namespace
            )
            
            if cached_result is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_result
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 存储到缓存
            await cache_manager.cache_manager_set(
                cache_key,
                result,
                self.ttl,
                self.namespace
            )
            
            logger.debug(f"Cache miss, stored result for key: {cache_key}")
            return result
        
        return wrapper


async def cache_config_initialize():
    """
    初始化缓存配置
    [core][cache_config][initialize]
    """
    await cache_manager.cache_manager_initialize()
    logger.info("Cache configuration initialized")


async def cache_config_cleanup():
    """
    清理缓存资源
    [core][cache_config][cleanup]
    """
    try:
        if cache_manager.redis_client:
            await cache_manager.redis_client.close()
        logger.info("Cache resources cleaned up")
    except Exception as e:
        logger.error(f"Error cleaning up cache resources: {str(e)}")