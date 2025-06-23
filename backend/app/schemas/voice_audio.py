"""
Voice Audio Schemas
音频管理响应模型 - [schemas][voice_audio]
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal

# ==================== 音频基础信息 ====================

class VoiceAudioBasicSchema(BaseModel):
    """
    音频基础信息响应模型
    [schemas][voice_audio][basic]
    """
    audio_id: int = Field(..., description="音频ID")
    audio_name: str = Field(..., description="音频名称")
    audio_description: Optional[str] = Field(None, description="音频描述")
    audio_file_id: int = Field(..., description="音频文件ID")
    audio_duration: Optional[Decimal] = Field(None, description="音频时长(秒)")
    audio_format: Optional[str] = Field(None, description="音频格式")
    audio_sample_rate: Optional[int] = Field(None, description="采样率")
    audio_bitrate: Optional[int] = Field(None, description="比特率")
    audio_source_text_id: Optional[int] = Field(None, description="源文本ID")
    audio_timbre_id: Optional[int] = Field(None, description="音色ID")
    audio_synthesis_params: Optional[dict] = Field(None, description="合成参数")
    audio_platform: str = Field(..., description="平台名称")
    audio_platform_task_id: Optional[str] = Field(None, description="平台任务ID")
    audio_created_user_id: int = Field(..., description="创建用户ID")
    audio_created_time: datetime = Field(..., description="创建时间")
    audio_updated_time: datetime = Field(..., description="更新时间")
    audio_status: str = Field(..., description="状态")
    audio_tags: Optional[List[str]] = Field(None, description="标签数组")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v) if v else None
        }

class VoiceAudioBasicCreateSchema(BaseModel):
    """
    音频创建请求模型
    [schemas][voice_audio][basic_create]
    """
    audio_name: str = Field(..., max_length=100, description="音频名称")
    audio_description: Optional[str] = Field(None, description="音频描述")
    audio_source_text_id: Optional[int] = Field(None, description="源文本ID")
    audio_timbre_id: Optional[int] = Field(None, description="音色ID")
    audio_synthesis_params: Optional[dict] = Field(None, description="合成参数")
    audio_platform: str = Field("volcano", max_length=50, description="平台名称")
    audio_tags: Optional[List[str]] = Field(None, description="标签数组")

class VoiceAudioBasicUpdateSchema(BaseModel):
    """
    音频更新请求模型
    [schemas][voice_audio][basic_update]
    """
    audio_name: Optional[str] = Field(None, max_length=100, description="音频名称")
    audio_description: Optional[str] = Field(None, description="音频描述")
    audio_synthesis_params: Optional[dict] = Field(None, description="合成参数")
    audio_tags: Optional[List[str]] = Field(None, description="标签数组")

# ==================== 音频分析信息 ====================

class VoiceAudioAnalyseSchema(BaseModel):
    """
    音频分析信息响应模型
    [schemas][voice_audio][analyse]
    """
    analyse_id: int = Field(..., description="分析ID")
    audio_id: int = Field(..., description="音频ID")
    analyse_type: str = Field(..., description="分析类型")
    analyse_result: Optional[dict] = Field(None, description="分析结果")
    analyse_summary: Optional[str] = Field(None, description="分析摘要")
    analyse_quality_score: Optional[Decimal] = Field(None, description="质量评分")
    analyse_confidence_score: Optional[Decimal] = Field(None, description="置信度评分")
    analyse_volume_level: Optional[Decimal] = Field(None, description="音量水平")
    analyse_noise_level: Optional[Decimal] = Field(None, description="噪音水平")
    analyse_clarity_score: Optional[Decimal] = Field(None, description="清晰度评分")
    analyse_speech_rate: Optional[Decimal] = Field(None, description="语速(字/分钟)")
    analyse_pause_count: Optional[int] = Field(None, description="停顿次数")
    analyse_emotion_data: Optional[dict] = Field(None, description="情感分析数据")
    analyse_created_user_id: int = Field(..., description="创建用户ID")
    analyse_created_time: datetime = Field(..., description="创建时间")
    analyse_status: str = Field(..., description="分析状态")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v) if v else None
        }

class VoiceAudioAnalyseCreateSchema(BaseModel):
    """
    音频分析创建请求模型
    [schemas][voice_audio][analyse_create]
    """
    analyse_type: str = Field(..., max_length=50, description="分析类型")
    analyse_summary: Optional[str] = Field(None, description="分析摘要")

# ==================== 音频模板信息 ====================

class VoiceAudioTemplateSchema(BaseModel):
    """
    音频模板响应模型
    [schemas][voice_audio][template]
    """
    template_id: int = Field(..., description="模板ID")
    template_name: str = Field(..., description="模板名称")
    template_description: Optional[str] = Field(None, description="模板描述")
    template_type: str = Field(..., description="模板类型")
    template_timbre_id: Optional[int] = Field(None, description="音色ID")
    template_text_template_id: Optional[int] = Field(None, description="文本模板ID")
    template_synthesis_params: Optional[dict] = Field(None, description="合成参数配置")
    template_output_format: str = Field(..., description="输出格式")
    template_sample_rate: Optional[int] = Field(None, description="采样率")
    template_bitrate: Optional[int] = Field(None, description="比特率")
    template_platform: str = Field(..., description="平台名称")
    template_platform_params: Optional[dict] = Field(None, description="平台特定参数")
    template_created_user_id: int = Field(..., description="创建用户ID")
    template_created_time: datetime = Field(..., description="创建时间")
    template_status: str = Field(..., description="模板状态")
    template_usage_count: int = Field(..., description="使用次数")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class VoiceAudioTemplateCreateSchema(BaseModel):
    """
    音频模板创建请求模型
    [schemas][voice_audio][template_create]
    """
    template_name: str = Field(..., max_length=100, description="模板名称")
    template_description: Optional[str] = Field(None, description="模板描述")
    template_type: str = Field(..., max_length=50, description="模板类型")
    template_timbre_id: Optional[int] = Field(None, description="音色ID")
    template_text_template_id: Optional[int] = Field(None, description="文本模板ID")
    template_synthesis_params: Optional[dict] = Field(None, description="合成参数配置")
    template_output_format: str = Field("mp3", max_length=20, description="输出格式")
    template_sample_rate: Optional[int] = Field(None, description="采样率")
    template_bitrate: Optional[int] = Field(None, description="比特率")
    template_platform: str = Field("volcano", max_length=50, description="平台名称")
    template_platform_params: Optional[dict] = Field(None, description="平台特定参数")

# ==================== 音频合成相关 ====================

class VoiceAudioSynthesisSchema(BaseModel):
    """
    音频合成请求模型
    [schemas][voice_audio][synthesis]
    """
    source_text: str = Field(..., min_length=1, description="源文本内容")
    timbre_id: int = Field(..., description="音色ID")
    template_id: Optional[int] = Field(None, description="模板ID")
    synthesis_params: Optional[dict] = Field(None, description="合成参数")
    output_format: str = Field("mp3", description="输出格式")
    sample_rate: Optional[int] = Field(None, description="采样率")
    speed: Optional[float] = Field(None, ge=0.5, le=2.0, description="语速倍率")
    pitch: Optional[float] = Field(None, ge=0.5, le=2.0, description="音调倍率")
    volume: Optional[float] = Field(None, ge=0.1, le=2.0, description="音量倍率")

class VoiceAudioBatchSynthesisSchema(BaseModel):
    """
    音频批量合成请求模型
    [schemas][voice_audio][batch_synthesis]
    """
    text_list: List[str] = Field(..., min_items=1, max_items=10, description="文本列表")
    timbre_id: int = Field(..., description="音色ID")
    template_id: Optional[int] = Field(None, description="模板ID")
    common_params: Optional[dict] = Field(None, description="通用参数")

# ==================== 音频处理相关 ====================

class VoiceAudioProcessSchema(BaseModel):
    """
    音频处理请求模型
    [schemas][voice_audio][process]
    """
    process_type: str = Field(..., description="处理类型")
    process_params: Optional[dict] = Field(None, description="处理参数")

class VoiceAudioMergeSchema(BaseModel):
    """
    音频合并请求模型
    [schemas][voice_audio][merge]
    """
    audio_ids: List[int] = Field(..., min_items=2, description="音频ID列表")
    merge_params: Optional[dict] = Field(None, description="合并参数")
    output_name: str = Field(..., description="输出文件名")

# ==================== 音频统计信息 ====================

class VoiceAudioStatsSchema(BaseModel):
    """
    音频统计信息响应模型
    [schemas][voice_audio][stats]
    """
    total_audios: int = Field(..., description="音频总数")
    total_duration: float = Field(..., description="总时长(秒)")
    platform_distribution: dict = Field(..., description="平台分布")
    format_distribution: dict = Field(..., description="格式分布")
    quality_distribution: dict = Field(..., description="质量分布")
    synthesis_trends: List[dict] = Field(..., description="合成趋势数据")
    popular_timbres: List[dict] = Field(..., description="热门音色")

# ==================== 完整音频信息 ====================

class VoiceAudioCompleteSchema(BaseModel):
    """
    完整音频信息响应模型
    [schemas][voice_audio][complete]
    """
    audio: VoiceAudioBasicSchema = Field(..., description="音频基础信息")
    analyses: List[VoiceAudioAnalyseSchema] = Field([], description="分析结果列表")
    download_url: Optional[str] = Field(None, description="下载链接")
    waveform_data: Optional[dict] = Field(None, description="波形数据")
    
    class Config:
        from_attributes = True