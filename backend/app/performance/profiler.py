"""
Performance Profiler
性能分析器 - [performance][profiler]
"""

import time
import asyncio
import cProfile
import pstats
import io
import functools
import threading
from typing import Dict, Any, Optional, Callable, List, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from contextlib import contextmanager
import logging


@dataclass
class ProfileResult:
    """
    性能分析结果
    [performance][profiler][profile_result]
    """
    name: str
    start_time: float
    end_time: float
    duration: float
    cpu_time: Optional[float] = None
    memory_before: Optional[int] = None
    memory_after: Optional[int] = None
    memory_peak: Optional[int] = None
    call_count: int = 1
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "cpu_time": self.cpu_time,
            "memory_before": self.memory_before,
            "memory_after": self.memory_after,
            "memory_peak": self.memory_peak,
            "call_count": self.call_count,
            "error": self.error,
            "details": self.details
        }


@dataclass
class FunctionProfile:
    """
    函数性能分析
    [performance][profiler][function_profile]
    """
    name: str
    total_calls: int = 0
    total_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    avg_duration: float = 0.0
    recent_calls: List[float] = field(default_factory=list)
    
    def add_call(self, duration: float):
        """添加一次调用记录"""
        self.total_calls += 1
        self.total_duration += duration
        self.min_duration = min(self.min_duration, duration)
        self.max_duration = max(self.max_duration, duration)
        self.avg_duration = self.total_duration / self.total_calls
        
        # 保留最近100次调用
        self.recent_calls.append(duration)
        if len(self.recent_calls) > 100:
            self.recent_calls.pop(0)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "total_calls": self.total_calls,
            "total_duration": self.total_duration,
            "min_duration": self.min_duration if self.min_duration != float('inf') else 0.0,
            "max_duration": self.max_duration,
            "avg_duration": self.avg_duration,
            "recent_avg": sum(self.recent_calls[-10:]) / min(10, len(self.recent_calls)) if self.recent_calls else 0.0
        }


