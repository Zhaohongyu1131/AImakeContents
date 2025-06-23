"""
Mixed Content Template Model
混合内容模板模型 - [mixed][content][template]
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import ModelBase

class MixedContentTemplate(ModelBase):
    """
    混合内容模板表
    [mixed][content][template]
    """
    __tablename__ = "mixed_content_template"
    
    # 主键
    template_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="模板ID")
    
    # 模板信息
    template_name = Column(String(100), nullable=False, comment="模板名称")
    template_description = Column(Text, nullable=True, comment="模板描述")
    template_type = Column(String(50), nullable=False, index=True, comment="模板类型")
    template_category = Column(String(50), nullable=True, index=True, comment="模板分类")
    
    # 关联模板
    template_text_template_ids = Column(JSONB, nullable=True, comment="文本模板ID数组")
    template_image_template_ids = Column(JSONB, nullable=True, comment="图像模板ID数组")
    template_audio_template_ids = Column(JSONB, nullable=True, comment="音频模板ID数组")
    template_video_template_ids = Column(JSONB, nullable=True, comment="视频模板ID数组")
    
    # 布局和样式配置
    template_layout_config = Column(JSONB, nullable=True, comment="布局配置模板")
    template_style_config = Column(JSONB, nullable=True, comment="样式配置模板")
    template_timing_config = Column(JSONB, nullable=True, comment="时序配置模板")
    template_interaction_config = Column(JSONB, nullable=True, comment="交互配置模板")
    
    # 生成配置
    template_generation_params = Column(JSONB, nullable=True, comment="生成参数配置")
    template_output_config = Column(JSONB, nullable=True, comment="输出配置")
    template_quality_config = Column(JSONB, nullable=True, comment="质量配置")
    
    # 预设内容
    template_default_content = Column(JSONB, nullable=True, comment="默认内容配置")
    template_placeholder_data = Column(JSONB, nullable=True, comment="占位符数据")
    
    # 用户和时间
    template_created_user_id = Column(Integer, ForeignKey("user_auth_basic.user_id"), nullable=False, index=True, comment="创建用户ID")
    template_created_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    
    # 状态和使用统计
    template_status = Column(String(20), nullable=False, default="active", index=True, comment="模板状态")
    template_usage_count = Column(Integer, nullable=False, default=0, comment="使用次数")
    template_rating = Column(Integer, nullable=True, comment="模板评分")
    
    # 关系映射
    created_user = relationship("UserAuthBasic", foreign_keys=[template_created_user_id])
    
    def __repr__(self) -> str:
        return f"<MixedContentTemplate(template_id={self.template_id}, template_name='{self.template_name}', template_type='{self.template_type}')>"
    
    def template_status_is_active(self) -> bool:
        """
        检查模板是否活跃
        [template][status][is_active]
        """
        return self.template_status == "active"
    
    def template_usage_count_increment(self) -> int:
        """
        增加使用次数
        [template][usage_count][increment]
        """
        self.template_usage_count += 1
        return self.template_usage_count
    
    def template_components_count(self) -> dict:
        """
        获取模板组件数量统计
        [template][components][count]
        """
        counts = {
            "text": len(self.template_text_template_ids) if isinstance(self.template_text_template_ids, list) else 0,
            "image": len(self.template_image_template_ids) if isinstance(self.template_image_template_ids, list) else 0,
            "audio": len(self.template_audio_template_ids) if isinstance(self.template_audio_template_ids, list) else 0,
            "video": len(self.template_video_template_ids) if isinstance(self.template_video_template_ids, list) else 0
        }
        counts["total"] = sum(counts.values())
        return counts
    
    def template_components_summary(self) -> str:
        """
        获取模板组件摘要描述
        [template][components][summary]
        """
        counts = self.template_components_count()
        parts = []
        
        if counts["text"] > 0:
            parts.append(f"{counts['text']}个文本模板")
        if counts["image"] > 0:
            parts.append(f"{counts['image']}个图像模板")
        if counts["audio"] > 0:
            parts.append(f"{counts['audio']}个音频模板")
        if counts["video"] > 0:
            parts.append(f"{counts['video']}个视频模板")
        
        if not parts:
            return "无组件模板"
        
        return "、".join(parts)
    
    def template_rating_description(self) -> str:
        """
        获取模板评分描述
        [template][rating][description]
        """
        if self.template_rating is None:
            return "未评分"
        
        rating = self.template_rating
        if rating >= 9:
            return "优秀"
        elif rating >= 7:
            return "良好"
        elif rating >= 5:
            return "一般"
        elif rating >= 3:
            return "较差"
        else:
            return "很差"
    
    def template_layout_config_get_field(self, field_name: str, default=None):
        """
        获取布局配置中的特定字段
        [template][layout_config][get_field]
        """
        if isinstance(self.template_layout_config, dict):
            return self.template_layout_config.get(field_name, default)
        return default
    
    def template_style_config_get_field(self, field_name: str, default=None):
        """
        获取样式配置中的特定字段
        [template][style_config][get_field]
        """
        if isinstance(self.template_style_config, dict):
            return self.template_style_config.get(field_name, default)
        return default
    
    def template_timing_config_get_field(self, field_name: str, default=None):
        """
        获取时序配置中的特定字段
        [template][timing_config][get_field]
        """
        if isinstance(self.template_timing_config, dict):
            return self.template_timing_config.get(field_name, default)
        return default
    
    def template_interaction_config_get_field(self, field_name: str, default=None):
        """
        获取交互配置中的特定字段
        [template][interaction_config][get_field]
        """
        if isinstance(self.template_interaction_config, dict):
            return self.template_interaction_config.get(field_name, default)
        return default
    
    def template_generation_params_get_field(self, field_name: str, default=None):
        """
        获取生成参数中的特定字段
        [template][generation_params][get_field]
        """
        if isinstance(self.template_generation_params, dict):
            return self.template_generation_params.get(field_name, default)
        return default
    
    def template_output_config_get_field(self, field_name: str, default=None):
        """
        获取输出配置中的特定字段
        [template][output_config][get_field]
        """
        if isinstance(self.template_output_config, dict):
            return self.template_output_config.get(field_name, default)
        return default
    
    def template_default_content_get_field(self, field_name: str, default=None):
        """
        获取默认内容中的特定字段
        [template][default_content][get_field]
        """
        if isinstance(self.template_default_content, dict):
            return self.template_default_content.get(field_name, default)
        return default
    
    def template_placeholder_data_get_field(self, field_name: str, default=None):
        """
        获取占位符数据中的特定字段
        [template][placeholder_data][get_field]
        """
        if isinstance(self.template_placeholder_data, dict):
            return self.template_placeholder_data.get(field_name, default)
        return default
    
    def template_layout_config_update(self, config: dict) -> None:
        """
        更新布局配置
        [template][layout_config][update]
        """
        if self.template_layout_config is None:
            self.template_layout_config = {}
        
        if isinstance(self.template_layout_config, dict) and isinstance(config, dict):
            self.template_layout_config = {**self.template_layout_config, **config}
        else:
            self.template_layout_config = config
    
    def template_style_config_update(self, config: dict) -> None:
        """
        更新样式配置
        [template][style_config][update]
        """
        if self.template_style_config is None:
            self.template_style_config = {}
        
        if isinstance(self.template_style_config, dict) and isinstance(config, dict):
            self.template_style_config = {**self.template_style_config, **config}
        else:
            self.template_style_config = config
    
    def template_type_display_name(self) -> str:
        """
        获取模板类型显示名称
        [template][type][display_name]
        """
        type_names = {
            "presentation": "演示文稿模板",
            "video_with_subtitles": "字幕视频模板",
            "audio_with_images": "图文音频模板",
            "interactive_story": "交互故事模板",
            "multimedia_article": "多媒体文章模板",
            "slideshow": "幻灯片模板",
            "podcast": "播客节目模板",
            "tutorial": "教程内容模板",
            "social_media": "社交媒体模板",
            "marketing": "营销内容模板"
        }
        return type_names.get(self.template_type, self.template_type)
    
    def template_category_display_name(self) -> str:
        """
        获取模板分类显示名称
        [template][category][display_name]
        """
        if not self.template_category:
            return "未分类"
        
        category_names = {
            "business": "商务",
            "education": "教育",
            "entertainment": "娱乐",
            "marketing": "营销",
            "technology": "技术",
            "art": "艺术",
            "lifestyle": "生活方式",
            "news": "新闻"
        }
        return category_names.get(self.template_category, self.template_category)