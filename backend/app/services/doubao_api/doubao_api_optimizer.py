"""
Doubao API Optimizer Service
豆包API优化服务 - [services][doubao_api][doubao_api_optimizer]
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import statistics

from app.cache.cache_manager import CacheManager
from app.services.doubao_api.doubao_api_manager import DoubaoApiManager, DoubaoServiceType
from app.utils.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from app.utils.rate_limiter import RateLimiter, RateLimitConfig

logger = logging.getLogger(__name__)


class OptimizationStrategy(Enum):
    """优化策略枚举"""
    CACHE_FIRST = "cache_first"
    BATCH_PROCESSING = "batch_processing"
    INTELLIGENT_RETRY = "intelligent_retry"
    LOAD_BALANCING = "load_balancing"
    COST_OPTIMIZATION = "cost_optimization"
    LATENCY_OPTIMIZATION = "latency_optimization"


@dataclass
class OptimizationConfig:
    """优化配置"""
    enable_intelligent_caching: bool = True
    enable_request_batching: bool = True
    enable_adaptive_retry: bool = True
    enable_load_balancing: bool = True
    enable_cost_optimization: bool = True
    
    # 缓存配置
    cache_ttl_short: int = 300      # 5分钟
    cache_ttl_medium: int = 1800    # 30分钟
    cache_ttl_long: int = 7200      # 2小时
    
    # 批处理配置
    batch_size: int = 10
    batch_timeout: float = 2.0
    
    # 重试配置
    max_retries: int = 3
    retry_backoff_base: float = 1.0
    retry_backoff_max: float = 30.0
    
    # 负载均衡配置
    health_check_interval: int = 60
    failover_threshold: float = 0.8


@dataclass
class RequestContext:
    """请求上下文"""
    service_type: DoubaoServiceType
    method: str
    params: Dict[str, Any]
    user_id: Optional[int] = None
    priority: int = 1
    timeout: float = 30.0
    retry_count: int = 0
    start_time: float = 0.0


@dataclass
class OptimizationResult:
    """优化结果"""
    strategy_used: List[OptimizationStrategy]
    cache_hit: bool = False
    batched: bool = False
    retried: int = 0
    load_balanced: bool = False
    cost_optimized: bool = False
    original_latency: float = 0.0
    optimized_latency: float = 0.0
    cost_saved: float = 0.0


class DoubaoApiOptimizer:
    """豆包API优化器 - [services][doubao_api][optimizer]"""
    
    def __init__(self, api_manager: DoubaoApiManager):
        self.api_manager = api_manager
        self.cache_manager = CacheManager()
        self.circuit_breaker = CircuitBreaker()
        self.rate_limiter = RateLimiter()
        
        self.config = OptimizationConfig()
        
        # 批处理队列
        self._batch_queues: Dict[str, List[RequestContext]] = {}
        self._batch_timers: Dict[str, float] = {}
        
        # 性能统计
        self._performance_stats: Dict[str, List[float]] = {}
        self._cost_stats: Dict[str, List[float]] = {}
        
        # 负载均衡状态
        self._endpoint_health: Dict[str, float] = {}
        self._endpoint_load: Dict[str, int] = {}
        
        # 智能缓存策略
        self._cache_strategies: Dict[str, int] = {}
        
    async def optimize_request(self, context: RequestContext) -> Tuple[Any, OptimizationResult]:
        """优化API请求"""
        result = OptimizationResult(strategy_used=[])
        context.start_time = time.time()
        
        try:
            # 1. 智能缓存检查
            cached_response = await self._check_intelligent_cache(context, result)
            if cached_response is not None:
                result.optimized_latency = time.time() - context.start_time
                return cached_response, result
            
            # 2. 请求批处理
            if self.config.enable_request_batching and self._should_batch_request(context):
                return await self._handle_batch_request(context, result)
            
            # 3. 负载均衡
            if self.config.enable_load_balancing:
                context = await self._apply_load_balancing(context, result)
            
            # 4. 成本优化
            if self.config.enable_cost_optimization:
                context = await self._apply_cost_optimization(context, result)
            
            # 5. 执行请求
            response = await self._execute_optimized_request(context, result)
            
            # 6. 后处理优化
            await self._post_process_optimization(context, response, result)
            
            result.optimized_latency = time.time() - context.start_time
            return response, result
            
        except Exception as e:
            # 7. 智能重试
            if self.config.enable_adaptive_retry and self._should_retry(context, e):
                return await self._handle_intelligent_retry(context, result, e)
            else:
                raise
    
    async def _check_intelligent_cache(self, context: RequestContext, 
                                     result: OptimizationResult) -> Optional[Any]:
        """智能缓存检查"""
        if not self.config.enable_intelligent_caching:
            return None
        
        cache_key = self._generate_intelligent_cache_key(context)
        
        # 根据请求类型选择缓存策略
        ttl = self._get_intelligent_cache_ttl(context)
        
        try:
            cached_data = await self.cache_manager.get(cache_key)
            if cached_data:
                result.strategy_used.append(OptimizationStrategy.CACHE_FIRST)
                result.cache_hit = True
                
                # 更新缓存命中统计
                self._update_cache_stats(cache_key, True)
                
                logger.debug(f"Cache hit for {context.service_type.value}.{context.method}")
                return cached_data
            
        except Exception as e:
            logger.warning(f"Cache check failed: {e}")
        
        return None
    
    def _generate_intelligent_cache_key(self, context: RequestContext) -> str:
        """生成智能缓存键"""
        # 根据服务类型和参数生成缓存键
        key_components = [
            context.service_type.value,
            context.method,
        ]
        
        # 对参数进行标准化处理
        normalized_params = self._normalize_cache_params(context.params)
        params_hash = hashlib.md5(
            json.dumps(normalized_params, sort_keys=True).encode()
        ).hexdigest()[:12]
        
        key_components.append(params_hash)
        
        # 添加用户ID（如果需要用户级缓存）
        if context.user_id and self._requires_user_cache(context):
            key_components.append(f"user_{context.user_id}")
        
        return "doubao_opt:" + ":".join(key_components)
    
    def _normalize_cache_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """标准化缓存参数"""
        # 移除不影响结果的参数
        ignore_keys = {'request_id', 'timestamp', 'callback_url', 'metadata'}
        
        normalized = {}
        for key, value in params.items():
            if key not in ignore_keys:
                # 对某些参数进行标准化
                if key == 'text' and isinstance(value, str):
                    # 文本内容去除首尾空格
                    normalized[key] = value.strip()
                elif key in ['rate', 'volume', 'pitch'] and isinstance(value, (int, float)):
                    # 音频参数四舍五入到两位小数
                    normalized[key] = round(float(value), 2)
                else:
                    normalized[key] = value
        
        return normalized
    
    def _get_intelligent_cache_ttl(self, context: RequestContext) -> int:
        """获取智能缓存TTL"""
        # 根据服务类型和历史性能确定缓存时间
        service_key = f"{context.service_type.value}.{context.method}"
        
        # 基础TTL策略
        if context.service_type == DoubaoServiceType.TTS:
            if context.method == "get_speakers":
                return self.config.cache_ttl_long  # 说话人列表变化不频繁
            else:
                return self.config.cache_ttl_medium  # TTS结果可以缓存较久
        elif context.service_type == DoubaoServiceType.VOICE_CLONE:
            if context.method == "get_clone_status":
                return self.config.cache_ttl_short  # 状态查询缓存时间短
            else:
                return self.config.cache_ttl_medium
        elif context.service_type == DoubaoServiceType.TEXT_ANALYSIS:
            return self.config.cache_ttl_medium
        else:
            return self.config.cache_ttl_short
    
    def _requires_user_cache(self, context: RequestContext) -> bool:
        """判断是否需要用户级缓存"""
        # 某些API结果是用户特定的
        user_specific_methods = {
            'get_cloned_speakers', 'get_user_voices', 'get_user_templates'
        }
        return context.method in user_specific_methods
    
    def _should_batch_request(self, context: RequestContext) -> bool:
        """判断是否应该批处理请求"""
        # 只有特定类型的请求支持批处理
        batchable_methods = {
            DoubaoServiceType.TTS: ['synthesize'],
            DoubaoServiceType.TEXT_ANALYSIS: ['analyze', 'preprocess'],
            DoubaoServiceType.IMAGE_GENERATION: ['generate']
        }
        
        return (context.service_type in batchable_methods and 
                context.method in batchable_methods[context.service_type])
    
    async def _handle_batch_request(self, context: RequestContext, 
                                   result: OptimizationResult) -> Tuple[Any, OptimizationResult]:
        """处理批处理请求"""
        batch_key = f"{context.service_type.value}.{context.method}"
        
        # 添加到批处理队列
        if batch_key not in self._batch_queues:
            self._batch_queues[batch_key] = []
            self._batch_timers[batch_key] = time.time()
        
        self._batch_queues[batch_key].append(context)
        
        # 检查是否达到批处理条件
        should_execute = (
            len(self._batch_queues[batch_key]) >= self.config.batch_size or
            time.time() - self._batch_timers[batch_key] >= self.config.batch_timeout
        )
        
        if should_execute:
            batch_contexts = self._batch_queues[batch_key].copy()
            self._batch_queues[batch_key].clear()
            
            result.strategy_used.append(OptimizationStrategy.BATCH_PROCESSING)
            result.batched = True
            
            # 执行批处理
            batch_response = await self._execute_batch_request(batch_contexts)
            
            # 找到当前请求的响应
            current_response = self._extract_response_from_batch(context, batch_response)
            return current_response, result
        else:
            # 等待批处理或超时
            await asyncio.sleep(0.1)
            return await self._handle_batch_request(context, result)
    
    async def _execute_batch_request(self, contexts: List[RequestContext]) -> Any:
        """执行批处理请求"""
        # 合并参数
        batch_params = self._merge_batch_params(contexts)
        
        # 使用第一个上下文作为模板
        template_context = contexts[0]
        
        # 调用批处理API
        response = await self.api_manager.call_api(
            service_type=template_context.service_type,
            method=f"batch_{template_context.method}",
            **batch_params
        )
        
        return response
    
    def _merge_batch_params(self, contexts: List[RequestContext]) -> Dict[str, Any]:
        """合并批处理参数"""
        # 这里需要根据具体的API实现参数合并逻辑
        batch_params = {"batch_size": len(contexts)}
        
        # 例如对于TTS批处理
        if contexts[0].service_type == DoubaoServiceType.TTS:
            batch_params["texts"] = [ctx.params.get("text", "") for ctx in contexts]
            batch_params["speaker_id"] = contexts[0].params.get("speaker_id")
            # 其他通用参数使用第一个请求的参数
            
        return batch_params
    
    def _extract_response_from_batch(self, context: RequestContext, batch_response: Any) -> Any:
        """从批处理响应中提取当前请求的响应"""
        # 这里需要根据批处理响应格式实现
        # 暂时返回整个批处理响应
        return batch_response
    
    async def _apply_load_balancing(self, context: RequestContext, 
                                   result: OptimizationResult) -> RequestContext:
        """应用负载均衡"""
        # 选择最佳端点
        best_endpoint = await self._select_best_endpoint(context)
        
        if best_endpoint:
            context.params['endpoint'] = best_endpoint
            result.strategy_used.append(OptimizationStrategy.LOAD_BALANCING)
            result.load_balanced = True
        
        return context
    
    async def _select_best_endpoint(self, context: RequestContext) -> Optional[str]:
        """选择最佳端点"""
        # 获取可用端点列表
        available_endpoints = self._get_available_endpoints(context.service_type)
        
        if not available_endpoints:
            return None
        
        # 根据健康状态和负载选择最佳端点
        best_endpoint = None
        best_score = -1
        
        for endpoint in available_endpoints:
            score = self._calculate_endpoint_score(endpoint)
            if score > best_score:
                best_score = score
                best_endpoint = endpoint
        
        return best_endpoint
    
    def _get_available_endpoints(self, service_type: DoubaoServiceType) -> List[str]:
        """获取可用端点列表"""
        # 这里应该从配置或服务发现中获取端点列表
        # 暂时返回示例端点
        if service_type == DoubaoServiceType.TTS:
            return [
                "https://openspeech.bytedance.com/api/v1/tts",
                "https://openspeech-backup.bytedance.com/api/v1/tts"
            ]
        return []
    
    def _calculate_endpoint_score(self, endpoint: str) -> float:
        """计算端点评分"""
        health = self._endpoint_health.get(endpoint, 1.0)
        load = self._endpoint_load.get(endpoint, 0)
        
        # 综合考虑健康状态和负载
        score = health * (1.0 - min(load / 100.0, 0.9))
        return score
    
    async def _apply_cost_optimization(self, context: RequestContext, 
                                      result: OptimizationResult) -> RequestContext:
        """应用成本优化"""
        # 根据服务类型应用不同的成本优化策略
        if context.service_type == DoubaoServiceType.TTS:
            context = await self._optimize_tts_cost(context)
        elif context.service_type == DoubaoServiceType.VOICE_CLONE:
            context = await self._optimize_voice_clone_cost(context)
        elif context.service_type == DoubaoServiceType.TEXT_ANALYSIS:
            context = await self._optimize_text_analysis_cost(context)
        
        result.strategy_used.append(OptimizationStrategy.COST_OPTIMIZATION)
        result.cost_optimized = True
        
        return context
    
    async def _optimize_tts_cost(self, context: RequestContext) -> RequestContext:
        """优化TTS成本"""
        params = context.params
        
        # 智能选择音质
        text_length = len(params.get('text', ''))
        if text_length < 100:
            # 短文本使用标准音质
            params['quality'] = 'standard'
        elif text_length < 1000:
            # 中等长度文本使用高音质
            params['quality'] = 'high'
        else:
            # 长文本根据用户设置或使用标准音质
            params['quality'] = params.get('quality', 'standard')
        
        # 智能选择编码格式
        if 'encoding' not in params:
            params['encoding'] = 'mp3'  # 默认使用压缩格式
        
        return context
    
    async def _optimize_voice_clone_cost(self, context: RequestContext) -> RequestContext:
        """优化语音克隆成本"""
        # 语音克隆的成本优化策略
        return context
    
    async def _optimize_text_analysis_cost(self, context: RequestContext) -> RequestContext:
        """优化文本分析成本"""
        # 文本分析的成本优化策略
        return context
    
    async def _execute_optimized_request(self, context: RequestContext, 
                                        result: OptimizationResult) -> Any:
        """执行优化后的请求"""
        try:
            response = await self.api_manager.call_api(
                service_type=context.service_type,
                method=context.method,
                user_id=context.user_id,
                **context.params
            )
            return response
            
        except Exception as e:
            logger.error(f"Optimized request failed: {e}")
            raise
    
    async def _post_process_optimization(self, context: RequestContext, 
                                        response: Any, result: OptimizationResult):
        """后处理优化"""
        # 缓存响应
        if self.config.enable_intelligent_caching and not result.cache_hit:
            cache_key = self._generate_intelligent_cache_key(context)
            ttl = self._get_intelligent_cache_ttl(context)
            
            try:
                await self.cache_manager.set(cache_key, response, ttl=ttl)
                self._update_cache_stats(cache_key, False)
            except Exception as e:
                logger.warning(f"Failed to cache response: {e}")
        
        # 更新性能统计
        service_key = f"{context.service_type.value}.{context.method}"
        latency = result.optimized_latency
        
        if service_key not in self._performance_stats:
            self._performance_stats[service_key] = []
        
        self._performance_stats[service_key].append(latency)
        
        # 保持统计数据在合理范围内
        if len(self._performance_stats[service_key]) > 1000:
            self._performance_stats[service_key] = self._performance_stats[service_key][-500:]
    
    def _should_retry(self, context: RequestContext, error: Exception) -> bool:
        """判断是否应该重试"""
        if context.retry_count >= self.config.max_retries:
            return False
        
        # 根据错误类型判断是否应该重试
        retryable_errors = {
            'TimeoutError', 'ConnectionError', 'HTTPError',
            'ServiceUnavailable', 'RateLimitExceeded'
        }
        
        error_type = type(error).__name__
        return error_type in retryable_errors
    
    async def _handle_intelligent_retry(self, context: RequestContext, 
                                       result: OptimizationResult, 
                                       error: Exception) -> Tuple[Any, OptimizationResult]:
        """处理智能重试"""
        context.retry_count += 1
        result.retried = context.retry_count
        result.strategy_used.append(OptimizationStrategy.INTELLIGENT_RETRY)
        
        # 计算重试延迟
        delay = self._calculate_retry_delay(context, error)
        
        logger.info(f"Retrying request {context.retry_count}/{self.config.max_retries} "
                   f"after {delay}s delay")
        
        await asyncio.sleep(delay)
        
        # 重新执行优化请求
        return await self.optimize_request(context)
    
    def _calculate_retry_delay(self, context: RequestContext, error: Exception) -> float:
        """计算重试延迟"""
        base_delay = self.config.retry_backoff_base
        
        # 指数退避
        delay = base_delay * (2 ** (context.retry_count - 1))
        
        # 添加抖动
        import random
        jitter = random.uniform(0.1, 0.3) * delay
        delay += jitter
        
        # 限制最大延迟
        delay = min(delay, self.config.retry_backoff_max)
        
        return delay
    
    def _update_cache_stats(self, cache_key: str, hit: bool):
        """更新缓存统计"""
        # 更新缓存策略统计
        if cache_key not in self._cache_strategies:
            self._cache_strategies[cache_key] = 0
        
        if hit:
            self._cache_strategies[cache_key] += 1
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """获取优化统计信息"""
        stats = {
            "performance_stats": {},
            "cache_stats": {
                "total_keys": len(self._cache_strategies),
                "avg_hits_per_key": 0
            },
            "batch_stats": {
                "active_queues": len(self._batch_queues),
                "total_batched_requests": sum(len(queue) for queue in self._batch_queues.values())
            },
            "load_balancing_stats": {
                "endpoint_health": self._endpoint_health.copy(),
                "endpoint_load": self._endpoint_load.copy()
            }
        }
        
        # 计算性能统计
        for service_key, latencies in self._performance_stats.items():
            if latencies:
                stats["performance_stats"][service_key] = {
                    "avg_latency": statistics.mean(latencies),
                    "min_latency": min(latencies),
                    "max_latency": max(latencies),
                    "p95_latency": statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies),
                    "total_requests": len(latencies)
                }
        
        # 计算缓存统计
        if self._cache_strategies:
            stats["cache_stats"]["avg_hits_per_key"] = statistics.mean(self._cache_strategies.values())
        
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "status": "healthy",
            "active_batch_queues": len(self._batch_queues),
            "cache_keys": len(self._cache_strategies),
            "performance_metrics_count": sum(len(latencies) for latencies in self._performance_stats.values()),
            "optimization_config": {
                "intelligent_caching": self.config.enable_intelligent_caching,
                "request_batching": self.config.enable_request_batching,
                "adaptive_retry": self.config.enable_adaptive_retry,
                "load_balancing": self.config.enable_load_balancing,
                "cost_optimization": self.config.enable_cost_optimization
            }
        }