"""
Rate Limiter Implementation
速率限制器实现 - [utils][rate_limiter]
"""

import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, field
from collections import deque
import redis.asyncio as redis

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """速率限制配置"""
    requests_per_second: float = 10.0
    requests_per_minute: float = 600.0
    requests_per_hour: float = 36000.0
    requests_per_day: float = 864000.0
    burst_capacity: int = 20
    enable_sliding_window: bool = True


@dataclass
class RateLimitWindow:
    """时间窗口"""
    requests: deque = field(default_factory=deque)
    window_size: int = 60  # 窗口大小（秒）
    max_requests: int = 100  # 最大请求数


class TokenBucket:
    """令牌桶算法实现"""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate  # 每秒添加的令牌数
        self.last_refill = time.time()
        self._lock = asyncio.Lock()
    
    async def consume(self, tokens: int = 1) -> bool:
        """消费令牌"""
        async with self._lock:
            now = time.time()
            
            # 计算需要添加的令牌数
            time_passed = now - self.last_refill
            tokens_to_add = time_passed * self.refill_rate
            
            # 添加令牌，不超过桶容量
            self.tokens = min(self.capacity, self.tokens + tokens_to_add)
            self.last_refill = now
            
            # 检查是否有足够的令牌
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    def get_tokens(self) -> float:
        """获取当前令牌数"""
        return self.tokens


class SlidingWindowCounter:
    """滑动窗口计数器"""
    
    def __init__(self, window_size: int, max_requests: int):
        self.window_size = window_size
        self.max_requests = max_requests
        self.requests: deque = deque()
        self._lock = asyncio.Lock()
    
    async def is_allowed(self) -> bool:
        """检查是否允许请求"""
        async with self._lock:
            now = time.time()
            
            # 移除超出时间窗口的请求
            while self.requests and now - self.requests[0] >= self.window_size:
                self.requests.popleft()
            
            # 检查是否超过限制
            if len(self.requests) >= self.max_requests:
                return False
            
            # 添加当前请求
            self.requests.append(now)
            return True
    
    def get_current_count(self) -> int:
        """获取当前窗口内的请求数"""
        now = time.time()
        
        # 清理过期请求
        while self.requests and now - self.requests[0] >= self.window_size:
            self.requests.popleft()
        
        return len(self.requests)


