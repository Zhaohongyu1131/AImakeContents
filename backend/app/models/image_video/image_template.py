"""
Image Template Model
图像模板模型 - [image][template]
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import ModelBase

class ImageTemplate(ModelBase):
    """
    图像模板表
    [image][template]
    """
    __tablename__ = "image_template"
    
    # 主键
    template_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="模板ID")
    
    # 模板信息
    template_name = Column(String(100), nullable=False, comment="模板名称")
    template_description = Column(Text, nullable=True, comment="模板描述")
    template_type = Column(String(50), nullable=False, index=True, comment="模板类型")
    
    # 文本关联
    template_text_template_id = Column(Integer, ForeignKey("text_template_basic.template_id"), nullable=True, comment="文本模板ID")
    
    # 生成配置
    template_generation_params = Column(JSONB, nullable=True, comment="生成参数配置")
    template_prompt_template = Column(Text, nullable=True, comment="提示词模板")
    template_negative_prompt = Column(Text, nullable=True, comment="负向提示词")
    template_style_presets = Column(JSONB, nullable=True, comment="风格预设")
    
    # 输出配置
    template_output_width = Column(Integer, nullable=True, comment="输出宽度")
    template_output_height = Column(Integer, nullable=True, comment="输出高度")
    template_output_format = Column(String(20), nullable=False, default="png", comment="输出格式")
    template_quality_level = Column(String(20), nullable=False, default="high", comment="质量级别")
    
    # 平台配置
    template_platform = Column(String(50), nullable=False, default="local", index=True, comment="平台名称")
    template_model_name = Column(String(100), nullable=True, comment="模型名称")
    template_platform_params = Column(JSONB, nullable=True, comment="平台特定参数")
    
    # 用户和时间
    template_created_user_id = Column(Integer, ForeignKey("user_auth_basic.user_id"), nullable=False, index=True, comment="创建用户ID")
    template_created_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    
    # 状态和使用统计
    template_status = Column(String(20), nullable=False, default="active", index=True, comment="模板状态")
    template_usage_count = Column(Integer, nullable=False, default=0, comment="使用次数")
    
    # 关系映射
    text_template = relationship("TextTemplateBasic", foreign_keys=[template_text_template_id])
    created_user = relationship("UserAuthBasic", foreign_keys=[template_created_user_id])
    
    def __repr__(self) -> str:
        return f"<ImageTemplate(template_id={self.template_id}, template_name='{self.template_name}', template_type='{self.template_type}')>"
    
    def template_status_is_active(self) -> bool:
        """
        检查模板是否活跃
        [template][status][is_active]
        """
        return self.template_status == "active"
    
    def template_usage_count_increment(self) -> int:
        """
        增加使用次数
        [template][usage_count][increment]
        """
        self.template_usage_count += 1
        return self.template_usage_count
    
    def template_resolution_display(self) -> str:
        """
        获取模板分辨率显示
        [template][resolution][display]
        """
        if self.template_output_width and self.template_output_height:
            return f"{self.template_output_width} × {self.template_output_height}"
        return "自动"
    
    def template_generation_params_get_field(self, field_name: str, default=None):
        """
        获取生成参数中的特定字段
        [template][generation_params][get_field]
        """
        if isinstance(self.template_generation_params, dict):
            return self.template_generation_params.get(field_name, default)
        return default
    
    def template_style_presets_get_field(self, field_name: str, default=None):
        """
        获取风格预设中的特定字段
        [template][style_presets][get_field]
        """
        if isinstance(self.template_style_presets, dict):
            return self.template_style_presets.get(field_name, default)
        return default
    
    def template_platform_params_get_field(self, field_name: str, default=None):
        """
        获取平台参数中的特定字段
        [template][platform_params][get_field]
        """
        if isinstance(self.template_platform_params, dict):
            return self.template_platform_params.get(field_name, default)
        return default
    
    def template_generation_params_update(self, params: dict) -> None:
        """
        更新生成参数
        [template][generation_params][update]
        """
        if self.template_generation_params is None:
            self.template_generation_params = {}
        
        if isinstance(self.template_generation_params, dict) and isinstance(params, dict):
            self.template_generation_params = {**self.template_generation_params, **params}
        else:
            self.template_generation_params = params
    
    def template_style_presets_update(self, presets: dict) -> None:
        """
        更新风格预设
        [template][style_presets][update]
        """
        if self.template_style_presets is None:
            self.template_style_presets = {}
        
        if isinstance(self.template_style_presets, dict) and isinstance(presets, dict):
            self.template_style_presets = {**self.template_style_presets, **presets}
        else:
            self.template_style_presets = presets
    
    def template_platform_params_update(self, params: dict) -> None:
        """
        更新平台参数
        [template][platform_params][update]
        """
        if self.template_platform_params is None:
            self.template_platform_params = {}
        
        if isinstance(self.template_platform_params, dict) and isinstance(params, dict):
            self.template_platform_params = {**self.template_platform_params, **params}
        else:
            self.template_platform_params = params
    
    def template_type_display_name(self) -> str:
        """
        获取模板类型显示名称
        [template][type][display_name]
        """
        type_names = {
            "text_to_image": "文本生图模板",
            "style_transfer": "风格转换模板",
            "image_enhancement": "图像增强模板",
            "creative": "创意生成模板",
            "portrait": "肖像生成模板",
            "landscape": "风景生成模板",
            "product": "产品图模板"
        }
        return type_names.get(self.template_type, self.template_type)
    
    def template_platform_display_name(self) -> str:
        """
        获取平台显示名称
        [template][platform][display_name]
        """
        platform_names = {
            "openai": "OpenAI DALL-E",
            "midjourney": "Midjourney",
            "stable_diffusion": "Stable Diffusion",
            "local": "本地模型",
            "custom": "自定义模型"
        }
        return platform_names.get(self.template_platform, self.template_platform)
    
    def template_quality_level_display_name(self) -> str:
        """
        获取质量级别显示名称
        [template][quality_level][display_name]
        """
        quality_names = {
            "low": "低质量",
            "medium": "中等质量",
            "high": "高质量",
            "ultra": "超高质量"
        }
        return quality_names.get(self.template_quality_level, self.template_quality_level)
    
    def template_output_format_display_name(self) -> str:
        """
        获取输出格式显示名称
        [template][output_format][display_name]
        """
        format_names = {
            "png": "PNG格式",
            "jpg": "JPG格式",
            "jpeg": "JPEG格式",
            "webp": "WebP格式",
            "bmp": "BMP格式"
        }
        return format_names.get(self.template_output_format, self.template_output_format)