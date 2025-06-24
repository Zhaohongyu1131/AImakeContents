"""
File Storage Basic Model
文件存储基础模型 - [file][storage][basic]
"""

from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.models.base import ModelBase

class FileStorageBasic(ModelBase):
    """
    文件存储基础表
    [file][storage][basic]
    """
    __tablename__ = "file_storage_basic"
    
    # 主键
    file_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="文件ID")
    
    # 文件基础信息
    file_name = Column(String(255), nullable=False, comment="文件名称")
    file_original_name = Column(String(255), nullable=False, comment="原始文件名")
    file_path = Column(String(1000), nullable=False, comment="文件路径")
    file_size = Column(BigInteger, nullable=False, comment="文件大小(字节)")
    
    # 文件类型和格式
    file_type = Column(String(100), nullable=False, index=True, comment="文件类型")
    file_mime_type = Column(String(100), nullable=False, comment="MIME类型")
    file_hash_md5 = Column(String(32), nullable=False, index=True, comment="文件MD5哈希")
    
    # 存储配置
    file_storage_type = Column(String(50), nullable=False, default="local", comment="存储类型")
    
    # 时间和用户
    file_created_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    file_created_user_id = Column(Integer, ForeignKey("user_auth_basic.user_id"), nullable=False, index=True, comment="创建用户ID")
    
    # 状态
    file_status = Column(String(20), nullable=False, default="active", index=True, comment="文件状态")
    
    # 关系映射
    created_user = relationship("UserAuthBasic", foreign_keys=[file_created_user_id])
    meta_list = relationship("FileStorageMeta", back_populates="file_storage")
    
    def __repr__(self) -> str:
        return f"<FileStorageBasic(file_id={self.file_id}, file_name='{self.file_name}', file_type='{self.file_type}')>"
    
    @property
    def file_size_human_readable(self) -> str:
        """
        获取人类可读的文件大小
        [file][size][human_readable]
        """
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    @property
    def file_extension(self) -> str:
        """
        获取文件扩展名
        [file][extension]
        """
        import os
        return os.path.splitext(self.file_original_name)[1].lower()
    
    def file_url_generate(self, base_url: str = "") -> str:
        """
        生成文件访问URL
        [file][url][generate]
        """
        if self.file_storage_type == "local":
            return f"{base_url}/files/download/{self.file_id}"
        else:
            # 对于云存储，直接返回文件路径作为URL
            return self.file_path
    
    def file_is_image(self) -> bool:
        """
        检查是否为图像文件
        [file][is_image]
        """
        return self.file_type == "image" or self.file_mime_type.startswith("image/")
    
    def file_is_audio(self) -> bool:
        """
        检查是否为音频文件
        [file][is_audio]
        """
        return self.file_type == "audio" or self.file_mime_type.startswith("audio/")
    
    def file_is_video(self) -> bool:
        """
        检查是否为视频文件
        [file][is_video]
        """
        return self.file_type == "video" or self.file_mime_type.startswith("video/")
    
    def file_is_text(self) -> bool:
        """
        检查是否为文本文件
        [file][is_text]
        """
        return self.file_type == "text" or self.file_mime_type.startswith("text/")