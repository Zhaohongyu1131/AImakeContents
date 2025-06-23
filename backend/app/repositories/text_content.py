"""
Text Content Repository
文本内容数据访问层 - [repositories][text_content]
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from app.repositories.base import RepositoryBase
from app.models.text_content.text_content_basic import TextContentBasic
from app.models.text_content.text_content_analyse import TextContentAnalyse
from app.models.text_content.text_content_template import TextContentTemplate


class TextContentRepository(RepositoryBase[TextContentBasic]):
    """
    文本内容数据访问层
    [repositories][text_content]
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        初始化文本内容仓储
        [repositories][text_content][init]
        """
        super().__init__(db_session, TextContentBasic)
    
    async def text_content_repository_get_by_type(
        self,
        text_type: str,
        user_id: Optional[int] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        根据文本类型获取内容列表
        [repositories][text_content][get_by_type]
        """
        conditions = [
            TextContentBasic.text_type == text_type,
            TextContentBasic.text_status == "active"
        ]
        
        if user_id:
            conditions.append(TextContentBasic.text_created_user_id == user_id)
        
        return await self.repository_base_paginate(
            page=page,
            size=size,
            conditions=conditions,
            order_by="text_created_time"
        )
    
    async def text_content_repository_get_user_texts(
        self,
        user_id: int,
        text_type: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        获取用户文本内容列表
        [repositories][text_content][get_user_texts]
        """
        conditions = [
            TextContentBasic.text_created_user_id == user_id,
            TextContentBasic.text_status == "active"
        ]
        
        if text_type:
            conditions.append(TextContentBasic.text_type == text_type)
        
        return await self.repository_base_paginate(
            page=page,
            size=size,
            conditions=conditions,
            order_by="text_updated_time"
        )
    
    async def text_content_repository_search_texts(
        self,
        search_term: str,
        user_id: Optional[int] = None,
        text_type: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        搜索文本内容
        [repositories][text_content][search_texts]
        """
        conditions = [TextContentBasic.text_status == "active"]
        
        if user_id:
            conditions.append(TextContentBasic.text_created_user_id == user_id)
        
        if text_type:
            conditions.append(TextContentBasic.text_type == text_type)
        
        return await self.repository_base_search(
            search_fields=["text_title", "text_content"],
            search_term=search_term,
            conditions=conditions,
            page=page,
            size=size
        )
    
    async def text_content_repository_get_by_template(
        self,
        template_id: int,
        user_id: Optional[int] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        根据模板获取文本内容列表
        [repositories][text_content][get_by_template]
        """
        conditions = [
            TextContentBasic.text_template_id == template_id,
            TextContentBasic.text_status == "active"
        ]
        
        if user_id:
            conditions.append(TextContentBasic.text_created_user_id == user_id)
        
        return await self.repository_base_paginate(
            page=page,
            size=size,
            conditions=conditions,
            order_by="text_created_time"
        )
    
    async def text_content_repository_soft_delete_text(
        self,
        text_id: int,
        deleted_user_id: int
    ) -> Optional[TextContentBasic]:
        """
        软删除文本内容
        [repositories][text_content][soft_delete_text]
        """
        return await self.repository_base_update(
            text_id,
            text_status="deleted",
            text_deleted_time=datetime.utcnow(),
            text_deleted_user_id=deleted_user_id
        )
    
    async def text_content_repository_get_text_stats(
        self,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        获取文本内容统计信息
        [repositories][text_content][get_text_stats]
        """
        conditions = [TextContentBasic.text_status == "active"]
        
        if user_id:
            conditions.append(TextContentBasic.text_created_user_id == user_id)
        
        # 文本总数
        total_texts = await self.repository_base_count(conditions)
        
        # 总字数
        word_count_stmt = select(func.sum(TextContentBasic.text_word_count)).where(
            and_(*conditions)
        )
        word_result = await self.db.execute(word_count_stmt)
        total_words = word_result.scalar() or 0
        
        # 总字符数
        char_count_stmt = select(func.sum(TextContentBasic.text_character_count)).where(
            and_(*conditions)
        )
        char_result = await self.db.execute(char_count_stmt)
        total_characters = char_result.scalar() or 0
        
        # 按类型统计
        type_stmt = select(
            TextContentBasic.text_type,
            func.count(TextContentBasic.text_id).label("count"),
            func.sum(TextContentBasic.text_word_count).label("words")
        ).where(and_(*conditions)).group_by(TextContentBasic.text_type)
        
        type_result = await self.db.execute(type_stmt)
        type_distribution = {
            row.text_type: {"count": row.count, "words": row.words or 0}
            for row in type_result
        }
        
        return {
            "total_texts": total_texts,
            "total_words": total_words,
            "total_characters": total_characters,
            "type_distribution": type_distribution
        }
    
    async def text_content_repository_get_recent_texts(
        self,
        user_id: Optional[int] = None,
        days: int = 7,
        limit: int = 10
    ) -> List[TextContentBasic]:
        """
        获取最近创建的文本内容
        [repositories][text_content][get_recent_texts]
        """
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        conditions = [
            TextContentBasic.text_created_time >= cutoff_date,
            TextContentBasic.text_status == "active"
        ]
        
        if user_id:
            conditions.append(TextContentBasic.text_created_user_id == user_id)
        
        return await self.repository_base_get_all(
            conditions=conditions,
            order_by="text_created_time",
            limit=limit
        )
    
    async def text_content_repository_get_popular_texts(
        self,
        user_id: Optional[int] = None,
        limit: int = 10
    ) -> List[TextContentBasic]:
        """
        获取热门文本内容（按使用次数排序）
        [repositories][text_content][get_popular_texts]
        """
        conditions = [TextContentBasic.text_status == "active"]
        
        if user_id:
            conditions.append(TextContentBasic.text_created_user_id == user_id)
        
        # 这里假设有使用次数字段，如果没有可以通过关联查询音频生成记录
        return await self.repository_base_get_all(
            conditions=conditions,
            order_by="text_updated_time",  # 暂时按更新时间排序
            limit=limit
        )


class TextContentAnalyseRepository(RepositoryBase[TextContentAnalyse]):
    """
    文本内容分析数据访问层
    [repositories][text_content][analyse]
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        初始化文本分析仓储
        [repositories][text_content][analyse][init]
        """
        super().__init__(db_session, TextContentAnalyse)
    
    async def text_content_analyse_repository_get_by_text_id(
        self,
        text_id: int
    ) -> List[TextContentAnalyse]:
        """
        根据文本ID获取所有分析结果
        [repositories][text_content][analyse][get_by_text_id]
        """
        return await self.repository_base_get_all(
            conditions=[TextContentAnalyse.text_id == text_id],
            order_by="analyse_created_time"
        )
    
    async def text_content_analyse_repository_get_by_type(
        self,
        text_id: int,
        analyse_type: str
    ) -> List[TextContentAnalyse]:
        """
        根据文本ID和分析类型获取分析结果
        [repositories][text_content][analyse][get_by_type]
        """
        conditions = [
            TextContentAnalyse.text_id == text_id,
            TextContentAnalyse.analyse_type == analyse_type
        ]
        
        return await self.repository_base_get_all(
            conditions=conditions,
            order_by="analyse_created_time"
        )
    
    async def text_content_analyse_repository_get_latest_analysis(
        self,
        text_id: int,
        analyse_type: str
    ) -> Optional[TextContentAnalyse]:
        """
        获取最新的分析结果
        [repositories][text_content][analyse][get_latest_analysis]
        """
        stmt = select(TextContentAnalyse).where(
            and_(
                TextContentAnalyse.text_id == text_id,
                TextContentAnalyse.analyse_type == analyse_type,
                TextContentAnalyse.analyse_status == "completed"
            )
        ).order_by(TextContentAnalyse.analyse_created_time.desc()).limit(1)
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def text_content_analyse_repository_get_analysis_stats(
        self,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        获取分析统计信息
        [repositories][text_content][analyse][get_analysis_stats]
        """
        base_conditions = [TextContentAnalyse.analyse_status == "completed"]
        
        if user_id:
            base_conditions.append(TextContentAnalyse.analyse_created_user_id == user_id)
        
        # 总分析数
        total_analyses = await self.repository_base_count(base_conditions)
        
        # 按类型统计
        type_stmt = select(
            TextContentAnalyse.analyse_type,
            func.count(TextContentAnalyse.analyse_id).label("count"),
            func.avg(TextContentAnalyse.analyse_score).label("avg_score")
        ).where(and_(*base_conditions)).group_by(TextContentAnalyse.analyse_type)
        
        type_result = await self.db.execute(type_stmt)
        type_distribution = {
            row.analyse_type: {
                "count": row.count,
                "avg_score": float(row.avg_score or 0)
            }
            for row in type_result
        }
        
        return {
            "total_analyses": total_analyses,
            "type_distribution": type_distribution
        }
    
    async def text_content_analyse_repository_cleanup_old_analyses(
        self,
        days_old: int = 90,
        keep_latest: int = 5
    ) -> int:
        """
        清理旧的分析记录（保留最新的几条）
        [repositories][text_content][analyse][cleanup_old_analyses]
        """
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # 获取需要清理的分析记录
        # 这里需要复杂的查询来保留每个文本的最新几条分析记录
        # 简化实现：只删除超过指定天数的记录
        from sqlalchemy import delete
        
        stmt = delete(TextContentAnalyse).where(
            and_(
                TextContentAnalyse.analyse_created_time <= cutoff_date,
                TextContentAnalyse.analyse_status == "completed"
            )
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount


class TextContentTemplateRepository(RepositoryBase[TextContentTemplate]):
    """
    文本内容模板数据访问层
    [repositories][text_content][template]
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        初始化文本模板仓储
        [repositories][text_content][template][init]
        """
        super().__init__(db_session, TextContentTemplate)
    
    async def text_content_template_repository_get_by_type(
        self,
        template_type: str,
        user_id: Optional[int] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        根据模板类型获取模板列表
        [repositories][text_content][template][get_by_type]
        """
        conditions = [
            TextContentTemplate.template_type == template_type,
            TextContentTemplate.template_status == "active"
        ]
        
        if user_id:
            conditions.append(TextContentTemplate.template_created_user_id == user_id)
        
        return await self.repository_base_paginate(
            page=page,
            size=size,
            conditions=conditions,
            order_by="template_created_time"
        )
    
    async def text_content_template_repository_get_public_templates(
        self,
        template_type: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        获取公共模板列表
        [repositories][text_content][template][get_public_templates]
        """
        conditions = [
            TextContentTemplate.template_status == "active",
            TextContentTemplate.template_is_public == True
        ]
        
        if template_type:
            conditions.append(TextContentTemplate.template_type == template_type)
        
        return await self.repository_base_paginate(
            page=page,
            size=size,
            conditions=conditions,
            order_by="template_usage_count"
        )
    
    async def text_content_template_repository_get_user_templates(
        self,
        user_id: int,
        template_type: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        获取用户模板列表
        [repositories][text_content][template][get_user_templates]
        """
        conditions = [
            TextContentTemplate.template_created_user_id == user_id,
            TextContentTemplate.template_status == "active"
        ]
        
        if template_type:
            conditions.append(TextContentTemplate.template_type == template_type)
        
        return await self.repository_base_paginate(
            page=page,
            size=size,
            conditions=conditions,
            order_by="template_updated_time"
        )
    
    async def text_content_template_repository_search_templates(
        self,
        search_term: str,
        user_id: Optional[int] = None,
        template_type: Optional[str] = None,
        include_public: bool = True,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        搜索模板
        [repositories][text_content][template][search_templates]
        """
        conditions = [TextContentTemplate.template_status == "active"]
        
        # 构建权限条件
        permission_conditions = []
        if user_id:
            permission_conditions.append(
                TextContentTemplate.template_created_user_id == user_id
            )
        if include_public:
            permission_conditions.append(
                TextContentTemplate.template_is_public == True
            )
        
        if permission_conditions:
            conditions.append(or_(*permission_conditions))
        
        if template_type:
            conditions.append(TextContentTemplate.template_type == template_type)
        
        return await self.repository_base_search(
            search_fields=["template_name", "template_description"],
            search_term=search_term,
            conditions=conditions,
            page=page,
            size=size
        )
    
    async def text_content_template_repository_increment_usage(
        self,
        template_id: int
    ) -> Optional[TextContentTemplate]:
        """
        增加模板使用次数
        [repositories][text_content][template][increment_usage]
        """
        template = await self.repository_base_get_by_id(template_id)
        if template:
            current_count = template.template_usage_count or 0
            return await self.repository_base_update(
                template_id,
                template_usage_count=current_count + 1,
                template_updated_time=datetime.utcnow()
            )
        return None
    
    async def text_content_template_repository_get_popular_templates(
        self,
        template_type: Optional[str] = None,
        limit: int = 10,
        days: int = 30
    ) -> List[TextContentTemplate]:
        """
        获取热门模板
        [repositories][text_content][template][get_popular_templates]
        """
        from datetime import timedelta
        
        conditions = [
            TextContentTemplate.template_status == "active",
            TextContentTemplate.template_is_public == True
        ]
        
        if template_type:
            conditions.append(TextContentTemplate.template_type == template_type)
        
        # 可以根据最近使用情况或使用次数排序
        return await self.repository_base_get_all(
            conditions=conditions,
            order_by="template_usage_count",
            limit=limit
        )