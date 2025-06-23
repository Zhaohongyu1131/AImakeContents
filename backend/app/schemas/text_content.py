"""
Text Content Schemas
文本内容响应模型 - [schemas][text_content]
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

# ==================== 文本内容基础信息 ====================

class TextContentBasicSchema(BaseModel):
    """
    文本内容基础信息响应模型
    [schemas][text_content][basic]
    """
    content_id: int = Field(..., description="内容ID")
    content_title: str = Field(..., description="内容标题")
    content_text: str = Field(..., description="文本内容")
    content_type: str = Field(..., description="内容类型")
    content_language: str = Field(..., description="内容语言")
    content_word_count: Optional[int] = Field(None, description="字数统计")
    content_template_id: Optional[int] = Field(None, description="模板ID")
    content_source_prompt: Optional[str] = Field(None, description="生成提示词")
    content_generation_params: Optional[dict] = Field(None, description="生成参数")
    content_created_user_id: int = Field(..., description="创建用户ID")
    content_created_time: datetime = Field(..., description="创建时间")
    content_updated_time: datetime = Field(..., description="更新时间")
    content_status: str = Field(..., description="内容状态")
    content_tags: Optional[List[str]] = Field(None, description="标签列表")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TextContentBasicCreateSchema(BaseModel):
    """
    文本内容创建请求模型
    [schemas][text_content][basic_create]
    """
    content_title: str = Field(..., max_length=200, description="内容标题")
    content_text: str = Field(..., min_length=1, description="文本内容")
    content_type: str = Field(..., max_length=50, description="内容类型")
    content_language: str = Field("zh-CN", max_length=10, description="内容语言")
    content_template_id: Optional[int] = Field(None, description="模板ID")
    content_source_prompt: Optional[str] = Field(None, description="生成提示词")
    content_generation_params: Optional[dict] = Field(None, description="生成参数")
    content_tags: Optional[List[str]] = Field(None, description="标签列表")

class TextContentBasicUpdateSchema(BaseModel):
    """
    文本内容更新请求模型
    [schemas][text_content][basic_update]
    """
    content_title: Optional[str] = Field(None, max_length=200, description="内容标题")
    content_text: Optional[str] = Field(None, min_length=1, description="文本内容")
    content_type: Optional[str] = Field(None, max_length=50, description="内容类型")
    content_language: Optional[str] = Field(None, max_length=10, description="内容语言")
    content_source_prompt: Optional[str] = Field(None, description="生成提示词")
    content_generation_params: Optional[dict] = Field(None, description="生成参数")
    content_tags: Optional[List[str]] = Field(None, description="标签列表")

# ==================== 文本内容分析信息 ====================

class TextContentAnalyseSchema(BaseModel):
    """
    文本内容分析信息响应模型
    [schemas][text_content][analyse]
    """
    analyse_id: int = Field(..., description="分析ID")
    content_id: int = Field(..., description="内容ID")
    analyse_type: str = Field(..., description="分析类型")
    analyse_result: Optional[dict] = Field(None, description="分析结果")
    analyse_summary: Optional[str] = Field(None, description="分析摘要")
    analyse_sentiment_score: Optional[float] = Field(None, description="情感评分")
    analyse_readability_score: Optional[float] = Field(None, description="可读性评分")
    analyse_quality_score: Optional[float] = Field(None, description="质量评分")
    analyse_keywords: Optional[List[str]] = Field(None, description="关键词列表")
    analyse_topics: Optional[List[str]] = Field(None, description="话题列表")
    analyse_created_user_id: int = Field(..., description="创建用户ID")
    analyse_created_time: datetime = Field(..., description="创建时间")
    analyse_status: str = Field(..., description="分析状态")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TextContentAnalyseCreateSchema(BaseModel):
    """
    文本内容分析创建请求模型
    [schemas][text_content][analyse_create]
    """
    analyse_type: str = Field(..., max_length=50, description="分析类型")
    analyse_summary: Optional[str] = Field(None, description="分析摘要")

# ==================== 文本模板信息 ====================

class TextTemplateBasicSchema(BaseModel):
    """
    文本模板基础信息响应模型
    [schemas][text_template][basic]
    """
    template_id: int = Field(..., description="模板ID")
    template_name: str = Field(..., description="模板名称")
    template_description: Optional[str] = Field(None, description="模板描述")
    template_content: str = Field(..., description="模板内容")
    template_type: str = Field(..., description="模板类型")
    template_variables: Optional[dict] = Field(None, description="模板变量定义")
    template_created_user_id: int = Field(..., description="创建用户ID")
    template_created_time: datetime = Field(..., description="创建时间")
    template_status: str = Field(..., description="模板状态")
    template_usage_count: int = Field(..., description="使用次数")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TextTemplateBasicCreateSchema(BaseModel):
    """
    文本模板创建请求模型
    [schemas][text_template][basic_create]
    """
    template_name: str = Field(..., max_length=100, description="模板名称")
    template_description: Optional[str] = Field(None, description="模板描述")
    template_content: str = Field(..., min_length=1, description="模板内容")
    template_type: str = Field(..., max_length=50, description="模板类型")
    template_variables: Optional[dict] = Field(None, description="模板变量定义")

class TextTemplateBasicUpdateSchema(BaseModel):
    """
    文本模板更新请求模型
    [schemas][text_template][basic_update]
    """
    template_name: Optional[str] = Field(None, max_length=100, description="模板名称")
    template_description: Optional[str] = Field(None, description="模板描述")
    template_content: Optional[str] = Field(None, min_length=1, description="模板内容")
    template_type: Optional[str] = Field(None, max_length=50, description="模板类型")
    template_variables: Optional[dict] = Field(None, description="模板变量定义")

# ==================== 文本生成相关 ====================

class TextContentGenerateSchema(BaseModel):
    """
    文本生成请求模型
    [schemas][text_content][generate]
    """
    prompt: str = Field(..., min_length=1, description="生成提示词")
    template_id: Optional[int] = Field(None, description="使用的模板ID")
    template_variables: Optional[dict] = Field(None, description="模板变量值")
    content_type: str = Field("article", description="内容类型")
    content_language: str = Field("zh-CN", description="内容语言")
    generation_params: Optional[dict] = Field(None, description="生成参数")
    max_length: Optional[int] = Field(None, ge=1, le=10000, description="最大长度")
    style: Optional[str] = Field(None, description="写作风格")

class TextContentBatchGenerateSchema(BaseModel):
    """
    文本批量生成请求模型
    [schemas][text_content][batch_generate]
    """
    prompts: List[str] = Field(..., min_items=1, max_items=10, description="提示词列表")
    template_id: Optional[int] = Field(None, description="使用的模板ID")
    common_params: Optional[dict] = Field(None, description="通用参数")

# ==================== 文本统计信息 ====================

class TextContentStatsSchema(BaseModel):
    """
    文本内容统计信息响应模型
    [schemas][text_content][stats]
    """
    total_contents: int = Field(..., description="内容总数")
    total_words: int = Field(..., description="总字数")
    content_types: dict = Field(..., description="内容类型分布")
    language_distribution: dict = Field(..., description="语言分布")
    creation_trends: List[dict] = Field(..., description="创建趋势数据")
    popular_templates: List[dict] = Field(..., description="热门模板")

# ==================== 完整文本信息 ====================

class TextContentCompleteSchema(BaseModel):
    """
    完整文本内容信息响应模型
    [schemas][text_content][complete]
    """
    content: TextContentBasicSchema = Field(..., description="文本内容基础信息")
    template: Optional[TextTemplateBasicSchema] = Field(None, description="使用的模板")
    analyses: List[TextContentAnalyseSchema] = Field([], description="分析结果列表")
    
    class Config:
        from_attributes = True