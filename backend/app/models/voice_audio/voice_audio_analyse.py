"""
Voice Audio Analyse Model
音频分析模型 - [voice][audio][analyse]
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import ModelBase

class VoiceAudioAnalyse(ModelBase):
    """
    音频分析表
    [voice][audio][analyse]
    """
    __tablename__ = "voice_audio_analyse"
    
    # 主键
    analyse_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="分析ID")
    
    # 关联信息
    audio_id = Column(Integer, ForeignKey("voice_audio_basic.audio_id"), nullable=False, index=True, comment="音频ID")
    
    # 分析类型和结果
    analyse_type = Column(String(50), nullable=False, index=True, comment="分析类型")
    analyse_result = Column(JSONB, nullable=True, comment="分析结果")
    analyse_summary = Column(Text, nullable=True, comment="分析摘要")
    
    # 质量评估
    analyse_quality_score = Column(DECIMAL(5, 2), nullable=True, comment="质量评分")
    analyse_confidence_score = Column(DECIMAL(5, 2), nullable=True, comment="置信度评分")
    
    # 技术参数
    analyse_volume_level = Column(DECIMAL(5, 2), nullable=True, comment="音量水平")
    analyse_noise_level = Column(DECIMAL(5, 2), nullable=True, comment="噪音水平")
    analyse_clarity_score = Column(DECIMAL(5, 2), nullable=True, comment="清晰度评分")
    
    # 语音特征
    analyse_speech_rate = Column(DECIMAL(5, 2), nullable=True, comment="语速(字/分钟)")
    analyse_pause_count = Column(Integer, nullable=True, comment="停顿次数")
    analyse_emotion_data = Column(JSONB, nullable=True, comment="情感分析数据")
    
    # 用户和时间
    analyse_created_user_id = Column(Integer, ForeignKey("user_auth_basic.user_id"), nullable=False, index=True, comment="创建用户ID")
    analyse_created_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    
    # 状态
    analyse_status = Column(String(20), nullable=False, default="completed", index=True, comment="分析状态")
    
    # 关系映射
    audio = relationship("VoiceAudioBasic", back_populates="analyses")
    created_user = relationship("UserAuthBasic", foreign_keys=[analyse_created_user_id])
    
    def __repr__(self) -> str:
        return f"<VoiceAudioAnalyse(analyse_id={self.analyse_id}, audio_id={self.audio_id}, analyse_type='{self.analyse_type}')>"
    
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
    
    def analyse_volume_level_description(self) -> str:
        """
        获取音量水平描述
        [analyse][volume_level][description]
        """
        if self.analyse_volume_level is None:
            return "未知"
        
        level = float(self.analyse_volume_level)
        if level >= 80:
            return "很大声"
        elif level >= 60:
            return "大声"
        elif level >= 40:
            return "适中"
        elif level >= 20:
            return "小声"
        else:
            return "很小声"
    
    def analyse_noise_level_description(self) -> str:
        """
        获取噪音水平描述
        [analyse][noise_level][description]
        """
        if self.analyse_noise_level is None:
            return "未知"
        
        level = float(self.analyse_noise_level)
        if level >= 80:
            return "噪音很大"
        elif level >= 60:
            return "噪音明显"
        elif level >= 40:
            return "噪音适中"
        elif level >= 20:
            return "噪音轻微"
        else:
            return "几乎无噪音"
    
    def analyse_speech_rate_description(self) -> str:
        """
        获取语速描述
        [analyse][speech_rate][description]
        """
        if self.analyse_speech_rate is None:
            return "未知"
        
        rate = float(self.analyse_speech_rate)
        if rate >= 200:
            return "很快"
        elif rate >= 160:
            return "快"
        elif rate >= 120:
            return "正常"
        elif rate >= 80:
            return "慢"
        else:
            return "很慢"
    
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
    
    def analyse_type_display_name(self) -> str:
        """
        获取分析类型显示名称
        [analyse][type][display_name]
        """
        type_names = {
            "quality": "质量分析",
            "emotion": "情感分析",
            "speech_rate": "语速分析",
            "noise": "噪音检测",
            "volume": "音量分析",
            "clarity": "清晰度分析",
            "comprehensive": "综合分析"
        }
        return type_names.get(self.analyse_type, self.analyse_type)