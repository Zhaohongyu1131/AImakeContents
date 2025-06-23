"""
Image Basic Model
图像基础模型 - [image][basic]
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import ModelBase

class ImageBasic(ModelBase):
    """
    图像基础表
    [image][basic]
    """
    __tablename__ = "image_basic"
    
    # 主键
    image_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="图像ID")
    
    # 图像基础信息
    image_name = Column(String(100), nullable=False, comment="图像名称")
    image_description = Column(Text, nullable=True, comment="图像描述")
    
    # 文件信息
    image_file_id = Column(Integer, ForeignKey("file_storage_basic.file_id"), nullable=False, comment="图像文件ID")
    image_width = Column(Integer, nullable=True, comment="图像宽度")
    image_height = Column(Integer, nullable=True, comment="图像高度")
    image_format = Column(String(20), nullable=True, comment="图像格式")
    
    # 生成信息
    image_source_text_id = Column(Integer, ForeignKey("text_content_basic.content_id"), nullable=True, comment="源文本ID")
    image_generation_params = Column(JSONB, nullable=True, comment="生成参数")
    image_prompt = Column(Text, nullable=True, comment="生成提示词")
    image_negative_prompt = Column(Text, nullable=True, comment="负向提示词")
    
    # 平台信息
    image_platform = Column(String(50), nullable=False, default="local", index=True, comment="平台名称")
    image_platform_task_id = Column(String(100), nullable=True, comment="平台任务ID")
    image_model_name = Column(String(100), nullable=True, comment="使用的模型名称")
    
    # 用户和时间
    image_created_user_id = Column(Integer, ForeignKey("user_auth_basic.user_id"), nullable=False, index=True, comment="创建用户ID")
    image_created_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    image_updated_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    
    # 状态和标签
    image_status = Column(String(20), nullable=False, default="pending", index=True, comment="状态")
    image_tags = Column(ARRAY(String), nullable=True, comment="标签数组")
    
    # 关系映射
    created_user = relationship("UserAuthBasic", foreign_keys=[image_created_user_id])
    image_file = relationship("FileStorageBasic", foreign_keys=[image_file_id])
    source_text = relationship("TextContentBasic", foreign_keys=[image_source_text_id])
    analyses = relationship("ImageAnalyse", back_populates="image", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<ImageBasic(image_id={self.image_id}, image_name='{self.image_name}', image_platform='{self.image_platform}')>"
    
    def image_status_is_completed(self) -> bool:
        """
        检查图像是否生成完成
        [image][status][is_completed]
        """
        return self.image_status == "completed"
    
    def image_status_is_failed(self) -> bool:
        """
        检查图像是否生成失败
        [image][status][is_failed]
        """
        return self.image_status == "failed"
    
    def image_status_is_processing(self) -> bool:
        """
        检查图像是否正在处理
        [image][status][is_processing]
        """
        return self.image_status == "processing"
    
    def image_resolution_display(self) -> str:
        """
        获取图像分辨率显示
        [image][resolution][display]
        """
        if self.image_width and self.image_height:
            return f"{self.image_width} × {self.image_height}"
        return "未知"
    
    def image_aspect_ratio(self) -> str:
        """
        获取图像宽高比
        [image][aspect_ratio]
        """
        if not self.image_width or not self.image_height:
            return "未知"
        
        width, height = self.image_width, self.image_height
        
        # 计算最大公约数
        def gcd(a, b):
            while b:
                a, b = b, a % b
            return a
        
        divisor = gcd(width, height)
        ratio_w = width // divisor
        ratio_h = height // divisor
        
        # 常见比例的友好显示
        if ratio_w == 16 and ratio_h == 9:
            return "16:9 (宽屏)"
        elif ratio_w == 4 and ratio_h == 3:
            return "4:3 (标准)"
        elif ratio_w == 1 and ratio_h == 1:
            return "1:1 (正方形)"
        elif ratio_w == 3 and ratio_h == 2:
            return "3:2 (摄影)"
        else:
            return f"{ratio_w}:{ratio_h}"
    
    def image_file_size_human_readable(self) -> str:
        """
        获取人类可读的文件大小
        [image][file_size][human_readable]
        """
        if not self.image_file or not self.image_file.file_size:
            return "未知"
        
        size = self.image_file.file_size
        units = ['B', 'KB', 'MB', 'GB']
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.1f} {units[unit_index]}"
    
    def image_generation_params_get_field(self, field_name: str, default=None):
        """
        获取生成参数中的特定字段
        [image][generation_params][get_field]
        """
        if isinstance(self.image_generation_params, dict):
            return self.image_generation_params.get(field_name, default)
        return default
    
    def image_tags_add(self, tag: str) -> None:
        """
        添加标签
        [image][tags][add]
        """
        if self.image_tags is None:
            self.image_tags = []
        if tag not in self.image_tags:
            self.image_tags = self.image_tags + [tag]
    
    def image_tags_remove(self, tag: str) -> None:
        """
        移除标签
        [image][tags][remove]
        """
        if self.image_tags and tag in self.image_tags:
            self.image_tags = [t for t in self.image_tags if t != tag]
    
    def image_platform_display_name(self) -> str:
        """
        获取平台显示名称
        [image][platform][display_name]
        """
        platform_names = {
            "openai": "OpenAI DALL-E",
            "midjourney": "Midjourney",
            "stable_diffusion": "Stable Diffusion",
            "local": "本地模型",
            "custom": "自定义模型"
        }
        return platform_names.get(self.image_platform, self.image_platform)
    
    def image_status_display_name(self) -> str:
        """
        获取状态显示名称
        [image][status][display_name]
        """
        status_names = {
            "pending": "等待中",
            "processing": "处理中", 
            "completed": "已完成",
            "failed": "失败"
        }
        return status_names.get(self.image_status, self.image_status)