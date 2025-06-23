"""
Redis Cache Implementation
Redis缓存实现 - [cache][redis_cache]
"""

import json
import pickle
from typing import Any, Optional, Union, Dict, List
from datetime import datetime, timedelta
import redis.asyncio as redis
import logging


class RedisCache:
    """
    Redis缓存实现
    [cache][redis_cache]
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化Redis缓存
        [cache][redis_cache][init]
        """
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        
        # Redis连接配置
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 6379)
        self.db = config.get("db", 0)
        self.password = config.get("password")
        self.max_connections = config.get("max_connections", 20)
        
        # 缓存配置
        self.default_expire = config.get("default_expire", 3600)  # 1小时
        self.key_prefix = config.get("key_prefix", "datasay:")
        self.serialization = config.get("serialization", "json")  # json, pickle
        
        # Redis连接池
        self.redis_pool: Optional[redis.ConnectionPool] = None
        self.redis_client: Optional[redis.Redis] = None
    
    async def redis_cache_initialize(self) -> bool:
        """
        初始化Redis连接
        [cache][redis_cache][initialize]
        """
        try:
            # 创建连接池
            self.redis_pool = redis.ConnectionPool(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                max_connections=self.max_connections,
                decode_responses=False  # 保持二进制模式以支持pickle
            )
            
            # 创建Redis客户端
            self.redis_client = redis.Redis(connection_pool=self.redis_pool)
            
            # 测试连接
            await self.redis_client.ping()
            
            self.logger.info("Redis cache initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Redis cache: {str(e)}")
            return False
    
    async def redis_cache_cleanup(self):
        """
        清理Redis连接
        [cache][redis_cache][cleanup]
        """
        if self.redis_client:
            await self.redis_client.close()
        
        if self.redis_pool:
            await self.redis_pool.disconnect()
        
        self.logger.info("Redis cache cleaned up")
    
    def _get_cache_key(self, key: str) -> str:
        """
        获取完整的缓存键
        [cache][redis_cache][_get_cache_key]
        """
        return f"{self.key_prefix}{key}"
    
    def _serialize_value(self, value: Any) -> bytes:
        """
        序列化值
        [cache][redis_cache][_serialize_value]
        """
        try:
            if self.serialization == "json":
                return json.dumps(value, ensure_ascii=False).encode('utf-8')
            elif self.serialization == "pickle":
                return pickle.dumps(value)
            else:
                # 默认转为字符串
                return str(value).encode('utf-8')
        except Exception as e:
            self.logger.error(f"Failed to serialize value: {str(e)}")
            raise
    
    def _deserialize_value(self, data: bytes) -> Any:
        """
        反序列化值
        [cache][redis_cache][_deserialize_value]
        """
        try:
            if self.serialization == "json":
                return json.loads(data.decode('utf-8'))
            elif self.serialization == "pickle":
                return pickle.loads(data)
            else:
                # 默认解码为字符串
                return data.decode('utf-8')
        except Exception as e:
            self.logger.error(f"Failed to deserialize value: {str(e)}")
            raise
    
    async def redis_cache_get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        [cache][redis_cache][get]
        """
        try:
            if not self.redis_client:
                return None
            
            cache_key = self._get_cache_key(key)
            data = await self.redis_client.get(cache_key)
            
            if data is None:
                return None
            
            return self._deserialize_value(data)
            
        except Exception as e:
            self.logger.error(f"Failed to get cache key '{key}': {str(e)}")
            return None
    
    async def redis_cache_set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """
        设置缓存值
        [cache][redis_cache][set]
        """
        try:
            if not self.redis_client:
                return False
            
            cache_key = self._get_cache_key(key)
            serialized_value = self._serialize_value(value)
            expire_time = expire or self.default_expire
            
            await self.redis_client.setex(cache_key, expire_time, serialized_value)
            
            self.logger.debug(f"Set cache key '{key}' with expire {expire_time}s")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set cache key '{key}': {str(e)}")
            return False
    
    async def redis_cache_delete(self, key: str) -> bool:
        """
        删除缓存值
        [cache][redis_cache][delete]
        """
        try:
            if not self.redis_client:
                return False
            
            cache_key = self._get_cache_key(key)
            result = await self.redis_client.delete(cache_key)
            
            self.logger.debug(f"Deleted cache key '{key}': {result > 0}")
            return result > 0
            
        except Exception as e:
            self.logger.error(f"Failed to delete cache key '{key}': {str(e)}")
            return False
    
    async def redis_cache_exists(self, key: str) -> bool:
        """
        检查缓存键是否存在
        [cache][redis_cache][exists]
        """
        try:
            if not self.redis_client:
                return False
            
            cache_key = self._get_cache_key(key)
            result = await self.redis_client.exists(cache_key)
            
            return result > 0
            
        except Exception as e:
            self.logger.error(f"Failed to check cache key '{key}': {str(e)}")
            return False
    
    async def redis_cache_expire(self, key: str, seconds: int) -> bool:
        """
        设置缓存过期时间
        [cache][redis_cache][expire]
        """
        try:
            if not self.redis_client:
                return False
            
            cache_key = self._get_cache_key(key)
            result = await self.redis_client.expire(cache_key, seconds)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to set expire for cache key '{key}': {str(e)}")
            return False
    
    async def redis_cache_ttl(self, key: str) -> int:
        """
        获取缓存剩余时间（秒）
        [cache][redis_cache][ttl]
        """
        try:
            if not self.redis_client:
                return -1
            
            cache_key = self._get_cache_key(key)
            return await self.redis_client.ttl(cache_key)
            
        except Exception as e:
            self.logger.error(f"Failed to get TTL for cache key '{key}': {str(e)}")
            return -1
    
    async def redis_cache_increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        增加缓存值
        [cache][redis_cache][increment]
        """
        try:
            if not self.redis_client:
                return None
            
            cache_key = self._get_cache_key(key)
            result = await self.redis_client.incrby(cache_key, amount)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to increment cache key '{key}': {str(e)}")
            return None
    
    async def redis_cache_decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """
        减少缓存值
        [cache][redis_cache][decrement]
        """
        try:
            if not self.redis_client:
                return None
            
            cache_key = self._get_cache_key(key)
            result = await self.redis_client.decrby(cache_key, amount)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to decrement cache key '{key}': {str(e)}")
            return None
    
    async def redis_cache_mget(self, keys: List[str]) -> Dict[str, Any]:
        """
        批量获取缓存值
        [cache][redis_cache][mget]
        """
        try:
            if not self.redis_client or not keys:
                return {}
            
            cache_keys = [self._get_cache_key(key) for key in keys]
            values = await self.redis_client.mget(cache_keys)
            
            result = {}
            for i, key in enumerate(keys):
                if values[i] is not None:
                    try:
                        result[key] = self._deserialize_value(values[i])
                    except Exception:
                        self.logger.warning(f"Failed to deserialize value for key '{key}'")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to mget cache keys: {str(e)}")
            return {}
    
    async def redis_cache_mset(self, mapping: Dict[str, Any], expire: Optional[int] = None) -> bool:
        """
        批量设置缓存值
        [cache][redis_cache][mset]
        """
        try:
            if not self.redis_client or not mapping:
                return False
            
            # 准备数据
            cache_mapping = {}
            for key, value in mapping.items():
                cache_key = self._get_cache_key(key)
                cache_mapping[cache_key] = self._serialize_value(value)
            
            # 批量设置
            await self.redis_client.mset(cache_mapping)
            
            # 设置过期时间
            if expire:
                for cache_key in cache_mapping.keys():
                    await self.redis_client.expire(cache_key, expire)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to mset cache keys: {str(e)}")
            return False
    
    async def redis_cache_clear_prefix(self, prefix: str = "") -> int:
        """
        清理指定前缀的缓存
        [cache][redis_cache][clear_prefix]
        """
        try:
            if not self.redis_client:
                return 0
            
            pattern = f"{self.key_prefix}{prefix}*"
            keys = []
            
            # 使用scan迭代获取键
            async for key in self.redis_client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                deleted = await self.redis_client.delete(*keys)
                self.logger.info(f"Cleared {deleted} cache keys with prefix '{prefix}'")
                return deleted
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Failed to clear cache with prefix '{prefix}': {str(e)}")
            return 0
    
    async def redis_cache_get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        [cache][redis_cache][get_stats]
        """
        try:
            if not self.redis_client:
                return {}
            
            info = await self.redis_client.info()
            
            return {
                "redis_version": info.get("redis_version"),
                "used_memory": info.get("used_memory"),
                "used_memory_human": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_connections_received": info.get("total_connections_received"),
                "total_commands_processed": info.get("total_commands_processed"),
                "keyspace_hits": info.get("keyspace_hits"),
                "keyspace_misses": info.get("keyspace_misses"),
                "expired_keys": info.get("expired_keys"),
                "evicted_keys": info.get("evicted_keys")
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get cache stats: {str(e)}")
            return {}
    
    async def redis_cache_health_check(self) -> bool:
        """
        健康检查
        [cache][redis_cache][health_check]
        """
        try:
            if not self.redis_client:
                return False
            
            # 简单的ping测试
            await self.redis_client.ping()
            return True
            
        except Exception as e:
            self.logger.error(f"Redis health check failed: {str(e)}")
            return False