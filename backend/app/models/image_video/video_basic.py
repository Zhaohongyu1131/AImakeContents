"""
Video Basic Model
视频基础模型 - [video][basic]
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL, func, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import ModelBase

class VideoBasic(ModelBase):
    """
    视频基础表
    [video][basic]
    """
    __tablename__ = "video_basic"
    
    # 主键
    video_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="视频ID")
    
    # 视频基础信息
    video_name = Column(String(100), nullable=False, comment="视频名称")
    video_description = Column(Text, nullable=True, comment="视频描述")
    
    # 文件信息
    video_file_id = Column(Integer, ForeignKey("file_storage_basic.file_id"), nullable=False, comment="视频文件ID")
    video_duration = Column(DECIMAL(10, 2), nullable=True, comment="视频时长(秒)")
    video_width = Column(Integer, nullable=True, comment="视频宽度")
    video_height = Column(Integer, nullable=True, comment="视频高度")
    video_format = Column(String(20), nullable=True, comment="视频格式")
    video_fps = Column(DECIMAL(5, 2), nullable=True, comment="帧率")
    video_bitrate = Column(Integer, nullable=True, comment="比特率")
    
    # 生成信息
    video_source_text_id = Column(Integer, ForeignKey("text_content_basic.content_id"), nullable=True, comment="源文本ID")
    video_source_image_id = Column(Integer, ForeignKey("image_basic.image_id"), nullable=True, comment="源图像ID")
    video_source_audio_id = Column(Integer, ForeignKey("voice_audio_basic.audio_id"), nullable=True, comment="源音频ID")
    video_generation_params = Column(JSONB, nullable=True, comment="生成参数")
    
    # 平台信息
    video_platform = Column(String(50), nullable=False, default="local", index=True, comment="平台名称")
    video_platform_task_id = Column(String(100), nullable=True, comment="平台任务ID")
    video_model_name = Column(String(100), nullable=True, comment="使用的模型名称")
    
    # 用户和时间
    video_created_user_id = Column(Integer, ForeignKey("user_auth_basic.user_id"), nullable=False, index=True, comment="创建用户ID")
    video_created_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    video_updated_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    
    # 状态和标签
    video_status = Column(String(20), nullable=False, default="pending", index=True, comment="状态")
    video_tags = Column(ARRAY(String), nullable=True, comment="标签数组")
    
    # 关系映射
    created_user = relationship("UserAuthBasic", foreign_keys=[video_created_user_id])
    video_file = relationship("FileStorageBasic", foreign_keys=[video_file_id])
    source_text = relationship("TextContentBasic", foreign_keys=[video_source_text_id])
    source_image = relationship("ImageBasic", foreign_keys=[video_source_image_id])
    source_audio = relationship("VoiceAudioBasic", foreign_keys=[video_source_audio_id])
    analyses = relationship("VideoAnalyse", back_populates="video", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<VideoBasic(video_id={self.video_id}, video_name='{self.video_name}', video_platform='{self.video_platform}')>"
    
    def video_status_is_completed(self) -> bool:
        """
        检查视频是否生成完成
        [video][status][is_completed]
        """
        return self.video_status == "completed"
    
    def video_status_is_failed(self) -> bool:
        """
        检查视频是否生成失败
        [video][status][is_failed]
        """
        return self.video_status == "failed"
    
    def video_status_is_processing(self) -> bool:
        """
        检查视频是否正在处理
        [video][status][is_processing]
        """
        return self.video_status == "processing"
    
    def video_duration_human_readable(self) -> str:
        """
        获取人类可读的时长
        [video][duration][human_readable]
        """
        if self.video_duration is None:
            return "未知"
        
        duration = float(self.video_duration)
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    def video_resolution_display(self) -> str:
        """
        获取视频分辨率显示
        [video][resolution][display]
        """
        if self.video_width and self.video_height:
            return f"{self.video_width} × {self.video_height}"
        return "未知"
    
    def video_quality_description(self) -> str:
        """
        获取视频质量描述
        [video][quality][description]
        """
        if not self.video_width or not self.video_height:
            return "未知"
        
        height = self.video_height
        if height >= 2160:
            return "4K超高清"
        elif height >= 1080:
            return "1080P高清"
        elif height >= 720:
            return "720P高清"
        elif height >= 480:
            return "480P标清"
        else:
            return "低清"
    
    def video_file_size_human_readable(self) -> str:
        """
        获取人类可读的文件大小
        [video][file_size][human_readable]
        """
        if not self.video_file or not self.video_file.file_size:
            return "未知"
        
        size = self.video_file.file_size
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.1f} {units[unit_index]}"
    
    def video_fps_display(self) -> str:
        """
        获取帧率显示
        [video][fps][display]
        """
        if self.video_fps is None:
            return "未知"
        return f"{float(self.video_fps):.1f} fps"
    
    def video_bitrate_human_readable(self) -> str:
        """
        获取人类可读的比特率
        [video][bitrate][human_readable]
        """
        if self.video_bitrate is None:
            return "未知"
        
        bitrate = self.video_bitrate
        if bitrate >= 1000000:
            return f"{bitrate/1000000:.1f} Mbps"
        elif bitrate >= 1000:
            return f"{bitrate/1000:.1f} Kbps"
        else:
            return f"{bitrate} bps"
    
    def video_generation_params_get_field(self, field_name: str, default=None):
        """
        获取生成参数中的特定字段
        [video][generation_params][get_field]
        """
        if isinstance(self.video_generation_params, dict):
            return self.video_generation_params.get(field_name, default)
        return default
    
    def video_tags_add(self, tag: str) -> None:
        """
        添加标签
        [video][tags][add]
        """
        if self.video_tags is None:
            self.video_tags = []
        if tag not in self.video_tags:
            self.video_tags = self.video_tags + [tag]
    
    def video_tags_remove(self, tag: str) -> None:
        """
        移除标签
        [video][tags][remove]
        """
        if self.video_tags and tag in self.video_tags:
            self.video_tags = [t for t in self.video_tags if t != tag]
    
    def video_platform_display_name(self) -> str:
        """
        获取平台显示名称
        [video][platform][display_name]
        """
        platform_names = {
            "openai": "OpenAI Sora",
            "runway": "Runway ML",
            "stable_video": "Stable Video Diffusion",
            "local": "本地模型",
            "custom": "自定义模型"
        }
        return platform_names.get(self.video_platform, self.video_platform)
    
    def video_status_display_name(self) -> str:
        """
        获取状态显示名称
        [video][status][display_name]
        """
        status_names = {
            "pending": "等待中",
            "processing": "处理中",
            "completed": "已完成",
            "failed": "失败"
        }
        return status_names.get(self.video_status, self.video_status)