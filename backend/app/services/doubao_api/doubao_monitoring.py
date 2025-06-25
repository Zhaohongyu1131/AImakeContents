"""
Doubao API Monitoring Service
豆包API监控服务 - [services][doubao_api][doubao_monitoring]
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
from collections import defaultdict, deque

import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry

from app.core.config import settings
from app.cache.cache_manager import CacheManager
from app.services.doubao_api.doubao_api_manager import DoubaoApiManager, DoubaoServiceType
from app.services.doubao_api.doubao_usage_statistics import DoubaoUsageStatisticsService
from app.services.doubao_api.doubao_load_balancer import DoubaoLoadBalancer

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """指标类型"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class AlertRule:
    """告警规则"""
    rule_id: str
    name: str
    description: str
    metric_name: str
    operator: str  # >, <, >=, <=, ==, !=
    threshold: float
    level: AlertLevel
    enabled: bool = True
    cooldown_minutes: int = 5
    callback: Optional[Callable] = None


@dataclass
class Alert:
    """告警实例"""
    alert_id: str
    rule_id: str
    level: AlertLevel
    message: str
    metric_value: float
    threshold: float
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class MonitoringConfig:
    """监控配置"""
    enable_prometheus: bool = True
    enable_alerts: bool = True
    enable_custom_metrics: bool = True
    metrics_retention_hours: int = 168  # 7天
    alert_retention_hours: int = 72  # 3天
    export_interval_seconds: int = 15
    health_check_interval: int = 30


class DoubaoMonitoringService:
    """豆包API监控服务 - [services][doubao_api][monitoring]"""
    
    def __init__(self, api_manager: DoubaoApiManager, 
                 usage_stats: DoubaoUsageStatisticsService,
                 load_balancer: DoubaoLoadBalancer):
        self.api_manager = api_manager
        self.usage_stats = usage_stats
        self.load_balancer = load_balancer
        self.cache_manager = CacheManager()
        
        self.config = MonitoringConfig()
        
        # Prometheus指标
        if self.config.enable_prometheus:
            self._setup_prometheus_metrics()
        
        # 告警系统
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: deque = deque(maxlen=10000)
        
        # 自定义指标
        self.custom_metrics: Dict[str, Any] = defaultdict(lambda: defaultdict(float))
        self.metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # 监控任务
        self._monitoring_tasks: List[asyncio.Task] = []
        
        # 初始化默认告警规则
        self._setup_default_alert_rules()
    
    def _setup_prometheus_metrics(self):
        """设置Prometheus指标"""
        self.registry = CollectorRegistry()
        
        # API调用计数器
        self.api_requests_total = Counter(
            'doubao_api_requests_total',
            'Total number of API requests',
            ['service_type', 'method', 'status'],
            registry=self.registry
        )
        
        # API响应时间直方图
        self.api_request_duration = Histogram(
            'doubao_api_request_duration_seconds',
            'API request duration in seconds',
            ['service_type', 'method'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 25.0, 50.0, 100.0],
            registry=self.registry
        )
        
        # API成本计量器
        self.api_cost_total = Counter(
            'doubao_api_cost_total',
            'Total API cost',
            ['service_type', 'method'],
            registry=self.registry
        )
        
        # Token使用计量器
        self.api_tokens_total = Counter(
            'doubao_api_tokens_total',
            'Total tokens used',
            ['service_type', 'method'],
            registry=self.registry
        )
        
        # 缓存命中率
        self.cache_hit_rate = Gauge(
            'doubao_cache_hit_rate',
            'Cache hit rate percentage',
            ['service_type'],
            registry=self.registry
        )
        
        # 活跃连接数
        self.active_connections = Gauge(
            'doubao_active_connections',
            'Number of active connections',
            ['endpoint_id'],
            registry=self.registry
        )
        
        # 端点健康状态
        self.endpoint_health = Gauge(
            'doubao_endpoint_health',
            'Endpoint health status (1=healthy, 0=unhealthy)',
            ['endpoint_id', 'status'],
            registry=self.registry
        )
        
        # 配额使用率
        self.quota_usage_ratio = Gauge(
            'doubao_quota_usage_ratio',
            'Quota usage ratio',
            ['service_type', 'quota_type', 'user_id'],
            registry=self.registry
        )
        
        # 错误率
        self.error_rate = Gauge(
            'doubao_error_rate',
            'Error rate percentage',
            ['service_type', 'method'],
            registry=self.registry
        )
    
    def _setup_default_alert_rules(self):
        """设置默认告警规则"""
        default_rules = [
            AlertRule(
                rule_id="high_error_rate",
                name="High Error Rate",
                description="Error rate exceeds 10%",
                metric_name="error_rate",
                operator=">",
                threshold=10.0,
                level=AlertLevel.WARNING,
                cooldown_minutes=5
            ),
            AlertRule(
                rule_id="critical_error_rate",
                name="Critical Error Rate",
                description="Error rate exceeds 25%",
                metric_name="error_rate",
                operator=">",
                threshold=25.0,
                level=AlertLevel.CRITICAL,
                cooldown_minutes=2
            ),
            AlertRule(
                rule_id="high_latency",
                name="High Latency",
                description="Average latency exceeds 5 seconds",
                metric_name="average_latency",
                operator=">",
                threshold=5.0,
                level=AlertLevel.WARNING,
                cooldown_minutes=5
            ),
            AlertRule(
                rule_id="quota_warning",
                name="Quota Usage Warning",
                description="Quota usage exceeds 80%",
                metric_name="quota_usage_ratio",
                operator=">",
                threshold=0.8,
                level=AlertLevel.WARNING,
                cooldown_minutes=15
            ),
            AlertRule(
                rule_id="quota_critical",
                name="Quota Usage Critical",
                description="Quota usage exceeds 95%",
                metric_name="quota_usage_ratio",
                operator=">",
                threshold=0.95,
                level=AlertLevel.CRITICAL,
                cooldown_minutes=5
            ),
            AlertRule(
                rule_id="endpoint_down",
                name="Endpoint Down",
                description="Endpoint is unhealthy",
                metric_name="endpoint_health",
                operator="==",
                threshold=0.0,
                level=AlertLevel.ERROR,
                cooldown_minutes=3
            ),
            AlertRule(
                rule_id="high_cost",
                name="High Cost Usage",
                description="Hourly cost exceeds threshold",
                metric_name="hourly_cost",
                operator=">",
                threshold=100.0,
                level=AlertLevel.WARNING,
                cooldown_minutes=30
            )
        ]
        
        for rule in default_rules:
            self.add_alert_rule(rule)
    
    def add_alert_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.alert_rules[rule.rule_id] = rule
        logger.info(f"Added alert rule: {rule.name} ({rule.rule_id})")
    
    def remove_alert_rule(self, rule_id: str):
        """移除告警规则"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            logger.info(f"Removed alert rule: {rule_id}")
    
    async def start_monitoring(self):
        """启动监控"""
        logger.info("Starting Doubao API monitoring...")
        
        # 启动监控任务
        self._monitoring_tasks = [
            asyncio.create_task(self._metrics_collection_loop()),
            asyncio.create_task(self._alert_evaluation_loop()),
            asyncio.create_task(self._health_check_loop()),
            asyncio.create_task(self._cleanup_loop())
        ]
        
        if self.config.enable_prometheus:
            self._monitoring_tasks.append(
                asyncio.create_task(self._prometheus_export_loop())
            )
        
        logger.info("Doubao API monitoring started")
    
    async def stop_monitoring(self):
        """停止监控"""
        logger.info("Stopping Doubao API monitoring...")
        
        # 取消所有监控任务
        for task in self._monitoring_tasks:
            task.cancel()
        
        # 等待任务完成
        if self._monitoring_tasks:
            await asyncio.gather(*self._monitoring_tasks, return_exceptions=True)
        
        self._monitoring_tasks.clear()
        logger.info("Doubao API monitoring stopped")
    
    async def _metrics_collection_loop(self):
        """指标收集循环"""
        while True:
            try:
                await self._collect_metrics()
                await asyncio.sleep(self.config.export_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(5)
    
    async def _collect_metrics(self):
        """收集指标"""
        try:
            # 收集API管理器指标
            api_metrics = self.api_manager.get_metrics()
            await self._process_api_metrics(api_metrics)
            
            # 收集负载均衡器指标
            lb_metrics = self.load_balancer.get_metrics()
            await self._process_load_balancer_metrics(lb_metrics)
            
            # 收集使用统计指标
            realtime_metrics = await self.usage_stats.get_realtime_metrics()
            await self._process_usage_metrics(realtime_metrics)
            
            # 收集配额指标
            quota_status = await self.usage_stats.get_quota_status()
            await self._process_quota_metrics(quota_status)
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
    
    async def _process_api_metrics(self, metrics: Dict[str, Any]):
        """处理API指标"""
        for service_type, service_metrics in metrics.items():
            if isinstance(service_metrics, dict):
                # 更新Prometheus指标
                if self.config.enable_prometheus:
                    self.cache_hit_rate.labels(service_type=service_type).set(
                        service_metrics.get('cached_requests', 0) / 
                        max(service_metrics.get('total_requests', 1), 1) * 100
                    )
                    
                    error_rate = (service_metrics.get('failed_requests', 0) / 
                                max(service_metrics.get('total_requests', 1), 1) * 100)
                    self.error_rate.labels(service_type=service_type, method='all').set(error_rate)
                
                # 更新自定义指标
                self.custom_metrics[service_type]['total_requests'] = service_metrics.get('total_requests', 0)
                self.custom_metrics[service_type]['success_rate'] = (
                    service_metrics.get('successful_requests', 0) / 
                    max(service_metrics.get('total_requests', 1), 1) * 100
                )
                self.custom_metrics[service_type]['error_rate'] = error_rate
                self.custom_metrics[service_type]['average_latency'] = service_metrics.get('average_latency', 0.0)
                self.custom_metrics[service_type]['total_cost'] = service_metrics.get('total_cost', 0.0)
                
                # 记录历史数据
                timestamp = time.time()
                self.metric_history[f"{service_type}_error_rate"].append((timestamp, error_rate))
                self.metric_history[f"{service_type}_latency"].append(
                    (timestamp, service_metrics.get('average_latency', 0.0))
                )
    
    async def _process_load_balancer_metrics(self, metrics: Dict[str, Any]):
        """处理负载均衡器指标"""
        endpoints = metrics.get('endpoints', {})
        
        for endpoint_id, endpoint_metrics in endpoints.items():
            if self.config.enable_prometheus:
                # 活跃连接数
                self.active_connections.labels(endpoint_id=endpoint_id).set(
                    endpoint_metrics.get('active_connections', 0)
                )
                
                # 端点健康状态
                health_value = 1.0 if endpoint_metrics.get('status') == 'healthy' else 0.0
                self.endpoint_health.labels(
                    endpoint_id=endpoint_id,
                    status=endpoint_metrics.get('status', 'unknown')
                ).set(health_value)
            
            # 更新自定义指标
            self.custom_metrics[f"endpoint_{endpoint_id}"]["health"] = health_value
            self.custom_metrics[f"endpoint_{endpoint_id}"]["error_rate"] = endpoint_metrics.get('error_rate', 0.0)
            self.custom_metrics[f"endpoint_{endpoint_id}"]["response_time"] = endpoint_metrics.get('average_response_time', 0.0)
    
    async def _process_usage_metrics(self, metrics: Dict[str, Any]):
        """处理使用统计指标"""
        for service_type, service_metrics in metrics.items():
            if self.config.enable_prometheus:
                # 记录API调用次数（增量）
                current_requests = service_metrics.get('total_requests', 0)
                previous_requests = self.custom_metrics[service_type].get('previous_total_requests', 0)
                new_requests = current_requests - previous_requests
                
                if new_requests > 0:
                    self.api_requests_total.labels(
                        service_type=service_type,
                        method='all',
                        status='success'
                    ).inc(service_metrics.get('successful_requests', 0) - 
                         self.custom_metrics[service_type].get('previous_successful_requests', 0))
                    
                    self.api_requests_total.labels(
                        service_type=service_type,
                        method='all',
                        status='error'
                    ).inc(service_metrics.get('failed_requests', 0) - 
                         self.custom_metrics[service_type].get('previous_failed_requests', 0))
                
                # 记录成本（增量）
                current_cost = service_metrics.get('total_cost', 0.0)
                previous_cost = self.custom_metrics[service_type].get('previous_total_cost', 0.0)
                new_cost = current_cost - previous_cost
                
                if new_cost > 0:
                    self.api_cost_total.labels(
                        service_type=service_type,
                        method='all'
                    ).inc(new_cost)
                
                # 记录Token使用（增量）
                current_tokens = service_metrics.get('total_tokens', 0)
                previous_tokens = self.custom_metrics[service_type].get('previous_total_tokens', 0)
                new_tokens = current_tokens - previous_tokens
                
                if new_tokens > 0:
                    self.api_tokens_total.labels(
                        service_type=service_type,
                        method='all'
                    ).inc(new_tokens)
                
                # 更新前值记录
                self.custom_metrics[service_type]['previous_total_requests'] = current_requests
                self.custom_metrics[service_type]['previous_successful_requests'] = service_metrics.get('successful_requests', 0)
                self.custom_metrics[service_type]['previous_failed_requests'] = service_metrics.get('failed_requests', 0)
                self.custom_metrics[service_type]['previous_total_cost'] = current_cost
                self.custom_metrics[service_type]['previous_total_tokens'] = current_tokens
    
    async def _process_quota_metrics(self, quota_status: List[Any]):
        """处理配额指标"""
        for quota in quota_status:
            if self.config.enable_prometheus:
                self.quota_usage_ratio.labels(
                    service_type=quota.service_type,
                    quota_type=quota.quota_type,
                    user_id=str(quota.user_id) if hasattr(quota, 'user_id') else 'global'
                ).set(quota.usage_percentage / 100.0)
            
            # 记录配额使用率历史
            timestamp = time.time()
            metric_key = f"quota_{quota.service_type}_{quota.quota_type}"
            self.metric_history[metric_key].append((timestamp, quota.usage_percentage / 100.0))
    
    async def _alert_evaluation_loop(self):
        """告警评估循环"""
        while True:
            try:
                if self.config.enable_alerts:
                    await self._evaluate_alerts()
                await asyncio.sleep(30)  # 每30秒评估一次
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Alert evaluation error: {e}")
                await asyncio.sleep(5)
    
    async def _evaluate_alerts(self):
        """评估告警规则"""
        for rule_id, rule in self.alert_rules.items():
            if not rule.enabled:
                continue
            
            try:
                # 获取指标值
                metric_value = await self._get_metric_value(rule.metric_name)
                
                if metric_value is None:
                    continue
                
                # 评估阈值
                alert_triggered = self._evaluate_threshold(
                    metric_value, rule.operator, rule.threshold
                )
                
                # 处理告警
                if alert_triggered:
                    await self._trigger_alert(rule, metric_value)
                else:
                    await self._resolve_alert(rule_id)
                    
            except Exception as e:
                logger.error(f"Error evaluating alert rule {rule_id}: {e}")
    
    async def _get_metric_value(self, metric_name: str) -> Optional[float]:
        """获取指标值"""
        # 从自定义指标中获取
        for service_type, metrics in self.custom_metrics.items():
            if metric_name in metrics:
                return metrics[metric_name]
        
        # 从历史数据中获取最新值
        if metric_name in self.metric_history:
            history = self.metric_history[metric_name]
            if history:
                return history[-1][1]  # 返回最新值
        
        # 特殊指标处理
        if metric_name == "hourly_cost":
            # 计算过去一小时的成本
            now = time.time()
            hour_ago = now - 3600
            total_cost = 0.0
            
            for service_type, metrics in self.custom_metrics.items():
                if 'total_cost' in metrics:
                    total_cost += metrics['total_cost']
            
            return total_cost
        
        return None
    
    def _evaluate_threshold(self, value: float, operator: str, threshold: float) -> bool:
        """评估阈值条件"""
        if operator == ">":
            return value > threshold
        elif operator == "<":
            return value < threshold
        elif operator == ">=":
            return value >= threshold
        elif operator == "<=":
            return value <= threshold
        elif operator == "==":
            return abs(value - threshold) < 0.0001  # 浮点数比较
        elif operator == "!=":
            return abs(value - threshold) >= 0.0001
        else:
            return False
    
    async def _trigger_alert(self, rule: AlertRule, metric_value: float):
        """触发告警"""
        # 检查冷却期
        existing_alert = self.active_alerts.get(rule.rule_id)
        if existing_alert:
            time_since_alert = datetime.now() - existing_alert.timestamp
            if time_since_alert.total_seconds() < rule.cooldown_minutes * 60:
                return  # 仍在冷却期内
        
        # 创建新告警
        alert = Alert(
            alert_id=f"{rule.rule_id}_{int(time.time())}",
            rule_id=rule.rule_id,
            level=rule.level,
            message=f"{rule.description}. Current value: {metric_value:.2f}, Threshold: {rule.threshold}",
            metric_value=metric_value,
            threshold=rule.threshold,
            timestamp=datetime.now()
        )
        
        self.active_alerts[rule.rule_id] = alert
        self.alert_history.append(alert)
        
        logger.warning(f"ALERT [{rule.level.value.upper()}] {rule.name}: {alert.message}")
        
        # 调用回调函数
        if rule.callback:
            try:
                await rule.callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
    
    async def _resolve_alert(self, rule_id: str):
        """解决告警"""
        if rule_id in self.active_alerts:
            alert = self.active_alerts[rule_id]
            alert.resolved = True
            alert.resolved_at = datetime.now()
            
            del self.active_alerts[rule_id]
            
            logger.info(f"RESOLVED: Alert {alert.alert_id} has been resolved")
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.config.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(10)
    
    async def _perform_health_checks(self):
        """执行健康检查"""
        # 检查各组件健康状态
        components = [
            ("api_manager", self.api_manager.health_check()),
            ("usage_stats", self.usage_stats.health_check()),
            ("load_balancer", self.load_balancer.health_check()),
            ("cache_manager", self.cache_manager.health_check())
        ]
        
        for component_name, health_check_coro in components:
            try:
                health_status = await health_check_coro
                self.custom_metrics[f"component_{component_name}"]["health"] = (
                    1.0 if health_status.get("status") == "healthy" else 0.0
                )
            except Exception as e:
                logger.error(f"Health check failed for {component_name}: {e}")
                self.custom_metrics[f"component_{component_name}"]["health"] = 0.0
    
    async def _cleanup_loop(self):
        """清理循环"""
        while True:
            try:
                await self._cleanup_old_data()
                await asyncio.sleep(3600)  # 每小时清理一次
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
                await asyncio.sleep(300)
    
    async def _cleanup_old_data(self):
        """清理旧数据"""
        now = time.time()
        
        # 清理指标历史数据
        retention_seconds = self.config.metrics_retention_hours * 3600
        
        for metric_name, history in self.metric_history.items():
            # 移除过期数据
            while history and now - history[0][0] > retention_seconds:
                history.popleft()
        
        # 清理告警历史
        alert_retention_seconds = self.config.alert_retention_hours * 3600
        cutoff_time = datetime.now() - timedelta(seconds=alert_retention_seconds)
        
        # 保留最近的告警
        recent_alerts = deque()
        for alert in self.alert_history:
            if alert.timestamp > cutoff_time:
                recent_alerts.append(alert)
        
        self.alert_history = recent_alerts
    
    async def _prometheus_export_loop(self):
        """Prometheus导出循环"""
        while True:
            try:
                # 这里可以实现将指标推送到Pushgateway的逻辑
                # 或者提供HTTP端点供Prometheus拉取
                await asyncio.sleep(self.config.export_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Prometheus export error: {e}")
                await asyncio.sleep(5)
    
    def get_prometheus_registry(self) -> Optional[CollectorRegistry]:
        """获取Prometheus注册表"""
        return self.registry if self.config.enable_prometheus else None
    
    def get_active_alerts(self) -> List[Alert]:
        """获取活跃告警"""
        return list(self.active_alerts.values())
    
    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """获取告警历史"""
        return list(self.alert_history)[-limit:]
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "active_alerts_count": len(self.active_alerts),
            "alert_rules_count": len(self.alert_rules),
            "custom_metrics": dict(self.custom_metrics),
            "monitoring_config": {
                "prometheus_enabled": self.config.enable_prometheus,
                "alerts_enabled": self.config.enable_alerts,
                "retention_hours": self.config.metrics_retention_hours
            }
        }
        
        # 添加系统状态
        total_requests = sum(
            metrics.get('total_requests', 0) 
            for metrics in self.custom_metrics.values()
            if isinstance(metrics, dict)
        )
        
        total_errors = sum(
            metrics.get('total_requests', 0) * metrics.get('error_rate', 0) / 100.0
            for metrics in self.custom_metrics.values()
            if isinstance(metrics, dict)
        )
        
        summary["system_overview"] = {
            "total_requests": total_requests,
            "total_errors": total_errors,
            "overall_error_rate": (total_errors / max(total_requests, 1)) * 100,
            "total_cost": sum(
                metrics.get('total_cost', 0.0)
                for metrics in self.custom_metrics.values()
                if isinstance(metrics, dict)
            )
        }
        
        return summary
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "status": "healthy",
            "monitoring_tasks": len([t for t in self._monitoring_tasks if not t.done()]),
            "active_alerts": len(self.active_alerts),
            "alert_rules": len(self.alert_rules),
            "prometheus_enabled": self.config.enable_prometheus,
            "alerts_enabled": self.config.enable_alerts
        }