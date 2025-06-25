"""
Doubao API Manager Service
豆包API管理服务 - [services][doubao_api][doubao_api_manager]
"""

import asyncio
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json

import aiohttp
import aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.cache.cache_manager import CacheManager
from app.integrations.volcano_enhanced import VolcanoEnhancedIntegration
from app.services.doubao_service import DoubaoService
from app.models.doubao_usage import DoubaoUsageRecord
from app.utils.rate_limiter import RateLimiter
from app.utils.circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)


class DoubaoServiceType(Enum):
    """豆包服务类型枚举"""
    TTS = "tts"
    VOICE_CLONE = "voice_clone" 
    TEXT_ANALYSIS = "text_analysis"
    IMAGE_GENERATION = "image_generation"
    BATCH_PROCESSING = "batch_processing"


class DoubaoApiPriority(Enum):
    """API调用优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class DoubaoApiConfig:
    """豆包API配置"""
    app_id: str
    access_token: str
    secret_key: str
    cluster: str
    endpoint: str
    max_connections: int = 100
    connection_timeout: int = 30
    read_timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 1.0
    cache_ttl: int = 3600


@dataclass
class DoubaoApiMetrics:
    """豆包API指标统计"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    cached_requests: int = 0
    total_cost: float = 0.0
    average_latency: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class DoubaoUsageQuota:
    """豆包使用配额管理"""
    service_type: DoubaoServiceType
    daily_limit: int
    monthly_limit: int
    current_daily_usage: int = 0
    current_monthly_usage: int = 0
    cost_per_request: float = 0.0
    last_reset_date: datetime = field(default_factory=datetime.now)


