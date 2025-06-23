"""
Mixed Content Schemas
混合内容响应模型 - [schemas][mixed_content]
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal

# ==================== 混合内容基础信息 ====================

class MixedContentBasicSchema(BaseModel):
    """
    混合内容基础信息响应模型
    [schemas][mixed_content][basic]
    """
    content_id: int = Field(..., description="混合内容ID")
    content_name: str = Field(..., description="内容名称")
    content_description: Optional[str] = Field(None, description="内容描述")
    content_type: str = Field(..., description="内容类型")
    content_text_ids: Optional[List[int]] = Field(None, description="关联的文本内容ID数组")
    content_image_ids: Optional[List[int]] = Field(None, description="关联的图像内容ID数组")
    content_audio_ids: Optional[List[int]] = Field(None, description="关联的音频内容ID数组")
    content_video_ids: Optional[List[int]] = Field(None, description="关联的视频内容ID数组")
    content_output_file_id: Optional[int] = Field(None, description="输出文件ID")
    content_generation_params: Optional[dict] = Field(None, description="生成参数")
    content_layout_config: Optional[dict] = Field(None, description="布局配置")
    content_style_config: Optional[dict] = Field(None, description="样式配置")
    content_timing_config: Optional[dict] = Field(None, description="时序配置")
    content_created_user_id: int = Field(..., description="创建用户ID")
    content_created_time: datetime = Field(..., description="创建时间")
    content_updated_time: datetime = Field(..., description="更新时间")
    content_status: str = Field(..., description="状态")
    content_tags: Optional[List[str]] = Field(None, description="标签数组")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class MixedContentBasicCreateSchema(BaseModel):
    """
    混合内容创建请求模型
    [schemas][mixed_content][basic_create]
    """
    content_name: str = Field(..., max_length=100, description="内容名称")
    content_description: Optional[str] = Field(None, description="内容描述")
    content_type: str = Field(..., max_length=50, description="内容类型")
    content_text_ids: Optional[List[int]] = Field(None, description="关联的文本内容ID数组")
    content_image_ids: Optional[List[int]] = Field(None, description="关联的图像内容ID数组")
    content_audio_ids: Optional[List[int]] = Field(None, description="关联的音频内容ID数组")
    content_video_ids: Optional[List[int]] = Field(None, description="关联的视频内容ID数组")
    content_generation_params: Optional[dict] = Field(None, description="生成参数")
    content_layout_config: Optional[dict] = Field(None, description="布局配置")
    content_style_config: Optional[dict] = Field(None, description="样式配置")
    content_timing_config: Optional[dict] = Field(None, description="时序配置")
    content_tags: Optional[List[str]] = Field(None, description="标签数组")

class MixedContentBasicUpdateSchema(BaseModel):
    """
    混合内容更新请求模型
    [schemas][mixed_content][basic_update]
    """
    content_name: Optional[str] = Field(None, max_length=100, description="内容名称")
    content_description: Optional[str] = Field(None, description="内容描述")
    content_text_ids: Optional[List[int]] = Field(None, description="关联的文本内容ID数组")
    content_image_ids: Optional[List[int]] = Field(None, description="关联的图像内容ID数组")
    content_audio_ids: Optional[List[int]] = Field(None, description="关联的音频内容ID数组")
    content_video_ids: Optional[List[int]] = Field(None, description="关联的视频内容ID数组")
    content_generation_params: Optional[dict] = Field(None, description="生成参数")
    content_layout_config: Optional[dict] = Field(None, description="布局配置")
    content_style_config: Optional[dict] = Field(None, description="样式配置")
    content_timing_config: Optional[dict] = Field(None, description="时序配置")
    content_tags: Optional[List[str]] = Field(None, description="标签数组")

# ==================== 混合内容分析信息 ====================

class MixedContentAnalyseSchema(BaseModel):
    """
    混合内容分析信息响应模型
    [schemas][mixed_content][analyse]
    """
    analyse_id: int = Field(..., description="分析ID")
    content_id: int = Field(..., description="混合内容ID")
    analyse_type: str = Field(..., description="分析类型")
    analyse_result: Optional[dict] = Field(None, description="分析结果")
    analyse_summary: Optional[str] = Field(None, description="分析摘要")
    analyse_quality_score: Optional[Decimal] = Field(None, description="质量评分")
    analyse_confidence_score: Optional[Decimal] = Field(None, description="置信度评分")
    analyse_coherence_score: Optional[Decimal] = Field(None, description="连贯性评分")
    analyse_synchronization_score: Optional[Decimal] = Field(None, description="同步性评分")
    analyse_engagement_score: Optional[Decimal] = Field(None, description="参与度评分")
    analyse_effectiveness_score: Optional[Decimal] = Field(None, description="有效性评分")
    analyse_load_time: Optional[Decimal] = Field(None, description="加载时间(秒)")
    analyse_file_size: Optional[int] = Field(None, description="文件大小(字节)")
    analyse_compatibility_score: Optional[Decimal] = Field(None, description="兼容性评分")
    analyse_content_balance: Optional[dict] = Field(None, description="内容平衡分析")
    analyse_user_flow: Optional[dict] = Field(None, description="用户流程分析")
    analyse_accessibility: Optional[dict] = Field(None, description="可访问性分析")
    analyse_created_user_id: int = Field(..., description="创建用户ID")
    analyse_created_time: datetime = Field(..., description="创建时间")
    analyse_status: str = Field(..., description="分析状态")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v) if v else None
        }

class MixedContentAnalyseCreateSchema(BaseModel):
    """
    混合内容分析创建请求模型
    [schemas][mixed_content][analyse_create]
    """
    analyse_type: str = Field(..., max_length=50, description="分析类型")
    analyse_summary: Optional[str] = Field(None, description="分析摘要")

# ==================== 混合内容模板信息 ====================

class MixedContentTemplateSchema(BaseModel):
    """
    混合内容模板响应模型
    [schemas][mixed_content][template]
    """
    template_id: int = Field(..., description="模板ID")
    template_name: str = Field(..., description="模板名称")
    template_description: Optional[str] = Field(None, description="模板描述")
    template_type: str = Field(..., description="模板类型")
    template_category: Optional[str] = Field(None, description="模板分类")
    template_text_template_ids: Optional[dict] = Field(None, description="文本模板ID数组")
    template_image_template_ids: Optional[dict] = Field(None, description="图像模板ID数组")
    template_audio_template_ids: Optional[dict] = Field(None, description="音频模板ID数组")
    template_video_template_ids: Optional[dict] = Field(None, description="视频模板ID数组")
    template_layout_config: Optional[dict] = Field(None, description="布局配置模板")
    template_style_config: Optional[dict] = Field(None, description="样式配置模板")
    template_timing_config: Optional[dict] = Field(None, description="时序配置模板")
    template_interaction_config: Optional[dict] = Field(None, description="交互配置模板")
    template_generation_params: Optional[dict] = Field(None, description="生成参数配置")
    template_output_config: Optional[dict] = Field(None, description="输出配置")
    template_quality_config: Optional[dict] = Field(None, description="质量配置")
    template_default_content: Optional[dict] = Field(None, description="默认内容配置")
    template_placeholder_data: Optional[dict] = Field(None, description="占位符数据")
    template_created_user_id: int = Field(..., description="创建用户ID")
    template_created_time: datetime = Field(..., description="创建时间")
    template_status: str = Field(..., description="模板状态")
    template_usage_count: int = Field(..., description="使用次数")
    template_rating: Optional[int] = Field(None, description="模板评分")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class MixedContentTemplateCreateSchema(BaseModel):
    """
    混合内容模板创建请求模型
    [schemas][mixed_content][template_create]
    """
    template_name: str = Field(..., max_length=100, description="模板名称")
    template_description: Optional[str] = Field(None, description="模板描述")
    template_type: str = Field(..., max_length=50, description="模板类型")
    template_category: Optional[str] = Field(None, max_length=50, description="模板分类")
    template_text_template_ids: Optional[dict] = Field(None, description="文本模板ID数组")
    template_image_template_ids: Optional[dict] = Field(None, description="图像模板ID数组")
    template_audio_template_ids: Optional[dict] = Field(None, description="音频模板ID数组")
    template_video_template_ids: Optional[dict] = Field(None, description="视频模板ID数组")
    template_layout_config: Optional[dict] = Field(None, description="布局配置模板")
    template_style_config: Optional[dict] = Field(None, description="样式配置模板")
    template_timing_config: Optional[dict] = Field(None, description="时序配置模板")
    template_interaction_config: Optional[dict] = Field(None, description="交互配置模板")
    template_generation_params: Optional[dict] = Field(None, description="生成参数配置")
    template_output_config: Optional[dict] = Field(None, description="输出配置")
    template_quality_config: Optional[dict] = Field(None, description="质量配置")
    template_default_content: Optional[dict] = Field(None, description="默认内容配置")
    template_placeholder_data: Optional[dict] = Field(None, description="占位符数据")

# ==================== 混合内容生成相关 ====================

class MixedContentGenerationSchema(BaseModel):
    """
    混合内容生成请求模型
    [schemas][mixed_content][generation]
    """
    template_id: int = Field(..., description="模板ID")
    input_data: dict = Field(..., description="输入数据")
    generation_params: Optional[dict] = Field(None, description="生成参数")
    output_format: str = Field("html", description="输出格式")
    quality: str = Field("high", description="生成质量")

class MixedContentBatchGenerationSchema(BaseModel):
    """
    混合内容批量生成请求模型
    [schemas][mixed_content][batch_generation]
    """
    template_id: int = Field(..., description="模板ID")
    input_data_list: List[dict] = Field(..., min_items=1, max_items=10, description="输入数据列表")
    common_params: Optional[dict] = Field(None, description="通用参数")

# ==================== 混合内容导出相关 ====================

class MixedContentExportSchema(BaseModel):
    """
    混合内容导出请求模型
    [schemas][mixed_content][export]
    """
    export_format: str = Field(..., description="导出格式")
    export_params: Optional[dict] = Field(None, description="导出参数")
    include_assets: bool = Field(True, description="是否包含资源文件")

class MixedContentPublishSchema(BaseModel):
    """
    混合内容发布请求模型
    [schemas][mixed_content][publish]
    """
    platform: str = Field(..., description="发布平台")
    publish_params: Optional[dict] = Field(None, description="发布参数")
    schedule_time: Optional[datetime] = Field(None, description="定时发布时间")

# ==================== 混合内容统计信息 ====================

class MixedContentStatsSchema(BaseModel):
    """
    混合内容统计信息响应模型
    [schemas][mixed_content][stats]
    """
    total_contents: int = Field(..., description="内容总数")
    type_distribution: dict = Field(..., description="类型分布")
    template_usage: dict = Field(..., description="模板使用情况")
    component_distribution: dict = Field(..., description="组件分布")
    quality_distribution: dict = Field(..., description="质量分布")
    creation_trends: List[dict] = Field(..., description="创建趋势数据")
    popular_templates: List[dict] = Field(..., description="热门模板")

# ==================== 完整混合内容信息 ====================

class MixedContentCompleteSchema(BaseModel):
    """
    完整混合内容信息响应模型
    [schemas][mixed_content][complete]
    """
    content: MixedContentBasicSchema = Field(..., description="混合内容基础信息")
    template: Optional[MixedContentTemplateSchema] = Field(None, description="使用的模板")
    analyses: List[MixedContentAnalyseSchema] = Field([], description="分析结果列表")
    text_contents: List[dict] = Field([], description="关联的文本内容")
    image_contents: List[dict] = Field([], description="关联的图像内容")
    audio_contents: List[dict] = Field([], description="关联的音频内容")
    video_contents: List[dict] = Field([], description="关联的视频内容")
    preview_url: Optional[str] = Field(None, description="预览链接")
    download_url: Optional[str] = Field(None, description="下载链接")
    
    class Config:
        from_attributes = True