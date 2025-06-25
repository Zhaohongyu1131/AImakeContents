"""
Doubao Load Balancer Service
豆包负载均衡服务 - [services][doubao_api][doubao_load_balancer]
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random
import statistics
from collections import defaultdict, deque

import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.doubao_usage import DoubaoAccountBalance
from app.cache.cache_manager import CacheManager
from app.utils.circuit_breaker import CircuitBreaker, CircuitBreakerConfig

logger = logging.getLogger(__name__)


class LoadBalancingStrategy(Enum):
    """负载均衡策略"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    RESOURCE_BASED = "resource_based"
    COST_OPTIMIZED = "cost_optimized"
    INTELLIGENT = "intelligent"


class EndpointStatus(Enum):
    """端点状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"


@dataclass
class EndpointConfig:
    """端点配置"""
    endpoint_id: str
    url: str
    app_id: str
    access_token: str
    secret_key: str
    cluster: str
    weight: int = 100
    max_connections: int = 100
    timeout: float = 30.0
    cost_per_request: float = 0.01
    priority: int = 1  # 1=high, 2=medium, 3=low
    region: str = "default"
    service_types: List[str] = field(default_factory=list)


@dataclass
class EndpointMetrics:
    """端点指标"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    active_connections: int = 0
    total_response_time: float = 0.0
    last_response_time: float = 0.0
    average_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    error_rate: float = 0.0
    last_health_check: datetime = field(default_factory=datetime.now)
    status: EndpointStatus = EndpointStatus.HEALTHY
    consecutive_failures: int = 0
    last_failure_time: Optional[datetime] = None


@dataclass
class LoadBalancerConfig:
    """负载均衡配置"""
    strategy: LoadBalancingStrategy = LoadBalancingStrategy.INTELLIGENT
    health_check_interval: int = 30  # 秒
    health_check_timeout: float = 5.0
    max_consecutive_failures: int = 3
    circuit_breaker_enabled: bool = True
    enable_sticky_sessions: bool = False
    enable_failover: bool = True
    failover_threshold: float = 0.8  # 错误率阈值
    degraded_threshold: float = 0.5  # 降级阈值


