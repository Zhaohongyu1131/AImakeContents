"""
Doubao Unified Service
豆包统一服务 - [services][doubao_api][doubao_unified_service]
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from contextlib import asynccontextmanager

from .doubao_api_manager import DoubaoApiManager, DoubaoServiceType, DoubaoApiPriority
from .doubao_api_optimizer import DoubaoApiOptimizer, RequestContext, OptimizationResult
from .doubao_usage_statistics import DoubaoUsageStatisticsService
from .doubao_load_balancer import DoubaoLoadBalancer
from .doubao_monitoring import DoubaoMonitoringService

logger = logging.getLogger(__name__)


class DoubaoUnifiedService:
    """豆包统一服务 - [services][doubao_api][unified_service]
    
    这是豆包API的统一入口点，整合了所有子服务：
    - API管理器
    - 优化器
    - 使用统计
    - 负载均衡
    - 监控系统
    """
    
    def __init__(self):
        # 初始化核心组件
        self.api_manager = DoubaoApiManager()
        self.usage_statistics = DoubaoUsageStatisticsService()
        self.load_balancer = DoubaoLoadBalancer()
        
        # 初始化高级组件
        self.optimizer = DoubaoApiOptimizer(self.api_manager)
        self.monitoring = DoubaoMonitoringService(
            self.api_manager, 
            self.usage_statistics, 
            self.load_balancer
        )
        
        # 服务状态
        self._started = False
        self._startup_time: Optional[datetime] = None
    
    async def start(self):
        """启动所有服务"""
        if self._started:
            logger.warning("Doubao unified service is already started")
            return
        
        logger.info("Starting Doubao unified service...")
        
        try:
            # 按依赖顺序启动服务
            await self.api_manager.start()
            await self.load_balancer.start_health_checks()
            await self.monitoring.start_monitoring()
            
            self._started = True
            self._startup_time = datetime.now()
            
            logger.info("Doubao unified service started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Doubao unified service: {e}")
            await self.stop()  # 清理已启动的服务
            raise
    
    async def stop(self):
        """停止所有服务"""
        if not self._started:
            return
        
        logger.info("Stopping Doubao unified service...")
        
        try:
            # 按相反顺序停止服务
            await self.monitoring.stop_monitoring()
            await self.load_balancer.stop_health_checks()
            await self.api_manager.stop()
            
            self._started = False
            
            logger.info("Doubao unified service stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping Doubao unified service: {e}")
    
    @asynccontextmanager
    async def service_context(self):
        """服务上下文管理器"""
        await self.start()
        try:
            yield self
        finally:
            await self.stop()
    
    async def call_api(self, service_type: DoubaoServiceType, method: str,
                       priority: DoubaoApiPriority = DoubaoApiPriority.NORMAL,
                       user_id: Optional[int] = None,
                       session_id: Optional[str] = None,
                       enable_optimization: bool = True,
                       **kwargs) -> Tuple[Any, Dict[str, Any]]:
        """统一API调用接口
        
        Args:
            service_type: 服务类型
            method: 调用方法
            priority: 优先级
            user_id: 用户ID
            session_id: 会话ID
            enable_optimization: 是否启用优化
            **kwargs: 其他参数
            
        Returns:
            Tuple[响应数据, 调用信息]
        """
        if not self._started:
            raise RuntimeError("Doubao unified service is not started")
        
        start_time = datetime.now()
        
        try:
            # 选择最佳端点
            endpoint = await self.load_balancer.select_endpoint(
                service_type.value, user_id, session_id
            )
            
            if endpoint:
                kwargs['endpoint'] = endpoint.url
                kwargs['app_id'] = endpoint.app_id
                kwargs['access_token'] = endpoint.access_token
                kwargs['secret_key'] = endpoint.secret_key
            
            # 创建请求上下文
            context = RequestContext(
                service_type=service_type,
                method=method,
                params=kwargs,
                user_id=user_id,
                priority=priority.value,
                timeout=kwargs.get('timeout', 30.0)
            )
            
            # 记录请求开始
            if endpoint:
                await self.load_balancer.record_request_start(endpoint.endpoint_id)
            
            # 执行API调用
            if enable_optimization:
                response, optimization_result = await self.optimizer.optimize_request(context)
            else:
                response = await self.api_manager.call_api(
                    service_type=service_type,
                    method=method,
                    priority=priority,
                    user_id=user_id,
                    **kwargs
                )
                optimization_result = None
            
            # 计算执行时间
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # 记录请求结束
            if endpoint:
                await self.load_balancer.record_request_end(
                    endpoint.endpoint_id, True, execution_time
                )
            
            # 记录使用统计
            await self._record_api_usage(
                service_type, method, user_id, True, 
                execution_time, kwargs.get('cost', 0.0)
            )
            
            # 构建调用信息
            call_info = {
                "success": True,
                "execution_time": execution_time,
                "endpoint_used": endpoint.endpoint_id if endpoint else None,
                "optimization_applied": enable_optimization,
                "optimization_result": optimization_result.__dict__ if optimization_result else None,
                "timestamp": end_time.isoformat()
            }
            
            return response, call_info
            
        except Exception as e:
            # 计算执行时间
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # 记录失败
            if endpoint:
                await self.load_balancer.record_request_end(
                    endpoint.endpoint_id, False, execution_time
                )
            
            # 记录使用统计
            await self._record_api_usage(
                service_type, method, user_id, False, 
                execution_time, 0.0
            )
            
            logger.error(f"Doubao API call failed: {e}")
            
            # 构建错误信息
            call_info = {
                "success": False,
                "error": str(e),
                "execution_time": execution_time,
                "endpoint_used": endpoint.endpoint_id if endpoint else None,
                "optimization_applied": enable_optimization,
                "timestamp": end_time.isoformat()
            }
            
            raise Exception(f"API call failed: {e}") from e
    
    async def _record_api_usage(self, service_type: DoubaoServiceType, method: str,
                               user_id: Optional[int], success: bool,
                               latency: float, cost: float):
        """记录API使用情况"""
        try:
            from app.models.doubao_usage import DoubaoUsageRecord
            
            usage_record = DoubaoUsageRecord(
                user_id=user_id,
                service_type=service_type.value,
                method=method,
                success=success,
                latency=latency,
                cost=cost,
                created_at=datetime.now()
            )
            
            await self.usage_statistics.record_usage(usage_record)
            
        except Exception as e:
            logger.error(f"Failed to record API usage: {e}")
    
    # TTS相关方法
    async def text_to_speech(self, text: str, speaker_id: Optional[str] = None,
                            encoding: str = "mp3", rate: float = 1.0,
                            volume: float = 1.0, pitch: float = 1.0,
                            user_id: Optional[int] = None,
                            enable_optimization: bool = True) -> Tuple[Any, Dict[str, Any]]:
        """文本转语音"""
        return await self.call_api(
            service_type=DoubaoServiceType.TTS,
            method="synthesize",
            user_id=user_id,
            enable_optimization=enable_optimization,
            text=text,
            speaker_id=speaker_id,
            encoding=encoding,
            rate=rate,
            volume=volume,
            pitch=pitch
        )
    
    async def get_speaker_list(self, user_id: Optional[int] = None,
                              enable_optimization: bool = True) -> Tuple[Any, Dict[str, Any]]:
        """获取说话人列表"""
        return await self.call_api(
            service_type=DoubaoServiceType.TTS,
            method="get_speakers",
            user_id=user_id,
            enable_optimization=enable_optimization
        )
    
    # 语音克隆相关方法
    async def clone_voice(self, audio_data: bytes, speaker_name: str,
                         speaker_gender: str = "male",
                         user_id: Optional[int] = None,
                         enable_optimization: bool = True) -> Tuple[Any, Dict[str, Any]]:
        """克隆语音"""
        return await self.call_api(
            service_type=DoubaoServiceType.VOICE_CLONE,
            method="upload_audio",
            priority=DoubaoApiPriority.HIGH,  # 语音克隆优先级较高
            user_id=user_id,
            enable_optimization=enable_optimization,
            audio_data=audio_data,
            speaker_name=speaker_name,
            speaker_gender=speaker_gender
        )
    
    async def get_clone_status(self, clone_id: str,
                              user_id: Optional[int] = None,
                              enable_optimization: bool = True) -> Tuple[Any, Dict[str, Any]]:
        """获取克隆状态"""
        return await self.call_api(
            service_type=DoubaoServiceType.VOICE_CLONE,
            method="get_clone_status",
            user_id=user_id,
            enable_optimization=enable_optimization,
            clone_id=clone_id
        )
    
    async def get_cloned_speakers(self, user_id: Optional[int] = None,
                                 enable_optimization: bool = True) -> Tuple[Any, Dict[str, Any]]:
        """获取已克隆的说话人"""
        return await self.call_api(
            service_type=DoubaoServiceType.VOICE_CLONE,
            method="get_cloned_speakers",
            user_id=user_id,
            enable_optimization=enable_optimization
        )
    
    # 文本分析相关方法
    async def analyze_text(self, text: str, analysis_type: str = "sentiment",
                          user_id: Optional[int] = None,
                          enable_optimization: bool = True) -> Tuple[Any, Dict[str, Any]]:
        """分析文本"""
        return await self.call_api(
            service_type=DoubaoServiceType.TEXT_ANALYSIS,
            method="analyze",
            user_id=user_id,
            enable_optimization=enable_optimization,
            text=text,
            analysis_type=analysis_type
        )
    
    async def preprocess_text(self, text: str,
                             user_id: Optional[int] = None,
                             enable_optimization: bool = True) -> Tuple[Any, Dict[str, Any]]:
        """预处理文本"""
        return await self.call_api(
            service_type=DoubaoServiceType.TEXT_ANALYSIS,
            method="preprocess",
            user_id=user_id,
            enable_optimization=enable_optimization,
            text=text
        )
    
    # 批处理方法
    async def batch_text_to_speech(self, texts: List[str], speaker_id: Optional[str] = None,
                                  user_id: Optional[int] = None,
                                  enable_optimization: bool = True) -> Tuple[Any, Dict[str, Any]]:
        """批量文本转语音"""
        return await self.call_api(
            service_type=DoubaoServiceType.BATCH_PROCESSING,
            method="batch_tts",
            priority=DoubaoApiPriority.LOW,  # 批处理优先级较低
            user_id=user_id,
            enable_optimization=enable_optimization,
            texts=texts,
            speaker_id=speaker_id
        )
    
    # 统计和监控方法
    async def get_usage_statistics(self, service_type: Optional[str] = None,
                                  user_id: Optional[int] = None,
                                  period: str = "day") -> Dict[str, Any]:
        """获取使用统计"""
        from .doubao_usage_statistics import StatisticsPeriod
        
        period_enum = StatisticsPeriod(period)
        stats = await self.usage_statistics.get_usage_statistics(
            service_type=service_type,
            user_id=user_id,
            period=period_enum
        )
        
        return stats.__dict__
    
    async def get_quota_status(self, user_id: Optional[int] = None,
                              service_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取配额状态"""
        quota_statuses = await self.usage_statistics.get_quota_status(
            user_id=user_id,
            service_type=service_type
        )
        
        return [status.__dict__ for status in quota_statuses]
    
    def get_load_balancer_metrics(self) -> Dict[str, Any]:
        """获取负载均衡器指标"""
        return self.load_balancer.get_metrics()
    
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """获取监控摘要"""
        return self.monitoring.get_metrics_summary()
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """获取活跃告警"""
        alerts = self.monitoring.get_active_alerts()
        return [alert.__dict__ for alert in alerts]
    
    async def health_check(self) -> Dict[str, Any]:
        """系统健康检查"""
        if not self._started:
            return {
                "status": "stopped",
                "message": "Service is not started"
            }
        
        try:
            # 检查各组件健康状态
            api_manager_health = await self.api_manager.health_check() if hasattr(self.api_manager, 'health_check') else {"status": "unknown"}
            usage_stats_health = await self.usage_statistics.health_check()
            load_balancer_health = await self.load_balancer.health_check()
            monitoring_health = await self.monitoring.health_check()
            
            # 统计健康组件数量
            components = [api_manager_health, usage_stats_health, load_balancer_health, monitoring_health]
            healthy_count = sum(1 for comp in components if comp.get("status") == "healthy")
            
            overall_status = "healthy" if healthy_count == len(components) else "degraded" if healthy_count > 0 else "unhealthy"
            
            return {
                "status": overall_status,
                "started": self._started,
                "startup_time": self._startup_time.isoformat() if self._startup_time else None,
                "uptime_seconds": (datetime.now() - self._startup_time).total_seconds() if self._startup_time else 0,
                "components": {
                    "api_manager": api_manager_health,
                    "usage_statistics": usage_stats_health,
                    "load_balancer": load_balancer_health,
                    "monitoring": monitoring_health
                },
                "healthy_components": healthy_count,
                "total_components": len(components)
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# 全局单例
doubao_unified_service = DoubaoUnifiedService()