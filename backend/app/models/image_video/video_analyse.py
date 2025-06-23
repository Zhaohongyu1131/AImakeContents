"""
Video Analyse Model
视频分析模型 - [video][analyse]
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import ModelBase

class VideoAnalyse(ModelBase):
    """
    视频分析表
    [video][analyse]
    """
    __tablename__ = "video_analyse"
    
    # 主键
    analyse_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="分析ID")
    
    # 关联信息
    video_id = Column(Integer, ForeignKey("video_basic.video_id"), nullable=False, index=True, comment="视频ID")
    
    # 分析类型和结果
    analyse_type = Column(String(50), nullable=False, index=True, comment="分析类型")
    analyse_result = Column(JSONB, nullable=True, comment="分析结果")
    analyse_summary = Column(Text, nullable=True, comment="分析摘要")
    
    # 质量评估
    analyse_quality_score = Column(DECIMAL(5, 2), nullable=True, comment="质量评分")
    analyse_confidence_score = Column(DECIMAL(5, 2), nullable=True, comment="置信度评分")
    
    # 技术参数
    analyse_frame_quality = Column(DECIMAL(5, 2), nullable=True, comment="帧质量评分")
    analyse_motion_smoothness = Column(DECIMAL(5, 2), nullable=True, comment="运动平滑度")
    analyse_color_consistency = Column(DECIMAL(5, 2), nullable=True, comment="颜色一致性")
    analyse_audio_sync = Column(DECIMAL(5, 2), nullable=True, comment="音画同步评分")
    
    # 内容分析
    analyse_scene_changes = Column(Integer, nullable=True, comment="场景变化次数")
    analyse_objects_detected = Column(JSONB, nullable=True, comment="检测到的对象")
    analyse_faces_detected = Column(JSONB, nullable=True, comment="检测到的人脸")
    analyse_text_content = Column(Text, nullable=True, comment="视频中的文本内容")
    
    # 情感和内容
    analyse_emotion_timeline = Column(JSONB, nullable=True, comment="情感时间线")
    analyse_activity_level = Column(DECIMAL(5, 2), nullable=True, comment="活动水平")
    analyse_content_tags = Column(JSONB, nullable=True, comment="内容标签")
    
    # 用户和时间
    analyse_created_user_id = Column(Integer, ForeignKey("user_auth_basic.user_id"), nullable=False, index=True, comment="创建用户ID")
    analyse_created_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    
    # 状态
    analyse_status = Column(String(20), nullable=False, default="completed", index=True, comment="分析状态")
    
    # 关系映射
    video = relationship("VideoBasic", back_populates="analyses")
    created_user = relationship("UserAuthBasic", foreign_keys=[analyse_created_user_id])
    
    def __repr__(self) -> str:
        return f"<VideoAnalyse(analyse_id={self.analyse_id}, video_id={self.video_id}, analyse_type='{self.analyse_type}')>"
    
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
    
    def analyse_motion_smoothness_description(self) -> str:
        """
        获取运动平滑度描述
        [analyse][motion_smoothness][description]
        """
        if self.analyse_motion_smoothness is None:
            return "未知"
        
        smoothness = float(self.analyse_motion_smoothness)
        if smoothness >= 90:
            return "非常流畅"
        elif smoothness >= 80:
            return "流畅"
        elif smoothness >= 70:
            return "较流畅"
        elif smoothness >= 60:
            return "一般"
        else:
            return "不流畅"
    
    def analyse_color_consistency_description(self) -> str:
        """
        获取颜色一致性描述
        [analyse][color_consistency][description]
        """
        if self.analyse_color_consistency is None:
            return "未知"
        
        consistency = float(self.analyse_color_consistency)
        if consistency >= 90:
            return "颜色非常一致"
        elif consistency >= 80:
            return "颜色一致"
        elif consistency >= 70:
            return "颜色较一致"
        elif consistency >= 60:
            return "颜色一般"
        else:
            return "颜色不一致"
    
    def analyse_audio_sync_description(self) -> str:
        """
        获取音画同步描述
        [analyse][audio_sync][description]
        """
        if self.analyse_audio_sync is None:
            return "未知"
        
        sync = float(self.analyse_audio_sync)
        if sync >= 90:
            return "音画完全同步"
        elif sync >= 80:
            return "音画同步良好"
        elif sync >= 70:
            return "音画基本同步"
        elif sync >= 60:
            return "音画略有延迟"
        else:
            return "音画不同步"
    
    def analyse_activity_level_description(self) -> str:
        """
        获取活动水平描述
        [analyse][activity_level][description]
        """
        if self.analyse_activity_level is None:
            return "未知"
        
        level = float(self.analyse_activity_level)
        if level >= 80:
            return "活动密集"
        elif level >= 60:
            return "活动较多"
        elif level >= 40:
            return "活动适中"
        elif level >= 20:
            return "活动较少"
        else:
            return "活动稀少"
    
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
    
    def analyse_faces_detected_count(self) -> int:
        """
        获取检测到的人脸数量
        [analyse][faces_detected][count]
        """
        if isinstance(self.analyse_faces_detected, list):
            return len(self.analyse_faces_detected)
        elif isinstance(self.analyse_faces_detected, dict):
            return len(self.analyse_faces_detected.get('faces', []))
        return 0
    
    def analyse_result_get_field(self, field_name: str, default=None):
        """
        获取分析结果中的特定字段
        [analyse][result][get_field]
        """
        if isinstance(self.analyse_result, dict):
            return self.analyse_result.get(field_name, default)
        return default
    
    def analyse_emotion_timeline_get_field(self, field_name: str, default=None):
        """
        获取情感时间线中的特定字段
        [analyse][emotion_timeline][get_field]
        """
        if isinstance(self.analyse_emotion_timeline, dict):
            return self.analyse_emotion_timeline.get(field_name, default)
        return default
    
    def analyse_content_tags_list(self) -> list:
        """
        获取内容标签列表
        [analyse][content_tags][list]
        """
        if isinstance(self.analyse_content_tags, list):
            return self.analyse_content_tags
        elif isinstance(self.analyse_content_tags, dict):
            return self.analyse_content_tags.get('tags', [])
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
            "scene": "场景分析",
            "motion": "运动分析",
            "emotion": "情感分析",
            "audio_sync": "音画同步",
            "comprehensive": "综合分析"
        }
        return type_names.get(self.analyse_type, self.analyse_type)