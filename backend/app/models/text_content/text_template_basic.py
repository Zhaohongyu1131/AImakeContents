"""
Text Template Basic Model
文本模板基础模型 - [text][template][basic]
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import ModelBase

class TextTemplateBasic(ModelBase):
    """
    文本模板基础表
    [text][template][basic]
    """
    __tablename__ = "text_template_basic"
    
    # 主键
    template_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="模板ID")
    
    # 模板信息
    template_name = Column(String(100), nullable=False, comment="模板名称")
    template_description = Column(Text, nullable=True, comment="模板描述")
    template_content = Column(Text, nullable=False, comment="模板内容")
    template_type = Column(String(50), nullable=False, index=True, comment="模板类型")
    template_variables = Column(JSONB, nullable=True, comment="模板变量定义")
    
    # 用户和时间
    template_created_user_id = Column(Integer, ForeignKey("user_auth_basic.user_id"), nullable=False, index=True, comment="创建用户ID")
    template_created_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    
    # 状态和使用统计
    template_status = Column(String(20), nullable=False, default="active", index=True, comment="模板状态")
    template_usage_count = Column(Integer, nullable=False, default=0, comment="使用次数")
    
    # 关系映射
    created_user = relationship("UserAuthBasic", foreign_keys=[template_created_user_id])
    text_contents = relationship("TextContentBasic", back_populates="template")
    
    def __repr__(self) -> str:
        return f"<TextTemplateBasic(template_id={self.template_id}, template_name='{self.template_name}', template_type='{self.template_type}')>"
    
    def template_variables_get_list(self) -> list:
        """
        获取模板变量列表
        [template][variables][get_list]
        """
        if isinstance(self.template_variables, dict):
            return list(self.template_variables.keys())
        return []
    
    def template_content_render(self, variables: dict = None) -> str:
        """
        渲染模板内容
        [template][content][render]
        """
        content = self.template_content
        if variables and isinstance(variables, dict):
            for key, value in variables.items():
                placeholder = f"{{{key}}}"
                content = content.replace(placeholder, str(value))
        return content
    
    def template_usage_count_increment(self) -> int:
        """
        增加使用次数
        [template][usage_count][increment]
        """
        self.template_usage_count += 1
        return self.template_usage_count
    
    def template_status_is_active(self) -> bool:
        """
        检查模板是否活跃
        [template][status][is_active]
        """
        return self.template_status == "active"
    
    def template_type_display_name(self) -> str:
        """
        获取模板类型显示名称
        [template][type][display_name]
        """
        type_names = {
            "prompt": "提示词模板",
            "structure": "结构模板",
            "format": "格式模板",
            "article": "文章模板",
            "script": "脚本模板"
        }
        return type_names.get(self.template_type, self.template_type)