"""
Text Content Basic Model
文本内容基础模型 - [text][content][basic]
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, ARRAY
from sqlalchemy.orm import relationship
from app.models.base import ModelBase

class TextContentBasic(ModelBase):
    """
    文本内容基础表
    [text][content][basic]
    """
    __tablename__ = "text_content_basic"
    
    # 主键
    text_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="文本ID")
    
    # 内容信息
    text_title = Column(String(200), nullable=False, comment="文本标题")
    text_content = Column(Text, nullable=False, comment="文本内容")
    text_content_type = Column(String(50), nullable=False, index=True, comment="内容类型")
    text_language = Column(String(10), nullable=False, default="zh-CN", comment="语言")
    text_word_count = Column(Integer, nullable=True, comment="字数统计")
    
    # 用户和时间
    text_created_user_id = Column(Integer, ForeignKey("user_auth_basic.user_id"), nullable=False, index=True, comment="创建用户ID")
    text_created_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    text_updated_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    
    # 状态和标签
    text_status = Column(String(20), nullable=False, default="draft", index=True, comment="状态")
    text_tags = Column(ARRAY(String), nullable=True, comment="标签数组")
    
    # 模板关联
    text_template_id = Column(Integer, ForeignKey("text_template_basic.template_id"), nullable=True, comment="模板ID")
    
    # 关系映射
    created_user = relationship("UserAuthBasic", foreign_keys=[text_created_user_id])
    template = relationship("TextTemplateBasic", foreign_keys=[text_template_id])
    analyse_results = relationship("TextAnalyseResult", back_populates="text", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<TextContentBasic(text_id={self.text_id}, text_title='{self.text_title}', text_content_type='{self.text_content_type}')>"
    
    @property
    def text_content_preview(self) -> str:
        """
        获取内容预览（前100字符）
        [text][content][preview]
        """
        if len(self.text_content) <= 100:
            return self.text_content
        return self.text_content[:100] + "..."
    
    def text_word_count_update(self) -> int:
        """
        更新并返回字数统计
        [text][word_count][update]
        """
        # 简单的中文字数统计
        import re
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', self.text_content)
        english_words = re.findall(r'\b[a-zA-Z]+\b', self.text_content)
        self.text_word_count = len(chinese_chars) + len(english_words)
        return self.text_word_count
    
    def text_tags_add(self, tag: str) -> None:
        """
        添加标签
        [text][tags][add]
        """
        if self.text_tags is None:
            self.text_tags = []
        if tag not in self.text_tags:
            self.text_tags = self.text_tags + [tag]
    
    def text_tags_remove(self, tag: str) -> None:
        """
        移除标签
        [text][tags][remove]
        """
        if self.text_tags and tag in self.text_tags:
            self.text_tags = [t for t in self.text_tags if t != tag]
    
    def text_status_is_published(self) -> bool:
        """
        检查是否已发布
        [text][status][is_published]
        """
        return self.text_status == "published"