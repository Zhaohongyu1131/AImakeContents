"""
Image Analyse Model
图像分析模型 - [image][analyse]
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import ModelBase

class ImageAnalyse(ModelBase):
    """
    图像分析表
    [image][analyse]
    """
    __tablename__ = "image_analyse"
    
    # 主键
    analyse_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="分析ID")
    
    # 关联信息
    image_id = Column(Integer, ForeignKey("image_basic.image_id"), nullable=False, index=True, comment="图像ID")
    
    # 分析类型和结果
    analyse_type = Column(String(50), nullable=False, index=True, comment="分析类型")
    analyse_result = Column(JSONB, nullable=True, comment="分析结果")
    analyse_summary = Column(Text, nullable=True, comment="分析摘要")
    
    # 质量评估
    analyse_quality_score = Column(DECIMAL(5, 2), nullable=True, comment="质量评分")
    analyse_confidence_score = Column(DECIMAL(5, 2), nullable=True, comment="置信度评分")
    
    # 技术参数
    analyse_brightness = Column(DECIMAL(5, 2), nullable=True, comment="亮度")
    analyse_contrast = Column(DECIMAL(5, 2), nullable=True, comment="对比度")
    analyse_saturation = Column(DECIMAL(5, 2), nullable=True, comment="饱和度")
    analyse_sharpness = Column(DECIMAL(5, 2), nullable=True, comment="清晰度")
    
    # 内容识别
    analyse_objects_detected = Column(JSONB, nullable=True, comment="检测到的对象")
    analyse_faces_count = Column(Integer, nullable=True, comment="人脸数量")
    analyse_text_content = Column(Text, nullable=True, comment="图像中的文本内容")
    analyse_dominant_colors = Column(JSONB, nullable=True, comment="主要颜色")
    
    # 情感和风格
    analyse_emotion_data = Column(JSONB, nullable=True, comment="情感分析数据")
    analyse_style_tags = Column(JSONB, nullable=True, comment="风格标签")
    
    # 用户和时间
    analyse_created_user_id = Column(Integer, ForeignKey("user_auth_basic.user_id"), nullable=False, index=True, comment="创建用户ID")
    analyse_created_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    
    # 状态
    analyse_status = Column(String(20), nullable=False, default="completed", index=True, comment="分析状态")
    
    # 关系映射
    image = relationship("ImageBasic", back_populates="analyses")
    created_user = relationship("UserAuthBasic", foreign_keys=[analyse_created_user_id])
    
    def __repr__(self) -> str:
        return f"<ImageAnalyse(analyse_id={self.analyse_id}, image_id={self.image_id}, analyse_type='{self.analyse_type}')>"
    
    def analyse_quality_grade(self) -> str:
        """
        获取质量等级
        [analyse][quality][grade]
        """
        if self.analyse_quality_score is None:
            return "未评分"
        
        score = float(self.analyse_quality_score)
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
    
    def analyse_confidence_grade(self) -> str:
        """
        获取置信度等级
        [analyse][confidence][grade]
        """
        if self.analyse_confidence_score is None:
            return "未知"
        
        score = float(self.analyse_confidence_score)
        if score >= 90:
            return "很高"
        elif score >= 80:
            return "高"
        elif score >= 70:
            return "中等"
        elif score >= 60:
            return "低"
        else:
            return "很低"
    
    def analyse_brightness_description(self) -> str:
        """
        获取亮度描述
        [analyse][brightness][description]
        """
        if self.analyse_brightness is None:
            return "未知"
        
        brightness = float(self.analyse_brightness)
        if brightness >= 80:
            return "很亮"
        elif brightness >= 60:
            return "亮"
        elif brightness >= 40:
            return "适中"
        elif brightness >= 20:
            return "暗"
        else:
            return "很暗"
    
    def analyse_contrast_description(self) -> str:
        """
        获取对比度描述
        [analyse][contrast][description]
        """
        if self.analyse_contrast is None:
            return "未知"
        
        contrast = float(self.analyse_contrast)
        if contrast >= 80:
            return "对比强烈"
        elif contrast >= 60:
            return "对比较强"
        elif contrast >= 40:
            return "对比适中"
        elif contrast >= 20:
            return "对比较弱"
        else:
            return "对比很弱"
    
    def analyse_objects_detected_count(self) -> int:
        """
        获取检测到的对象数量
        [analyse][objects_detected][count]
        """
        if isinstance(self.analyse_objects_detected, list):
            return len(self.analyse_objects_detected)
        elif isinstance(self.analyse_objects_detected, dict):
            return len(self.analyse_objects_detected.get('objects', []))
        return 0
    
    def analyse_dominant_colors_list(self) -> list:
        """
        获取主要颜色列表
        [analyse][dominant_colors][list]
        """
        if isinstance(self.analyse_dominant_colors, list):
            return self.analyse_dominant_colors
        elif isinstance(self.analyse_dominant_colors, dict):
            return self.analyse_dominant_colors.get('colors', [])
        return []
    
    def analyse_result_get_field(self, field_name: str, default=None):
        """
        获取分析结果中的特定字段
        [analyse][result][get_field]
        """
        if isinstance(self.analyse_result, dict):
            return self.analyse_result.get(field_name, default)
        return default
    
    def analyse_emotion_data_get_field(self, field_name: str, default=None):
        """
        获取情感数据中的特定字段
        [analyse][emotion_data][get_field]
        """
        if isinstance(self.analyse_emotion_data, dict):
            return self.analyse_emotion_data.get(field_name, default)
        return default
    
    def analyse_style_tags_list(self) -> list:
        """
        获取风格标签列表
        [analyse][style_tags][list]
        """
        if isinstance(self.analyse_style_tags, list):
            return self.analyse_style_tags
        elif isinstance(self.analyse_style_tags, dict):
            return self.analyse_style_tags.get('tags', [])
        return []
    
    def analyse_type_display_name(self) -> str:
        """
        获取分析类型显示名称
        [analyse][type][display_name]
        """
        type_names = {
            "quality": "质量分析",
            "content": "内容识别",
            "face": "人脸检测",
            "object": "物体识别",
            "text": "文本识别",
            "color": "颜色分析",
            "emotion": "情感分析",
            "style": "风格分析",
            "comprehensive": "综合分析"
        }
        return type_names.get(self.analyse_type, self.analyse_type)