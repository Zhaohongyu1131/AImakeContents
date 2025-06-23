"""
Mixed Content Analyse Model
混合内容分析模型 - [mixed][content][analyse]
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import ModelBase

class MixedContentAnalyse(ModelBase):
    """
    混合内容分析表
    [mixed][content][analyse]
    """
    __tablename__ = "mixed_content_analyse"
    
    # 主键
    analyse_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="分析ID")
    
    # 关联信息
    content_id = Column(Integer, ForeignKey("mixed_content_basic.content_id"), nullable=False, index=True, comment="混合内容ID")
    
    # 分析类型和结果
    analyse_type = Column(String(50), nullable=False, index=True, comment="分析类型")
    analyse_result = Column(JSONB, nullable=True, comment="分析结果")
    analyse_summary = Column(Text, nullable=True, comment="分析摘要")
    
    # 质量评估
    analyse_quality_score = Column(DECIMAL(5, 2), nullable=True, comment="质量评分")
    analyse_confidence_score = Column(DECIMAL(5, 2), nullable=True, comment="置信度评分")
    
    # 组合评估
    analyse_coherence_score = Column(DECIMAL(5, 2), nullable=True, comment="连贯性评分")
    analyse_synchronization_score = Column(DECIMAL(5, 2), nullable=True, comment="同步性评分")
    analyse_engagement_score = Column(DECIMAL(5, 2), nullable=True, comment="参与度评分")
    analyse_effectiveness_score = Column(DECIMAL(5, 2), nullable=True, comment="有效性评分")
    
    # 技术参数
    analyse_load_time = Column(DECIMAL(10, 2), nullable=True, comment="加载时间(秒)")
    analyse_file_size = Column(Integer, nullable=True, comment="文件大小(字节)")
    analyse_compatibility_score = Column(DECIMAL(5, 2), nullable=True, comment="兼容性评分")
    
    # 内容分析
    analyse_content_balance = Column(JSONB, nullable=True, comment="内容平衡分析")
    analyse_user_flow = Column(JSONB, nullable=True, comment="用户流程分析")
    analyse_accessibility = Column(JSONB, nullable=True, comment="可访问性分析")
    
    # 用户和时间
    analyse_created_user_id = Column(Integer, ForeignKey("user_auth_basic.user_id"), nullable=False, index=True, comment="创建用户ID")
    analyse_created_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    
    # 状态
    analyse_status = Column(String(20), nullable=False, default="completed", index=True, comment="分析状态")
    
    # 关系映射
    content = relationship("MixedContentBasic", back_populates="analyses")
    created_user = relationship("UserAuthBasic", foreign_keys=[analyse_created_user_id])
    
    def __repr__(self) -> str:
        return f"<MixedContentAnalyse(analyse_id={self.analyse_id}, content_id={self.content_id}, analyse_type='{self.analyse_type}')>"
    
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
    
    def analyse_coherence_description(self) -> str:
        """
        获取连贯性描述
        [analyse][coherence][description]
        """
        if self.analyse_coherence_score is None:
            return "未知"
        
        score = float(self.analyse_coherence_score)
        if score >= 90:
            return "连贯性极佳"
        elif score >= 80:
            return "连贯性良好"
        elif score >= 70:
            return "连贯性一般"
        elif score >= 60:
            return "连贯性较差"
        else:
            return "连贯性很差"
    
    def analyse_synchronization_description(self) -> str:
        """
        获取同步性描述
        [analyse][synchronization][description]
        """
        if self.analyse_synchronization_score is None:
            return "未知"
        
        score = float(self.analyse_synchronization_score)
        if score >= 90:
            return "同步性极佳"
        elif score >= 80:
            return "同步性良好"
        elif score >= 70:
            return "同步性一般"
        elif score >= 60:
            return "同步性较差"
        else:
            return "同步性很差"
    
    def analyse_engagement_description(self) -> str:
        """
        获取参与度描述
        [analyse][engagement][description]
        """
        if self.analyse_engagement_score is None:
            return "未知"
        
        score = float(self.analyse_engagement_score)
        if score >= 90:
            return "参与度极高"
        elif score >= 80:
            return "参与度较高"
        elif score >= 70:
            return "参与度一般"
        elif score >= 60:
            return "参与度较低"
        else:
            return "参与度很低"
    
    def analyse_effectiveness_description(self) -> str:
        """
        获取有效性描述
        [analyse][effectiveness][description]
        """
        if self.analyse_effectiveness_score is None:
            return "未知"
        
        score = float(self.analyse_effectiveness_score)
        if score >= 90:
            return "非常有效"
        elif score >= 80:
            return "比较有效"
        elif score >= 70:
            return "一般有效"
        elif score >= 60:
            return "效果较差"
        else:
            return "效果很差"
    
    def analyse_load_time_description(self) -> str:
        """
        获取加载时间描述
        [analyse][load_time][description]
        """
        if self.analyse_load_time is None:
            return "未知"
        
        time = float(self.analyse_load_time)
        if time <= 1:
            return "加载很快"
        elif time <= 3:
            return "加载较快"
        elif time <= 5:
            return "加载一般"
        elif time <= 10:
            return "加载较慢"
        else:
            return "加载很慢"
    
    def analyse_file_size_human_readable(self) -> str:
        """
        获取人类可读的文件大小
        [analyse][file_size][human_readable]
        """
        if self.analyse_file_size is None:
            return "未知"
        
        size = self.analyse_file_size
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.1f} {units[unit_index]}"
    
    def analyse_compatibility_description(self) -> str:
        """
        获取兼容性描述
        [analyse][compatibility][description]
        """
        if self.analyse_compatibility_score is None:
            return "未知"
        
        score = float(self.analyse_compatibility_score)
        if score >= 90:
            return "兼容性极佳"
        elif score >= 80:
            return "兼容性良好"
        elif score >= 70:
            return "兼容性一般"
        elif score >= 60:
            return "兼容性较差"
        else:
            return "兼容性很差"
    
    def analyse_result_get_field(self, field_name: str, default=None):
        """
        获取分析结果中的特定字段
        [analyse][result][get_field]
        """
        if isinstance(self.analyse_result, dict):
            return self.analyse_result.get(field_name, default)
        return default
    
    def analyse_content_balance_get_field(self, field_name: str, default=None):
        """
        获取内容平衡分析中的特定字段
        [analyse][content_balance][get_field]
        """
        if isinstance(self.analyse_content_balance, dict):
            return self.analyse_content_balance.get(field_name, default)
        return default
    
    def analyse_user_flow_get_field(self, field_name: str, default=None):
        """
        获取用户流程分析中的特定字段
        [analyse][user_flow][get_field]
        """
        if isinstance(self.analyse_user_flow, dict):
            return self.analyse_user_flow.get(field_name, default)
        return default
    
    def analyse_accessibility_get_field(self, field_name: str, default=None):
        """
        获取可访问性分析中的特定字段
        [analyse][accessibility][get_field]
        """
        if isinstance(self.analyse_accessibility, dict):
            return self.analyse_accessibility.get(field_name, default)
        return default
    
    def analyse_type_display_name(self) -> str:
        """
        获取分析类型显示名称
        [analyse][type][display_name]
        """
        type_names = {
            "quality": "质量分析",
            "coherence": "连贯性分析",
            "synchronization": "同步性分析",
            "engagement": "参与度分析",
            "effectiveness": "有效性分析",
            "performance": "性能分析",
            "accessibility": "可访问性分析",
            "user_experience": "用户体验分析",
            "comprehensive": "综合分析"
        }
        return type_names.get(self.analyse_type, self.analyse_type)