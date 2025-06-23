"""
Voice Timbre Basic Model
音色基础模型 - [voice][timbre][basic]
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL, func, ARRAY
from sqlalchemy.orm import relationship
from app.models.base import ModelBase

class VoiceTimbreBasic(ModelBase):
    """
    音色基础表
    [voice][timbre][basic]
    """
    __tablename__ = "voice_timbre_basic"
    
    # 主键
    timbre_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="音色ID")
    
    # 音色基础信息
    timbre_name = Column(String(100), nullable=False, comment="音色名称")
    timbre_description = Column(Text, nullable=True, comment="音色描述")
    
    # 文件和平台信息
    timbre_source_file_id = Column(Integer, ForeignKey("file_storage_basic.file_id"), nullable=True, comment="克隆源音频文件ID")
    timbre_platform_id = Column(String(100), nullable=True, comment="第三方平台音色ID")
    timbre_platform = Column(String(50), nullable=False, default="volcano", index=True, comment="平台名称")
    
    # 音色特征
    timbre_language = Column(String(10), nullable=False, default="zh-CN", comment="语言")
    timbre_gender = Column(String(10), nullable=True, index=True, comment="性别")
    timbre_age_range = Column(String(20), nullable=True, comment="年龄范围")
    timbre_style = Column(String(50), nullable=True, index=True, comment="音色风格")
    timbre_quality_score = Column(DECIMAL(5, 2), nullable=True, comment="音色质量评分")
    
    # 用户和时间
    timbre_created_user_id = Column(Integer, ForeignKey("user_auth_basic.user_id"), nullable=False, index=True, comment="创建用户ID")
    timbre_created_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    timbre_updated_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    
    # 状态和标签
    timbre_status = Column(String(20), nullable=False, default="training", index=True, comment="状态")
    timbre_tags = Column(ARRAY(String), nullable=True, comment="标签数组")
    
    # 关系映射
    created_user = relationship("UserAuthBasic", foreign_keys=[timbre_created_user_id])
    source_file = relationship("FileStorageBasic", foreign_keys=[timbre_source_file_id])
    clone_records = relationship("VoiceTimbreClone", back_populates="timbre", cascade="all, delete-orphan")
    templates = relationship("VoiceTimbreTemplate", back_populates="timbre")
    audio_contents = relationship("VoiceAudioBasic", back_populates="timbre")
    
    def __repr__(self) -> str:
        return f"<VoiceTimbreBasic(timbre_id={self.timbre_id}, timbre_name='{self.timbre_name}', timbre_platform='{self.timbre_platform}')>"
    
    def timbre_status_is_ready(self) -> bool:
        """
        检查音色是否就绪
        [timbre][status][is_ready]
        """
        return self.timbre_status == "ready"
    
    def timbre_quality_grade(self) -> str:
        """
        获取音色质量等级
        [timbre][quality][grade]
        """
        if self.timbre_quality_score is None:
            return "未评分"
        
        score = float(self.timbre_quality_score)
        if score >= 90:
            return "优秀"
        elif score >= 80:
            return "良好"
        elif score >= 70:
            return "中等"
        elif score >= 60:
            return "及格"
        else:
            return "需改进"
    
    def timbre_tags_add(self, tag: str) -> None:
        """
        添加标签
        [timbre][tags][add]
        """
        if self.timbre_tags is None:
            self.timbre_tags = []
        if tag not in self.timbre_tags:
            self.timbre_tags = self.timbre_tags + [tag]
    
    def timbre_tags_remove(self, tag: str) -> None:
        """
        移除标签
        [timbre][tags][remove]
        """
        if self.timbre_tags and tag in self.timbre_tags:
            self.timbre_tags = [t for t in self.timbre_tags if t != tag]
    
    def timbre_gender_display_name(self) -> str:
        """
        获取性别显示名称
        [timbre][gender][display_name]
        """
        gender_names = {
            "male": "男性",
            "female": "女性",
            "neutral": "中性"
        }
        return gender_names.get(self.timbre_gender, "未知")
    
    def timbre_platform_display_name(self) -> str:
        """
        获取平台显示名称
        [timbre][platform][display_name]
        """
        platform_names = {
            "volcano": "豆包(火山引擎)",
            "azure": "Azure认知服务",
            "openai": "OpenAI",
            "local": "本地模型"
        }
        return platform_names.get(self.timbre_platform, self.timbre_platform)