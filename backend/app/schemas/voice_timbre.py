"""
Voice Timbre Schemas
音色管理响应模型 - [schemas][voice_timbre]
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal

# ==================== 音色基础信息 ====================

class VoiceTimbreBasicSchema(BaseModel):
    """
    音色基础信息响应模型
    [schemas][voice_timbre][basic]
    """
    timbre_id: int = Field(..., description="音色ID")
    timbre_name: str = Field(..., description="音色名称")
    timbre_description: Optional[str] = Field(None, description="音色描述")
    timbre_source_file_id: Optional[int] = Field(None, description="克隆源音频文件ID")
    timbre_platform_id: Optional[str] = Field(None, description="第三方平台音色ID")
    timbre_platform: str = Field(..., description="平台名称")
    timbre_language: str = Field(..., description="语言")
    timbre_gender: Optional[str] = Field(None, description="性别")
    timbre_age_range: Optional[str] = Field(None, description="年龄范围")
    timbre_style: Optional[str] = Field(None, description="音色风格")
    timbre_quality_score: Optional[Decimal] = Field(None, description="音色质量评分")
    timbre_created_user_id: int = Field(..., description="创建用户ID")
    timbre_created_time: datetime = Field(..., description="创建时间")
    timbre_updated_time: datetime = Field(..., description="更新时间")
    timbre_status: str = Field(..., description="状态")
    timbre_tags: Optional[List[str]] = Field(None, description="标签数组")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v) if v else None
        }

class VoiceTimbreBasicCreateSchema(BaseModel):
    """
    音色创建请求模型
    [schemas][voice_timbre][basic_create]
    """
    timbre_name: str = Field(..., max_length=100, description="音色名称")
    timbre_description: Optional[str] = Field(None, description="音色描述")
    timbre_source_file_id: Optional[int] = Field(None, description="克隆源音频文件ID")
    timbre_platform: str = Field("volcano", max_length=50, description="平台名称")
    timbre_language: str = Field("zh-CN", max_length=10, description="语言")
    timbre_gender: Optional[str] = Field(None, max_length=10, description="性别")
    timbre_age_range: Optional[str] = Field(None, max_length=20, description="年龄范围")
    timbre_style: Optional[str] = Field(None, max_length=50, description="音色风格")
    timbre_tags: Optional[List[str]] = Field(None, description="标签数组")

class VoiceTimbreBasicUpdateSchema(BaseModel):
    """
    音色更新请求模型
    [schemas][voice_timbre][basic_update]
    """
    timbre_name: Optional[str] = Field(None, max_length=100, description="音色名称")
    timbre_description: Optional[str] = Field(None, description="音色描述")
    timbre_gender: Optional[str] = Field(None, max_length=10, description="性别")
    timbre_age_range: Optional[str] = Field(None, max_length=20, description="年龄范围")
    timbre_style: Optional[str] = Field(None, max_length=50, description="音色风格")
    timbre_tags: Optional[List[str]] = Field(None, description="标签数组")

# ==================== 音色克隆信息 ====================

class VoiceTimbreCloneSchema(BaseModel):
    """
    音色克隆记录响应模型
    [schemas][voice_timbre][clone]
    """
    clone_id: int = Field(..., description="克隆记录ID")
    timbre_id: int = Field(..., description="音色ID")
    clone_source_file_id: int = Field(..., description="源音频文件ID")
    clone_source_duration: Optional[Decimal] = Field(None, description="源音频时长(秒)")
    clone_training_params: Optional[dict] = Field(None, description="训练参数")
    clone_progress: int = Field(..., description="训练进度百分比")
    clone_created_user_id: int = Field(..., description="创建用户ID")
    clone_created_time: datetime = Field(..., description="创建时间")
    clone_completed_time: Optional[datetime] = Field(None, description="完成时间")
    clone_status: str = Field(..., description="克隆状态")
    clone_error_message: Optional[str] = Field(None, description="错误信息")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v) if v else None
        }

class VoiceTimbreCloneCreateSchema(BaseModel):
    """
    音色克隆创建请求模型
    [schemas][voice_timbre][clone_create]
    """
    timbre_id: int = Field(..., description="音色ID")
    clone_source_file_id: int = Field(..., description="源音频文件ID")
    clone_training_params: Optional[dict] = Field(None, description="训练参数")

# ==================== 音色模板信息 ====================

class VoiceTimbreTemplateSchema(BaseModel):
    """
    音色模板响应模型
    [schemas][voice_timbre][template]
    """
    template_id: int = Field(..., description="模板ID")
    template_name: str = Field(..., description="模板名称")
    template_description: Optional[str] = Field(None, description="模板描述")
    template_timbre_id: Optional[int] = Field(None, description="音色ID")
    template_clone_params: Optional[dict] = Field(None, description="克隆参数配置")
    template_quality_requirements: Optional[dict] = Field(None, description="质量要求")
    template_created_user_id: int = Field(..., description="创建用户ID")
    template_created_time: datetime = Field(..., description="创建时间")
    template_status: str = Field(..., description="模板状态")
    template_usage_count: int = Field(..., description="使用次数")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class VoiceTimbreTemplateCreateSchema(BaseModel):
    """
    音色模板创建请求模型
    [schemas][voice_timbre][template_create]
    """
    template_name: str = Field(..., max_length=100, description="模板名称")
    template_description: Optional[str] = Field(None, description="模板描述")
    template_timbre_id: Optional[int] = Field(None, description="音色ID")
    template_clone_params: Optional[dict] = Field(None, description="克隆参数配置")
    template_quality_requirements: Optional[dict] = Field(None, description="质量要求")

class VoiceTimbreTemplateUpdateSchema(BaseModel):
    """
    音色模板更新请求模型
    [schemas][voice_timbre][template_update]
    """
    template_name: Optional[str] = Field(None, max_length=100, description="模板名称")
    template_description: Optional[str] = Field(None, description="模板描述")
    template_clone_params: Optional[dict] = Field(None, description="克隆参数配置")
    template_quality_requirements: Optional[dict] = Field(None, description="质量要求")

# ==================== 音色克隆相关 ====================

class VoiceTimbreCloneRequestSchema(BaseModel):
    """
    音色克隆请求模型
    [schemas][voice_timbre][clone_request]
    """
    timbre_name: str = Field(..., max_length=100, description="音色名称")
    timbre_description: Optional[str] = Field(None, description="音色描述")
    source_file_id: int = Field(..., description="源音频文件ID")
    clone_params: Optional[dict] = Field(None, description="克隆参数")
    target_platform: str = Field("volcano", description="目标平台")

class VoiceTimbreTestSchema(BaseModel):
    """
    音色测试请求模型
    [schemas][voice_timbre][test]
    """
    test_text: str = Field(..., min_length=1, max_length=500, description="测试文本")
    synthesis_params: Optional[dict] = Field(None, description="合成参数")

# ==================== 音色搜索过滤 ====================

class VoiceTimbreFilterSchema(BaseModel):
    """
    音色过滤请求模型
    [schemas][voice_timbre][filter]
    """
    platform: Optional[str] = Field(None, description="平台筛选")
    gender: Optional[str] = Field(None, description="性别筛选")
    language: Optional[str] = Field(None, description="语言筛选")
    style: Optional[str] = Field(None, description="风格筛选")
    quality_min: Optional[float] = Field(None, ge=0, le=100, description="最低质量评分")
    tags: Optional[List[str]] = Field(None, description="标签筛选")
    status: Optional[str] = Field(None, description="状态筛选")

# ==================== 音色统计信息 ====================

class VoiceTimbreStatsSchema(BaseModel):
    """
    音色统计信息响应模型
    [schemas][voice_timbre][stats]
    """
    total_timbres: int = Field(..., description="音色总数")
    platform_distribution: dict = Field(..., description="平台分布")
    gender_distribution: dict = Field(..., description="性别分布")
    language_distribution: dict = Field(..., description="语言分布")
    quality_distribution: dict = Field(..., description="质量分布")
    clone_success_rate: float = Field(..., description="克隆成功率")
    popular_styles: List[dict] = Field(..., description="热门风格")

# ==================== 完整音色信息 ====================

class VoiceTimbreCompleteSchema(BaseModel):
    """
    完整音色信息响应模型
    [schemas][voice_timbre][complete]
    """
    timbre: VoiceTimbreBasicSchema = Field(..., description="音色基础信息")
    clone_records: List[VoiceTimbreCloneSchema] = Field([], description="克隆记录列表")
    templates: List[VoiceTimbreTemplateSchema] = Field([], description="相关模板列表")
    test_audio_url: Optional[str] = Field(None, description="测试音频链接")
    
    class Config:
        from_attributes = True