class PerformanceProfiler:
    """
    性能分析器
    [performance][profiler]
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化性能分析器
        [performance][profiler][init]
        """
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        
        # 配置参数
        self.enable_profiling = config.get("enable_profiling", True)
        self.enable_memory_profiling = config.get("enable_memory_profiling", False)
        self.max_profiles = config.get("max_profiles", 1000)
        self.profile_threshold = config.get("profile_threshold", 0.001)  # 1ms
        
        # 分析结果存储
        self.profiles: List[ProfileResult] = []
        self.function_profiles: Dict[str, FunctionProfile] = {}
        self.active_profiles: Dict[str, Dict[str, Any]] = {}
        
        # 线程锁
        self._lock = threading.RLock()
        
        # 内存分析相关
        self._memory_profiler = None
        if self.enable_memory_profiling:
            try:
                import tracemalloc
                self._memory_profiler = tracemalloc
            except ImportError:
                self.logger.warning("tracemalloc not available, memory profiling disabled")
                self.enable_memory_profiling = False
    
    async def performance_profiler_initialize(self) -> bool:
        """
        初始化性能分析器
        [performance][profiler][initialize]
        """
        try:
            if self.enable_memory_profiling and self._memory_profiler:
                self._memory_profiler.start()
                self.logger.info("Memory profiling started")
            
            self.logger.info("Performance profiler initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize performance profiler: {str(e)}")
            return False
    
    async def performance_profiler_cleanup(self):
        """
        清理性能分析器
        [performance][profiler][cleanup]
        """
        try:
            if self.enable_memory_profiling and self._memory_profiler:
                self._memory_profiler.stop()
                self.logger.info("Memory profiling stopped")
            
            with self._lock:
                self.profiles.clear()
                self.function_profiles.clear()
                self.active_profiles.clear()
            
            self.logger.info("Performance profiler cleaned up")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup performance profiler: {str(e)}")
    
    @contextmanager
    def performance_profiler_profile(self, name: str, **kwargs):
        """
        性能分析上下文管理器
        [performance][profiler][profile]
        """
        if not self.enable_profiling:
            yield
            return
        
        profile_id = f"{name}_{time.time()}_{threading.current_thread().ident}"
        start_time = time.time()
        cpu_start = time.process_time()
        
        # 内存分析
        memory_before = None
        if self.enable_memory_profiling and self._memory_profiler:
            try:
                current, peak = self._memory_profiler.get_traced_memory()
                memory_before = current
            except Exception:
                pass
        
        # 记录开始状态
        with self._lock:
            self.active_profiles[profile_id] = {
                "name": name,
                "start_time": start_time,
                "cpu_start": cpu_start,
                "memory_before": memory_before,
                "kwargs": kwargs
            }
        
        error = None
        try:
            yield
        except Exception as e:
            error = str(e)
            raise
        finally:
            end_time = time.time()
            cpu_end = time.process_time()
            duration = end_time - start_time
            cpu_time = cpu_end - cpu_start
            
            # 内存分析
            memory_after = None
            memory_peak = None
            if self.enable_memory_profiling and self._memory_profiler:
                try:
                    current, peak = self._memory_profiler.get_traced_memory()
                    memory_after = current
                    memory_peak = peak
                except Exception:
                    pass
            
            # 只记录超过阈值的分析结果
            if duration >= self.profile_threshold:
                result = ProfileResult(
                    name=name,
                    start_time=start_time,
                    end_time=end_time,
                    duration=duration,
                    cpu_time=cpu_time,
                    memory_before=memory_before,
                    memory_after=memory_after,
                    memory_peak=memory_peak,
                    error=error,
                    details=kwargs
                )
                
                self._add_profile_result(result)
            
            # 清理活跃分析记录
            with self._lock:
                self.active_profiles.pop(profile_id, None)
    
    def performance_profiler_profile_function(self, name: Optional[str] = None):
        """
        函数性能分析装饰器
        [performance][profiler][profile_function]
        """
        def decorator(func: Callable) -> Callable:
            profile_name = name or f"{func.__module__}.{func.__name__}"
            
            if asyncio.iscoroutinefunction(func):
                @functools.wraps(func)
                async def async_wrapper(*args, **kwargs):
                    with self.performance_profiler_profile(profile_name):
                        return await func(*args, **kwargs)
                return async_wrapper
            else:
                @functools.wraps(func)
                def sync_wrapper(*args, **kwargs):
                    with self.performance_profiler_profile(profile_name):
                        return func(*args, **kwargs)
                return sync_wrapper
        
        return decorator
    
    async def performance_profiler_profile_code(
        self, 
        name: str, 
        code: str, 
        globals_dict: Optional[Dict[str, Any]] = None,
        locals_dict: Optional[Dict[str, Any]] = None
    ) -> ProfileResult:
        """
        分析代码片段性能
        [performance][profiler][profile_code]
        """
        try:
            profiler = cProfile.Profile()
            start_time = time.time()
            
            # 内存分析
            memory_before = None
            if self.enable_memory_profiling and self._memory_profiler:
                try:
                    current, peak = self._memory_profiler.get_traced_memory()
                    memory_before = current
                except Exception:
                    pass
            
            error = None
            try:
                profiler.enable()
                exec(code, globals_dict or {}, locals_dict or {})
                profiler.disable()
            except Exception as e:
                error = str(e)
                profiler.disable()
            
            end_time = time.time()
            duration = end_time - start_time
            
            # 内存分析
            memory_after = None
            memory_peak = None
            if self.enable_memory_profiling and self._memory_profiler:
                try:
                    current, peak = self._memory_profiler.get_traced_memory()
                    memory_after = current
                    memory_peak = peak
                except Exception:
                    pass
            
            # 生成统计信息
            stats_stream = io.StringIO()
            stats = pstats.Stats(profiler, stream=stats_stream)
            stats.sort_stats('cumulative')
            stats.print_stats(20)  # 显示前20个函数
            
            result = ProfileResult(
                name=name,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                memory_before=memory_before,
                memory_after=memory_after,
                memory_peak=memory_peak,
                error=error,
                details={
                    "code": code,
                    "profile_stats": stats_stream.getvalue()
                }
            )
            
            self._add_profile_result(result)
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to profile code '{name}': {str(e)}")
            return ProfileResult(
                name=name,
                start_time=time.time(),
                end_time=time.time(),
                duration=0.0,
                error=str(e)
            )
    
    async def performance_profiler_get_profiles(
        self, 
        name_filter: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        获取性能分析结果
        [performance][profiler][get_profiles]
        """
        try:
            with self._lock:
                profiles = self.profiles.copy()
            
            # 过滤结果
            if name_filter:
                profiles = [p for p in profiles if name_filter in p.name]
            
            # 按时间排序并限制数量
            profiles.sort(key=lambda x: x.start_time, reverse=True)
            profiles = profiles[:limit]
            
            return [p.to_dict() for p in profiles]
            
        except Exception as e:
            self.logger.error(f"Failed to get profiles: {str(e)}")
            return []
    
    async def performance_profiler_get_function_profiles(self) -> Dict[str, Dict[str, Any]]:
        """
        获取函数性能分析统计
        [performance][profiler][get_function_profiles]
        """
        try:
            with self._lock:
                return {name: profile.to_dict() for name, profile in self.function_profiles.items()}
                
        except Exception as e:
            self.logger.error(f"Failed to get function profiles: {str(e)}")
            return {}
    
    async def performance_profiler_get_summary(self) -> Dict[str, Any]:
        """
        获取性能分析摘要
        [performance][profiler][get_summary]
        """
        try:
            with self._lock:
                profiles = self.profiles.copy()
                function_profiles = self.function_profiles.copy()
            
            if not profiles:
                return {
                    "total_profiles": 0,
                    "total_functions": 0,
                    "active_profiles": len(self.active_profiles)
                }
            
            # 计算统计信息
            total_duration = sum(p.duration for p in profiles)
            avg_duration = total_duration / len(profiles)
            max_duration = max(p.duration for p in profiles)
            min_duration = min(p.duration for p in profiles)
            
            # 最慢的前10个分析
            slowest_profiles = sorted(profiles, key=lambda x: x.duration, reverse=True)[:10]
            
            # 内存使用统计
            memory_profiles = [p for p in profiles if p.memory_before is not None and p.memory_after is not None]
            memory_stats = {}
            if memory_profiles:
                memory_usage = [p.memory_after - p.memory_before for p in memory_profiles]
                memory_stats = {
                    "total_profiles_with_memory": len(memory_profiles),
                    "avg_memory_change": sum(memory_usage) / len(memory_usage),
                    "max_memory_change": max(memory_usage),
                    "min_memory_change": min(memory_usage)
                }
            
            return {
                "total_profiles": len(profiles),
                "total_functions": len(function_profiles),
                "active_profiles": len(self.active_profiles),
                "duration_stats": {
                    "total": total_duration,
                    "average": avg_duration,
                    "max": max_duration,
                    "min": min_duration
                },
                "memory_stats": memory_stats,
                "slowest_profiles": [
                    {
                        "name": p.name,
                        "duration": p.duration,
                        "start_time": p.start_time
                    } for p in slowest_profiles
                ],
                "most_called_functions": [
                    {
                        "name": name,
                        "calls": profile.total_calls,
                        "avg_duration": profile.avg_duration
                    } for name, profile in sorted(
                        function_profiles.items(),
                        key=lambda x: x[1].total_calls,
                        reverse=True
                    )[:10]
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get profiler summary: {str(e)}")
            return {}
    
    async def performance_profiler_clear_profiles(self):
        """
        清理性能分析记录
        [performance][profiler][clear_profiles]
        """
        try:
            with self._lock:
                self.profiles.clear()
                self.function_profiles.clear()
            
            self.logger.info("Performance profiles cleared")
            
        except Exception as e:
            self.logger.error(f"Failed to clear profiles: {str(e)}")
    
    def _add_profile_result(self, result: ProfileResult):
        """
        添加性能分析结果
        [performance][profiler][_add_profile_result]
        """
        try:
            with self._lock:
                # 添加到结果列表
                self.profiles.append(result)
                
                # 限制结果数量
                if len(self.profiles) > self.max_profiles:
                    self.profiles = self.profiles[-self.max_profiles:]
                
                # 更新函数统计
                if result.name not in self.function_profiles:
                    self.function_profiles[result.name] = FunctionProfile(result.name)
                
                self.function_profiles[result.name].add_call(result.duration)
                
        except Exception as e:
            self.logger.error(f"Failed to add profile result: {str(e)}")
    
    async def performance_profiler_health_check(self) -> bool:
        """
        健康检查
        [performance][profiler][health_check]
        """
        try:
            # 检查是否有卡死的活跃分析
            current_time = time.time()
            stuck_profiles = []
            
            with self._lock:
                for profile_id, profile_data in self.active_profiles.items():
                    if current_time - profile_data["start_time"] > 300:  # 5分钟
                        stuck_profiles.append(profile_id)
                
                # 清理卡死的分析
                for profile_id in stuck_profiles:
                    self.active_profiles.pop(profile_id, None)
            
            if stuck_profiles:
                self.logger.warning(f"Cleared {len(stuck_profiles)} stuck profiles")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Performance profiler health check failed: {str(e)}")
            return False