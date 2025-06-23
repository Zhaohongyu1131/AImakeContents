"""
Video Template Model
视频模板模型 - [video][template]
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import ModelBase

class VideoTemplate(ModelBase):
    """
    视频模板表
    [video][template]
    """
    __tablename__ = "video_template"
    
    # 主键
    template_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="模板ID")
    
    # 模板信息
    template_name = Column(String(100), nullable=False, comment="模板名称")
    template_description = Column(Text, nullable=True, comment="模板描述")
    template_type = Column(String(50), nullable=False, index=True, comment="模板类型")
    
    # 关联模板
    template_text_template_id = Column(Integer, ForeignKey("text_template_basic.template_id"), nullable=True, comment="文本模板ID")
    template_image_template_id = Column(Integer, ForeignKey("image_template.template_id"), nullable=True, comment="图像模板ID")
    template_audio_template_id = Column(Integer, ForeignKey("voice_audio_template.template_id"), nullable=True, comment="音频模板ID")
    
    # 生成配置
    template_generation_params = Column(JSONB, nullable=True, comment="生成参数配置")
    template_prompt_template = Column(Text, nullable=True, comment="提示词模板")
    template_style_presets = Column(JSONB, nullable=True, comment="风格预设")
    
    # 输出配置
    template_output_width = Column(Integer, nullable=True, comment="输出宽度")
    template_output_height = Column(Integer, nullable=True, comment="输出高度")
    template_output_fps = Column(DECIMAL(5, 2), nullable=True, comment="输出帧率")
    template_output_duration = Column(DECIMAL(10, 2), nullable=True, comment="输出时长(秒)")
    template_output_format = Column(String(20), nullable=False, default="mp4", comment="输出格式")
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
    image_template = relationship("ImageTemplate", foreign_keys=[template_image_template_id])
    audio_template = relationship("VoiceAudioTemplate", foreign_keys=[template_audio_template_id])
    created_user = relationship("UserAuthBasic", foreign_keys=[template_created_user_id])
    
    def __repr__(self) -> str:
        return f"<VideoTemplate(template_id={self.template_id}, template_name='{self.template_name}', template_type='{self.template_type}')>"
    
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
    
    def template_duration_display(self) -> str:
        """
        获取模板时长显示
        [template][duration][display]
        """
        if self.template_output_duration is None:
            return "自动"
        
        duration = float(self.template_output_duration)
        if duration >= 60:
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            return f"{minutes}:{seconds:02d}"
        else:
            return f"{duration:.1f}秒"
    
    def template_fps_display(self) -> str:
        """
        获取帧率显示
        [template][fps][display]
        """
        if self.template_output_fps is None:
            return "自动"
        return f"{float(self.template_output_fps):.1f} fps"
    
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
            "text_to_video": "文本生成视频模板",
            "image_to_video": "图像生成视频模板",
            "audio_to_video": "音频生成视频模板",
            "multimodal": "多模态生成模板",
            "animation": "动画生成模板",
            "slideshow": "幻灯片模板",
            "presentation": "演示视频模板"
        }
        return type_names.get(self.template_type, self.template_type)
    
    def template_platform_display_name(self) -> str:
        """
        获取平台显示名称
        [template][platform][display_name]
        """
        platform_names = {
            "openai": "OpenAI Sora",
            "runway": "Runway ML",
            "stable_video": "Stable Video Diffusion",
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
            "mp4": "MP4格式",
            "avi": "AVI格式",
            "mov": "MOV格式",
            "mkv": "MKV格式",
            "webm": "WebM格式"
        }
        return format_names.get(self.template_output_format, self.template_output_format)