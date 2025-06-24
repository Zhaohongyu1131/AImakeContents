"""
File Storage Meta Model
文件存储元数据模型 - [file][storage][meta]
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
from app.models.base import ModelBase

class FileStorageMeta(ModelBase):
    """
    文件存储元数据表
    [file][storage][meta]
    """
    __tablename__ = "file_storage_meta"
    
    # 主键
    meta_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="元数据ID")
    
    # 关联文件
    file_id = Column(Integer, ForeignKey("file_storage_basic.file_id"), nullable=False, index=True, comment="文件ID")
    
    # 元数据信息
    meta_key = Column(String(100), nullable=False, index=True, comment="元数据键")
    meta_value = Column(Text, nullable=True, comment="元数据值")
    meta_type = Column(String(50), nullable=False, default="string", comment="数据类型")
    
    # JSON格式的复杂元数据
    meta_json = Column(JSON, nullable=True, comment="JSON格式元数据")
    
    # 元数据分类
    meta_category = Column(String(50), nullable=False, default="general", index=True, comment="元数据分类")
    meta_description = Column(String(500), nullable=True, comment="元数据描述")
    
    # 时间信息
    meta_created_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    meta_updated_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    
    # 创建用户
    meta_created_user_id = Column(Integer, ForeignKey("user_auth_basic.user_id"), nullable=False, index=True, comment="创建用户ID")
    
    # 状态
    meta_status = Column(String(20), nullable=False, default="active", index=True, comment="元数据状态")
    
    # 关系映射
    file_storage = relationship("FileStorageBasic", back_populates="meta_list")
    created_user = relationship("UserAuthBasic", foreign_keys=[meta_created_user_id])
    
    def __repr__(self) -> str:
        return f"<FileStorageMeta(meta_id={self.meta_id}, file_id={self.file_id}, meta_key='{self.meta_key}')>"
    
    def meta_value_get_typed(self):
        """
        根据数据类型返回适当的值
        [file][storage][meta][get_typed_value]
        """
        if self.meta_type == "integer":
            try:
                return int(self.meta_value) if self.meta_value else None
            except (ValueError, TypeError):
                return None
        elif self.meta_type == "float":
            try:
                return float(self.meta_value) if self.meta_value else None
            except (ValueError, TypeError):
                return None
        elif self.meta_type == "boolean":
            if self.meta_value is None:
                return None
            return str(self.meta_value).lower() in ('true', '1', 'yes', 'on')
        elif self.meta_type == "json":
            return self.meta_json
        else:
            return self.meta_value
    
    def meta_value_set_typed(self, value):
        """
        根据数据类型设置值
        [file][storage][meta][set_typed_value]
        """
        if value is None:
            self.meta_value = None
            self.meta_json = None
            return
        
        if self.meta_type == "json":
            self.meta_json = value
            self.meta_value = str(value)
        else:
            self.meta_value = str(value)
    
    @classmethod
    def meta_create_audio_metadata(cls, file_id: int, duration: float, sample_rate: int, 
                                  channels: int, bitrate: int, user_id: int):
        """
        创建音频文件元数据
        [file][storage][meta][create_audio_metadata]
        """
        audio_meta = {
            "duration": duration,
            "sample_rate": sample_rate,
            "channels": channels,
            "bitrate": bitrate
        }
        
        return cls(
            file_id=file_id,
            meta_key="audio_properties",
            meta_type="json",
            meta_json=audio_meta,
            meta_category="audio",
            meta_description="音频文件属性信息",
            meta_created_user_id=user_id
        )
    
    @classmethod
    def meta_create_image_metadata(cls, file_id: int, width: int, height: int, 
                                  format_name: str, user_id: int):
        """
        创建图像文件元数据
        [file][storage][meta][create_image_metadata]
        """
        image_meta = {
            "width": width,
            "height": height,
            "format": format_name,
            "aspect_ratio": round(width / height, 2) if height > 0 else 0
        }
        
        return cls(
            file_id=file_id,
            meta_key="image_properties",
            meta_type="json",
            meta_json=image_meta,
            meta_category="image",
            meta_description="图像文件属性信息",
            meta_created_user_id=user_id
        )
    
    @classmethod
    def meta_create_text_metadata(cls, file_id: int, encoding: str, line_count: int, 
                                 char_count: int, user_id: int):
        """
        创建文本文件元数据
        [file][storage][meta][create_text_metadata]
        """
        text_meta = {
            "encoding": encoding,
            "line_count": line_count,
            "char_count": char_count
        }
        
        return cls(
            file_id=file_id,
            meta_key="text_properties",
            meta_type="json",
            meta_json=text_meta,
            meta_category="text",
            meta_description="文本文件属性信息",
            meta_created_user_id=user_id
        )