class DoubaoLoadBalancer:
    """豆包负载均衡器 - [services][doubao_api][load_balancer]"""
    
    def __init__(self):
        self.config = LoadBalancerConfig()
        self.endpoints: Dict[str, EndpointConfig] = {}
        self.metrics: Dict[str, EndpointMetrics] = {}
        self.circuit_breaker = CircuitBreaker()
        self.cache_manager = CacheManager()
        
        # 负载均衡状态
        self._round_robin_index = 0
        self._session_affinity: Dict[str, str] = {}  # user_id -> endpoint_id
        
        # 响应时间历史
        self._response_time_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # 健康检查任务
        self._health_check_task: Optional[asyncio.Task] = None
        
        # 初始化默认端点
        self._initialize_default_endpoints()
    
    def _initialize_default_endpoints(self):
        """初始化默认端点"""
        # 主端点
        primary_endpoint = EndpointConfig(
            endpoint_id="primary",
            url="https://openspeech.bytedance.com",
            app_id=settings.VOLCANO_VOICE_APPID,
            access_token=settings.VOLCANO_VOICE_ACCESS_TOKEN,
            secret_key=settings.VOLCANO_VOICE_SECRETYKEY,
            cluster=settings.VOLCANO_VOICE_CLUSTER,
            weight=100,
            max_connections=200,
            cost_per_request=0.01,
            priority=1,
            region="main",
            service_types=["tts", "voice_clone", "text_analysis"]
        )
        
        self.add_endpoint(primary_endpoint)
        
        # 如果有备用配置，添加备用端点
        backup_endpoints = getattr(settings, 'DOUBAO_BACKUP_ENDPOINTS', [])
        for i, backup_config in enumerate(backup_endpoints):
            backup_endpoint = EndpointConfig(
                endpoint_id=f"backup_{i}",
                url=backup_config.get("url", "https://openspeech-backup.bytedance.com"),
                app_id=backup_config.get("app_id", settings.VOLCANO_VOICE_APPID),
                access_token=backup_config.get("access_token", settings.VOLCANO_VOICE_ACCESS_TOKEN),
                secret_key=backup_config.get("secret_key", settings.VOLCANO_VOICE_SECRETYKEY),
                cluster=backup_config.get("cluster", settings.VOLCANO_VOICE_CLUSTER),
                weight=backup_config.get("weight", 50),
                priority=2,
                region=backup_config.get("region", "backup"),
                service_types=backup_config.get("service_types", ["tts", "voice_clone"])
            )
            self.add_endpoint(backup_endpoint)
    
    def add_endpoint(self, endpoint: EndpointConfig):
        """添加端点"""
        self.endpoints[endpoint.endpoint_id] = endpoint
        self.metrics[endpoint.endpoint_id] = EndpointMetrics()
        
        # 注册熔断器
        if self.config.circuit_breaker_enabled:
            circuit_config = CircuitBreakerConfig(
                failure_threshold=self.config.max_consecutive_failures,
                timeout=60,  # 1分钟后尝试重置
                monitoring_period=300  # 5分钟监控周期
            )
            self.circuit_breaker.register_circuit(endpoint.endpoint_id, circuit_config)
        
        logger.info(f"Added endpoint: {endpoint.endpoint_id} ({endpoint.url})")
    
    def remove_endpoint(self, endpoint_id: str):
        """移除端点"""
        if endpoint_id in self.endpoints:
            del self.endpoints[endpoint_id]
            del self.metrics[endpoint_id]
            
            # 清理会话亲和性
            sessions_to_remove = [
                session_id for session_id, ep_id in self._session_affinity.items()
                if ep_id == endpoint_id
            ]
            for session_id in sessions_to_remove:
                del self._session_affinity[session_id]
            
            logger.info(f"Removed endpoint: {endpoint_id}")
    
    async def select_endpoint(self, service_type: str, user_id: Optional[int] = None,
                             session_id: Optional[str] = None) -> Optional[EndpointConfig]:
        """选择最佳端点"""
        # 过滤支持该服务类型的健康端点
        available_endpoints = self._get_available_endpoints(service_type)
        
        if not available_endpoints:
            logger.warning(f"No available endpoints for service type: {service_type}")
            return None
        
        # 会话亲和性
        if self.config.enable_sticky_sessions and session_id:
            if session_id in self._session_affinity:
                preferred_endpoint_id = self._session_affinity[session_id]
                if preferred_endpoint_id in available_endpoints:
                    return self.endpoints[preferred_endpoint_id]
        
        # 根据策略选择端点
        selected_endpoint = await self._apply_load_balancing_strategy(
            available_endpoints, service_type, user_id
        )
        
        # 记录会话亲和性
        if self.config.enable_sticky_sessions and session_id and selected_endpoint:
            self._session_affinity[session_id] = selected_endpoint.endpoint_id
        
        return selected_endpoint
    
    def _get_available_endpoints(self, service_type: str) -> Dict[str, EndpointConfig]:
        """获取可用端点"""
        available = {}
        
        for endpoint_id, endpoint in self.endpoints.items():
            # 检查服务类型支持
            if service_type not in endpoint.service_types:
                continue
            
            # 检查端点状态
            metrics = self.metrics[endpoint_id]
            if metrics.status == EndpointStatus.UNHEALTHY:
                continue
            
            # 检查熔断器状态
            if (self.config.circuit_breaker_enabled and 
                not self.circuit_breaker.can_execute(endpoint_id)):
                continue
            
            # 检查连接数限制
            if metrics.active_connections >= endpoint.max_connections:
                continue
            
            available[endpoint_id] = endpoint
        
        return available
    
    async def _apply_load_balancing_strategy(self, available_endpoints: Dict[str, EndpointConfig],
                                           service_type: str, user_id: Optional[int]) -> Optional[EndpointConfig]:
        """应用负载均衡策略"""
        if not available_endpoints:
            return None
        
        strategy = self.config.strategy
        
        if strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin_selection(available_endpoints)
        elif strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_selection(available_endpoints)
        elif strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._least_connections_selection(available_endpoints)
        elif strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
            return self._least_response_time_selection(available_endpoints)
        elif strategy == LoadBalancingStrategy.RESOURCE_BASED:
            return self._resource_based_selection(available_endpoints)
        elif strategy == LoadBalancingStrategy.COST_OPTIMIZED:
            return await self._cost_optimized_selection(available_endpoints, user_id)
        elif strategy == LoadBalancingStrategy.INTELLIGENT:
            return await self._intelligent_selection(available_endpoints, service_type, user_id)
        else:
            # 默认使用加权轮询
            return self._weighted_round_robin_selection(available_endpoints)
    
    def _round_robin_selection(self, available_endpoints: Dict[str, EndpointConfig]) -> EndpointConfig:
        """轮询选择"""
        endpoint_list = list(available_endpoints.values())
        selected = endpoint_list[self._round_robin_index % len(endpoint_list)]
        self._round_robin_index += 1
        return selected
    
    def _weighted_round_robin_selection(self, available_endpoints: Dict[str, EndpointConfig]) -> EndpointConfig:
        """加权轮询选择"""
        weights = []
        endpoints = []
        
        for endpoint in available_endpoints.values():
            # 根据健康状态调整权重
            metrics = self.metrics[endpoint.endpoint_id]
            adjusted_weight = endpoint.weight
            
            if metrics.status == EndpointStatus.DEGRADED:
                adjusted_weight = int(adjusted_weight * 0.5)
            
            weights.append(adjusted_weight)
            endpoints.append(endpoint)
        
        # 加权随机选择
        total_weight = sum(weights)
        if total_weight == 0:
            return random.choice(endpoints)
        
        rand_val = random.randint(1, total_weight)
        cumulative_weight = 0
        
        for i, weight in enumerate(weights):
            cumulative_weight += weight
            if rand_val <= cumulative_weight:
                return endpoints[i]
        
        return endpoints[-1]
    
    def _least_connections_selection(self, available_endpoints: Dict[str, EndpointConfig]) -> EndpointConfig:
        """最少连接选择"""
        min_connections = float('inf')
        selected_endpoint = None
        
        for endpoint in available_endpoints.values():
            metrics = self.metrics[endpoint.endpoint_id]
            if metrics.active_connections < min_connections:
                min_connections = metrics.active_connections
                selected_endpoint = endpoint
        
        return selected_endpoint or list(available_endpoints.values())[0]
    
    def _least_response_time_selection(self, available_endpoints: Dict[str, EndpointConfig]) -> EndpointConfig:
        """最少响应时间选择"""
        min_response_time = float('inf')
        selected_endpoint = None
        
        for endpoint in available_endpoints.values():
            metrics = self.metrics[endpoint.endpoint_id]
            avg_time = metrics.average_response_time if metrics.total_requests > 0 else 0
            
            # 考虑当前连接数的影响
            adjusted_time = avg_time * (1 + metrics.active_connections / endpoint.max_connections)
            
            if adjusted_time < min_response_time:
                min_response_time = adjusted_time
                selected_endpoint = endpoint
        
        return selected_endpoint or list(available_endpoints.values())[0]
    
    def _resource_based_selection(self, available_endpoints: Dict[str, EndpointConfig]) -> EndpointConfig:
        """基于资源的选择"""
        best_score = -1
        selected_endpoint = None
        
        for endpoint in available_endpoints.values():
            metrics = self.metrics[endpoint.endpoint_id]
            
            # 计算资源利用率评分
            connection_ratio = metrics.active_connections / endpoint.max_connections
            error_rate = metrics.error_rate / 100.0
            
            # 综合评分（越低越好）
            score = connection_ratio + error_rate
            
            # 考虑端点优先级
            score = score / endpoint.priority
            
            if best_score == -1 or score < best_score:
                best_score = score
                selected_endpoint = endpoint
        
        return selected_endpoint or list(available_endpoints.values())[0]
    
    async def _cost_optimized_selection(self, available_endpoints: Dict[str, EndpointConfig],
                                       user_id: Optional[int]) -> EndpointConfig:
        """成本优化选择"""
        # 根据用户的余额情况选择成本最优端点
        if user_id:
            try:
                async with get_db() as db:
                    # 获取用户账户余额
                    balance_info = await self._get_user_balance_info(db, user_id)
                    
                    if balance_info and balance_info.is_low_balance():
                        # 余额不足时选择成本最低的端点
                        return min(available_endpoints.values(), 
                                 key=lambda ep: ep.cost_per_request)
            except Exception as e:
                logger.warning(f"Failed to get user balance info: {e}")
        
        # 默认选择成本适中、性能好的端点
        return self._least_response_time_selection(available_endpoints)
    
    async def _intelligent_selection(self, available_endpoints: Dict[str, EndpointConfig],
                                    service_type: str, user_id: Optional[int]) -> EndpointConfig:
        """智能选择"""
        # 综合多个因素的智能选择算法
        best_score = -1
        selected_endpoint = None
        
        for endpoint in available_endpoints.values():
            metrics = self.metrics[endpoint.endpoint_id]
            
            # 性能评分 (0-1, 越高越好)
            if metrics.total_requests > 0:
                success_rate = metrics.successful_requests / metrics.total_requests
                avg_response_time = metrics.average_response_time
                performance_score = success_rate * (1.0 / max(avg_response_time, 0.001))
            else:
                performance_score = 1.0
            
            # 负载评分 (0-1, 越高越好)
            load_ratio = metrics.active_connections / endpoint.max_connections
            load_score = 1.0 - load_ratio
            
            # 优先级评分 (0-1, 越高越好)
            priority_score = 1.0 / endpoint.priority
            
            # 成本评分 (0-1, 越高越好，成本越低评分越高)
            max_cost = max(ep.cost_per_request for ep in available_endpoints.values())
            cost_score = 1.0 - (endpoint.cost_per_request / max_cost) if max_cost > 0 else 1.0
            
            # 健康状态评分
            health_score = {
                EndpointStatus.HEALTHY: 1.0,
                EndpointStatus.DEGRADED: 0.7,
                EndpointStatus.UNHEALTHY: 0.0,
                EndpointStatus.MAINTENANCE: 0.0
            }[metrics.status]
            
            # 综合评分
            score = (
                performance_score * 0.3 +
                load_score * 0.25 +
                priority_score * 0.2 +
                cost_score * 0.15 +
                health_score * 0.1
            )
            
            if score > best_score:
                best_score = score
                selected_endpoint = endpoint
        
        return selected_endpoint or list(available_endpoints.values())[0]
    
    async def _get_user_balance_info(self, db: AsyncSession, user_id: int) -> Optional[DoubaoAccountBalance]:
        """获取用户余额信息"""
        from sqlalchemy import select
        
        stmt = select(DoubaoAccountBalance).where(
            DoubaoAccountBalance.is_primary == True
        ).limit(1)
        
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def record_request_start(self, endpoint_id: str):
        """记录请求开始"""
        if endpoint_id in self.metrics:
            self.metrics[endpoint_id].active_connections += 1
            self.metrics[endpoint_id].total_requests += 1
    
    async def record_request_end(self, endpoint_id: str, success: bool, response_time: float):
        """记录请求结束"""
        if endpoint_id not in self.metrics:
            return
        
        metrics = self.metrics[endpoint_id]
        metrics.active_connections = max(0, metrics.active_connections - 1)
        
        if success:
            metrics.successful_requests += 1
            await self.circuit_breaker.record_success(endpoint_id)
            metrics.consecutive_failures = 0
        else:
            metrics.failed_requests += 1
            await self.circuit_breaker.record_failure(endpoint_id)
            metrics.consecutive_failures += 1
            metrics.last_failure_time = datetime.now()
        
        # 更新响应时间统计
        if response_time > 0:
            metrics.total_response_time += response_time
            metrics.last_response_time = response_time
            metrics.average_response_time = metrics.total_response_time / metrics.total_requests
            metrics.min_response_time = min(metrics.min_response_time, response_time)
            metrics.max_response_time = max(metrics.max_response_time, response_time)
            
            # 记录响应时间历史
            self._response_time_history[endpoint_id].append(response_time)
        
        # 更新错误率
        if metrics.total_requests > 0:
            metrics.error_rate = (metrics.failed_requests / metrics.total_requests) * 100
        
        # 更新状态
        await self._update_endpoint_status(endpoint_id)
    
    async def _update_endpoint_status(self, endpoint_id: str):
        """更新端点状态"""
        metrics = self.metrics[endpoint_id]
        
        # 检查连续失败次数
        if metrics.consecutive_failures >= self.config.max_consecutive_failures:
            metrics.status = EndpointStatus.UNHEALTHY
        elif metrics.error_rate > self.config.failover_threshold * 100:
            metrics.status = EndpointStatus.UNHEALTHY
        elif metrics.error_rate > self.config.degraded_threshold * 100:
            metrics.status = EndpointStatus.DEGRADED
        else:
            metrics.status = EndpointStatus.HEALTHY
    
    async def start_health_checks(self):
        """启动健康检查"""
        if self._health_check_task is None or self._health_check_task.done():
            self._health_check_task = asyncio.create_task(self._health_check_loop())
            logger.info("Health check started")
    
    async def stop_health_checks(self):
        """停止健康检查"""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            logger.info("Health check stopped")
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
    
    async def _perform_health_checks(self):
        """执行健康检查"""
        tasks = []
        
        for endpoint_id, endpoint in self.endpoints.items():
            task = asyncio.create_task(
                self._check_endpoint_health(endpoint_id, endpoint)
            )
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_endpoint_health(self, endpoint_id: str, endpoint: EndpointConfig):
        """检查单个端点健康状态"""
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.health_check_timeout)
            ) as session:
                health_url = f"{endpoint.url}/health"
                
                async with session.get(health_url) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        # 健康检查成功
                        await self.record_request_end(endpoint_id, True, response_time)
                        
                        # 如果之前是不健康状态，现在恢复了
                        if self.metrics[endpoint_id].status == EndpointStatus.UNHEALTHY:
                            self.metrics[endpoint_id].status = EndpointStatus.HEALTHY
                            self.metrics[endpoint_id].consecutive_failures = 0
                            logger.info(f"Endpoint {endpoint_id} recovered")
                    else:
                        # 健康检查失败
                        await self.record_request_end(endpoint_id, False, response_time)
                        logger.warning(f"Endpoint {endpoint_id} health check failed: {response.status}")
                    
                    self.metrics[endpoint_id].last_health_check = datetime.now()
        
        except Exception as e:
            # 健康检查异常
            await self.record_request_end(endpoint_id, False, 0)
            logger.warning(f"Endpoint {endpoint_id} health check error: {e}")
            self.metrics[endpoint_id].last_health_check = datetime.now()
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取负载均衡器指标"""
        metrics_data = {}
        
        for endpoint_id, endpoint in self.endpoints.items():
            metrics = self.metrics[endpoint_id]
            
            # 计算P95响应时间
            response_times = list(self._response_time_history[endpoint_id])
            p95_response_time = 0.0
            if response_times:
                sorted_times = sorted(response_times)
                p95_index = int(len(sorted_times) * 0.95)
                p95_response_time = sorted_times[p95_index] if p95_index < len(sorted_times) else sorted_times[-1]
            
            metrics_data[endpoint_id] = {
                "endpoint_url": endpoint.url,
                "status": metrics.status.value,
                "total_requests": metrics.total_requests,
                "successful_requests": metrics.successful_requests,
                "failed_requests": metrics.failed_requests,
                "active_connections": metrics.active_connections,
                "max_connections": endpoint.max_connections,
                "connection_ratio": metrics.active_connections / endpoint.max_connections,
                "average_response_time": metrics.average_response_time,
                "min_response_time": metrics.min_response_time if metrics.min_response_time != float('inf') else 0,
                "max_response_time": metrics.max_response_time,
                "p95_response_time": p95_response_time,
                "error_rate": metrics.error_rate,
                "consecutive_failures": metrics.consecutive_failures,
                "last_health_check": metrics.last_health_check.isoformat(),
                "weight": endpoint.weight,
                "priority": endpoint.priority,
                "cost_per_request": endpoint.cost_per_request,
                "service_types": endpoint.service_types
            }
        
        return {
            "strategy": self.config.strategy.value,
            "total_endpoints": len(self.endpoints),
            "healthy_endpoints": sum(1 for m in self.metrics.values() if m.status == EndpointStatus.HEALTHY),
            "endpoints": metrics_data
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        healthy_count = sum(1 for m in self.metrics.values() if m.status == EndpointStatus.HEALTHY)
        total_count = len(self.endpoints)
        
        return {
            "status": "healthy" if healthy_count > 0 else "unhealthy",
            "total_endpoints": total_count,
            "healthy_endpoints": healthy_count,
            "health_check_enabled": self._health_check_task is not None and not self._health_check_task.done(),
            "strategy": self.config.strategy.value,
            "circuit_breaker_enabled": self.config.circuit_breaker_enabled
        }