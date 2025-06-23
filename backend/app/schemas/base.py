"""
Base Schemas
基础响应模型 - [schemas][base]
"""

from typing import Optional, Any, List, Generic, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar('T')

class ResponseBaseSchema(BaseModel, Generic[T]):
    """
    API基础响应模型
    [schemas][base][response]
    """
    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PaginationSchema(BaseModel):
    """
    分页信息模型
    [schemas][base][pagination]
    """
    page: int = Field(..., ge=1, description="当前页码")
    size: int = Field(..., ge=1, le=100, description="每页大小")
    total: int = Field(..., ge=0, description="总记录数")
    pages: int = Field(..., ge=0, description="总页数")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")

class PaginatedResponseSchema(BaseModel, Generic[T]):
    """
    分页响应模型
    [schemas][base][paginated_response]
    """
    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="响应消息")
    data: List[T] = Field(..., description="数据列表")
    pagination: PaginationSchema = Field(..., description="分页信息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ErrorSchema(BaseModel):
    """
    错误响应模型
    [schemas][base][error]
    """
    success: bool = Field(False, description="请求是否成功")
    message: str = Field(..., description="错误消息")
    error_code: Optional[str] = Field(None, description="错误码")
    error_detail: Optional[Any] = Field(None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.now, description="错误时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class HealthCheckSchema(BaseModel):
    """
    健康检查响应模型
    [schemas][base][health_check]
    """
    success: bool = Field(True, description="服务状态")
    message: str = Field("Service is healthy", description="状态消息")
    version: str = Field(..., description="API版本")
    timestamp: datetime = Field(default_factory=datetime.now, description="检查时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }