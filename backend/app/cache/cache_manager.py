"""
Cache Manager
缓存管理器 - [cache][cache_manager]
"""

import asyncio
import logging
from typing import Any, Optional, Dict, List, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

from .redis_cache import RedisCache
from .memory_cache import MemoryCache


class CacheLevel(Enum):
    """
    缓存级别枚举
    [cache][cache_manager][cache_level]
    """
    MEMORY_ONLY = "memory_only"
    REDIS_ONLY = "redis_only"
    MEMORY_FIRST = "memory_first"  # 内存优先，回退到Redis
    REDIS_FIRST = "redis_first"    # Redis优先，回退到内存
    BOTH = "both"                  # 同时写入两个缓存


@dataclass
class CacheConfig:
    """
    缓存配置
    [cache][cache_manager][cache_config]
    """
    level: CacheLevel = CacheLevel.MEMORY_FIRST
    default_expire: int = 3600
    enable_stats: bool = True
    memory_config: Optional[Dict[str, Any]] = None
    redis_config: Optional[Dict[str, Any]] = None


class CacheManager:
    """
    缓存管理器
    统一管理内存缓存和Redis缓存
    [cache][cache_manager]
    """
    
    def __init__(self, config: CacheConfig):
        """
        初始化缓存管理器
        [cache][cache_manager][init]
        """
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        
        # 缓存实例
        self.memory_cache: Optional[MemoryCache] = None
        self.redis_cache: Optional[RedisCache] = None
        
        # 统计信息
        self._stats = {
            "total_gets": 0,
            "total_sets": 0,
            "total_deletes": 0,
            "memory_hits": 0,
            "redis_hits": 0,
            "cache_misses": 0,
            "errors": 0
        }
        
        # 初始化状态
        self._initialized = False
    
    async def cache_manager_initialize(self) -> bool:
        """
        初始化缓存管理器
        [cache][cache_manager][initialize]
        """
        try:
            # 根据配置初始化缓存实例
            if self.config.level in [
                CacheLevel.MEMORY_ONLY, 
                CacheLevel.MEMORY_FIRST, 
                CacheLevel.REDIS_FIRST, 
                CacheLevel.BOTH
            ]:
                if self.config.memory_config:
                    self.memory_cache = MemoryCache(self.config.memory_config)
                    await self.memory_cache.memory_cache_initialize()
                    self.logger.info("Memory cache initialized")
            
            if self.config.level in [
                CacheLevel.REDIS_ONLY, 
                CacheLevel.MEMORY_FIRST, 
                CacheLevel.REDIS_FIRST, 
                CacheLevel.BOTH
            ]:
                if self.config.redis_config:
                    self.redis_cache = RedisCache(self.config.redis_config)
                    await self.redis_cache.redis_cache_initialize()
                    self.logger.info("Redis cache initialized")
            
            self._initialized = True
            self.logger.info(f"Cache manager initialized with level: {self.config.level.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize cache manager: {str(e)}")
            return False
    
    async def cache_manager_cleanup(self):
        """
        清理缓存管理器
        [cache][cache_manager][cleanup]
        """
        try:
            if self.memory_cache:
                await self.memory_cache.memory_cache_cleanup()
                self.logger.info("Memory cache cleaned up")
            
            if self.redis_cache:
                await self.redis_cache.redis_cache_cleanup()
                self.logger.info("Redis cache cleaned up")
            
            self._initialized = False
            self.logger.info("Cache manager cleaned up")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup cache manager: {str(e)}")
    
    async def cache_manager_get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        [cache][cache_manager][get]
        """
        try:
            if not self._initialized:
                return None
            
            self._stats["total_gets"] += 1
            
            if self.config.level == CacheLevel.MEMORY_ONLY:
                return await self._get_from_memory(key)
            
            elif self.config.level == CacheLevel.REDIS_ONLY:
                return await self._get_from_redis(key)
            
            elif self.config.level == CacheLevel.MEMORY_FIRST:
                # 先从内存获取
                value = await self._get_from_memory(key)
                if value is not None:
                    return value
                
                # 内存中没有，从Redis获取
                value = await self._get_from_redis(key)
                if value is not None:
                    # 回写到内存缓存
                    await self._set_to_memory(key, value)
                
                return value
            
            elif self.config.level == CacheLevel.REDIS_FIRST:
                # 先从Redis获取
                value = await self._get_from_redis(key)
                if value is not None:
                    return value
                
                # Redis中没有，从内存获取
                return await self._get_from_memory(key)
            
            elif self.config.level == CacheLevel.BOTH:
                # 从内存和Redis同时获取，优先返回内存的值
                memory_value = await self._get_from_memory(key)
                if memory_value is not None:
                    return memory_value
                
                return await self._get_from_redis(key)
            
            return None
            
        except Exception as e:
            self._stats["errors"] += 1
            self.logger.error(f"Failed to get cache key '{key}': {str(e)}")
            return None
    
    async def cache_manager_set(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[int] = None
    ) -> bool:
        """
        设置缓存值
        [cache][cache_manager][set]
        """
        try:
            if not self._initialized:
                return False
            
            self._stats["total_sets"] += 1
            expire_time = expire or self.config.default_expire
            
            if self.config.level == CacheLevel.MEMORY_ONLY:
                return await self._set_to_memory(key, value, expire_time)
            
            elif self.config.level == CacheLevel.REDIS_ONLY:
                return await self._set_to_redis(key, value, expire_time)
            
            elif self.config.level in [CacheLevel.MEMORY_FIRST, CacheLevel.REDIS_FIRST]:
                # 写入主缓存
                primary_success = False
                secondary_success = False
                
                if self.config.level == CacheLevel.MEMORY_FIRST:
                    primary_success = await self._set_to_memory(key, value, expire_time)
                    secondary_success = await self._set_to_redis(key, value, expire_time)
                else:
                    primary_success = await self._set_to_redis(key, value, expire_time)
                    secondary_success = await self._set_to_memory(key, value, expire_time)
                
                return primary_success  # 主缓存成功即可
            
            elif self.config.level == CacheLevel.BOTH:
                # 同时写入两个缓存
                memory_success = await self._set_to_memory(key, value, expire_time)
                redis_success = await self._set_to_redis(key, value, expire_time)
                
                return memory_success or redis_success  # 任一成功即可
            
            return False
            
        except Exception as e:
            self._stats["errors"] += 1
            self.logger.error(f"Failed to set cache key '{key}': {str(e)}")
            return False
    
    async def cache_manager_delete(self, key: str) -> bool:
        """
        删除缓存值
        [cache][cache_manager][delete]
        """
        try:
            if not self._initialized:
                return False
            
            self._stats["total_deletes"] += 1
            
            memory_deleted = False
            redis_deleted = False
            
            # 从所有启用的缓存中删除
            if self.memory_cache:
                memory_deleted = await self.memory_cache.memory_cache_delete(key)
            
            if self.redis_cache:
                redis_deleted = await self.redis_cache.redis_cache_delete(key)
            
            return memory_deleted or redis_deleted
            
        except Exception as e:
            self._stats["errors"] += 1
            self.logger.error(f"Failed to delete cache key '{key}': {str(e)}")
            return False
    
    async def cache_manager_exists(self, key: str) -> bool:
        """
        检查缓存键是否存在
        [cache][cache_manager][exists]
        """
        try:
            if not self._initialized:
                return False
            
            # 根据配置级别检查
            if self.config.level == CacheLevel.MEMORY_ONLY and self.memory_cache:
                return await self.memory_cache.memory_cache_exists(key)
            
            elif self.config.level == CacheLevel.REDIS_ONLY and self.redis_cache:
                return await self.redis_cache.redis_cache_exists(key)
            
            else:
                # 多级缓存，检查任一缓存存在即返回True
                memory_exists = False
                redis_exists = False
                
                if self.memory_cache:
                    memory_exists = await self.memory_cache.memory_cache_exists(key)
                
                if self.redis_cache:
                    redis_exists = await self.redis_cache.redis_cache_exists(key)
                
                return memory_exists or redis_exists
            
        except Exception as e:
            self.logger.error(f"Failed to check cache key '{key}': {str(e)}")
            return False
    
    async def cache_manager_clear(self) -> bool:
        """
        清空所有缓存
        [cache][cache_manager][clear]
        """
        try:
            if not self._initialized:
                return False
            
            memory_cleared = False
            redis_cleared = False
            
            if self.memory_cache:
                memory_cleared = await self.memory_cache.memory_cache_clear()
            
            if self.redis_cache:
                # Redis使用前缀清理
                redis_cleared = await self.redis_cache.redis_cache_clear_prefix("") > 0
            
            self.logger.info("All caches cleared")
            return memory_cleared or redis_cleared
            
        except Exception as e:
            self.logger.error(f"Failed to clear caches: {str(e)}")
            return False
    
    async def cache_manager_mget(self, keys: List[str]) -> Dict[str, Any]:
        """
        批量获取缓存值
        [cache][cache_manager][mget]
        """
        try:
            if not self._initialized or not keys:
                return {}
            
            result = {}
            
            # 根据配置级别进行批量获取
            if self.config.level == CacheLevel.MEMORY_ONLY and self.memory_cache:
                # 内存缓存的批量获取需要逐个调用
                for key in keys:
                    value = await self.memory_cache.memory_cache_get(key)
                    if value is not None:
                        result[key] = value
            
            elif self.config.level == CacheLevel.REDIS_ONLY and self.redis_cache:
                result = await self.redis_cache.redis_cache_mget(keys)
            
            else:
                # 多级缓存，先从主缓存获取
                if self.config.level == CacheLevel.MEMORY_FIRST and self.memory_cache:
                    # 先从内存获取
                    for key in keys:
                        value = await self.memory_cache.memory_cache_get(key)
                        if value is not None:
                            result[key] = value
                    
                    # 获取内存中没有的键
                    missing_keys = [key for key in keys if key not in result]
                    if missing_keys and self.redis_cache:
                        redis_result = await self.redis_cache.redis_cache_mget(missing_keys)
                        result.update(redis_result)
                
                elif self.config.level == CacheLevel.REDIS_FIRST and self.redis_cache:
                    # 先从Redis获取
                    result = await self.redis_cache.redis_cache_mget(keys)
                    
                    # 获取Redis中没有的键
                    missing_keys = [key for key in keys if key not in result]
                    if missing_keys and self.memory_cache:
                        for key in missing_keys:
                            value = await self.memory_cache.memory_cache_get(key)
                            if value is not None:
                                result[key] = value
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to mget cache keys: {str(e)}")
            return {}
    
    async def cache_manager_mset(
        self, 
        mapping: Dict[str, Any], 
        expire: Optional[int] = None
    ) -> bool:
        """
        批量设置缓存值
        [cache][cache_manager][mset]
        """
        try:
            if not self._initialized or not mapping:
                return False
            
            expire_time = expire or self.config.default_expire
            memory_success = False
            redis_success = False
            
            # 根据配置级别进行批量设置
            if self.memory_cache and self.config.level in [
                CacheLevel.MEMORY_ONLY, 
                CacheLevel.MEMORY_FIRST, 
                CacheLevel.BOTH
            ]:
                # 内存缓存的批量设置需要逐个调用
                memory_success = True
                for key, value in mapping.items():
                    if not await self.memory_cache.memory_cache_set(key, value, expire_time):
                        memory_success = False
            
            if self.redis_cache and self.config.level in [
                CacheLevel.REDIS_ONLY, 
                CacheLevel.REDIS_FIRST, 
                CacheLevel.MEMORY_FIRST, 
                CacheLevel.BOTH
            ]:
                redis_success = await self.redis_cache.redis_cache_mset(mapping, expire_time)
            
            return memory_success or redis_success
            
        except Exception as e:
            self.logger.error(f"Failed to mset cache keys: {str(e)}")
            return False
    
    async def cache_manager_get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        [cache][cache_manager][get_stats]
        """
        try:
            stats = {
                "manager_stats": self._stats.copy(),
                "config": {
                    "level": self.config.level.value,
                    "default_expire": self.config.default_expire,
                    "enable_stats": self.config.enable_stats
                }
            }
            
            # 添加内存缓存统计
            if self.memory_cache:
                memory_stats = await self.memory_cache.memory_cache_get_stats()
                stats["memory_cache"] = memory_stats
            
            # 添加Redis缓存统计
            if self.redis_cache:
                redis_stats = await self.redis_cache.redis_cache_get_stats()
                stats["redis_cache"] = redis_stats
            
            # 计算综合统计
            total_requests = self._stats["total_gets"]
            if total_requests > 0:
                hit_rate = (self._stats["memory_hits"] + self._stats["redis_hits"]) / total_requests
                stats["overall_hit_rate"] = hit_rate
            else:
                stats["overall_hit_rate"] = 0.0
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get cache stats: {str(e)}")
            return {}
    
    async def cache_manager_health_check(self) -> Dict[str, bool]:
        """
        缓存健康检查
        [cache][cache_manager][health_check]
        """
        try:
            health_status = {
                "manager_initialized": self._initialized,
                "memory_cache_healthy": False,
                "redis_cache_healthy": False
            }
            
            # 检查内存缓存健康状态
            if self.memory_cache:
                health_status["memory_cache_healthy"] = await self.memory_cache.memory_cache_health_check()
            
            # 检查Redis缓存健康状态
            if self.redis_cache:
                health_status["redis_cache_healthy"] = await self.redis_cache.redis_cache_health_check()
            
            # 整体健康状态
            health_status["overall_healthy"] = (
                self._initialized and (
                    health_status["memory_cache_healthy"] or 
                    health_status["redis_cache_healthy"]
                )
            )
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Cache health check failed: {str(e)}")
            return {
                "manager_initialized": False,
                "memory_cache_healthy": False,
                "redis_cache_healthy": False,
                "overall_healthy": False
            }
    
    async def _get_from_memory(self, key: str) -> Optional[Any]:
        """
        从内存缓存获取值
        [cache][cache_manager][_get_from_memory]
        """
        if self.memory_cache:
            value = await self.memory_cache.memory_cache_get(key)
            if value is not None:
                self._stats["memory_hits"] += 1
                return value
        
        self._stats["cache_misses"] += 1
        return None
    
    async def _get_from_redis(self, key: str) -> Optional[Any]:
        """
        从Redis缓存获取值
        [cache][cache_manager][_get_from_redis]
        """
        if self.redis_cache:
            value = await self.redis_cache.redis_cache_get(key)
            if value is not None:
                self._stats["redis_hits"] += 1
                return value
        
        self._stats["cache_misses"] += 1
        return None
    
    async def _set_to_memory(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[int] = None
    ) -> bool:
        """
        设置值到内存缓存
        [cache][cache_manager][_set_to_memory]
        """
        if self.memory_cache:
            return await self.memory_cache.memory_cache_set(key, value, expire)
        return False
    
    async def _set_to_redis(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[int] = None
    ) -> bool:
        """
        设置值到Redis缓存
        [cache][cache_manager][_set_to_redis]
        """
        if self.redis_cache:
            return await self.redis_cache.redis_cache_set(key, value, expire)
        return False