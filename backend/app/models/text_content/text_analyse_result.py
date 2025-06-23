"""
Text Analyse Result Model
文本分析结果模型 - [text][analyse][result]
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import ModelBase

class TextAnalyseResult(ModelBase):
    """
    文本分析结果表
    [text][analyse][result]
    """
    __tablename__ = "text_analyse_result"
    
    # 主键
    analyse_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="分析ID")
    
    # 关联信息
    text_id = Column(Integer, ForeignKey("text_content_basic.text_id"), nullable=False, index=True, comment="文本ID")
    
    # 分析信息
    analyse_type = Column(String(50), nullable=False, index=True, comment="分析类型")
    analyse_result = Column(JSONB, nullable=False, comment="分析结果JSON")
    analyse_score = Column(DECIMAL(5, 2), nullable=True, comment="分析评分")
    
    # 时间和版本
    analyse_created_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="分析时间")
    analyse_model_version = Column(String(50), nullable=True, comment="模型版本")
    
    # 关系映射
    text = relationship("TextContentBasic", back_populates="analyse_results")
    
    def __repr__(self) -> str:
        return f"<TextAnalyseResult(analyse_id={self.analyse_id}, text_id={self.text_id}, analyse_type='{self.analyse_type}')>"
    
    def analyse_result_get_field(self, field_name: str, default=None):
        """
        获取分析结果中的特定字段
        [analyse][result][get_field]
        """
        if isinstance(self.analyse_result, dict):
            return self.analyse_result.get(field_name, default)
        return default
    
    def analyse_score_grade(self) -> str:
        """
        获取评分等级
        [analyse][score][grade]
        """
        if self.analyse_score is None:
            return "未评分"
        
        score = float(self.analyse_score)
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
    
    def analyse_type_display_name(self) -> str:
        """
        获取分析类型显示名称
        [analyse][type][display_name]
        """
        type_names = {
            "sentiment": "情感分析",
            "keyword": "关键词提取",
            "summary": "内容摘要",
            "readability": "可读性分析",
            "quality": "内容质量"
        }
        return type_names.get(self.analyse_type, self.analyse_type)