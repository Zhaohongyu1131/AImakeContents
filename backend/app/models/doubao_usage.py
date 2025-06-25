"""
Doubao Usage Models
豆包使用记录模型 - [models][doubao_usage]
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, Index, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from app.core.database import Base


class DoubaoUsageRecord(Base):
    """豆包API使用记录表 - [models][doubao_usage][record]"""
    
    __tablename__ = "doubao_usage_records"
    
    # 基础字段
    usage_id = Column(Integer, primary_key=True, index=True, comment="使用记录ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True, comment="用户ID")
    
    # 服务信息
    service_type = Column(String(50), nullable=False, index=True, comment="服务类型")
    method = Column(String(100), nullable=False, comment="调用方法")
    
    # 请求信息
    request_id = Column(String(100), nullable=True, index=True, comment="请求ID")
    request_params = Column(JSON, nullable=True, comment="请求参数")
    request_size = Column(Integer, default=0, comment="请求大小(字节)")
    
    # 响应信息
    success = Column(Boolean, default=True, nullable=False, index=True, comment="是否成功")
    response_size = Column(Integer, default=0, comment="响应大小(字节)")
    error_message = Column(Text, nullable=True, comment="错误信息")
    error_code = Column(String(50), nullable=True, comment="错误代码")
    
    # 性能指标
    latency = Column(Float, default=0.0, comment="延迟(秒)")
    processing_time = Column(Float, default=0.0, comment="处理时间(秒)")
    queue_time = Column(Float, default=0.0, comment="队列等待时间(秒)")
    
    # 成本信息
    cost = Column(Float, default=0.0, comment="调用成本")
    tokens_used = Column(Integer, default=0, comment="使用的token数")
    
    # 缓存信息
    cache_hit = Column(Boolean, default=False, comment="是否命中缓存")
    cache_key = Column(String(255), nullable=True, comment="缓存键")
    
    # 系统信息
    ip_address = Column(String(45), nullable=True, comment="客户端IP")
    user_agent = Column(String(500), nullable=True, comment="用户代理")
    api_version = Column(String(20), default="v1", comment="API版本")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True, comment="创建时间")
    
    # 关系
    user = relationship("User", back_populates="doubao_usage_records")
    
    # 索引
    __table_args__ = (
        Index('idx_doubao_usage_service_time', 'service_type', 'created_at'),
        Index('idx_doubao_usage_user_time', 'user_id', 'created_at'),
        Index('idx_doubao_usage_success_time', 'success', 'created_at'),
        Index('idx_doubao_usage_cost', 'cost', 'created_at'),
    )
    
    def __repr__(self):
        return f"<DoubaoUsageRecord(usage_id={self.usage_id}, service={self.service_type}, method={self.method})>"


class DoubaoQuotaRecord(Base):
    """豆包配额管理记录表 - [models][doubao_usage][quota]"""
    
    __tablename__ = "doubao_quota_records"
    
    # 基础字段
    quota_id = Column(Integer, primary_key=True, index=True, comment="配额记录ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True, comment="用户ID")
    
    # 配额信息
    service_type = Column(String(50), nullable=False, index=True, comment="服务类型")
    quota_type = Column(String(20), nullable=False, comment="配额类型(daily/monthly/yearly)")
    
    # 配额数量
    total_quota = Column(Integer, default=0, comment="总配额")
    used_quota = Column(Integer, default=0, comment="已使用配额")
    remaining_quota = Column(Integer, default=0, comment="剩余配额")
    
    # 成本配额
    total_cost_quota = Column(Float, default=0.0, comment="总成本配额")
    used_cost_quota = Column(Float, default=0.0, comment="已使用成本配额")
    remaining_cost_quota = Column(Float, default=0.0, comment="剩余成本配额")
    
    # 时间信息
    quota_period_start = Column(DateTime, nullable=False, comment="配额周期开始时间")
    quota_period_end = Column(DateTime, nullable=False, comment="配额周期结束时间")
    
    # 状态信息
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_exceeded = Column(Boolean, default=False, comment="是否超额")
    warning_threshold = Column(Float, default=0.8, comment="警告阈值(比例)")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    user = relationship("User", back_populates="doubao_quota_records")
    
    # 索引
    __table_args__ = (
        Index('idx_doubao_quota_user_service', 'user_id', 'service_type'),
        Index('idx_doubao_quota_period', 'quota_period_start', 'quota_period_end'),
        Index('idx_doubao_quota_active', 'is_active', 'quota_period_end'),
    )
    
    @property
    def usage_percentage(self) -> float:
        """使用百分比"""
        if self.total_quota <= 0:
            return 0.0
        return (self.used_quota / self.total_quota) * 100
    
    @property
    def cost_usage_percentage(self) -> float:
        """成本使用百分比"""
        if self.total_cost_quota <= 0:
            return 0.0
        return (self.used_cost_quota / self.total_cost_quota) * 100
    
    @property
    def is_warning(self) -> bool:
        """是否达到警告阈值"""
        return self.usage_percentage >= (self.warning_threshold * 100)
    
    def __repr__(self):
        return f"<DoubaoQuotaRecord(quota_id={self.quota_id}, service={self.service_type}, usage={self.usage_percentage:.1f}%)>"


class DoubaoServiceMetrics(Base):
    """豆包服务指标统计表 - [models][doubao_usage][metrics]"""
    
    __tablename__ = "doubao_service_metrics"
    
    # 基础字段
    metric_id = Column(Integer, primary_key=True, index=True, comment="指标ID")
    service_type = Column(String(50), nullable=False, index=True, comment="服务类型")
    
    # 时间信息
    metric_date = Column(DateTime, nullable=False, index=True, comment="指标日期")
    metric_hour = Column(Integer, nullable=True, comment="小时(0-23)")
    
    # 请求统计
    total_requests = Column(Integer, default=0, comment="总请求数")
    successful_requests = Column(Integer, default=0, comment="成功请求数")
    failed_requests = Column(Integer, default=0, comment="失败请求数")
    cached_requests = Column(Integer, default=0, comment="缓存命中请求数")
    
    # 性能统计
    total_latency = Column(Float, default=0.0, comment="总延迟")
    average_latency = Column(Float, default=0.0, comment="平均延迟")
    min_latency = Column(Float, default=0.0, comment="最小延迟")
    max_latency = Column(Float, default=0.0, comment="最大延迟")
    p95_latency = Column(Float, default=0.0, comment="95%延迟")
    p99_latency = Column(Float, default=0.0, comment="99%延迟")
    
    # 成本统计
    total_cost = Column(Float, default=0.0, comment="总成本")
    average_cost = Column(Float, default=0.0, comment="平均成本")
    total_tokens = Column(Integer, default=0, comment="总token数")
    
    # 数据传输统计
    total_request_size = Column(Integer, default=0, comment="总请求大小(字节)")
    total_response_size = Column(Integer, default=0, comment="总响应大小(字节)")
    average_request_size = Column(Float, default=0.0, comment="平均请求大小")
    average_response_size = Column(Float, default=0.0, comment="平均响应大小")
    
    # 错误统计
    error_rate = Column(Float, default=0.0, comment="错误率")
    cache_hit_rate = Column(Float, default=0.0, comment="缓存命中率")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 索引
    __table_args__ = (
        Index('idx_doubao_metrics_service_date', 'service_type', 'metric_date'),
        Index('idx_doubao_metrics_date_hour', 'metric_date', 'metric_hour'),
    )
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_requests <= 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    def update_metrics(self, usage_record: DoubaoUsageRecord):
        """更新指标数据"""
        self.total_requests += 1
        
        if usage_record.success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        if usage_record.cache_hit:
            self.cached_requests += 1
        
        # 更新延迟统计
        if usage_record.latency > 0:
            self.total_latency += usage_record.latency
            self.average_latency = self.total_latency / self.total_requests
            
            if self.min_latency == 0 or usage_record.latency < self.min_latency:
                self.min_latency = usage_record.latency
            
            if usage_record.latency > self.max_latency:
                self.max_latency = usage_record.latency
        
        # 更新成本统计
        self.total_cost += usage_record.cost
        self.average_cost = self.total_cost / self.total_requests
        self.total_tokens += usage_record.tokens_used
        
        # 更新数据传输统计
        self.total_request_size += usage_record.request_size
        self.total_response_size += usage_record.response_size
        self.average_request_size = self.total_request_size / self.total_requests
        self.average_response_size = self.total_response_size / self.total_requests
        
        # 更新错误率和缓存命中率
        self.error_rate = (self.failed_requests / self.total_requests) * 100
        self.cache_hit_rate = (self.cached_requests / self.total_requests) * 100
        
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f"<DoubaoServiceMetrics(metric_id={self.metric_id}, service={self.service_type}, date={self.metric_date.date()})>"


class DoubaoAccountBalance(Base):
    """豆包账户余额表 - [models][doubao_usage][balance]"""
    
    __tablename__ = "doubao_account_balances"
    
    # 基础字段
    balance_id = Column(Integer, primary_key=True, index=True, comment="余额记录ID")
    account_name = Column(String(100), nullable=False, unique=True, comment="账户名称")
    
    # 账户信息
    app_id = Column(String(100), nullable=False, comment="应用ID")
    access_token = Column(String(500), nullable=False, comment="访问令牌")
    cluster_name = Column(String(100), nullable=True, comment="集群名称")
    
    # 余额信息
    total_balance = Column(Float, default=0.0, comment="总余额")
    used_balance = Column(Float, default=0.0, comment="已使用余额")
    remaining_balance = Column(Float, default=0.0, comment="剩余余额")
    currency = Column(String(10), default="CNY", comment="货币单位")
    
    # 使用限制
    daily_limit = Column(Float, default=0.0, comment="日限额")
    monthly_limit = Column(Float, default=0.0, comment="月限额")
    
    # 状态信息
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_primary = Column(Boolean, default=False, comment="是否主账户")
    priority = Column(Integer, default=1, comment="优先级(1-10)")
    
    # 时间戳
    last_sync_at = Column(DateTime, nullable=True, comment="最后同步时间")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 索引
    __table_args__ = (
        Index('idx_doubao_balance_active', 'is_active', 'priority'),
        Index('idx_doubao_balance_primary', 'is_primary', 'is_active'),
    )
    
    @property
    def usage_percentage(self) -> float:
        """使用百分比"""
        if self.total_balance <= 0:
            return 0.0
        return (self.used_balance / self.total_balance) * 100
    
    @property
    def is_low_balance(self, threshold: float = 0.1) -> bool:
        """是否余额不足"""
        return self.remaining_balance <= (self.total_balance * threshold)
    
    def update_balance(self, cost: float):
        """更新余额"""
        self.used_balance += cost
        self.remaining_balance = self.total_balance - self.used_balance
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f"<DoubaoAccountBalance(account={self.account_name}, balance={self.remaining_balance:.2f})>"