class DoubaoApiManager:
    """豆包API统一管理器 - [services][doubao_api][manager]"""
    
    def __init__(self):
        self.config = self._load_config()
        self.cache_manager = CacheManager()
        self.rate_limiter = RateLimiter()
        self.circuit_breaker = CircuitBreaker()
        self.volcano_integration = VolcanoEnhancedIntegration()
        self.doubao_service = DoubaoService()
        
        # 连接池管理
        self._session_pool: Optional[aiohttp.ClientSession] = None
        self._connection_semaphore = asyncio.Semaphore(self.config.max_connections)
        
        # 指标统计
        self.metrics: Dict[DoubaoServiceType, DoubaoApiMetrics] = {
            service_type: DoubaoApiMetrics() for service_type in DoubaoServiceType
        }
        
        # 配额管理
        self.quotas: Dict[DoubaoServiceType, DoubaoUsageQuota] = {}
        self._init_quotas()
        
        # 请求队列
        self._request_queues: Dict[DoubaoApiPriority, asyncio.Queue] = {
            priority: asyncio.Queue(maxsize=1000) for priority in DoubaoApiPriority
        }
        
        # 缓存键前缀
        self.cache_prefix = "doubao_api"
        
    def _load_config(self) -> DoubaoApiConfig:
        """加载豆包API配置"""
        return DoubaoApiConfig(
            app_id=settings.VOLCANO_VOICE_APPID,
            access_token=settings.VOLCANO_VOICE_ACCESS_TOKEN,
            secret_key=settings.VOLCANO_VOICE_SECRETYKEY,
            cluster=settings.VOLCANO_VOICE_CLUSTER,
            endpoint=settings.VOLCANO_NLP_ENDPOINT,
            max_connections=getattr(settings, 'DOUBAO_MAX_CONNECTIONS', 100),
            connection_timeout=getattr(settings, 'DOUBAO_CONNECTION_TIMEOUT', 30),
            read_timeout=getattr(settings, 'DOUBAO_READ_TIMEOUT', 60),
            max_retries=getattr(settings, 'DOUBAO_MAX_RETRIES', 3),
            retry_delay=getattr(settings, 'DOUBAO_RETRY_DELAY', 1.0),
            cache_ttl=getattr(settings, 'DOUBAO_CACHE_TTL', 3600)
        )
    
    def _init_quotas(self):
        """初始化使用配额"""
        quota_configs = {
            DoubaoServiceType.TTS: DoubaoUsageQuota(
                service_type=DoubaoServiceType.TTS,
                daily_limit=10000,
                monthly_limit=300000,
                cost_per_request=0.01
            ),
            DoubaoServiceType.VOICE_CLONE: DoubaoUsageQuota(
                service_type=DoubaoServiceType.VOICE_CLONE,
                daily_limit=100,
                monthly_limit=3000,
                cost_per_request=0.1
            ),
            DoubaoServiceType.TEXT_ANALYSIS: DoubaoUsageQuota(
                service_type=DoubaoServiceType.TEXT_ANALYSIS,
                daily_limit=50000,
                monthly_limit=1500000,
                cost_per_request=0.001
            ),
            DoubaoServiceType.IMAGE_GENERATION: DoubaoUsageQuota(
                service_type=DoubaoServiceType.IMAGE_GENERATION,
                daily_limit=1000,
                monthly_limit=30000,
                cost_per_request=0.05
            ),
            DoubaoServiceType.BATCH_PROCESSING: DoubaoUsageQuota(
                service_type=DoubaoServiceType.BATCH_PROCESSING,
                daily_limit=5000,
                monthly_limit=150000,
                cost_per_request=0.002
            )
        }
        self.quotas.update(quota_configs)
    
    async def start(self):
        """启动API管理器"""
        logger.info("Starting Doubao API Manager...")
        
        # 初始化连接池
        connector = aiohttp.TCPConnector(
            limit=self.config.max_connections,
            limit_per_host=50,
            ttl_dns_cache=300,
            ttl_connection_pool=30,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(
            total=self.config.read_timeout,
            connect=self.config.connection_timeout
        )
        
        self._session_pool = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': 'DataSay-DoubaoManager/1.0'}
        )
        
        # 启动后台任务
        asyncio.create_task(self._quota_reset_scheduler())
        asyncio.create_task(self._metrics_updater())
        asyncio.create_task(self._request_processor())
        
        logger.info("Doubao API Manager started successfully")
    
    async def stop(self):
        """停止API管理器"""
        logger.info("Stopping Doubao API Manager...")
        
        if self._session_pool:
            await self._session_pool.close()
            self._session_pool = None
        
        logger.info("Doubao API Manager stopped")
    
    @asynccontextmanager
    async def _get_session(self):
        """获取HTTP会话连接"""
        async with self._connection_semaphore:
            if not self._session_pool or self._session_pool.closed:
                await self.start()
            yield self._session_pool
    
    def _generate_cache_key(self, service_type: DoubaoServiceType, 
                           method: str, **kwargs) -> str:
        """生成缓存键"""
        # 创建参数的哈希值
        params_str = json.dumps(kwargs, sort_keys=True, ensure_ascii=False)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
        
        return f"{self.cache_prefix}:{service_type.value}:{method}:{params_hash}"
    
    async def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """获取缓存结果"""
        try:
            cached_data = await self.cache_manager.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_data
        except Exception as e:
            logger.warning(f"Failed to get cache for key {cache_key}: {e}")
        return None
    
    async def _set_cached_result(self, cache_key: str, result: Dict[str, Any], 
                                ttl: Optional[int] = None):
        """设置缓存结果"""
        try:
            cache_ttl = ttl or self.config.cache_ttl
            await self.cache_manager.set(cache_key, result, ttl=cache_ttl)
            logger.debug(f"Cached result for key: {cache_key} (TTL: {cache_ttl}s)")
        except Exception as e:
            logger.warning(f"Failed to cache result for key {cache_key}: {e}")
    
    async def _check_quota(self, service_type: DoubaoServiceType, 
                          user_id: Optional[int] = None) -> bool:
        """检查使用配额"""
        quota = self.quotas.get(service_type)
        if not quota:
            return True
        
        # 检查是否需要重置配额
        now = datetime.now()
        if now.date() > quota.last_reset_date.date():
            quota.current_daily_usage = 0
            quota.last_reset_date = now
        
        # 检查月度重置
        if now.month != quota.last_reset_date.month:
            quota.current_monthly_usage = 0
        
        # 检查配额限制
        if quota.current_daily_usage >= quota.daily_limit:
            logger.warning(f"Daily quota exceeded for {service_type.value}")
            return False
        
        if quota.current_monthly_usage >= quota.monthly_limit:
            logger.warning(f"Monthly quota exceeded for {service_type.value}")
            return False
        
        return True
    
    async def _update_quota_usage(self, service_type: DoubaoServiceType, 
                                 user_id: Optional[int] = None):
        """更新配额使用量"""
        quota = self.quotas.get(service_type)
        if quota:
            quota.current_daily_usage += 1
            quota.current_monthly_usage += 1
            
            # 更新指标
            metrics = self.metrics[service_type]
            metrics.total_cost += quota.cost_per_request
    
    async def _record_usage(self, service_type: DoubaoServiceType, 
                           method: str, user_id: Optional[int], 
                           success: bool, latency: float, cost: float = 0.0):
        """记录使用情况到数据库"""
        try:
            async with get_db() as db:
                usage_record = DoubaoUsageRecord(
                    user_id=user_id,
                    service_type=service_type.value,
                    method=method,
                    success=success,
                    latency=latency,
                    cost=cost,
                    created_at=datetime.now()
                )
                db.add(usage_record)
                await db.commit()
        except Exception as e:
            logger.error(f"Failed to record usage: {e}")
    
    async def _update_metrics(self, service_type: DoubaoServiceType, 
                             success: bool, latency: float, cached: bool = False):
        """更新指标统计"""
        metrics = self.metrics[service_type]
        metrics.total_requests += 1
        
        if success:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1
        
        if cached:
            metrics.cached_requests += 1
        
        # 更新平均延迟
        total_latency = metrics.average_latency * (metrics.total_requests - 1) + latency
        metrics.average_latency = total_latency / metrics.total_requests
        
        metrics.last_updated = datetime.now()
    
    async def call_api(self, service_type: DoubaoServiceType, method: str,
                       priority: DoubaoApiPriority = DoubaoApiPriority.NORMAL,
                       use_cache: bool = True, cache_ttl: Optional[int] = None,
                       user_id: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """统一API调用接口"""
        start_time = time.time()
        
        try:
            # 检查配额
            if not await self._check_quota(service_type, user_id):
                raise Exception(f"Quota exceeded for service {service_type.value}")
            
            # 检查缓存
            cache_key = None
            if use_cache:
                cache_key = self._generate_cache_key(service_type, method, **kwargs)
                cached_result = await self._get_cached_result(cache_key)
                if cached_result:
                    latency = time.time() - start_time
                    await self._update_metrics(service_type, True, latency, cached=True)
                    return cached_result
            
            # 检查熔断器状态
            if not self.circuit_breaker.can_execute(service_type.value):
                raise Exception(f"Circuit breaker open for service {service_type.value}")
            
            # 添加到请求队列
            request_data = {
                'service_type': service_type,
                'method': method,
                'kwargs': kwargs,
                'user_id': user_id,
                'cache_key': cache_key,
                'cache_ttl': cache_ttl,
                'start_time': start_time
            }
            
            await self._request_queues[priority].put(request_data)
            
            # 等待结果（这里应该实现更复杂的结果返回机制）
            # 暂时直接调用API
            result = await self._execute_api_call(service_type, method, **kwargs)
            
            # 更新指标和配额
            latency = time.time() - start_time
            await self._update_metrics(service_type, True, latency)
            await self._update_quota_usage(service_type, user_id)
            
            # 记录使用情况
            quota = self.quotas.get(service_type, DoubaoUsageQuota(service_type, 0, 0))
            await self._record_usage(service_type, method, user_id, True, latency, quota.cost_per_request)
            
            # 缓存结果
            if use_cache and cache_key:
                await self._set_cached_result(cache_key, result, cache_ttl)
            
            # 通知熔断器成功
            self.circuit_breaker.record_success(service_type.value)
            
            return result
            
        except Exception as e:
            latency = time.time() - start_time
            await self._update_metrics(service_type, False, latency)
            
            # 记录失败
            await self._record_usage(service_type, method, user_id, False, latency)
            
            # 通知熔断器失败
            self.circuit_breaker.record_failure(service_type.value)
            
            logger.error(f"API call failed for {service_type.value}.{method}: {e}")
            raise
    
    async def _execute_api_call(self, service_type: DoubaoServiceType, 
                               method: str, **kwargs) -> Dict[str, Any]:
        """执行实际的API调用"""
        # 根据服务类型路由到相应的实现
        if service_type == DoubaoServiceType.TTS:
            return await self._call_tts_api(method, **kwargs)
        elif service_type == DoubaoServiceType.VOICE_CLONE:
            return await self._call_voice_clone_api(method, **kwargs)
        elif service_type == DoubaoServiceType.TEXT_ANALYSIS:
            return await self._call_text_analysis_api(method, **kwargs)
        elif service_type == DoubaoServiceType.IMAGE_GENERATION:
            return await self._call_image_generation_api(method, **kwargs)
        elif service_type == DoubaoServiceType.BATCH_PROCESSING:
            return await self._call_batch_processing_api(method, **kwargs)
        else:
            raise ValueError(f"Unknown service type: {service_type}")
    
    async def _call_tts_api(self, method: str, **kwargs) -> Dict[str, Any]:
        """调用TTS API"""
        if method == "synthesize":
            return await self.volcano_integration.text_to_speech(
                text=kwargs.get('text'),
                speaker_id=kwargs.get('speaker_id'),
                encoding=kwargs.get('encoding', 'mp3'),
                rate=kwargs.get('rate', 1.0),
                volume=kwargs.get('volume', 1.0),
                pitch=kwargs.get('pitch', 1.0)
            )
        elif method == "get_speakers":
            return await self.volcano_integration.get_speaker_list()
        else:
            raise ValueError(f"Unknown TTS method: {method}")
    
    async def _call_voice_clone_api(self, method: str, **kwargs) -> Dict[str, Any]:
        """调用语音克隆API"""
        if method == "upload_audio":
            return await self.volcano_integration.upload_audio_for_clone(
                audio_data=kwargs.get('audio_data'),
                speaker_name=kwargs.get('speaker_name'),
                speaker_gender=kwargs.get('speaker_gender')
            )
        elif method == "get_clone_status":
            return await self.volcano_integration.get_clone_status(
                clone_id=kwargs.get('clone_id')
            )
        elif method == "get_cloned_speakers":
            return await self.volcano_integration.get_cloned_speaker_list()
        else:
            raise ValueError(f"Unknown voice clone method: {method}")
    
    async def _call_text_analysis_api(self, method: str, **kwargs) -> Dict[str, Any]:
        """调用文本分析API"""
        if method == "analyze":
            return await self.doubao_service.analyze_text(
                text=kwargs.get('text'),
                analysis_type=kwargs.get('analysis_type', 'sentiment')
            )
        elif method == "preprocess":
            return await self.doubao_service.preprocess_text(
                text=kwargs.get('text')
            )
        else:
            raise ValueError(f"Unknown text analysis method: {method}")
    
    async def _call_image_generation_api(self, method: str, **kwargs) -> Dict[str, Any]:
        """调用图像生成API"""
        # 这里需要实现图像生成API调用
        # 目前返回占位符结果
        return {
            "status": "success",
            "message": "Image generation API not implemented yet",
            "method": method,
            "kwargs": kwargs
        }
    
    async def _call_batch_processing_api(self, method: str, **kwargs) -> Dict[str, Any]:
        """调用批处理API"""
        # 这里需要实现批处理API调用
        # 目前返回占位符结果
        return {
            "status": "success", 
            "message": "Batch processing API not implemented yet",
            "method": method,
            "kwargs": kwargs
        }
    
    async def _quota_reset_scheduler(self):
        """配额重置调度器"""
        while True:
            try:
                await asyncio.sleep(3600)  # 每小时检查一次
                now = datetime.now()
                
                for service_type, quota in self.quotas.items():
                    # 检查日度重置
                    if now.date() > quota.last_reset_date.date():
                        quota.current_daily_usage = 0
                        quota.last_reset_date = now
                        logger.info(f"Reset daily quota for {service_type.value}")
                    
                    # 检查月度重置
                    if now.month != quota.last_reset_date.month:
                        quota.current_monthly_usage = 0
                        logger.info(f"Reset monthly quota for {service_type.value}")
                        
            except Exception as e:
                logger.error(f"Error in quota reset scheduler: {e}")
    
    async def _metrics_updater(self):
        """指标更新器"""
        while True:
            try:
                await asyncio.sleep(300)  # 每5分钟更新一次
                
                # 这里可以将指标数据持久化到数据库或发送到监控系统
                for service_type, metrics in self.metrics.items():
                    logger.debug(f"Metrics for {service_type.value}: "
                               f"Total: {metrics.total_requests}, "
                               f"Success: {metrics.successful_requests}, "
                               f"Failed: {metrics.failed_requests}, "
                               f"Cached: {metrics.cached_requests}, "
                               f"Avg Latency: {metrics.average_latency:.3f}s")
                        
            except Exception as e:
                logger.error(f"Error in metrics updater: {e}")
    
    async def _request_processor(self):
        """请求处理器"""
        while True:
            try:
                # 按优先级处理请求
                for priority in reversed(list(DoubaoApiPriority)):
                    queue = self._request_queues[priority]
                    if not queue.empty():
                        request_data = await queue.get()
                        # 处理请求（这里应该实现异步处理逻辑）
                        logger.debug(f"Processing {priority.name} priority request")
                        
                await asyncio.sleep(0.1)  # 避免过度CPU使用
                        
            except Exception as e:
                logger.error(f"Error in request processor: {e}")
    
    def get_metrics(self, service_type: Optional[DoubaoServiceType] = None) -> Dict[str, Any]:
        """获取指标统计"""
        if service_type:
            return {
                service_type.value: {
                    'total_requests': self.metrics[service_type].total_requests,
                    'successful_requests': self.metrics[service_type].successful_requests,
                    'failed_requests': self.metrics[service_type].failed_requests,
                    'cached_requests': self.metrics[service_type].cached_requests,
                    'total_cost': self.metrics[service_type].total_cost,
                    'average_latency': self.metrics[service_type].average_latency,
                    'last_updated': self.metrics[service_type].last_updated.isoformat()
                }
            }
        
        return {
            service_type.value: {
                'total_requests': metrics.total_requests,
                'successful_requests': metrics.successful_requests,
                'failed_requests': metrics.failed_requests,
                'cached_requests': metrics.cached_requests,
                'total_cost': metrics.total_cost,
                'average_latency': metrics.average_latency,
                'last_updated': metrics.last_updated.isoformat()
            }
            for service_type, metrics in self.metrics.items()
        }
    
    def get_quotas(self) -> Dict[str, Any]:
        """获取配额信息"""
        return {
            service_type.value: {
                'daily_limit': quota.daily_limit,
                'monthly_limit': quota.monthly_limit,
                'current_daily_usage': quota.current_daily_usage,
                'current_monthly_usage': quota.current_monthly_usage,
                'cost_per_request': quota.cost_per_request,
                'daily_remaining': quota.daily_limit - quota.current_daily_usage,
                'monthly_remaining': quota.monthly_limit - quota.current_monthly_usage,
                'last_reset_date': quota.last_reset_date.isoformat()
            }
            for service_type, quota in self.quotas.items()
        }


# 全局单例
doubao_api_manager = DoubaoApiManager()