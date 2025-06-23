"""
Voice Audio Template Model
音频模板模型 - [voice][audio][template]
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import ModelBase

class VoiceAudioTemplate(ModelBase):
    """
    音频模板表
    [voice][audio][template]
    """
    __tablename__ = "voice_audio_template"
    
    # 主键
    template_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="模板ID")
    
    # 模板信息
    template_name = Column(String(100), nullable=False, comment="模板名称")
    template_description = Column(Text, nullable=True, comment="模板描述")
    template_type = Column(String(50), nullable=False, index=True, comment="模板类型")
    
    # 音色和文本关联
    template_timbre_id = Column(Integer, ForeignKey("voice_timbre_basic.timbre_id"), nullable=True, comment="音色ID")
    template_text_template_id = Column(Integer, ForeignKey("text_template_basic.template_id"), nullable=True, comment="文本模板ID")
    
    # 合成配置
    template_synthesis_params = Column(JSONB, nullable=True, comment="合成参数配置")
    template_output_format = Column(String(20), nullable=False, default="mp3", comment="输出格式")
    template_sample_rate = Column(Integer, nullable=True, comment="采样率")
    template_bitrate = Column(Integer, nullable=True, comment="比特率")
    
    # 平台配置
    template_platform = Column(String(50), nullable=False, default="volcano", index=True, comment="平台名称")
    template_platform_params = Column(JSONB, nullable=True, comment="平台特定参数")
    
    # 用户和时间
    template_created_user_id = Column(Integer, ForeignKey("user_auth_basic.user_id"), nullable=False, index=True, comment="创建用户ID")
    template_created_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    
    # 状态和使用统计
    template_status = Column(String(20), nullable=False, default="active", index=True, comment="模板状态")
    template_usage_count = Column(Integer, nullable=False, default=0, comment="使用次数")
    
    # 关系映射
    timbre = relationship("VoiceTimbreBasic", foreign_keys=[template_timbre_id])
    text_template = relationship("TextTemplateBasic", foreign_keys=[template_text_template_id])
    created_user = relationship("UserAuthBasic", foreign_keys=[template_created_user_id])
    
    def __repr__(self) -> str:
        return f"<VoiceAudioTemplate(template_id={self.template_id}, template_name='{self.template_name}', template_type='{self.template_type}')>"
    
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
    
    def template_synthesis_params_get_field(self, field_name: str, default=None):
        """
        获取合成参数中的特定字段
        [template][synthesis_params][get_field]
        """
        if isinstance(self.template_synthesis_params, dict):
            return self.template_synthesis_params.get(field_name, default)
        return default
    
    def template_platform_params_get_field(self, field_name: str, default=None):
        """
        获取平台参数中的特定字段
        [template][platform_params][get_field]
        """
        if isinstance(self.template_platform_params, dict):
            return self.template_platform_params.get(field_name, default)
        return default
    
    def template_synthesis_params_update(self, params: dict) -> None:
        """
        更新合成参数
        [template][synthesis_params][update]
        """
        if self.template_synthesis_params is None:
            self.template_synthesis_params = {}
        
        if isinstance(self.template_synthesis_params, dict) and isinstance(params, dict):
            self.template_synthesis_params = {**self.template_synthesis_params, **params}
        else:
            self.template_synthesis_params = params
    
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
            "tts": "文本转语音模板",
            "voice_clone": "音色克隆模板",
            "batch_synthesis": "批量合成模板",
            "interactive": "交互式模板",
            "broadcast": "广播模板"
        }
        return type_names.get(self.template_type, self.template_type)
    
    def template_platform_display_name(self) -> str:
        """
        获取平台显示名称
        [template][platform][display_name]
        """
        platform_names = {
            "volcano": "豆包(火山引擎)",
            "azure": "Azure认知服务",
            "openai": "OpenAI",
            "local": "本地模型"
        }
        return platform_names.get(self.template_platform, self.template_platform)
    
    def template_output_format_display_name(self) -> str:
        """
        获取输出格式显示名称
        [template][output_format][display_name]
        """
        format_names = {
            "mp3": "MP3格式",
            "wav": "WAV格式",
            "flac": "FLAC格式",
            "aac": "AAC格式",
            "ogg": "OGG格式"
        }
        return format_names.get(self.template_output_format, self.template_output_format)