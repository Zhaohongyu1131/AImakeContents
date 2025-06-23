"""
Mixed Content Basic Model
混合内容基础模型 - [mixed][content][basic]
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import ModelBase

class MixedContentBasic(ModelBase):
    """
    混合内容基础表
    [mixed][content][basic]
    """
    __tablename__ = "mixed_content_basic"
    
    # 主键
    content_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="混合内容ID")
    
    # 内容基础信息
    content_name = Column(String(100), nullable=False, comment="内容名称")
    content_description = Column(Text, nullable=True, comment="内容描述")
    content_type = Column(String(50), nullable=False, index=True, comment="内容类型")
    
    # 组件关联 - 支持多种内容类型组合
    content_text_ids = Column(ARRAY(Integer), nullable=True, comment="关联的文本内容ID数组")
    content_image_ids = Column(ARRAY(Integer), nullable=True, comment="关联的图像内容ID数组")
    content_audio_ids = Column(ARRAY(Integer), nullable=True, comment="关联的音频内容ID数组")
    content_video_ids = Column(ARRAY(Integer), nullable=True, comment="关联的视频内容ID数组")
    
    # 输出文件
    content_output_file_id = Column(Integer, ForeignKey("file_storage_basic.file_id"), nullable=True, comment="输出文件ID")
    
    # 生成配置
    content_generation_params = Column(JSONB, nullable=True, comment="生成参数")
    content_layout_config = Column(JSONB, nullable=True, comment="布局配置")
    content_style_config = Column(JSONB, nullable=True, comment="样式配置")
    content_timing_config = Column(JSONB, nullable=True, comment="时序配置")
    
    # 用户和时间
    content_created_user_id = Column(Integer, ForeignKey("user_auth_basic.user_id"), nullable=False, index=True, comment="创建用户ID")
    content_created_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    content_updated_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    
    # 状态和标签
    content_status = Column(String(20), nullable=False, default="pending", index=True, comment="状态")
    content_tags = Column(ARRAY(String), nullable=True, comment="标签数组")
    
    # 关系映射
    created_user = relationship("UserAuthBasic", foreign_keys=[content_created_user_id])
    output_file = relationship("FileStorageBasic", foreign_keys=[content_output_file_id])
    analyses = relationship("MixedContentAnalyse", back_populates="content", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<MixedContentBasic(content_id={self.content_id}, content_name='{self.content_name}', content_type='{self.content_type}')>"
    
    def content_status_is_completed(self) -> bool:
        """
        检查内容是否生成完成
        [content][status][is_completed]
        """
        return self.content_status == "completed"
    
    def content_status_is_failed(self) -> bool:
        """
        检查内容是否生成失败
        [content][status][is_failed]
        """
        return self.content_status == "failed"
    
    def content_status_is_processing(self) -> bool:
        """
        检查内容是否正在处理
        [content][status][is_processing]
        """
        return self.content_status == "processing"
    
    def content_components_count(self) -> dict:
        """
        获取各类型组件数量统计
        [content][components][count]
        """
        counts = {
            "text": len(self.content_text_ids) if self.content_text_ids else 0,
            "image": len(self.content_image_ids) if self.content_image_ids else 0,
            "audio": len(self.content_audio_ids) if self.content_audio_ids else 0,
            "video": len(self.content_video_ids) if self.content_video_ids else 0
        }
        counts["total"] = sum(counts.values())
        return counts
    
    def content_components_summary(self) -> str:
        """
        获取组件摘要描述
        [content][components][summary]
        """
        counts = self.content_components_count()
        parts = []
        
        if counts["text"] > 0:
            parts.append(f"{counts['text']}个文本")
        if counts["image"] > 0:
            parts.append(f"{counts['image']}个图像")
        if counts["audio"] > 0:
            parts.append(f"{counts['audio']}个音频")
        if counts["video"] > 0:
            parts.append(f"{counts['video']}个视频")
        
        if not parts:
            return "无组件"
        
        return "、".join(parts)
    
    def content_generation_params_get_field(self, field_name: str, default=None):
        """
        获取生成参数中的特定字段
        [content][generation_params][get_field]
        """
        if isinstance(self.content_generation_params, dict):
            return self.content_generation_params.get(field_name, default)
        return default
    
    def content_layout_config_get_field(self, field_name: str, default=None):
        """
        获取布局配置中的特定字段
        [content][layout_config][get_field]
        """
        if isinstance(self.content_layout_config, dict):
            return self.content_layout_config.get(field_name, default)
        return default
    
    def content_style_config_get_field(self, field_name: str, default=None):
        """
        获取样式配置中的特定字段
        [content][style_config][get_field]
        """
        if isinstance(self.content_style_config, dict):
            return self.content_style_config.get(field_name, default)
        return default
    
    def content_timing_config_get_field(self, field_name: str, default=None):
        """
        获取时序配置中的特定字段
        [content][timing_config][get_field]
        """
        if isinstance(self.content_timing_config, dict):
            return self.content_timing_config.get(field_name, default)
        return default
    
    def content_tags_add(self, tag: str) -> None:
        """
        添加标签
        [content][tags][add]
        """
        if self.content_tags is None:
            self.content_tags = []
        if tag not in self.content_tags:
            self.content_tags = self.content_tags + [tag]
    
    def content_tags_remove(self, tag: str) -> None:
        """
        移除标签
        [content][tags][remove]
        """
        if self.content_tags and tag in self.content_tags:
            self.content_tags = [t for t in self.content_tags if t != tag]
    
    def content_text_ids_add(self, text_id: int) -> None:
        """
        添加文本ID
        [content][text_ids][add]
        """
        if self.content_text_ids is None:
            self.content_text_ids = []
        if text_id not in self.content_text_ids:
            self.content_text_ids = self.content_text_ids + [text_id]
    
    def content_image_ids_add(self, image_id: int) -> None:
        """
        添加图像ID
        [content][image_ids][add]
        """
        if self.content_image_ids is None:
            self.content_image_ids = []
        if image_id not in self.content_image_ids:
            self.content_image_ids = self.content_image_ids + [image_id]
    
    def content_audio_ids_add(self, audio_id: int) -> None:
        """
        添加音频ID
        [content][audio_ids][add]
        """
        if self.content_audio_ids is None:
            self.content_audio_ids = []
        if audio_id not in self.content_audio_ids:
            self.content_audio_ids = self.content_audio_ids + [audio_id]
    
    def content_video_ids_add(self, video_id: int) -> None:
        """
        添加视频ID
        [content][video_ids][add]
        """
        if self.content_video_ids is None:
            self.content_video_ids = []
        if video_id not in self.content_video_ids:
            self.content_video_ids = self.content_video_ids + [video_id]
    
    def content_type_display_name(self) -> str:
        """
        获取内容类型显示名称
        [content][type][display_name]
        """
        type_names = {
            "presentation": "演示文稿",
            "video_with_subtitles": "字幕视频",
            "audio_with_images": "图文音频",
            "interactive_story": "交互故事",
            "multimedia_article": "多媒体文章",
            "slideshow": "幻灯片",
            "podcast": "播客节目",
            "tutorial": "教程内容"
        }
        return type_names.get(self.content_type, self.content_type)
    
    def content_status_display_name(self) -> str:
        """
        获取状态显示名称
        [content][status][display_name]
        """
        status_names = {
            "pending": "等待中",
            "processing": "处理中",
            "completed": "已完成",
            "failed": "失败"
        }
        return status_names.get(self.content_status, self.content_status)