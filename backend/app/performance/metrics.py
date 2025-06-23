"""
Performance Metrics
性能指标收集器 - [performance][metrics]
"""

import time
import psutil
import asyncio
import threading
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from collections import deque, defaultdict


@dataclass
class MetricPoint:
    """
    指标数据点
    [performance][metrics][metric_point]
    """
    timestamp: float
    value: float
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "timestamp": self.timestamp,
            "value": self.value,
            "tags": self.tags
        }


@dataclass
class TimeSeriesMetric:
    """
    时间序列指标
    [performance][metrics][time_series_metric]
    """
    name: str
    points: deque = field(default_factory=lambda: deque(maxlen=1000))
    max_points: int = 1000
    
    def add_point(self, value: float, tags: Optional[Dict[str, str]] = None):
        """添加数据点"""
        point = MetricPoint(
            timestamp=time.time(),
            value=value,
            tags=tags or {}
        )
        self.points.append(point)
    
    def get_recent_points(self, seconds: int = 300) -> List[MetricPoint]:
        """获取最近N秒的数据点"""
        cutoff_time = time.time() - seconds
        return [p for p in self.points if p.timestamp >= cutoff_time]
    
    def get_average(self, seconds: int = 300) -> float:
        """获取平均值"""
        points = self.get_recent_points(seconds)
        if not points:
            return 0.0
        return sum(p.value for p in points) / len(points)
    
    def get_max(self, seconds: int = 300) -> float:
        """获取最大值"""
        points = self.get_recent_points(seconds)
        if not points:
            return 0.0
        return max(p.value for p in points)
    
    def get_min(self, seconds: int = 300) -> float:
        """获取最小值"""
        points = self.get_recent_points(seconds)
        if not points:
            return 0.0
        return min(p.value for p in points)


