"""
Memory Cache Implementation
内存缓存实现 - [cache][memory_cache]
"""

import asyncio
import time
from typing import Any, Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import threading
import logging


@dataclass
class CacheItem:
    """
    缓存项
    [cache][memory_cache][cache_item]
    """
    value: Any
    expire_time: Optional[float] = None
    created_time: float = None
    access_count: int = 0
    last_access_time: float = None
    
    def __post_init__(self):
        if self.created_time is None:
            self.created_time = time.time()
        if self.last_access_time is None:
            self.last_access_time = self.created_time
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.expire_time is None:
            return False
        return time.time() > self.expire_time
    
    def update_access(self):
        """更新访问信息"""
        self.access_count += 1
        self.last_access_time = time.time()


class MemoryCache:
    """
    内存缓存实现
    [cache][memory_cache]
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化内存缓存
        [cache][memory_cache][init]
        """
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        
        # 缓存配置
        self.max_size = config.get("max_size", 10000)
        self.default_expire = config.get("default_expire", 3600)  # 1小时
        self.cleanup_interval = config.get("cleanup_interval", 300)  # 5分钟
        self.eviction_policy = config.get("eviction_policy", "lru")  # lru, lfu, fifo
        
        # 内存存储
        self._cache: Dict[str, CacheItem] = {}
        self._lock = threading.RLock()
        
        # 统计信息
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "evictions": 0,
            "expirations": 0
        }
        
        # 清理任务
        self._cleanup_task: Optional[asyncio.Task] = None
        self._shutdown = False
    
    async def memory_cache_initialize(self) -> bool:
        """
        初始化内存缓存
        [cache][memory_cache][initialize]
        """
        try:
            # 启动清理任务
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            self.logger.info(f"Memory cache initialized with max_size={self.max_size}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize memory cache: {str(e)}")
            return False
    
    async def memory_cache_cleanup(self):
        """
        清理内存缓存
        [cache][memory_cache][cleanup]
        """
        self._shutdown = True
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        with self._lock:
            self._cache.clear()
        
        self.logger.info("Memory cache cleaned up")
    
    async def memory_cache_get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        [cache][memory_cache][get]
        """
        try:
            with self._lock:
                item = self._cache.get(key)
                
                if item is None:
                    self._stats["misses"] += 1
                    return None
                
                if item.is_expired():
                    # 删除过期项
                    del self._cache[key]
                    self._stats["misses"] += 1
                    self._stats["expirations"] += 1
                    return None
                
                # 更新访问信息
                item.update_access()
                self._stats["hits"] += 1
                
                return item.value
                
        except Exception as e:
            self.logger.error(f"Failed to get cache key '{key}': {str(e)}")
            return None
    
    async def memory_cache_set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """
        设置缓存值
        [cache][memory_cache][set]
        """
        try:
            with self._lock:
                # 检查是否需要清理空间
                if len(self._cache) >= self.max_size and key not in self._cache:
                    self._evict_items(1)
                
                # 计算过期时间
                expire_time = None
                if expire is not None and expire > 0:
                    expire_time = time.time() + expire
                elif self.default_expire > 0:
                    expire_time = time.time() + self.default_expire
                
                # 创建缓存项
                item = CacheItem(
                    value=value,
                    expire_time=expire_time
                )
                
                self._cache[key] = item
                self._stats["sets"] += 1
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to set cache key '{key}': {str(e)}")
            return False
    
    async def memory_cache_delete(self, key: str) -> bool:
        """
        删除缓存值
        [cache][memory_cache][delete]
        """
        try:
            with self._lock:
                if key in self._cache:
                    del self._cache[key]
                    self._stats["deletes"] += 1
                    return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to delete cache key '{key}': {str(e)}")
            return False
    
    async def memory_cache_exists(self, key: str) -> bool:
        """
        检查缓存键是否存在
        [cache][memory_cache][exists]
        """
        try:
            with self._lock:
                item = self._cache.get(key)
                
                if item is None:
                    return False
                
                if item.is_expired():
                    del self._cache[key]
                    self._stats["expirations"] += 1
                    return False
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to check cache key '{key}': {str(e)}")
            return False
    
    async def memory_cache_clear(self) -> bool:
        """
        清空所有缓存
        [cache][memory_cache][clear]
        """
        try:
            with self._lock:
                self._cache.clear()
                self.logger.info("Memory cache cleared")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to clear memory cache: {str(e)}")
            return False
    
    async def memory_cache_size(self) -> int:
        """
        获取缓存大小
        [cache][memory_cache][size]
        """
        with self._lock:
            return len(self._cache)
    
    async def memory_cache_keys(self, pattern: Optional[str] = None) -> List[str]:
        """
        获取缓存键列表
        [cache][memory_cache][keys]
        """
        try:
            with self._lock:
                keys = list(self._cache.keys())
                
                if pattern:
                    import fnmatch
                    keys = [key for key in keys if fnmatch.fnmatch(key, pattern)]
                
                return keys
                
        except Exception as e:
            self.logger.error(f"Failed to get cache keys: {str(e)}")
            return []
    
    async def memory_cache_get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        [cache][memory_cache][get_stats]
        """
        with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = self._stats["hits"] / total_requests if total_requests > 0 else 0
            
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hit_rate": hit_rate,
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "sets": self._stats["sets"],
                "deletes": self._stats["deletes"],
                "evictions": self._stats["evictions"],
                "expirations": self._stats["expirations"],
                "eviction_policy": self.eviction_policy
            }
    
    def _evict_items(self, count: int):
        """
        清理缓存项
        [cache][memory_cache][_evict_items]
        """
        if not self._cache:
            return
        
        current_time = time.time()
        
        if self.eviction_policy == "lru":
            # 最近最少使用
            items_to_evict = sorted(
                self._cache.items(),
                key=lambda x: x[1].last_access_time
            )[:count]
        elif self.eviction_policy == "lfu":
            # 最少使用频次
            items_to_evict = sorted(
                self._cache.items(),
                key=lambda x: x[1].access_count
            )[:count]
        elif self.eviction_policy == "fifo":
            # 先进先出
            items_to_evict = sorted(
                self._cache.items(),
                key=lambda x: x[1].created_time
            )[:count]
        else:
            # 随机清理
            import random
            keys = list(self._cache.keys())
            random.shuffle(keys)
            items_to_evict = [(key, self._cache[key]) for key in keys[:count]]
        
        for key, _ in items_to_evict:
            if key in self._cache:
                del self._cache[key]
                self._stats["evictions"] += 1
    
    def _cleanup_expired_items(self):
        """
        清理过期项
        [cache][memory_cache][_cleanup_expired_items]
        """
        current_time = time.time()
        expired_keys = []
        
        for key, item in self._cache.items():
            if item.is_expired():
                expired_keys.append(key)
        
        for key in expired_keys:
            if key in self._cache:
                del self._cache[key]
                self._stats["expirations"] += 1
        
        if expired_keys:
            self.logger.debug(f"Cleaned up {len(expired_keys)} expired cache items")
    
    async def _cleanup_loop(self):
        """
        清理循环任务
        [cache][memory_cache][_cleanup_loop]
        """
        while not self._shutdown:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                if self._shutdown:
                    break
                
                with self._lock:
                    self._cleanup_expired_items()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {str(e)}")
    
    async def memory_cache_health_check(self) -> bool:
        """
        健康检查
        [cache][memory_cache][health_check]
        """
        try:
            # 测试基本操作
            test_key = "__health_check__"
            test_value = "test"
            
            await self.memory_cache_set(test_key, test_value, 1)
            result = await self.memory_cache_get(test_key)
            await self.memory_cache_delete(test_key)
            
            return result == test_value
            
        except Exception as e:
            self.logger.error(f"Memory cache health check failed: {str(e)}")
            return False