class RateLimiter:
    """速率限制器 - [utils][rate_limiter]"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.configs: Dict[str, RateLimitConfig] = {}
        self.token_buckets: Dict[str, TokenBucket] = {}
        self.sliding_windows: Dict[str, Dict[str, SlidingWindowCounter]] = {}
        self._locks: Dict[str, asyncio.Lock] = {}
        
        # 默认配置
        self.default_config = RateLimitConfig()
    
    def register_limiter(self, key: str, config: Optional[RateLimitConfig] = None):
        """注册速率限制器"""
        if key not in self.configs:
            self.configs[key] = config or self.default_config
            self._locks[key] = asyncio.Lock()
            
            # 初始化令牌桶
            conf = self.configs[key]
            self.token_buckets[key] = TokenBucket(
                capacity=conf.burst_capacity,
                refill_rate=conf.requests_per_second
            )
            
            # 初始化滑动窗口
            if conf.enable_sliding_window:
                self.sliding_windows[key] = {
                    'minute': SlidingWindowCounter(60, int(conf.requests_per_minute)),
                    'hour': SlidingWindowCounter(3600, int(conf.requests_per_hour)),
                    'day': SlidingWindowCounter(86400, int(conf.requests_per_day))
                }
            
            logger.info(f"Registered rate limiter: {key}")
    
    async def is_allowed(self, key: str, identifier: str = "default") -> Dict[str, Union[bool, float, int]]:
        """检查是否允许请求"""
        # 自动注册未知的限制器
        if key not in self.configs:
            self.register_limiter(key)
        
        limiter_key = f"{key}:{identifier}"
        
        # 使用Redis实现分布式限制
        if self.redis_client:
            return await self._check_distributed_limit(limiter_key)
        else:
            return await self._check_local_limit(key, identifier)
    
    async def _check_local_limit(self, key: str, identifier: str) -> Dict[str, Union[bool, float, int]]:
        """检查本地速率限制"""
        config = self.configs[key]
        bucket_key = f"{key}:{identifier}"
        
        # 确保令牌桶存在
        if bucket_key not in self.token_buckets:
            self.token_buckets[bucket_key] = TokenBucket(
                capacity=config.burst_capacity,
                refill_rate=config.requests_per_second
            )
        
        # 检查令牌桶
        bucket = self.token_buckets[bucket_key]
        allowed_by_bucket = await bucket.consume(1)
        
        result = {
            "allowed": allowed_by_bucket,
            "remaining_tokens": bucket.get_tokens(),
            "rate_limit_type": "token_bucket"
        }
        
        # 如果启用滑动窗口，同时检查
        if config.enable_sliding_window and key in self.sliding_windows:
            window_results = {}
            
            for window_name, window in self.sliding_windows[key].items():
                window_key = f"{bucket_key}:{window_name}"
                
                # 确保每个标识符都有独立的窗口
                if window_key not in self.sliding_windows:
                    # 这里需要为每个标识符创建独立的窗口实例
                    pass
                
                allowed_by_window = await window.is_allowed()
                window_results[window_name] = {
                    "allowed": allowed_by_window,
                    "current_count": window.get_current_count(),
                    "max_requests": window.max_requests
                }
                
                # 如果任何窗口不允许，整个请求就不允许
                if not allowed_by_window:
                    result["allowed"] = False
            
            result["windows"] = window_results
            result["rate_limit_type"] = "sliding_window"
        
        return result
    
    async def _check_distributed_limit(self, key: str) -> Dict[str, Union[bool, float, int]]:
        """检查分布式速率限制（Redis实现）"""
        try:
            # 使用Redis的滑动窗口算法
            now = time.time()
            window_size = 60  # 1分钟窗口
            max_requests = 60  # 每分钟最大请求数
            
            # Redis Lua脚本实现原子性操作
            lua_script = """
            local key = KEYS[1]
            local window = tonumber(ARGV[1])
            local limit = tonumber(ARGV[2])
            local now = tonumber(ARGV[3])
            
            -- 移除过期的记录
            redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
            
            -- 获取当前窗口内的请求数
            local current = redis.call('ZCARD', key)
            
            if current >= limit then
                return {0, current, limit}
            else
                -- 添加当前请求
                redis.call('ZADD', key, now, now)
                redis.call('EXPIRE', key, window)
                return {1, current + 1, limit}
            end
            """
            
            result = await self.redis_client.eval(
                lua_script, 1, key, window_size, max_requests, now
            )
            
            return {
                "allowed": bool(result[0]),
                "current_count": result[1],
                "limit": result[2],
                "rate_limit_type": "distributed_sliding_window"
            }
            
        except Exception as e:
            logger.error(f"Redis rate limiting error: {e}")
            # 降级到本地限制
            return await self._check_local_limit(key.split(':')[0], key.split(':')[1] if ':' in key else "default")
    
    async def wait_for_token(self, key: str, identifier: str = "default", timeout: float = 10.0) -> bool:
        """等待令牌可用"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = await self.is_allowed(key, identifier)
            if result["allowed"]:
                return True
            
            # 等待一小段时间后重试
            await asyncio.sleep(0.1)
        
        return False
    
    def get_stats(self, key: str, identifier: str = "default") -> Dict[str, Any]:
        """获取限制器统计信息"""
        if key not in self.configs:
            return {}
        
        config = self.configs[key]
        bucket_key = f"{key}:{identifier}"
        
        stats = {
            "key": key,
            "identifier": identifier,
            "config": {
                "requests_per_second": config.requests_per_second,
                "requests_per_minute": config.requests_per_minute,
                "requests_per_hour": config.requests_per_hour,
                "requests_per_day": config.requests_per_day,
                "burst_capacity": config.burst_capacity
            }
        }
        
        # 令牌桶统计
        if bucket_key in self.token_buckets:
            bucket = self.token_buckets[bucket_key]
            stats["token_bucket"] = {
                "current_tokens": bucket.get_tokens(),
                "capacity": bucket.capacity,
                "refill_rate": bucket.refill_rate
            }
        
        # 滑动窗口统计
        if config.enable_sliding_window and key in self.sliding_windows:
            window_stats = {}
            for window_name, window in self.sliding_windows[key].items():
                window_stats[window_name] = {
                    "current_count": window.get_current_count(),
                    "max_requests": window.max_requests,
                    "window_size": window.window_size
                }
            stats["sliding_windows"] = window_stats
        
        return stats
    
    def reset_limiter(self, key: str, identifier: str = "default"):
        """重置限制器"""
        bucket_key = f"{key}:{identifier}"
        
        # 重置令牌桶
        if bucket_key in self.token_buckets:
            config = self.configs[key]
            self.token_buckets[bucket_key] = TokenBucket(
                capacity=config.burst_capacity,
                refill_rate=config.requests_per_second
            )
        
        # 重置滑动窗口
        if key in self.sliding_windows:
            for window in self.sliding_windows[key].values():
                window.requests.clear()
        
        logger.info(f"Reset rate limiter: {bucket_key}")
    
    def decorator(self, key: str, config: Optional[RateLimitConfig] = None, 
                  identifier_func: Optional[callable] = None):
        """速率限制装饰器"""
        def decorator_wrapper(func):
            async def async_wrapper(*args, **kwargs):
                # 注册限制器
                if key not in self.configs:
                    self.register_limiter(key, config)
                
                # 确定标识符
                identifier = "default"
                if identifier_func:
                    try:
                        identifier = identifier_func(*args, **kwargs)
                    except Exception as e:
                        logger.warning(f"Failed to get identifier: {e}")
                
                # 检查速率限制
                result = await self.is_allowed(key, identifier)
                if not result["allowed"]:
                    raise Exception(f"Rate limit exceeded for {key}:{identifier}")
                
                return await func(*args, **kwargs)
            
            def sync_wrapper(*args, **kwargs):
                # 对于同步函数，需要在事件循环中执行
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(async_wrapper(*args, **kwargs))
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator_wrapper


# 全局速率限制器实例
global_rate_limiter = RateLimiter()