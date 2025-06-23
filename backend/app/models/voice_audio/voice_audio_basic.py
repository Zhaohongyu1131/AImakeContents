"""
Voice Audio Basic Model
音频基础模型 - [voice][audio][basic]
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL, func, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import ModelBase

class VoiceAudioBasic(ModelBase):
    """
    音频基础表
    [voice][audio][basic]
    """
    __tablename__ = "voice_audio_basic"
    
    # 主键
    audio_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="音频ID")
    
    # 音频基础信息
    audio_name = Column(String(100), nullable=False, comment="音频名称")
    audio_description = Column(Text, nullable=True, comment="音频描述")
    
    # 文件信息
    audio_file_id = Column(Integer, ForeignKey("file_storage_basic.file_id"), nullable=False, comment="音频文件ID")
    audio_duration = Column(DECIMAL(10, 2), nullable=True, comment="音频时长(秒)")
    audio_format = Column(String(20), nullable=True, comment="音频格式")
    audio_sample_rate = Column(Integer, nullable=True, comment="采样率")
    audio_bitrate = Column(Integer, nullable=True, comment="比特率")
    
    # 合成信息
    audio_source_text_id = Column(Integer, ForeignKey("text_content_basic.content_id"), nullable=True, comment="源文本ID")
    audio_timbre_id = Column(Integer, ForeignKey("voice_timbre_basic.timbre_id"), nullable=True, comment="音色ID")
    audio_synthesis_params = Column(JSONB, nullable=True, comment="合成参数")
    
    # 平台信息
    audio_platform = Column(String(50), nullable=False, default="volcano", index=True, comment="平台名称")
    audio_platform_task_id = Column(String(100), nullable=True, comment="平台任务ID")
    
    # 用户和时间
    audio_created_user_id = Column(Integer, ForeignKey("user_auth_basic.user_id"), nullable=False, index=True, comment="创建用户ID")
    audio_created_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    audio_updated_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    
    # 状态和标签
    audio_status = Column(String(20), nullable=False, default="pending", index=True, comment="状态")
    audio_tags = Column(ARRAY(String), nullable=True, comment="标签数组")
    
    # 关系映射
    created_user = relationship("UserAuthBasic", foreign_keys=[audio_created_user_id])
    audio_file = relationship("FileStorageBasic", foreign_keys=[audio_file_id])
    source_text = relationship("TextContentBasic", foreign_keys=[audio_source_text_id])
    timbre = relationship("VoiceTimbreBasic", back_populates="audio_contents")
    analyses = relationship("VoiceAudioAnalyse", back_populates="audio", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<VoiceAudioBasic(audio_id={self.audio_id}, audio_name='{self.audio_name}', audio_platform='{self.audio_platform}')>"
    
    def audio_status_is_completed(self) -> bool:
        """
        检查音频是否合成完成
        [audio][status][is_completed]
        """
        return self.audio_status == "completed"
    
    def audio_status_is_failed(self) -> bool:
        """
        检查音频是否合成失败
        [audio][status][is_failed]
        """
        return self.audio_status == "failed"
    
    def audio_status_is_processing(self) -> bool:
        """
        检查音频是否正在处理
        [audio][status][is_processing]
        """
        return self.audio_status == "processing"
    
    def audio_duration_human_readable(self) -> str:
        """
        获取人类可读的时长
        [audio][duration][human_readable]
        """
        if self.audio_duration is None:
            return "未知"
        
        duration = float(self.audio_duration)
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    def audio_file_size_human_readable(self) -> str:
        """
        获取人类可读的文件大小
        [audio][file_size][human_readable]
        """
        if not self.audio_file or not self.audio_file.file_size:
            return "未知"
        
        size = self.audio_file.file_size
        units = ['B', 'KB', 'MB', 'GB']
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.1f} {units[unit_index]}"
    
    def audio_synthesis_params_get_field(self, field_name: str, default=None):
        """
        获取合成参数中的特定字段
        [audio][synthesis_params][get_field]
        """
        if isinstance(self.audio_synthesis_params, dict):
            return self.audio_synthesis_params.get(field_name, default)
        return default
    
    def audio_tags_add(self, tag: str) -> None:
        """
        添加标签
        [audio][tags][add]
        """
        if self.audio_tags is None:
            self.audio_tags = []
        if tag not in self.audio_tags:
            self.audio_tags = self.audio_tags + [tag]
    
    def audio_tags_remove(self, tag: str) -> None:
        """
        移除标签
        [audio][tags][remove]
        """
        if self.audio_tags and tag in self.audio_tags:
            self.audio_tags = [t for t in self.audio_tags if t != tag]
    
    def audio_platform_display_name(self) -> str:
        """
        获取平台显示名称
        [audio][platform][display_name]
        """
        platform_names = {
            "volcano": "豆包(火山引擎)",
            "azure": "Azure认知服务",
            "openai": "OpenAI",
            "local": "本地模型"
        }
        return platform_names.get(self.audio_platform, self.audio_platform)
    
    def audio_status_display_name(self) -> str:
        """
        获取状态显示名称
        [audio][status][display_name]
        """
        status_names = {
            "pending": "等待中",
            "processing": "处理中",
            "completed": "已完成",
            "failed": "失败"
        }
        return status_names.get(self.audio_status, self.audio_status)