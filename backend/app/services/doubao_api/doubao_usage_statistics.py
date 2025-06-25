"""
Doubao Usage Statistics Service
豆包使用统计服务 - [services][doubao_api][doubao_usage_statistics]
"""

import asyncio
import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import statistics
from collections import defaultdict, deque

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.doubao_usage import (
    DoubaoUsageRecord, DoubaoQuotaRecord, 
    DoubaoServiceMetrics, DoubaoAccountBalance
)
from app.models.user import User
from app.cache.cache_manager import CacheManager

logger = logging.getLogger(__name__)


class StatisticsPeriod(Enum):
    """统计周期枚举"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class UsageMetricType(Enum):
    """使用指标类型"""
    REQUEST_COUNT = "request_count"
    SUCCESS_RATE = "success_rate"
    ERROR_RATE = "error_rate"
    AVERAGE_LATENCY = "average_latency"
    TOTAL_COST = "total_cost"
    CACHE_HIT_RATE = "cache_hit_rate"
    TOKENS_USED = "tokens_used"


@dataclass
class UsageStatistics:
    """使用统计数据"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    cached_requests: int = 0
    total_cost: float = 0.0
    total_tokens: int = 0
    average_latency: float = 0.0
    min_latency: float = 0.0
    max_latency: float = 0.0
    p95_latency: float = 0.0
    p99_latency: float = 0.0
    success_rate: float = 0.0
    error_rate: float = 0.0
    cache_hit_rate: float = 0.0
    period_start: datetime = None
    period_end: datetime = None


@dataclass
class QuotaStatus:
    """配额状态"""
    service_type: str
    quota_type: str
    total_quota: int
    used_quota: int
    remaining_quota: int
    usage_percentage: float
    is_exceeded: bool
    is_warning: bool
    reset_time: datetime


@dataclass
class CostBreakdown:
    """成本分析"""
    service_type: str
    total_cost: float
    cost_per_request: float
    cost_percentage: float
    request_count: int
    top_users: List[Tuple[int, str, float]]  # user_id, username, cost


