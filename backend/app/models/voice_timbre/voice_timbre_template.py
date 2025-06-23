"""
Voice Timbre Template Model
音色模板模型 - [voice][timbre][template]
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import ModelBase

class VoiceTimbreTemplate(ModelBase):
    """
    音色模板表
    [voice][timbre][template]
    """
    __tablename__ = "voice_timbre_template"
    
    # 主键
    template_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="模板ID")
    
    # 模板信息
    template_name = Column(String(100), nullable=False, comment="模板名称")
    template_description = Column(Text, nullable=True, comment="模板描述")
    
    # 音色关联
    template_timbre_id = Column(Integer, ForeignKey("voice_timbre_basic.timbre_id"), nullable=True, comment="音色ID")
    
    # 配置信息
    template_clone_params = Column(JSONB, nullable=True, comment="克隆参数配置")
    template_quality_requirements = Column(JSONB, nullable=True, comment="质量要求")
    
    # 用户和时间
    template_created_user_id = Column(Integer, ForeignKey("user_auth_basic.user_id"), nullable=False, index=True, comment="创建用户ID")
    template_created_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    
    # 状态和使用统计
    template_status = Column(String(20), nullable=False, default="active", index=True, comment="模板状态")
    template_usage_count = Column(Integer, nullable=False, default=0, comment="使用次数")
    
    # 关系映射
    timbre = relationship("VoiceTimbreBasic", back_populates="templates")
    created_user = relationship("UserAuthBasic", foreign_keys=[template_created_user_id])
    
    def __repr__(self) -> str:
        return f"<VoiceTimbreTemplate(template_id={self.template_id}, template_name='{self.template_name}')>"
    
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
    
    def template_clone_params_get_field(self, field_name: str, default=None):
        """
        获取克隆参数中的特定字段
        [template][clone_params][get_field]
        """
        if isinstance(self.template_clone_params, dict):
            return self.template_clone_params.get(field_name, default)
        return default
    
    def template_quality_requirements_get_field(self, field_name: str, default=None):
        """
        获取质量要求中的特定字段
        [template][quality_requirements][get_field]
        """
        if isinstance(self.template_quality_requirements, dict):
            return self.template_quality_requirements.get(field_name, default)
        return default
    
    def template_clone_params_update(self, params: dict) -> None:
        """
        更新克隆参数
        [template][clone_params][update]
        """
        if self.template_clone_params is None:
            self.template_clone_params = {}
        
        if isinstance(self.template_clone_params, dict) and isinstance(params, dict):
            self.template_clone_params = {**self.template_clone_params, **params}
        else:
            self.template_clone_params = params
    
    def template_quality_requirements_update(self, requirements: dict) -> None:
        """
        更新质量要求
        [template][quality_requirements][update]
        """
        if self.template_quality_requirements is None:
            self.template_quality_requirements = {}
        
        if isinstance(self.template_quality_requirements, dict) and isinstance(requirements, dict):
            self.template_quality_requirements = {**self.template_quality_requirements, **requirements}
        else:
            self.template_quality_requirements = requirements