class PerformanceMetrics:
    """
    性能指标收集器
    [performance][metrics]
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化性能指标收集器
        [performance][metrics][init]
        """
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        
        # 配置参数
        self.collection_interval = config.get("collection_interval", 5)  # 5秒
        self.max_metrics = config.get("max_metrics", 100)
        self.enable_system_metrics = config.get("enable_system_metrics", True)
        self.enable_application_metrics = config.get("enable_application_metrics", True)
        
        # 指标存储
        self.metrics: Dict[str, TimeSeriesMetric] = {}
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        
        # 收集任务
        self._collection_task: Optional[asyncio.Task] = None
        self._shutdown = False
        self._lock = threading.RLock()
        
        # 系统监控
        self.process = psutil.Process()
    
    async def performance_metrics_initialize(self) -> bool:
        """
        初始化性能指标收集器
        [performance][metrics][initialize]
        """
        try:
            # 启动指标收集任务
            self._collection_task = asyncio.create_task(self._collection_loop())
            
            self.logger.info(f"Performance metrics initialized with interval {self.collection_interval}s")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize performance metrics: {str(e)}")
            return False
    
    async def performance_metrics_cleanup(self):
        """
        清理性能指标收集器
        [performance][metrics][cleanup]
        """
        self._shutdown = True
        
        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass
        
        with self._lock:
            self.metrics.clear()
            self.counters.clear()
            self.gauges.clear()
            self.histograms.clear()
        
        self.logger.info("Performance metrics cleaned up")
    
    def performance_metrics_counter_increment(
        self, 
        name: str, 
        value: int = 1, 
        tags: Optional[Dict[str, str]] = None
    ):
        """
        递增计数器
        [performance][metrics][counter_increment]
        """
        try:
            with self._lock:
                full_name = self._build_metric_name(name, tags)
                self.counters[full_name] += value
                
                # 同时记录到时间序列
                if name not in self.metrics:
                    self.metrics[name] = TimeSeriesMetric(name)
                
                self.metrics[name].add_point(self.counters[full_name], tags)
                
        except Exception as e:
            self.logger.error(f"Failed to increment counter '{name}': {str(e)}")
    
    def performance_metrics_gauge_set(
        self, 
        name: str, 
        value: float, 
        tags: Optional[Dict[str, str]] = None
    ):
        """
        设置仪表值
        [performance][metrics][gauge_set]
        """
        try:
            with self._lock:
                full_name = self._build_metric_name(name, tags)
                self.gauges[full_name] = value
                
                # 同时记录到时间序列
                if name not in self.metrics:
                    self.metrics[name] = TimeSeriesMetric(name)
                
                self.metrics[name].add_point(value, tags)
                
        except Exception as e:
            self.logger.error(f"Failed to set gauge '{name}': {str(e)}")
    
    def performance_metrics_histogram_observe(
        self, 
        name: str, 
        value: float, 
        tags: Optional[Dict[str, str]] = None
    ):
        """
        观察直方图值
        [performance][metrics][histogram_observe]
        """
        try:
            with self._lock:
                full_name = self._build_metric_name(name, tags)
                self.histograms[full_name].append(value)
                
                # 限制历史数据大小
                if len(self.histograms[full_name]) > 1000:
                    self.histograms[full_name] = self.histograms[full_name][-1000:]
                
                # 同时记录到时间序列
                if name not in self.metrics:
                    self.metrics[name] = TimeSeriesMetric(name)
                
                self.metrics[name].add_point(value, tags)
                
        except Exception as e:
            self.logger.error(f"Failed to observe histogram '{name}': {str(e)}")
    
    def performance_metrics_timer_start(self, name: str) -> Callable[[], None]:
        """
        启动计时器
        [performance][metrics][timer_start]
        """
        start_time = time.time()
        
        def timer_end(tags: Optional[Dict[str, str]] = None):
            duration = time.time() - start_time
            self.performance_metrics_histogram_observe(f"{name}_duration", duration, tags)
        
        return timer_end
    
    async def performance_metrics_get_metric(
        self, 
        name: str, 
        seconds: int = 300
    ) -> Optional[Dict[str, Any]]:
        """
        获取指标数据
        [performance][metrics][get_metric]
        """
        try:
            with self._lock:
                if name not in self.metrics:
                    return None
                
                metric = self.metrics[name]
                points = metric.get_recent_points(seconds)
                
                if not points:
                    return None
                
                return {
                    "name": name,
                    "count": len(points),
                    "average": metric.get_average(seconds),
                    "max": metric.get_max(seconds),
                    "min": metric.get_min(seconds),
                    "latest": points[-1].value if points else 0.0,
                    "points": [p.to_dict() for p in points[-100:]]  # 最近100个点
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get metric '{name}': {str(e)}")
            return None
    
    async def performance_metrics_get_all_metrics(self) -> Dict[str, Any]:
        """
        获取所有指标数据
        [performance][metrics][get_all_metrics]
        """
        try:
            with self._lock:
                result = {
                    "system_metrics": await self._get_system_metrics(),
                    "application_metrics": {},
                    "counters": dict(self.counters),
                    "gauges": dict(self.gauges),
                    "histogram_summaries": self._get_histogram_summaries(),
                    "collection_time": time.time()
                }
                
                # 获取时间序列指标
                for name, metric in self.metrics.items():
                    metric_data = await self.performance_metrics_get_metric(name)
                    if metric_data:
                        result["application_metrics"][name] = metric_data
                
                return result
                
        except Exception as e:
            self.logger.error(f"Failed to get all metrics: {str(e)}")
            return {}
    
    async def performance_metrics_get_summary(self) -> Dict[str, Any]:
        """
        获取性能摘要
        [performance][metrics][get_summary]
        """
        try:
            system_metrics = await self._get_system_metrics()
            
            return {
                "timestamp": time.time(),
                "system": {
                    "cpu_percent": system_metrics.get("cpu_percent", 0),
                    "memory_percent": system_metrics.get("memory_percent", 0),
                    "memory_used_mb": system_metrics.get("memory_used_mb", 0),
                    "open_files": system_metrics.get("num_fds", 0)
                },
                "application": {
                    "total_metrics": len(self.metrics),
                    "total_counters": len(self.counters),
                    "total_gauges": len(self.gauges),
                    "total_histograms": len(self.histograms)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get performance summary: {str(e)}")
            return {}
    
    def _build_metric_name(self, name: str, tags: Optional[Dict[str, str]] = None) -> str:
        """
        构建完整的指标名称
        [performance][metrics][_build_metric_name]
        """
        if not tags:
            return name
        
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}{{{tag_str}}}"
    
    async def _get_system_metrics(self) -> Dict[str, Any]:
        """
        获取系统指标
        [performance][metrics][_get_system_metrics]
        """
        try:
            if not self.enable_system_metrics:
                return {}
            
            # CPU使用率
            cpu_percent = self.process.cpu_percent()
            
            # 内存使用情况
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()
            
            # 文件描述符
            try:
                num_fds = self.process.num_fds()
            except (AttributeError, psutil.AccessDenied):
                num_fds = 0
            
            # 线程数
            num_threads = self.process.num_threads()
            
            # 系统整体信息
            system_cpu_percent = psutil.cpu_percent()
            system_memory = psutil.virtual_memory()
            
            return {
                "process_cpu_percent": cpu_percent,
                "process_memory_percent": memory_percent,
                "process_memory_rss_mb": memory_info.rss / 1024 / 1024,
                "process_memory_vms_mb": memory_info.vms / 1024 / 1024,
                "memory_used_mb": memory_info.rss / 1024 / 1024,
                "num_fds": num_fds,
                "num_threads": num_threads,
                "system_cpu_percent": system_cpu_percent,
                "system_memory_percent": system_memory.percent,
                "system_memory_available_mb": system_memory.available / 1024 / 1024
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {str(e)}")
            return {}
    
    def _get_histogram_summaries(self) -> Dict[str, Dict[str, float]]:
        """
        获取直方图摘要统计
        [performance][metrics][_get_histogram_summaries]
        """
        summaries = {}
        
        for name, values in self.histograms.items():
            if not values:
                continue
            
            # 计算百分位数
            sorted_values = sorted(values)
            count = len(sorted_values)
            
            summaries[name] = {
                "count": count,
                "sum": sum(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / count,
                "p50": sorted_values[int(count * 0.5)] if count > 0 else 0,
                "p90": sorted_values[int(count * 0.9)] if count > 0 else 0,
                "p95": sorted_values[int(count * 0.95)] if count > 0 else 0,
                "p99": sorted_values[int(count * 0.99)] if count > 0 else 0
            }
        
        return summaries
    
    async def _collection_loop(self):
        """
        指标收集循环
        [performance][metrics][_collection_loop]
        """
        while not self._shutdown:
            try:
                await asyncio.sleep(self.collection_interval)
                
                if self._shutdown:
                    break
                
                # 收集系统指标
                if self.enable_system_metrics:
                    system_metrics = await self._get_system_metrics()
                    
                    # 记录关键系统指标
                    for metric_name, value in system_metrics.items():
                        if isinstance(value, (int, float)):
                            self.performance_metrics_gauge_set(f"system.{metric_name}", value)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in metrics collection loop: {str(e)}")
    
    async def performance_metrics_health_check(self) -> bool:
        """
        健康检查
        [performance][metrics][health_check]
        """
        try:
            # 检查收集任务是否正常运行
            if self._collection_task and self._collection_task.done():
                self.logger.warning("Metrics collection task has stopped")
                return False
            
            # 检查是否有最近的数据
            with self._lock:
                if not self.metrics:
                    return True  # 刚启动时没有数据是正常的
                
                # 检查是否有最近5分钟内的数据
                recent_data = False
                cutoff_time = time.time() - 300  # 5分钟
                
                for metric in self.metrics.values():
                    if metric.points and metric.points[-1].timestamp >= cutoff_time:
                        recent_data = True
                        break
                
                return recent_data
            
        except Exception as e:
            self.logger.error(f"Performance metrics health check failed: {str(e)}")
            return False