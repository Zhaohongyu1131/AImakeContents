"""
Voice Timbre Clone Model
音色克隆记录模型 - [voice][timbre][clone]
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import ModelBase

class VoiceTimbreClone(ModelBase):
    """
    音色克隆记录表
    [voice][timbre][clone]
    """
    __tablename__ = "voice_timbre_clone"
    
    # 主键
    clone_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="克隆记录ID")
    
    # 关联信息
    timbre_id = Column(Integer, ForeignKey("voice_timbre_basic.timbre_id"), nullable=False, index=True, comment="音色ID")
    clone_source_file_id = Column(Integer, ForeignKey("file_storage_basic.file_id"), nullable=False, comment="源音频文件ID")
    
    # 克隆信息
    clone_source_duration = Column(DECIMAL(10, 2), nullable=True, comment="源音频时长(秒)")
    clone_training_params = Column(JSONB, nullable=True, comment="训练参数")
    clone_progress = Column(Integer, nullable=False, default=0, comment="训练进度百分比")
    
    # 用户和时间
    clone_created_user_id = Column(Integer, ForeignKey("user_auth_basic.user_id"), nullable=False, index=True, comment="创建用户ID")
    clone_created_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    clone_completed_time = Column(DateTime(timezone=True), nullable=True, comment="完成时间")
    
    # 状态和错误
    clone_status = Column(String(20), nullable=False, default="pending", index=True, comment="克隆状态")
    clone_error_message = Column(Text, nullable=True, comment="错误信息")
    
    # 关系映射
    timbre = relationship("VoiceTimbreBasic", back_populates="clone_records")
    source_file = relationship("FileStorageBasic", foreign_keys=[clone_source_file_id])
    created_user = relationship("UserAuthBasic", foreign_keys=[clone_created_user_id])
    
    def __repr__(self) -> str:
        return f"<VoiceTimbreClone(clone_id={self.clone_id}, timbre_id={self.timbre_id}, clone_status='{self.clone_status}')>"
    
    def clone_status_is_completed(self) -> bool:
        """
        检查克隆是否完成
        [clone][status][is_completed]
        """
        return self.clone_status == "completed"
    
    def clone_status_is_failed(self) -> bool:
        """
        检查克隆是否失败
        [clone][status][is_failed]
        """
        return self.clone_status == "failed"
    
    def clone_status_is_training(self) -> bool:
        """
        检查是否正在训练
        [clone][status][is_training]
        """
        return self.clone_status == "training"
    
    def clone_progress_percentage(self) -> str:
        """
        获取进度百分比字符串
        [clone][progress][percentage]
        """
        return f"{self.clone_progress}%"
    
    def clone_duration_human_readable(self) -> str:
        """
        获取人类可读的时长
        [clone][duration][human_readable]
        """
        if self.clone_source_duration is None:
            return "未知"
        
        duration = float(self.clone_source_duration)
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    def clone_training_params_get_field(self, field_name: str, default=None):
        """
        获取训练参数中的特定字段
        [clone][training_params][get_field]
        """
        if isinstance(self.clone_training_params, dict):
            return self.clone_training_params.get(field_name, default)
        return default
    
    def clone_status_display_name(self) -> str:
        """
        获取状态显示名称
        [clone][status][display_name]
        """
        status_names = {
            "pending": "等待中",
            "training": "训练中",
            "completed": "已完成",
            "failed": "失败"
        }
        return status_names.get(self.clone_status, self.clone_status)