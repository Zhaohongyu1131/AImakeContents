"""
File Storage Schemas
文件存储响应模型 - [schemas][file_storage]
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

# ==================== 文件基础信息 ====================

class FileStorageBasicSchema(BaseModel):
    """
    文件基础信息响应模型
    [schemas][file_storage][basic]
    """
    file_id: int = Field(..., description="文件ID")
    file_name: str = Field(..., description="文件名称")
    file_original_name: str = Field(..., description="原始文件名")
    file_path: str = Field(..., description="文件路径")
    file_size: int = Field(..., description="文件大小(字节)")
    file_type: str = Field(..., description="文件类型")
    file_mime_type: Optional[str] = Field(None, description="MIME类型")
    file_extension: Optional[str] = Field(None, description="文件扩展名")
    file_hash: Optional[str] = Field(None, description="文件哈希值")
    file_upload_user_id: int = Field(..., description="上传用户ID")
    file_upload_time: datetime = Field(..., description="上传时间")
    file_access_count: int = Field(..., description="访问次数")
    file_last_access_time: Optional[datetime] = Field(None, description="最后访问时间")
    file_status: str = Field(..., description="文件状态")
    file_metadata: Optional[dict] = Field(None, description="文件元数据")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class FileStorageBasicCreateSchema(BaseModel):
    """
    文件上传请求模型
    [schemas][file_storage][basic_create]
    """
    file_name: str = Field(..., max_length=255, description="文件名称")
    file_type: str = Field(..., max_length=50, description="文件类型")
    file_metadata: Optional[dict] = Field(None, description="文件元数据")

class FileStorageBasicUpdateSchema(BaseModel):
    """
    文件信息更新请求模型
    [schemas][file_storage][basic_update]
    """
    file_name: Optional[str] = Field(None, max_length=255, description="文件名称")
    file_metadata: Optional[dict] = Field(None, description="文件元数据")

# ==================== 文件分析信息 ====================

class FileStorageAnalyseSchema(BaseModel):
    """
    文件分析信息响应模型
    [schemas][file_storage][analyse]
    """
    analyse_id: int = Field(..., description="分析ID")
    file_id: int = Field(..., description="文件ID")
    analyse_type: str = Field(..., description="分析类型")
    analyse_result: Optional[dict] = Field(None, description="分析结果")
    analyse_summary: Optional[str] = Field(None, description="分析摘要")
    analyse_quality_score: Optional[float] = Field(None, description="质量评分")
    analyse_confidence_score: Optional[float] = Field(None, description="置信度评分")
    analyse_created_user_id: int = Field(..., description="创建用户ID")
    analyse_created_time: datetime = Field(..., description="创建时间")
    analyse_status: str = Field(..., description="分析状态")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class FileStorageAnalyseCreateSchema(BaseModel):
    """
    文件分析创建请求模型
    [schemas][file_storage][analyse_create]
    """
    analyse_type: str = Field(..., max_length=50, description="分析类型")
    analyse_summary: Optional[str] = Field(None, description="分析摘要")

# ==================== 文件上传相关 ====================

class FileStorageUploadUrlSchema(BaseModel):
    """
    文件上传URL响应模型
    [schemas][file_storage][upload_url]
    """
    upload_url: str = Field(..., description="上传URL")
    file_id: int = Field(..., description="文件ID")
    expires_in: int = Field(..., description="URL过期时间(秒)")

class FileStorageDownloadUrlSchema(BaseModel):
    """
    文件下载URL响应模型
    [schemas][file_storage][download_url]
    """
    download_url: str = Field(..., description="下载URL")
    file_name: str = Field(..., description="文件名称")
    file_size: int = Field(..., description="文件大小")
    expires_in: int = Field(..., description="URL过期时间(秒)")

# ==================== 文件批量操作 ====================

class FileStorageBatchDeleteSchema(BaseModel):
    """
    文件批量删除请求模型
    [schemas][file_storage][batch_delete]
    """
    file_ids: List[int] = Field(..., min_items=1, description="文件ID列表")

class FileStorageBatchOperationResultSchema(BaseModel):
    """
    文件批量操作结果响应模型
    [schemas][file_storage][batch_operation_result]
    """
    success_count: int = Field(..., description="成功数量")
    failed_count: int = Field(..., description="失败数量")
    success_ids: List[int] = Field(..., description="成功的文件ID列表")
    failed_ids: List[int] = Field(..., description="失败的文件ID列表")
    failed_reasons: dict = Field(..., description="失败原因映射")

# ==================== 文件统计信息 ====================

class FileStorageStatsSchema(BaseModel):
    """
    文件存储统计信息响应模型
    [schemas][file_storage][stats]
    """
    total_files: int = Field(..., description="文件总数")
    total_size: int = Field(..., description="总存储大小(字节)")
    file_types: dict = Field(..., description="文件类型分布")
    upload_trends: List[dict] = Field(..., description="上传趋势数据")
    storage_usage: dict = Field(..., description="存储使用情况")

# ==================== 完整文件信息 ====================

class FileStorageCompleteSchema(BaseModel):
    """
    完整文件信息响应模型
    [schemas][file_storage][complete]
    """
    file: FileStorageBasicSchema = Field(..., description="文件基础信息")
    analyses: List[FileStorageAnalyseSchema] = Field([], description="文件分析列表")
    download_url: Optional[str] = Field(None, description="下载链接")
    
    class Config:
        from_attributes = True