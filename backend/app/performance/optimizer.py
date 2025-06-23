"""
Performance Optimizer
性能优化器 - [performance][optimizer]
"""

import asyncio
import gc
import logging
import time
import threading
from typing import Dict, Any, Optional, List, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum


class OptimizationLevel(Enum):
    """
    优化级别
    [performance][optimizer][optimization_level]
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    AGGRESSIVE = "aggressive"


@dataclass
class OptimizationRule:
    """
    优化规则
    [performance][optimizer][optimization_rule]
    """
    name: str
    condition: Callable[[], bool]
    action: Callable[[], None]
    priority: int = 1
    cooldown: int = 60  # 冷却时间（秒）
    last_executed: float = 0.0
    enabled: bool = True
    
    def can_execute(self) -> bool:
        """检查是否可以执行"""
        if not self.enabled:
            return False
        
        current_time = time.time()
        return current_time - self.last_executed >= self.cooldown
    
    def execute(self):
        """执行优化动作"""
        if self.can_execute() and self.condition():
            self.action()
            self.last_executed = time.time()


@dataclass
class OptimizationResult:
    """
    优化结果
    [performance][optimizer][optimization_result]
    """
    rule_name: str
    timestamp: float
    before_metrics: Dict[str, Any]
    after_metrics: Dict[str, Any]
    success: bool
    error: Optional[str] = None
    duration: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "rule_name": self.rule_name,
            "timestamp": self.timestamp,
            "before_metrics": self.before_metrics,
            "after_metrics": self.after_metrics,
            "success": self.success,
            "error": self.error,
            "duration": self.duration
        }


class PerformanceOptimizer:
    """
    性能优化器
    [performance][optimizer]
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化性能优化器
        [performance][optimizer][init]
        """
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        
        # 配置参数
        self.optimization_level = OptimizationLevel(config.get("optimization_level", "medium"))
        self.auto_optimize = config.get("auto_optimize", True)
        self.optimization_interval = config.get("optimization_interval", 300)  # 5分钟
        self.max_optimization_history = config.get("max_optimization_history", 1000)
        
        # 优化规则
        self.rules: List[OptimizationRule] = []
        self.optimization_history: List[OptimizationResult] = []
        
        # 监控指标
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.thresholds: Dict[str, float] = {
            "memory_usage_mb": config.get("memory_threshold_mb", 1000),
            "cpu_usage_percent": config.get("cpu_threshold_percent", 80),
            "response_time_ms": config.get("response_time_threshold_ms", 1000),
            "error_rate_percent": config.get("error_rate_threshold_percent", 5),
            "gc_frequency": config.get("gc_frequency_threshold", 10)
        }
        
        # 优化任务
        self._optimization_task: Optional[asyncio.Task] = None
        self._shutdown = False
        self._lock = threading.RLock()
        
        # 初始化内置优化规则
        self._initialize_builtin_rules()
    
    async def performance_optimizer_initialize(self) -> bool:
        """
        初始化性能优化器
        [performance][optimizer][initialize]
        """
        try:
            if self.auto_optimize:
                self._optimization_task = asyncio.create_task(self._optimization_loop())
            
            self.logger.info(f"Performance optimizer initialized with level: {self.optimization_level.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize performance optimizer: {str(e)}")
            return False
    
    async def performance_optimizer_cleanup(self):
        """
        清理性能优化器
        [performance][optimizer][cleanup]
        """
        self._shutdown = True
        
        if self._optimization_task:
            self._optimization_task.cancel()
            try:
                await self._optimization_task
            except asyncio.CancelledError:
                pass
        
        with self._lock:
            self.rules.clear()
            self.optimization_history.clear()
            self.metrics.clear()
        
        self.logger.info("Performance optimizer cleaned up")
    
    def performance_optimizer_add_rule(
        self, 
        name: str,
        condition: Callable[[], bool],
        action: Callable[[], None],
        priority: int = 1,
        cooldown: int = 60
    ):
        """
        添加优化规则
        [performance][optimizer][add_rule]
        """
        try:
            rule = OptimizationRule(
                name=name,
                condition=condition,
                action=action,
                priority=priority,
                cooldown=cooldown
            )
            
            with self._lock:
                self.rules.append(rule)
                self.rules.sort(key=lambda x: x.priority, reverse=True)
            
            self.logger.info(f"Added optimization rule: {name}")
            
        except Exception as e:
            self.logger.error(f"Failed to add optimization rule '{name}': {str(e)}")
    
    def performance_optimizer_remove_rule(self, name: str):
        """
        移除优化规则
        [performance][optimizer][remove_rule]
        """
        try:
            with self._lock:
                self.rules = [rule for rule in self.rules if rule.name != name]
            
            self.logger.info(f"Removed optimization rule: {name}")
            
        except Exception as e:
            self.logger.error(f"Failed to remove optimization rule '{name}': {str(e)}")
    
    def performance_optimizer_update_metric(self, metric_name: str, value: float):
        """
        更新性能指标
        [performance][optimizer][update_metric]
        """
        try:
            with self._lock:
                self.metrics[metric_name].append({
                    "value": value,
                    "timestamp": time.time()
                })
                
        except Exception as e:
            self.logger.error(f"Failed to update metric '{metric_name}': {str(e)}")
    
    async def performance_optimizer_run_optimization(self) -> List[OptimizationResult]:
        """
        手动运行优化
        [performance][optimizer][run_optimization]
        """
        try:
            results = []
            
            with self._lock:
                rules_to_execute = [rule for rule in self.rules if rule.can_execute()]
            
            for rule in rules_to_execute:
                try:
                    start_time = time.time()
                    before_metrics = self._get_current_metrics()
                    
                    # 执行优化规则
                    if rule.condition():
                        rule.action()
                        rule.last_executed = start_time
                        
                        # 等待一小段时间以观察效果
                        await asyncio.sleep(1)
                        
                        after_metrics = self._get_current_metrics()
                        duration = time.time() - start_time
                        
                        result = OptimizationResult(
                            rule_name=rule.name,
                            timestamp=start_time,
                            before_metrics=before_metrics,
                            after_metrics=after_metrics,
                            success=True,
                            duration=duration
                        )
                        
                        results.append(result)
                        self._add_optimization_result(result)
                        
                        self.logger.info(f"Executed optimization rule: {rule.name}")
                
                except Exception as e:
                    error_msg = str(e)
                    result = OptimizationResult(
                        rule_name=rule.name,
                        timestamp=time.time(),
                        before_metrics={},
                        after_metrics={},
                        success=False,
                        error=error_msg
                    )
                    
                    results.append(result)
                    self._add_optimization_result(result)
                    
                    self.logger.error(f"Failed to execute optimization rule '{rule.name}': {error_msg}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to run optimization: {str(e)}")
            return []
    
    async def performance_optimizer_get_recommendations(self) -> List[Dict[str, Any]]:
        """
        获取性能优化建议
        [performance][optimizer][get_recommendations]
        """
        try:
            recommendations = []
            current_metrics = self._get_current_metrics()
            
            # 内存使用建议
            memory_usage = current_metrics.get("memory_usage_mb", 0)
            if memory_usage > self.thresholds["memory_usage_mb"]:
                recommendations.append({
                    "type": "memory",
                    "severity": "high" if memory_usage > self.thresholds["memory_usage_mb"] * 1.5 else "medium",
                    "message": f"内存使用过高: {memory_usage:.1f}MB",
                    "suggestion": "考虑运行垃圾回收、清理缓存或优化数据结构",
                    "current_value": memory_usage,
                    "threshold": self.thresholds["memory_usage_mb"]
                })
            
            # CPU使用建议
            cpu_usage = current_metrics.get("cpu_usage_percent", 0)
            if cpu_usage > self.thresholds["cpu_usage_percent"]:
                recommendations.append({
                    "type": "cpu",
                    "severity": "high" if cpu_usage > self.thresholds["cpu_usage_percent"] * 1.2 else "medium",
                    "message": f"CPU使用率过高: {cpu_usage:.1f}%",
                    "suggestion": "检查是否有死循环、优化算法或增加异步处理",
                    "current_value": cpu_usage,
                    "threshold": self.thresholds["cpu_usage_percent"]
                })
            
            # 响应时间建议
            response_time = current_metrics.get("response_time_ms", 0)
            if response_time > self.thresholds["response_time_ms"]:
                recommendations.append({
                    "type": "response_time",
                    "severity": "medium",
                    "message": f"响应时间过慢: {response_time:.1f}ms",
                    "suggestion": "考虑添加缓存、优化数据库查询或使用CDN",
                    "current_value": response_time,
                    "threshold": self.thresholds["response_time_ms"]
                })
            
            # GC频率建议
            gc_frequency = current_metrics.get("gc_frequency", 0)
            if gc_frequency > self.thresholds["gc_frequency"]:
                recommendations.append({
                    "type": "gc",
                    "severity": "low",
                    "message": f"垃圾回收频率过高: {gc_frequency}/min",
                    "suggestion": "优化对象创建和内存使用模式",
                    "current_value": gc_frequency,
                    "threshold": self.thresholds["gc_frequency"]
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to get recommendations: {str(e)}")
            return []
    
    async def performance_optimizer_get_history(
        self, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        获取优化历史
        [performance][optimizer][get_history]
        """
        try:
            with self._lock:
                history = self.optimization_history.copy()
            
            # 按时间排序并限制数量
            history.sort(key=lambda x: x.timestamp, reverse=True)
            history = history[:limit]
            
            return [result.to_dict() for result in history]
            
        except Exception as e:
            self.logger.error(f"Failed to get optimization history: {str(e)}")
            return []
    
    async def performance_optimizer_get_metrics_summary(self) -> Dict[str, Any]:
        """
        获取性能指标摘要
        [performance][optimizer][get_metrics_summary]
        """
        try:
            current_metrics = self._get_current_metrics()
            
            summary = {
                "current_metrics": current_metrics,
                "thresholds": self.thresholds,
                "alerts": [],
                "optimization_level": self.optimization_level.value,
                "total_rules": len(self.rules),
                "enabled_rules": len([r for r in self.rules if r.enabled]),
                "total_optimizations": len(self.optimization_history)
            }
            
            # 检查告警
            for metric_name, threshold in self.thresholds.items():
                current_value = current_metrics.get(metric_name, 0)
                if current_value > threshold:
                    summary["alerts"].append({
                        "metric": metric_name,
                        "current": current_value,
                        "threshold": threshold,
                        "severity": "high" if current_value > threshold * 1.5 else "medium"
                    })
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get metrics summary: {str(e)}")
            return {}
    
    def _initialize_builtin_rules(self):
        """
        初始化内置优化规则
        [performance][optimizer][_initialize_builtin_rules]
        """
        try:
            # 垃圾回收优化规则
            self.performance_optimizer_add_rule(
                name="gc_optimization",
                condition=lambda: self._check_memory_pressure(),
                action=lambda: self._perform_gc_optimization(),
                priority=5,
                cooldown=60
            )
            
            # 缓存清理规则
            self.performance_optimizer_add_rule(
                name="cache_cleanup",
                condition=lambda: self._check_cache_size(),
                action=lambda: self._perform_cache_cleanup(),
                priority=3,
                cooldown=300
            )
            
            # 线程池优化规则
            if self.optimization_level in [OptimizationLevel.HIGH, OptimizationLevel.AGGRESSIVE]:
                self.performance_optimizer_add_rule(
                    name="thread_pool_optimization",
                    condition=lambda: self._check_thread_usage(),
                    action=lambda: self._optimize_thread_pool(),
                    priority=2,
                    cooldown=600
                )
            
            self.logger.info(f"Initialized {len(self.rules)} builtin optimization rules")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize builtin rules: {str(e)}")
    
    def _check_memory_pressure(self) -> bool:
        """检查内存压力"""
        try:
            import psutil
            memory_percent = psutil.virtual_memory().percent
            process = psutil.Process()
            process_memory_mb = process.memory_info().rss / 1024 / 1024
            
            return (memory_percent > 80 or 
                    process_memory_mb > self.thresholds["memory_usage_mb"])
        except Exception:
            return False
    
    def _check_cache_size(self) -> bool:
        """检查缓存大小"""
        # 这里应该检查实际的缓存使用情况
        # 为简化，返回False
        return False
    
    def _check_thread_usage(self) -> bool:
        """检查线程使用情况"""
        try:
            import psutil
            process = psutil.Process()
            thread_count = process.num_threads()
            return thread_count > 50  # 阈值可配置
        except Exception:
            return False
    
    def _perform_gc_optimization(self):
        """执行垃圾回收优化"""
        try:
            # 强制垃圾回收
            collected = gc.collect()
            self.logger.info(f"Garbage collection freed {collected} objects")
            
            # 如果是激进模式，执行更深度的清理
            if self.optimization_level == OptimizationLevel.AGGRESSIVE:
                for generation in range(3):
                    gc.collect(generation)
            
        except Exception as e:
            self.logger.error(f"Failed to perform GC optimization: {str(e)}")
    
    def _perform_cache_cleanup(self):
        """执行缓存清理"""
        try:
            # 这里应该清理实际的缓存
            # 为演示目的，只记录日志
            self.logger.info("Cache cleanup performed")
            
        except Exception as e:
            self.logger.error(f"Failed to perform cache cleanup: {str(e)}")
    
    def _optimize_thread_pool(self):
        """优化线程池"""
        try:
            # 这里应该优化实际的线程池配置
            # 为演示目的，只记录日志
            self.logger.info("Thread pool optimization performed")
            
        except Exception as e:
            self.logger.error(f"Failed to optimize thread pool: {str(e)}")
    
    def _get_current_metrics(self) -> Dict[str, float]:
        """获取当前指标"""
        try:
            import psutil
            
            # 获取系统指标
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                "memory_usage_mb": memory_info.rss / 1024 / 1024,
                "cpu_usage_percent": process.cpu_percent(),
                "thread_count": process.num_threads(),
                "timestamp": time.time()
            }
            
        except Exception:
            return {"timestamp": time.time()}
    
    def _add_optimization_result(self, result: OptimizationResult):
        """添加优化结果"""
        try:
            with self._lock:
                self.optimization_history.append(result)
                
                # 限制历史记录数量
                if len(self.optimization_history) > self.max_optimization_history:
                    self.optimization_history = self.optimization_history[-self.max_optimization_history:]
                    
        except Exception as e:
            self.logger.error(f"Failed to add optimization result: {str(e)}")
    
    async def _optimization_loop(self):
        """
        优化循环任务
        [performance][optimizer][_optimization_loop]
        """
        while not self._shutdown:
            try:
                await asyncio.sleep(self.optimization_interval)
                
                if self._shutdown:
                    break
                
                # 运行自动优化
                await self.performance_optimizer_run_optimization()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in optimization loop: {str(e)}")
    
    async def performance_optimizer_health_check(self) -> bool:
        """
        健康检查
        [performance][optimizer][health_check]
        """
        try:
            # 检查优化任务是否正常运行
            if self.auto_optimize and (not self._optimization_task or self._optimization_task.done()):
                self.logger.warning("Optimization task has stopped")
                return False
            
            # 检查最近是否有优化执行
            if self.optimization_history:
                latest_optimization = max(self.optimization_history, key=lambda x: x.timestamp)
                if time.time() - latest_optimization.timestamp > self.optimization_interval * 3:
                    self.logger.warning("No recent optimization executed")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Performance optimizer health check failed: {str(e)}")
            return False