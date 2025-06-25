"""
Circuit Breaker Pattern Implementation
熔断器模式实现 - [utils][circuit_breaker]
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass, field
import asyncio

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """熔断器状态"""
    CLOSED = "closed"       # 正常状态
    OPEN = "open"           # 熔断开启
    HALF_OPEN = "half_open" # 半开状态


@dataclass
class CircuitBreakerConfig:
    """熔断器配置"""
    failure_threshold: int = 5          # 失败阈值
    success_threshold: int = 3          # 成功阈值（半开状态）
    timeout: int = 60                   # 熔断超时时间（秒）
    monitoring_period: int = 60         # 监控周期（秒）
    expected_exception: type = Exception # 预期异常类型


@dataclass
class CircuitBreakerStats:
    """熔断器统计信息"""
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    total_requests: int = 0
    total_failures: int = 0
    state_changed_time: datetime = field(default_factory=datetime.now)


class CircuitBreaker:
    """熔断器实现 - [utils][circuit_breaker]"""
    
    def __init__(self):
        self._circuits: Dict[str, CircuitBreakerStats] = {}
        self._configs: Dict[str, CircuitBreakerConfig] = {}
        self._locks: Dict[str, asyncio.Lock] = {}
        
        # 默认配置
        self.default_config = CircuitBreakerConfig()
    
    def register_circuit(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        """注册熔断器"""
        if name not in self._circuits:
            self._circuits[name] = CircuitBreakerStats()
            self._configs[name] = config or self.default_config
            self._locks[name] = asyncio.Lock()
            logger.info(f"Registered circuit breaker: {name}")
    
    def can_execute(self, circuit_name: str) -> bool:
        """检查是否可以执行请求"""
        # 自动注册未知的熔断器
        if circuit_name not in self._circuits:
            self.register_circuit(circuit_name)
        
        stats = self._circuits[circuit_name]
        config = self._configs[circuit_name]
        
        if stats.state == CircuitState.CLOSED:
            return True
        elif stats.state == CircuitState.OPEN:
            # 检查是否可以转换到半开状态
            if self._should_attempt_reset(circuit_name):
                self._transition_to_half_open(circuit_name)
                return True
            return False
        elif stats.state == CircuitState.HALF_OPEN:
            return True
        
        return False
    
    async def record_success(self, circuit_name: str):
        """记录成功调用"""
        if circuit_name not in self._circuits:
            self.register_circuit(circuit_name)
        
        async with self._locks[circuit_name]:
            stats = self._circuits[circuit_name]
            config = self._configs[circuit_name]
            
            stats.total_requests += 1
            stats.success_count += 1
            stats.last_success_time = datetime.now()
            
            if stats.state == CircuitState.HALF_OPEN:
                if stats.success_count >= config.success_threshold:
                    self._transition_to_closed(circuit_name)
            elif stats.state == CircuitState.CLOSED:
                # 重置失败计数
                stats.failure_count = 0
    
    async def record_failure(self, circuit_name: str, exception: Optional[Exception] = None):
        """记录失败调用"""
        if circuit_name not in self._circuits:
            self.register_circuit(circuit_name)
        
        async with self._locks[circuit_name]:
            stats = self._circuits[circuit_name]
            config = self._configs[circuit_name]
            
            # 检查是否是预期的异常类型
            if exception and not isinstance(exception, config.expected_exception):
                logger.debug(f"Ignoring unexpected exception type: {type(exception)}")
                return
            
            stats.total_requests += 1
            stats.total_failures += 1
            stats.failure_count += 1
            stats.last_failure_time = datetime.now()
            
            if stats.state == CircuitState.CLOSED:
                if stats.failure_count >= config.failure_threshold:
                    self._transition_to_open(circuit_name)
            elif stats.state == CircuitState.HALF_OPEN:
                # 半开状态下的失败直接转换到开启状态
                self._transition_to_open(circuit_name)
    
    def _should_attempt_reset(self, circuit_name: str) -> bool:
        """检查是否应该尝试重置熔断器"""
        stats = self._circuits[circuit_name]
        config = self._configs[circuit_name]
        
        if stats.last_failure_time is None:
            return True
        
        time_since_failure = (datetime.now() - stats.last_failure_time).total_seconds()
        return time_since_failure >= config.timeout
    
    def _transition_to_closed(self, circuit_name: str):
        """转换到关闭状态"""
        stats = self._circuits[circuit_name]
        old_state = stats.state
        
        stats.state = CircuitState.CLOSED
        stats.failure_count = 0
        stats.success_count = 0
        stats.state_changed_time = datetime.now()
        
        logger.info(f"Circuit breaker {circuit_name} transitioned from {old_state.value} to {stats.state.value}")
    
    def _transition_to_open(self, circuit_name: str):
        """转换到开启状态"""
        stats = self._circuits[circuit_name]
        old_state = stats.state
        
        stats.state = CircuitState.OPEN
        stats.success_count = 0
        stats.state_changed_time = datetime.now()
        
        logger.warning(f"Circuit breaker {circuit_name} transitioned from {old_state.value} to {stats.state.value}")
    
    def _transition_to_half_open(self, circuit_name: str):
        """转换到半开状态"""
        stats = self._circuits[circuit_name]
        old_state = stats.state
        
        stats.state = CircuitState.HALF_OPEN
        stats.success_count = 0
        stats.failure_count = 0
        stats.state_changed_time = datetime.now()
        
        logger.info(f"Circuit breaker {circuit_name} transitioned from {old_state.value} to {stats.state.value}")
    
    def get_stats(self, circuit_name: str) -> Optional[Dict[str, Any]]:
        """获取熔断器统计信息"""
        if circuit_name not in self._circuits:
            return None
        
        stats = self._circuits[circuit_name]
        config = self._configs[circuit_name]
        
        return {
            "name": circuit_name,
            "state": stats.state.value,
            "failure_count": stats.failure_count,
            "success_count": stats.success_count,
            "total_requests": stats.total_requests,
            "total_failures": stats.total_failures,
            "failure_rate": stats.total_failures / max(stats.total_requests, 1),
            "last_failure_time": stats.last_failure_time.isoformat() if stats.last_failure_time else None,
            "last_success_time": stats.last_success_time.isoformat() if stats.last_success_time else None,
            "state_changed_time": stats.state_changed_time.isoformat(),
            "config": {
                "failure_threshold": config.failure_threshold,
                "success_threshold": config.success_threshold,
                "timeout": config.timeout,
                "monitoring_period": config.monitoring_period
            }
        }
    
    def get_all_stats(self) -> Dict[str, Any]:
        """获取所有熔断器统计信息"""
        return {
            circuit_name: self.get_stats(circuit_name)
            for circuit_name in self._circuits.keys()
        }
    
    def reset_circuit(self, circuit_name: str):
        """重置熔断器"""
        if circuit_name in self._circuits:
            self._transition_to_closed(circuit_name)
            logger.info(f"Circuit breaker {circuit_name} has been reset")
    
    def force_open(self, circuit_name: str):
        """强制开启熔断器"""
        if circuit_name not in self._circuits:
            self.register_circuit(circuit_name)
        
        self._transition_to_open(circuit_name)
        logger.warning(f"Circuit breaker {circuit_name} has been forced open")
    
    def decorator(self, circuit_name: str, config: Optional[CircuitBreakerConfig] = None):
        """熔断器装饰器"""
        def decorator_wrapper(func: Callable):
            async def async_wrapper(*args, **kwargs):
                # 注册熔断器
                if circuit_name not in self._circuits:
                    self.register_circuit(circuit_name, config)
                
                # 检查是否可以执行
                if not self.can_execute(circuit_name):
                    raise Exception(f"Circuit breaker {circuit_name} is open")
                
                try:
                    result = await func(*args, **kwargs)
                    await self.record_success(circuit_name)
                    return result
                except Exception as e:
                    await self.record_failure(circuit_name, e)
                    raise
            
            def sync_wrapper(*args, **kwargs):
                # 检查是否可以执行
                if not self.can_execute(circuit_name):
                    raise Exception(f"Circuit breaker {circuit_name} is open")
                
                try:
                    result = func(*args, **kwargs)
                    # 对于同步函数，直接调用异步方法（需要在事件循环中）
                    asyncio.create_task(self.record_success(circuit_name))
                    return result
                except Exception as e:
                    asyncio.create_task(self.record_failure(circuit_name, e))
                    raise
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator_wrapper


# 全局熔断器实例
global_circuit_breaker = CircuitBreaker()