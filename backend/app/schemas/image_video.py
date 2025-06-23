"""
Image Video Schemas
图像视频响应模型 - [schemas][image_video]
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal

# ==================== 图像基础信息 ====================

class ImageBasicSchema(BaseModel):
    """
    图像基础信息响应模型
    [schemas][image][basic]
    """
    image_id: int = Field(..., description="图像ID")
    image_name: str = Field(..., description="图像名称")
    image_description: Optional[str] = Field(None, description="图像描述")
    image_file_id: int = Field(..., description="图像文件ID")
    image_width: Optional[int] = Field(None, description="图像宽度")
    image_height: Optional[int] = Field(None, description="图像高度")
    image_format: Optional[str] = Field(None, description="图像格式")
    image_source_text_id: Optional[int] = Field(None, description="源文本ID")
    image_generation_params: Optional[dict] = Field(None, description="生成参数")
    image_prompt: Optional[str] = Field(None, description="生成提示词")
    image_negative_prompt: Optional[str] = Field(None, description="负向提示词")
    image_platform: str = Field(..., description="平台名称")
    image_platform_task_id: Optional[str] = Field(None, description="平台任务ID")
    image_model_name: Optional[str] = Field(None, description="使用的模型名称")
    image_created_user_id: int = Field(..., description="创建用户ID")
    image_created_time: datetime = Field(..., description="创建时间")
    image_updated_time: datetime = Field(..., description="更新时间")
    image_status: str = Field(..., description="状态")
    image_tags: Optional[List[str]] = Field(None, description="标签数组")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ImageBasicCreateSchema(BaseModel):
    """
    图像创建请求模型
    [schemas][image][basic_create]
    """
    image_name: str = Field(..., max_length=100, description="图像名称")
    image_description: Optional[str] = Field(None, description="图像描述")
    image_source_text_id: Optional[int] = Field(None, description="源文本ID")
    image_generation_params: Optional[dict] = Field(None, description="生成参数")
    image_prompt: Optional[str] = Field(None, description="生成提示词")
    image_negative_prompt: Optional[str] = Field(None, description="负向提示词")
    image_platform: str = Field("local", max_length=50, description="平台名称")
    image_model_name: Optional[str] = Field(None, max_length=100, description="使用的模型名称")
    image_tags: Optional[List[str]] = Field(None, description="标签数组")

# ==================== 图像分析信息 ====================

class ImageAnalyseSchema(BaseModel):
    """
    图像分析信息响应模型
    [schemas][image][analyse]
    """
    analyse_id: int = Field(..., description="分析ID")
    image_id: int = Field(..., description="图像ID")
    analyse_type: str = Field(..., description="分析类型")
    analyse_result: Optional[dict] = Field(None, description="分析结果")
    analyse_summary: Optional[str] = Field(None, description="分析摘要")
    analyse_quality_score: Optional[Decimal] = Field(None, description="质量评分")
    analyse_confidence_score: Optional[Decimal] = Field(None, description="置信度评分")
    analyse_brightness: Optional[Decimal] = Field(None, description="亮度")
    analyse_contrast: Optional[Decimal] = Field(None, description="对比度")
    analyse_saturation: Optional[Decimal] = Field(None, description="饱和度")
    analyse_sharpness: Optional[Decimal] = Field(None, description="清晰度")
    analyse_objects_detected: Optional[dict] = Field(None, description="检测到的对象")
    analyse_faces_count: Optional[int] = Field(None, description="人脸数量")
    analyse_text_content: Optional[str] = Field(None, description="图像中的文本内容")
    analyse_dominant_colors: Optional[dict] = Field(None, description="主要颜色")
    analyse_emotion_data: Optional[dict] = Field(None, description="情感分析数据")
    analyse_style_tags: Optional[dict] = Field(None, description="风格标签")
    analyse_created_user_id: int = Field(..., description="创建用户ID")
    analyse_created_time: datetime = Field(..., description="创建时间")
    analyse_status: str = Field(..., description="分析状态")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v) if v else None
        }

# ==================== 图像模板信息 ====================

class ImageTemplateSchema(BaseModel):
    """
    图像模板响应模型
    [schemas][image][template]
    """
    template_id: int = Field(..., description="模板ID")
    template_name: str = Field(..., description="模板名称")
    template_description: Optional[str] = Field(None, description="模板描述")
    template_type: str = Field(..., description="模板类型")
    template_text_template_id: Optional[int] = Field(None, description="文本模板ID")
    template_generation_params: Optional[dict] = Field(None, description="生成参数配置")
    template_prompt_template: Optional[str] = Field(None, description="提示词模板")
    template_negative_prompt: Optional[str] = Field(None, description="负向提示词")
    template_style_presets: Optional[dict] = Field(None, description="风格预设")
    template_output_width: Optional[int] = Field(None, description="输出宽度")
    template_output_height: Optional[int] = Field(None, description="输出高度")
    template_output_format: str = Field(..., description="输出格式")
    template_quality_level: str = Field(..., description="质量级别")
    template_platform: str = Field(..., description="平台名称")
    template_model_name: Optional[str] = Field(None, description="模型名称")
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

# ==================== 视频基础信息 ====================

class VideoBasicSchema(BaseModel):
    """
    视频基础信息响应模型
    [schemas][video][basic]
    """
    video_id: int = Field(..., description="视频ID")
    video_name: str = Field(..., description="视频名称")
    video_description: Optional[str] = Field(None, description="视频描述")
    video_file_id: int = Field(..., description="视频文件ID")
    video_duration: Optional[Decimal] = Field(None, description="视频时长(秒)")
    video_width: Optional[int] = Field(None, description="视频宽度")
    video_height: Optional[int] = Field(None, description="视频高度")
    video_format: Optional[str] = Field(None, description="视频格式")
    video_fps: Optional[Decimal] = Field(None, description="帧率")
    video_bitrate: Optional[int] = Field(None, description="比特率")
    video_source_text_id: Optional[int] = Field(None, description="源文本ID")
    video_source_image_id: Optional[int] = Field(None, description="源图像ID")
    video_source_audio_id: Optional[int] = Field(None, description="源音频ID")
    video_generation_params: Optional[dict] = Field(None, description="生成参数")
    video_platform: str = Field(..., description="平台名称")
    video_platform_task_id: Optional[str] = Field(None, description="平台任务ID")
    video_model_name: Optional[str] = Field(None, description="使用的模型名称")
    video_created_user_id: int = Field(..., description="创建用户ID")
    video_created_time: datetime = Field(..., description="创建时间")
    video_updated_time: datetime = Field(..., description="更新时间")
    video_status: str = Field(..., description="状态")
    video_tags: Optional[List[str]] = Field(None, description="标签数组")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v) if v else None
        }

class VideoBasicCreateSchema(BaseModel):
    """
    视频创建请求模型
    [schemas][video][basic_create]
    """
    video_name: str = Field(..., max_length=100, description="视频名称")
    video_description: Optional[str] = Field(None, description="视频描述")
    video_source_text_id: Optional[int] = Field(None, description="源文本ID")
    video_source_image_id: Optional[int] = Field(None, description="源图像ID")
    video_source_audio_id: Optional[int] = Field(None, description="源音频ID")
    video_generation_params: Optional[dict] = Field(None, description="生成参数")
    video_platform: str = Field("local", max_length=50, description="平台名称")
    video_model_name: Optional[str] = Field(None, max_length=100, description="使用的模型名称")
    video_tags: Optional[List[str]] = Field(None, description="标签数组")

# ==================== 视频分析信息 ====================

class VideoAnalyseSchema(BaseModel):
    """
    视频分析信息响应模型
    [schemas][video][analyse]
    """
    analyse_id: int = Field(..., description="分析ID")
    video_id: int = Field(..., description="视频ID")
    analyse_type: str = Field(..., description="分析类型")
    analyse_result: Optional[dict] = Field(None, description="分析结果")
    analyse_summary: Optional[str] = Field(None, description="分析摘要")
    analyse_quality_score: Optional[Decimal] = Field(None, description="质量评分")
    analyse_confidence_score: Optional[Decimal] = Field(None, description="置信度评分")
    analyse_frame_quality: Optional[Decimal] = Field(None, description="帧质量评分")
    analyse_motion_smoothness: Optional[Decimal] = Field(None, description="运动平滑度")
    analyse_color_consistency: Optional[Decimal] = Field(None, description="颜色一致性")
    analyse_audio_sync: Optional[Decimal] = Field(None, description="音画同步评分")
    analyse_scene_changes: Optional[int] = Field(None, description="场景变化次数")
    analyse_objects_detected: Optional[dict] = Field(None, description="检测到的对象")
    analyse_faces_detected: Optional[dict] = Field(None, description="检测到的人脸")
    analyse_text_content: Optional[str] = Field(None, description="视频中的文本内容")
    analyse_emotion_timeline: Optional[dict] = Field(None, description="情感时间线")
    analyse_activity_level: Optional[Decimal] = Field(None, description="活动水平")
    analyse_content_tags: Optional[dict] = Field(None, description="内容标签")
    analyse_created_user_id: int = Field(..., description="创建用户ID")
    analyse_created_time: datetime = Field(..., description="创建时间")
    analyse_status: str = Field(..., description="分析状态")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v) if v else None
        }

# ==================== 视频模板信息 ====================

class VideoTemplateSchema(BaseModel):
    """
    视频模板响应模型
    [schemas][video][template]
    """
    template_id: int = Field(..., description="模板ID")
    template_name: str = Field(..., description="模板名称")
    template_description: Optional[str] = Field(None, description="模板描述")
    template_type: str = Field(..., description="模板类型")
    template_text_template_id: Optional[int] = Field(None, description="文本模板ID")
    template_image_template_id: Optional[int] = Field(None, description="图像模板ID")
    template_audio_template_id: Optional[int] = Field(None, description="音频模板ID")
    template_generation_params: Optional[dict] = Field(None, description="生成参数配置")
    template_prompt_template: Optional[str] = Field(None, description="提示词模板")
    template_style_presets: Optional[dict] = Field(None, description="风格预设")
    template_output_width: Optional[int] = Field(None, description="输出宽度")
    template_output_height: Optional[int] = Field(None, description="输出高度")
    template_output_fps: Optional[Decimal] = Field(None, description="输出帧率")
    template_output_duration: Optional[Decimal] = Field(None, description="输出时长(秒)")
    template_output_format: str = Field(..., description="输出格式")
    template_quality_level: str = Field(..., description="质量级别")
    template_platform: str = Field(..., description="平台名称")
    template_model_name: Optional[str] = Field(None, description="模型名称")
    template_platform_params: Optional[dict] = Field(None, description="平台特定参数")
    template_created_user_id: int = Field(..., description="创建用户ID")
    template_created_time: datetime = Field(..., description="创建时间")
    template_status: str = Field(..., description="模板状态")
    template_usage_count: int = Field(..., description="使用次数")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v) if v else None
        }

# ==================== 图像生成相关 ====================

class ImageGenerationSchema(BaseModel):
    """
    图像生成请求模型
    [schemas][image][generation]
    """
    prompt: str = Field(..., min_length=1, description="生成提示词")
    negative_prompt: Optional[str] = Field(None, description="负向提示词")
    width: Optional[int] = Field(None, ge=64, le=2048, description="图像宽度")
    height: Optional[int] = Field(None, ge=64, le=2048, description="图像高度")
    style: Optional[str] = Field(None, description="艺术风格")
    quality: str = Field("high", description="生成质量")
    template_id: Optional[int] = Field(None, description="使用的模板ID")
    generation_params: Optional[dict] = Field(None, description="生成参数")

# ==================== 视频生成相关 ====================

class VideoGenerationSchema(BaseModel):
    """
    视频生成请求模型
    [schemas][video][generation]
    """
    prompt: Optional[str] = Field(None, description="生成提示词")
    source_image_id: Optional[int] = Field(None, description="源图像ID")
    source_audio_id: Optional[int] = Field(None, description="源音频ID")
    duration: Optional[float] = Field(None, ge=1, le=60, description="视频时长(秒)")
    fps: Optional[float] = Field(None, ge=12, le=60, description="帧率")
    quality: str = Field("high", description="生成质量")
    template_id: Optional[int] = Field(None, description="使用的模板ID")
    generation_params: Optional[dict] = Field(None, description="生成参数")

# ==================== 统计信息 ====================

class ImageVideoStatsSchema(BaseModel):
    """
    图像视频统计信息响应模型
    [schemas][image_video][stats]
    """
    total_images: int = Field(..., description="图像总数")
    total_videos: int = Field(..., description="视频总数")
    platform_distribution: dict = Field(..., description="平台分布")
    format_distribution: dict = Field(..., description="格式分布")
    quality_distribution: dict = Field(..., description="质量分布")
    generation_trends: List[dict] = Field(..., description="生成趋势数据")
    popular_styles: List[dict] = Field(..., description="热门风格")