class DoubaoUsageStatisticsService:
    """豆包使用统计服务 - [services][doubao_api][usage_statistics]"""
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.cache_prefix = "doubao_stats"
        self.cache_ttl = 300  # 5分钟缓存
        
        # 实时统计缓存
        self._realtime_stats = defaultdict(lambda: defaultdict(int))
        self._latency_buffer = defaultdict(lambda: deque(maxlen=1000))
        
    async def record_usage(self, usage_record: DoubaoUsageRecord) -> bool:
        """记录使用情况"""
        try:
            async with get_db() as db:
                db.add(usage_record)
                await db.commit()
                
                # 更新实时统计
                await self._update_realtime_stats(usage_record)
                
                # 更新服务指标
                await self._update_service_metrics(usage_record, db)
                
                # 更新配额使用
                if usage_record.user_id:
                    await self._update_quota_usage(usage_record, db)
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to record usage: {e}")
            return False
    
    async def _update_realtime_stats(self, usage_record: DoubaoUsageRecord):
        """更新实时统计"""
        service_key = usage_record.service_type
        
        self._realtime_stats[service_key]["total_requests"] += 1
        
        if usage_record.success:
            self._realtime_stats[service_key]["successful_requests"] += 1
        else:
            self._realtime_stats[service_key]["failed_requests"] += 1
        
        if usage_record.cache_hit:
            self._realtime_stats[service_key]["cached_requests"] += 1
        
        self._realtime_stats[service_key]["total_cost"] += usage_record.cost
        self._realtime_stats[service_key]["total_tokens"] += usage_record.tokens_used
        
        # 记录延迟
        if usage_record.latency > 0:
            self._latency_buffer[service_key].append(usage_record.latency)
    
    async def _update_service_metrics(self, usage_record: DoubaoUsageRecord, db: AsyncSession):
        """更新服务指标"""
        # 获取当前小时的指标记录
        current_hour = usage_record.created_at.replace(minute=0, second=0, microsecond=0)
        
        stmt = select(DoubaoServiceMetrics).where(
            and_(
                DoubaoServiceMetrics.service_type == usage_record.service_type,
                DoubaoServiceMetrics.metric_date == current_hour.date(),
                DoubaoServiceMetrics.metric_hour == current_hour.hour
            )
        )
        
        result = await db.execute(stmt)
        metrics = result.scalar_one_or_none()
        
        if not metrics:
            metrics = DoubaoServiceMetrics(
                service_type=usage_record.service_type,
                metric_date=current_hour.date(),
                metric_hour=current_hour.hour
            )
            db.add(metrics)
        
        # 更新指标
        metrics.update_metrics(usage_record)
        await db.commit()
    
    async def _update_quota_usage(self, usage_record: DoubaoUsageRecord, db: AsyncSession):
        """更新配额使用"""
        today = usage_record.created_at.date()
        current_month_start = today.replace(day=1)
        
        # 更新日配额
        daily_quota = await self._get_or_create_quota(
            db, usage_record.user_id, usage_record.service_type,
            "daily", today, today + timedelta(days=1)
        )
        daily_quota.used_quota += 1
        daily_quota.used_cost_quota += usage_record.cost
        daily_quota.remaining_quota = daily_quota.total_quota - daily_quota.used_quota
        daily_quota.remaining_cost_quota = daily_quota.total_cost_quota - daily_quota.used_cost_quota
        
        # 更新月配额
        next_month = (current_month_start + timedelta(days=32)).replace(day=1)
        monthly_quota = await self._get_or_create_quota(
            db, usage_record.user_id, usage_record.service_type,
            "monthly", current_month_start, next_month
        )
        monthly_quota.used_quota += 1
        monthly_quota.used_cost_quota += usage_record.cost
        monthly_quota.remaining_quota = monthly_quota.total_quota - monthly_quota.used_quota
        monthly_quota.remaining_cost_quota = monthly_quota.total_cost_quota - monthly_quota.used_cost_quota
        
        # 检查是否超额
        if daily_quota.used_quota >= daily_quota.total_quota:
            daily_quota.is_exceeded = True
        if monthly_quota.used_quota >= monthly_quota.total_quota:
            monthly_quota.is_exceeded = True
        
        await db.commit()
    
    async def _get_or_create_quota(self, db: AsyncSession, user_id: int, 
                                  service_type: str, quota_type: str,
                                  period_start: date, period_end: date) -> DoubaoQuotaRecord:
        """获取或创建配额记录"""
        stmt = select(DoubaoQuotaRecord).where(
            and_(
                DoubaoQuotaRecord.user_id == user_id,
                DoubaoQuotaRecord.service_type == service_type,
                DoubaoQuotaRecord.quota_type == quota_type,
                DoubaoQuotaRecord.quota_period_start == period_start
            )
        )
        
        result = await db.execute(stmt)
        quota = result.scalar_one_or_none()
        
        if not quota:
            # 获取默认配额设置
            default_quotas = self._get_default_quotas(service_type, quota_type)
            
            quota = DoubaoQuotaRecord(
                user_id=user_id,
                service_type=service_type,
                quota_type=quota_type,
                total_quota=default_quotas["requests"],
                total_cost_quota=default_quotas["cost"],
                quota_period_start=period_start,
                quota_period_end=period_end
            )
            db.add(quota)
            await db.flush()
        
        return quota
    
    def _get_default_quotas(self, service_type: str, quota_type: str) -> Dict[str, Any]:
        """获取默认配额设置"""
        quotas = {
            "tts": {
                "daily": {"requests": 1000, "cost": 10.0},
                "monthly": {"requests": 30000, "cost": 300.0}
            },
            "voice_clone": {
                "daily": {"requests": 10, "cost": 5.0},
                "monthly": {"requests": 300, "cost": 150.0}
            },
            "text_analysis": {
                "daily": {"requests": 5000, "cost": 5.0},
                "monthly": {"requests": 150000, "cost": 150.0}
            },
            "image_generation": {
                "daily": {"requests": 100, "cost": 10.0},
                "monthly": {"requests": 3000, "cost": 300.0}
            }
        }
        
        return quotas.get(service_type, {}).get(quota_type, {"requests": 100, "cost": 1.0})
    
    async def get_usage_statistics(self, service_type: Optional[str] = None,
                                  user_id: Optional[int] = None,
                                  period: StatisticsPeriod = StatisticsPeriod.DAY,
                                  start_date: Optional[datetime] = None,
                                  end_date: Optional[datetime] = None) -> UsageStatistics:
        """获取使用统计"""
        # 生成缓存键
        cache_key = self._generate_stats_cache_key(
            service_type, user_id, period, start_date, end_date
        )
        
        # 检查缓存
        cached_stats = await self.cache_manager.get(cache_key)
        if cached_stats:
            return UsageStatistics(**cached_stats)
        
        # 计算时间范围
        if not start_date or not end_date:
            start_date, end_date = self._calculate_period_range(period)
        
        async with get_db() as db:
            # 构建查询
            query = select(DoubaoUsageRecord).where(
                and_(
                    DoubaoUsageRecord.created_at >= start_date,
                    DoubaoUsageRecord.created_at <= end_date
                )
            )
            
            if service_type:
                query = query.where(DoubaoUsageRecord.service_type == service_type)
            
            if user_id:
                query = query.where(DoubaoUsageRecord.user_id == user_id)
            
            result = await db.execute(query)
            records = result.scalars().all()
            
            # 计算统计数据
            stats = self._calculate_statistics(records, start_date, end_date)
            
            # 缓存结果
            await self.cache_manager.set(
                cache_key, stats.__dict__, ttl=self.cache_ttl
            )
            
            return stats
    
    def _generate_stats_cache_key(self, service_type: Optional[str], 
                                 user_id: Optional[int],
                                 period: StatisticsPeriod,
                                 start_date: Optional[datetime],
                                 end_date: Optional[datetime]) -> str:
        """生成统计缓存键"""
        key_parts = [self.cache_prefix, "stats"]
        
        if service_type:
            key_parts.append(f"service_{service_type}")
        if user_id:
            key_parts.append(f"user_{user_id}")
        
        key_parts.append(f"period_{period.value}")
        
        if start_date and end_date:
            key_parts.append(f"range_{start_date.date()}_{end_date.date()}")
        
        return ":".join(key_parts)
    
    def _calculate_period_range(self, period: StatisticsPeriod) -> Tuple[datetime, datetime]:
        """计算周期时间范围"""
        now = datetime.now()
        
        if period == StatisticsPeriod.HOUR:
            start = now.replace(minute=0, second=0, microsecond=0)
            end = start + timedelta(hours=1)
        elif period == StatisticsPeriod.DAY:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif period == StatisticsPeriod.WEEK:
            days_since_monday = now.weekday()
            start = (now - timedelta(days=days_since_monday)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            end = start + timedelta(days=7)
        elif period == StatisticsPeriod.MONTH:
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month = (start + timedelta(days=32)).replace(day=1)
            end = next_month
        elif period == StatisticsPeriod.YEAR:
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = start.replace(year=start.year + 1)
        else:
            start = now - timedelta(hours=1)
            end = now
        
        return start, end
    
    def _calculate_statistics(self, records: List[DoubaoUsageRecord],
                            start_date: datetime, end_date: datetime) -> UsageStatistics:
        """计算统计数据"""
        if not records:
            return UsageStatistics(period_start=start_date, period_end=end_date)
        
        total_requests = len(records)
        successful_requests = sum(1 for r in records if r.success)
        failed_requests = total_requests - successful_requests
        cached_requests = sum(1 for r in records if r.cache_hit)
        
        total_cost = sum(r.cost for r in records)
        total_tokens = sum(r.tokens_used for r in records)
        
        # 延迟统计
        latencies = [r.latency for r in records if r.latency > 0]
        if latencies:
            average_latency = statistics.mean(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            
            # 计算百分位数
            sorted_latencies = sorted(latencies)
            p95_index = int(len(sorted_latencies) * 0.95)
            p99_index = int(len(sorted_latencies) * 0.99)
            p95_latency = sorted_latencies[p95_index] if p95_index < len(sorted_latencies) else max_latency
            p99_latency = sorted_latencies[p99_index] if p99_index < len(sorted_latencies) else max_latency
        else:
            average_latency = min_latency = max_latency = p95_latency = p99_latency = 0.0
        
        # 计算比率
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0.0
        error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0.0
        cache_hit_rate = (cached_requests / total_requests * 100) if total_requests > 0 else 0.0
        
        return UsageStatistics(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            cached_requests=cached_requests,
            total_cost=total_cost,
            total_tokens=total_tokens,
            average_latency=average_latency,
            min_latency=min_latency,
            max_latency=max_latency,
            p95_latency=p95_latency,
            p99_latency=p99_latency,
            success_rate=success_rate,
            error_rate=error_rate,
            cache_hit_rate=cache_hit_rate,
            period_start=start_date,
            period_end=end_date
        )
    
    async def get_quota_status(self, user_id: Optional[int] = None,
                              service_type: Optional[str] = None) -> List[QuotaStatus]:
        """获取配额状态"""
        async with get_db() as db:
            query = select(DoubaoQuotaRecord).where(
                DoubaoQuotaRecord.is_active == True
            )
            
            if user_id:
                query = query.where(DoubaoQuotaRecord.user_id == user_id)
            
            if service_type:
                query = query.where(DoubaoQuotaRecord.service_type == service_type)
            
            # 只查询当前有效的配额
            now = datetime.now()
            query = query.where(
                and_(
                    DoubaoQuotaRecord.quota_period_start <= now.date(),
                    DoubaoQuotaRecord.quota_period_end > now.date()
                )
            )
            
            result = await db.execute(query)
            quotas = result.scalars().all()
            
            quota_statuses = []
            for quota in quotas:
                status = QuotaStatus(
                    service_type=quota.service_type,
                    quota_type=quota.quota_type,
                    total_quota=quota.total_quota,
                    used_quota=quota.used_quota,
                    remaining_quota=quota.remaining_quota,
                    usage_percentage=quota.usage_percentage,
                    is_exceeded=quota.is_exceeded,
                    is_warning=quota.is_warning,
                    reset_time=quota.quota_period_end
                )
                quota_statuses.append(status)
            
            return quota_statuses
    
    async def get_cost_breakdown(self, period: StatisticsPeriod = StatisticsPeriod.MONTH,
                                start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None) -> List[CostBreakdown]:
        """获取成本分析"""
        if not start_date or not end_date:
            start_date, end_date = self._calculate_period_range(period)
        
        async with get_db() as db:
            # 按服务类型统计成本
            stmt = select(
                DoubaoUsageRecord.service_type,
                func.sum(DoubaoUsageRecord.cost).label('total_cost'),
                func.count(DoubaoUsageRecord.usage_id).label('request_count'),
                func.avg(DoubaoUsageRecord.cost).label('avg_cost')
            ).where(
                and_(
                    DoubaoUsageRecord.created_at >= start_date,
                    DoubaoUsageRecord.created_at <= end_date,
                    DoubaoUsageRecord.success == True
                )
            ).group_by(DoubaoUsageRecord.service_type)
            
            result = await db.execute(stmt)
            service_costs = result.all()
            
            # 计算总成本
            total_cost = sum(row.total_cost for row in service_costs)
            
            cost_breakdowns = []
            for row in service_costs:
                # 获取该服务的top用户
                top_users = await self._get_top_users_by_cost(
                    db, row.service_type, start_date, end_date
                )
                
                breakdown = CostBreakdown(
                    service_type=row.service_type,
                    total_cost=float(row.total_cost),
                    cost_per_request=float(row.avg_cost),
                    cost_percentage=(row.total_cost / total_cost * 100) if total_cost > 0 else 0.0,
                    request_count=row.request_count,
                    top_users=top_users
                )
                cost_breakdowns.append(breakdown)
            
            return cost_breakdowns
    
    async def _get_top_users_by_cost(self, db: AsyncSession, service_type: str,
                                    start_date: datetime, end_date: datetime,
                                    limit: int = 5) -> List[Tuple[int, str, float]]:
        """获取消费最高的用户"""
        stmt = select(
            DoubaoUsageRecord.user_id,
            func.sum(DoubaoUsageRecord.cost).label('total_cost')
        ).where(
            and_(
                DoubaoUsageRecord.service_type == service_type,
                DoubaoUsageRecord.created_at >= start_date,
                DoubaoUsageRecord.created_at <= end_date,
                DoubaoUsageRecord.user_id.isnot(None)
            )
        ).group_by(
            DoubaoUsageRecord.user_id
        ).order_by(
            func.sum(DoubaoUsageRecord.cost).desc()
        ).limit(limit)
        
        result = await db.execute(stmt)
        user_costs = result.all()
        
        # 获取用户信息
        top_users = []
        for user_cost in user_costs:
            user_stmt = select(User.username).where(User.id == user_cost.user_id)
            user_result = await db.execute(user_stmt)
            username = user_result.scalar_one_or_none() or "Unknown"
            
            top_users.append((
                user_cost.user_id,
                username,
                float(user_cost.total_cost)
            ))
        
        return top_users
    
    async def get_realtime_metrics(self) -> Dict[str, Any]:
        """获取实时指标"""
        realtime_data = {}
        
        for service_type, stats in self._realtime_stats.items():
            latencies = list(self._latency_buffer[service_type])
            
            metrics = {
                "total_requests": stats["total_requests"],
                "successful_requests": stats["successful_requests"],
                "failed_requests": stats["failed_requests"],
                "cached_requests": stats["cached_requests"],
                "total_cost": stats["total_cost"],
                "total_tokens": stats["total_tokens"],
                "success_rate": (stats["successful_requests"] / max(stats["total_requests"], 1)) * 100,
                "cache_hit_rate": (stats["cached_requests"] / max(stats["total_requests"], 1)) * 100
            }
            
            if latencies:
                metrics.update({
                    "average_latency": statistics.mean(latencies),
                    "min_latency": min(latencies),
                    "max_latency": max(latencies),
                    "p95_latency": statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)
                })
            
            realtime_data[service_type] = metrics
        
        return realtime_data
    
    async def reset_quota(self, user_id: int, service_type: str, quota_type: str) -> bool:
        """重置用户配额"""
        try:
            async with get_db() as db:
                now = datetime.now()
                
                stmt = select(DoubaoQuotaRecord).where(
                    and_(
                        DoubaoQuotaRecord.user_id == user_id,
                        DoubaoQuotaRecord.service_type == service_type,
                        DoubaoQuotaRecord.quota_type == quota_type,
                        DoubaoQuotaRecord.is_active == True,
                        DoubaoQuotaRecord.quota_period_start <= now.date(),
                        DoubaoQuotaRecord.quota_period_end > now.date()
                    )
                )
                
                result = await db.execute(stmt)
                quota = result.scalar_one_or_none()
                
                if quota:
                    quota.used_quota = 0
                    quota.used_cost_quota = 0.0
                    quota.remaining_quota = quota.total_quota
                    quota.remaining_cost_quota = quota.total_cost_quota
                    quota.is_exceeded = False
                    
                    await db.commit()
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"Failed to reset quota: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            async with get_db() as db:
                # 检查最近的使用记录
                recent_record_stmt = select(DoubaoUsageRecord).order_by(
                    DoubaoUsageRecord.created_at.desc()
                ).limit(1)
                
                result = await db.execute(recent_record_stmt)
                latest_record = result.scalar_one_or_none()
                
                return {
                    "status": "healthy",
                    "latest_record_time": latest_record.created_at.isoformat() if latest_record else None,
                    "realtime_services": list(self._realtime_stats.keys()),
                    "cache_status": await self.cache_manager.health_check()
                }
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }