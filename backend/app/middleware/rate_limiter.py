"""
Rate Limiter Middleware
API限流中间件 - [middleware][rate_limiter]
"""

import time
import asyncio
from typing import Dict, Optional, Callable, Any
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis.asyncio as redis
import hashlib
import json
import logging

from app.config.settings import app_config_get_settings
from app.core.logging_config import get_logger

logger = get_logger("app.middleware.rate_limiter")


class RateLimiterConfig:
    """
    限流配置类
    [middleware][rate_limiter][config]
    """
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        requests_per_day: int = 10000,
        burst_size: int = 10,
        enabled: bool = True
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day
        self.burst_size = burst_size
        self.enabled = enabled


class TokenBucket:
    """
    令牌桶算法实现
    [middleware][rate_limiter][token_bucket]
    """
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        """消费令牌"""
        now = time.time()
        # 添加令牌
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
        
        # 检查是否有足够令牌
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    API限流中间件
    [middleware][rate_limiter][middleware]
    """
    
    def __init__(
        self,
        app,
        default_config: Optional[RateLimiterConfig] = None,
        path_configs: Optional[Dict[str, RateLimiterConfig]] = None,
        key_generator: Optional[Callable] = None,
        storage_backend: str = "redis"  # redis or memory
    ):
        super().__init__(app)
        self.default_config = default_config or RateLimiterConfig()
        self.path_configs = path_configs or {}
        self.key_generator = key_generator or self._default_key_generator
        self.storage_backend = storage_backend
        
        # 初始化存储后端
        if storage_backend == "redis":
            settings = app_config_get_settings()
            self.redis_client = redis.from_url(settings.REDIS_URL)
        else:
            self.memory_storage = {}
            self.token_buckets = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Any:
        """
        处理请求限流
        [middleware][rate_limiter][dispatch]
        """
        # 获取配置
        config = self._get_config_for_path(request.url.path)
        
        if not config.enabled:
            return await call_next(request)
        
        # 生成限流键
        rate_limit_key = self.key_generator(request)
        
        # 检查限流
        allowed, retry_after = await self._check_rate_limit(rate_limit_key, config)
        
        if not allowed:
            return self._create_rate_limit_response(retry_after)
        
        # 处理请求
        response = await call_next(request)
        
        # 添加限流头
        await self._add_rate_limit_headers(response, rate_limit_key, config)
        
        return response
    
    def _get_config_for_path(self, path: str) -> RateLimiterConfig:
        """
        获取路径对应的限流配置
        [middleware][rate_limiter][get_config_for_path]
        """
        # 检查精确匹配
        if path in self.path_configs:
            return self.path_configs[path]
        
        # 检查前缀匹配
        for pattern, config in self.path_configs.items():
            if path.startswith(pattern):
                return config
        
        return self.default_config
    
    def _default_key_generator(self, request: Request) -> str:
        """
        默认限流键生成器
        [middleware][rate_limiter][default_key_generator]
        """
        # 基于IP和用户ID（如果有）
        client_ip = request.client.host if request.client else "unknown"
        
        # 尝试从请求中获取用户ID
        user_id = getattr(request.state, "user_id", None)
        
        if user_id:
            return f"rate_limit:user:{user_id}"
        else:
            return f"rate_limit:ip:{client_ip}"
    
    async def _check_rate_limit(self, key: str, config: RateLimiterConfig) -> tuple[bool, int]:
        """
        检查是否超过限流
        [middleware][rate_limiter][check_rate_limit]
        """
        if self.storage_backend == "redis":
            return await self._check_rate_limit_redis(key, config)
        else:
            return await self._check_rate_limit_memory(key, config)
    
    async def _check_rate_limit_redis(self, key: str, config: RateLimiterConfig) -> tuple[bool, int]:
        """
        使用Redis检查限流
        [middleware][rate_limiter][check_rate_limit_redis]
        """
        now = int(time.time())
        
        # 滑动窗口算法检查每分钟、每小时、每天的限制
        checks = [
            (f"{key}:minute", 60, config.requests_per_minute),
            (f"{key}:hour", 3600, config.requests_per_hour),
            (f"{key}:day", 86400, config.requests_per_day)
        ]
        
        pipe = self.redis_client.pipeline()
        
        for window_key, window_size, limit in checks:
            # 移除过期的记录
            pipe.zremrangebyscore(window_key, 0, now - window_size)
            # 统计当前窗口内的请求数
            pipe.zcard(window_key)
            # 添加当前请求
            pipe.zadd(window_key, {str(now): now})
            # 设置过期时间
            pipe.expire(window_key, window_size)
        
        results = await pipe.execute()
        
        # 检查每个窗口的限制
        for i, (window_key, window_size, limit) in enumerate(checks):
            current_requests = results[i * 4 + 1]  # zcard结果
            
            if current_requests >= limit:
                # 计算重试时间
                retry_after = window_size
                return False, retry_after
        
        return True, 0
    
    async def _check_rate_limit_memory(self, key: str, config: RateLimiterConfig) -> tuple[bool, int]:
        """
        使用内存检查限流（令牌桶算法）
        [middleware][rate_limiter][check_rate_limit_memory]
        """
        # 获取或创建令牌桶
        if key not in self.token_buckets:
            # 使用每分钟限制作为令牌桶容量
            capacity = config.burst_size
            refill_rate = config.requests_per_minute / 60.0  # 每秒添加的令牌数
            self.token_buckets[key] = TokenBucket(capacity, refill_rate)
        
        bucket = self.token_buckets[key]
        
        if bucket.consume():
            return True, 0
        else:
            # 计算需要等待的时间
            retry_after = int(1.0 / bucket.refill_rate) + 1
            return False, retry_after
    
    def _create_rate_limit_response(self, retry_after: int) -> JSONResponse:
        """
        创建限流响应
        [middleware][rate_limiter][create_rate_limit_response]
        """
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "success": False,
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "请求频率过高，请稍后再试",
                    "retry_after": retry_after
                }
            },
            headers={"Retry-After": str(retry_after)}
        )
    
    async def _add_rate_limit_headers(self, response: Any, key: str, config: RateLimiterConfig):
        """
        添加限流相关的响应头
        [middleware][rate_limiter][add_rate_limit_headers]
        """
        if hasattr(response, "headers"):
            response.headers["X-RateLimit-Limit"] = str(config.requests_per_minute)
            
            # 获取剩余请求数
            remaining = await self._get_remaining_requests(key, config)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            
            # 重置时间
            reset_time = int(time.time()) + 60
            response.headers["X-RateLimit-Reset"] = str(reset_time)
    
    async def _get_remaining_requests(self, key: str, config: RateLimiterConfig) -> int:
        """
        获取剩余请求数
        [middleware][rate_limiter][get_remaining_requests]
        """
        if self.storage_backend == "redis":
            minute_key = f"{key}:minute"
            current_requests = await self.redis_client.zcard(minute_key)
            return max(0, config.requests_per_minute - current_requests)
        else:
            if key in self.token_buckets:
                return int(self.token_buckets[key].tokens)
            return config.requests_per_minute


def add_rate_limiter_middleware(
    app,
    default_config: Optional[RateLimiterConfig] = None,
    path_configs: Optional[Dict[str, RateLimiterConfig]] = None,
    **kwargs
):
    """
    添加API限流中间件
    [middleware][rate_limiter][add_middleware]
    """
    # 默认配置
    if default_config is None:
        default_config = RateLimiterConfig(
            requests_per_minute=60,
            requests_per_hour=1000,
            requests_per_day=10000
        )
    
    # 路径特定配置
    if path_configs is None:
        path_configs = {
            "/api/v1/auth/login": RateLimiterConfig(
                requests_per_minute=5,
                requests_per_hour=50,
                requests_per_day=200
            ),
            "/api/v1/auth/register": RateLimiterConfig(
                requests_per_minute=3,
                requests_per_hour=20,
                requests_per_day=100
            ),
            "/api/v1/files/upload": RateLimiterConfig(
                requests_per_minute=10,
                requests_per_hour=100,
                requests_per_day=500
            )
        }
    
    app.add_middleware(
        RateLimiterMiddleware,
        default_config=default_config,
        path_configs=path_configs,
        **kwargs
    )
    
    logger.info("Rate limiter middleware added")