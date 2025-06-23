"""
Voice Timbre Repository
音色管理数据访问层 - [repositories][voice_timbre]
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.repositories.base import RepositoryBase
from app.models.voice_timbre.voice_timbre_basic import VoiceTimbreBasic
from app.models.voice_timbre.voice_timbre_clone import VoiceTimbreClone
from app.models.voice_timbre.voice_timbre_template import VoiceTimbreTemplate


class VoiceTimbreRepository(RepositoryBase[VoiceTimbreBasic]):
    """
    音色管理数据访问层
    [repositories][voice_timbre]
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        初始化音色管理仓储
        [repositories][voice_timbre][init]
        """
        super().__init__(db_session, VoiceTimbreBasic)
    
    async def voice_timbre_repository_get_by_name(
        self,
        timbre_name: str,
        user_id: Optional[int] = None
    ) -> Optional[VoiceTimbreBasic]:
        """
        根据音色名称获取音色
        [repositories][voice_timbre][get_by_name]
        """
        conditions = [VoiceTimbreBasic.timbre_name == timbre_name]
        
        if user_id:
            conditions.append(VoiceTimbreBasic.timbre_created_user_id == user_id)
        
        stmt = select(VoiceTimbreBasic).where(and_(*conditions))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def voice_timbre_repository_get_by_platform(
        self,
        platform: str,
        user_id: Optional[int] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        根据平台获取音色列表
        [repositories][voice_timbre][get_by_platform]
        """
        conditions = [
            VoiceTimbreBasic.timbre_platform == platform,
            VoiceTimbreBasic.timbre_status != "deleted"
        ]
        
        if user_id:
            conditions.append(VoiceTimbreBasic.timbre_created_user_id == user_id)
        
        return await self.repository_base_paginate(
            page=page,
            size=size,
            conditions=conditions,
            order_by="timbre_created_time"
        )
    
    async def voice_timbre_repository_get_by_characteristics(
        self,
        gender: Optional[str] = None,
        language: Optional[str] = None,
        age_range: Optional[str] = None,
        style: Optional[str] = None,
        user_id: Optional[int] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        根据音色特征获取音色列表
        [repositories][voice_timbre][get_by_characteristics]
        """
        conditions = [VoiceTimbreBasic.timbre_status != "deleted"]
        
        if gender:
            conditions.append(VoiceTimbreBasic.timbre_gender == gender)
        
        if language:
            conditions.append(VoiceTimbreBasic.timbre_language == language)
        
        if age_range:
            conditions.append(VoiceTimbreBasic.timbre_age_range == age_range)
        
        if style:
            conditions.append(VoiceTimbreBasic.timbre_style == style)
        
        if user_id:
            conditions.append(VoiceTimbreBasic.timbre_created_user_id == user_id)
        
        return await self.repository_base_paginate(
            page=page,
            size=size,
            conditions=conditions,
            order_by="timbre_quality_score"
        )
    
    async def voice_timbre_repository_get_ready_timbres(
        self,
        user_id: Optional[int] = None,
        platform: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        获取可用的音色列表
        [repositories][voice_timbre][get_ready_timbres]
        """
        conditions = [VoiceTimbreBasic.timbre_status == "ready"]
        
        if user_id:
            conditions.append(VoiceTimbreBasic.timbre_created_user_id == user_id)
        
        if platform:
            conditions.append(VoiceTimbreBasic.timbre_platform == platform)
        
        return await self.repository_base_paginate(
            page=page,
            size=size,
            conditions=conditions,
            order_by="timbre_quality_score"
        )
    
    async def voice_timbre_repository_search_timbres(
        self,
        search_term: str,
        user_id: Optional[int] = None,
        platform: Optional[str] = None,
        gender: Optional[str] = None,
        language: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        搜索音色
        [repositories][voice_timbre][search_timbres]
        """
        conditions = [VoiceTimbreBasic.timbre_status != "deleted"]
        
        if user_id:
            conditions.append(VoiceTimbreBasic.timbre_created_user_id == user_id)
        
        if platform:
            conditions.append(VoiceTimbreBasic.timbre_platform == platform)
        
        if gender:
            conditions.append(VoiceTimbreBasic.timbre_gender == gender)
        
        if language:
            conditions.append(VoiceTimbreBasic.timbre_language == language)
        
        return await self.repository_base_search(
            search_fields=["timbre_name", "timbre_description"],
            search_term=search_term,
            conditions=conditions,
            page=page,
            size=size
        )
    
    async def voice_timbre_repository_get_high_quality_timbres(
        self,
        min_score: float = 80.0,
        user_id: Optional[int] = None,
        limit: int = 20
    ) -> List[VoiceTimbreBasic]:
        """
        获取高质量音色列表
        [repositories][voice_timbre][get_high_quality_timbres]
        """
        conditions = [
            VoiceTimbreBasic.timbre_status == "ready",
            VoiceTimbreBasic.timbre_quality_score >= min_score
        ]
        
        if user_id:
            conditions.append(VoiceTimbreBasic.timbre_created_user_id == user_id)
        
        return await self.repository_base_get_all(
            conditions=conditions,
            order_by="timbre_quality_score",
            limit=limit
        )
    
    async def voice_timbre_repository_soft_delete_timbre(
        self,
        timbre_id: int,
        deleted_user_id: int
    ) -> Optional[VoiceTimbreBasic]:
        """
        软删除音色
        [repositories][voice_timbre][soft_delete_timbre]
        """
        return await self.repository_base_update(
            timbre_id,
            timbre_status="deleted",
            timbre_deleted_time=datetime.utcnow(),
            timbre_deleted_user_id=deleted_user_id
        )
    
    async def voice_timbre_repository_update_quality_score(
        self,
        timbre_id: int,
        quality_score: float
    ) -> Optional[VoiceTimbreBasic]:
        """
        更新音色质量评分
        [repositories][voice_timbre][update_quality_score]
        """
        return await self.repository_base_update(
            timbre_id,
            timbre_quality_score=quality_score,
            timbre_updated_time=datetime.utcnow()
        )
    
    async def voice_timbre_repository_get_timbre_stats(
        self,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        获取音色统计信息
        [repositories][voice_timbre][get_timbre_stats]
        """
        conditions = [VoiceTimbreBasic.timbre_status != "deleted"]
        
        if user_id:
            conditions.append(VoiceTimbreBasic.timbre_created_user_id == user_id)
        
        # 音色总数
        total_timbres = await self.repository_base_count(conditions)
        
        # 按平台统计
        platform_stmt = select(
            VoiceTimbreBasic.timbre_platform,
            func.count(VoiceTimbreBasic.timbre_id).label("count")
        ).where(and_(*conditions)).group_by(VoiceTimbreBasic.timbre_platform)
        
        platform_result = await self.db.execute(platform_stmt)
        platform_distribution = {row.timbre_platform: row.count for row in platform_result}
        
        # 按性别统计
        gender_stmt = select(
            VoiceTimbreBasic.timbre_gender,
            func.count(VoiceTimbreBasic.timbre_id).label("count")
        ).where(and_(*conditions)).group_by(VoiceTimbreBasic.timbre_gender)
        
        gender_result = await self.db.execute(gender_stmt)
        gender_distribution = {row.timbre_gender: row.count for row in gender_result}
        
        # 按语言统计
        language_stmt = select(
            VoiceTimbreBasic.timbre_language,
            func.count(VoiceTimbreBasic.timbre_id).label("count")
        ).where(and_(*conditions)).group_by(VoiceTimbreBasic.timbre_language)
        
        language_result = await self.db.execute(language_stmt)
        language_distribution = {row.timbre_language: row.count for row in language_result}
        
        # 按状态统计
        status_stmt = select(
            VoiceTimbreBasic.timbre_status,
            func.count(VoiceTimbreBasic.timbre_id).label("count")
        ).where(and_(*conditions)).group_by(VoiceTimbreBasic.timbre_status)
        
        status_result = await self.db.execute(status_stmt)
        status_distribution = {row.timbre_status: row.count for row in status_result}
        
        # 平均质量评分
        avg_score_stmt = select(func.avg(VoiceTimbreBasic.timbre_quality_score)).where(
            and_(*conditions, VoiceTimbreBasic.timbre_quality_score.isnot(None))
        )
        avg_result = await self.db.execute(avg_score_stmt)
        avg_quality_score = float(avg_result.scalar() or 0)
        
        return {
            "total_timbres": total_timbres,
            "platform_distribution": platform_distribution,
            "gender_distribution": gender_distribution,
            "language_distribution": language_distribution,
            "status_distribution": status_distribution,
            "avg_quality_score": avg_quality_score
        }
    
    async def voice_timbre_repository_get_popular_timbres(
        self,
        user_id: Optional[int] = None,
        days: int = 30,
        limit: int = 10
    ) -> List[VoiceTimbreBasic]:
        """
        获取热门音色（基于使用频率）
        [repositories][voice_timbre][get_popular_timbres]
        """
        conditions = [VoiceTimbreBasic.timbre_status == "ready"]
        
        if user_id:
            conditions.append(VoiceTimbreBasic.timbre_created_user_id == user_id)
        
        # 这里可以通过关联查询音频生成记录来统计使用频率
        # 目前简化实现：按质量评分排序
        return await self.repository_base_get_all(
            conditions=conditions,
            order_by="timbre_quality_score",
            limit=limit
        )


class VoiceTimbreCloneRepository(RepositoryBase[VoiceTimbreClone]):
    """
    音色克隆数据访问层
    [repositories][voice_timbre][clone]
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        初始化音色克隆仓储
        [repositories][voice_timbre][clone][init]
        """
        super().__init__(db_session, VoiceTimbreClone)
    
    async def voice_timbre_clone_repository_get_by_timbre_id(
        self,
        timbre_id: int
    ) -> List[VoiceTimbreClone]:
        """
        根据音色ID获取克隆记录
        [repositories][voice_timbre][clone][get_by_timbre_id]
        """
        return await self.repository_base_get_all(
            conditions=[VoiceTimbreClone.timbre_id == timbre_id],
            order_by="clone_created_time"
        )
    
    async def voice_timbre_clone_repository_get_active_clones(
        self,
        user_id: Optional[int] = None
    ) -> List[VoiceTimbreClone]:
        """
        获取进行中的克隆任务
        [repositories][voice_timbre][clone][get_active_clones]
        """
        conditions = [VoiceTimbreClone.clone_status.in_(["pending", "training"])]
        
        if user_id:
            conditions.append(VoiceTimbreClone.clone_created_user_id == user_id)
        
        return await self.repository_base_get_all(
            conditions=conditions,
            order_by="clone_created_time"
        )
    
    async def voice_timbre_clone_repository_update_progress(
        self,
        clone_id: int,
        progress: int,
        status: Optional[str] = None
    ) -> Optional[VoiceTimbreClone]:
        """
        更新克隆进度
        [repositories][voice_timbre][clone][update_progress]
        """
        update_data = {"clone_progress": progress}
        
        if status:
            update_data["clone_status"] = status
            
            if status == "completed":
                update_data["clone_completed_time"] = datetime.utcnow()
        
        return await self.repository_base_update(clone_id, **update_data)
    
    async def voice_timbre_clone_repository_mark_failed(
        self,
        clone_id: int,
        error_message: str
    ) -> Optional[VoiceTimbreClone]:
        """
        标记克隆失败
        [repositories][voice_timbre][clone][mark_failed]
        """
        return await self.repository_base_update(
            clone_id,
            clone_status="failed",
            clone_error_message=error_message,
            clone_completed_time=datetime.utcnow()
        )
    
    async def voice_timbre_clone_repository_get_clone_stats(
        self,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        获取克隆统计信息
        [repositories][voice_timbre][clone][get_clone_stats]
        """
        base_conditions = []
        
        if user_id:
            base_conditions.append(VoiceTimbreClone.clone_created_user_id == user_id)
        
        # 总克隆数
        total_clones = await self.repository_base_count(base_conditions)
        
        # 按状态统计
        status_stmt = select(
            VoiceTimbreClone.clone_status,
            func.count(VoiceTimbreClone.clone_id).label("count")
        ).where(and_(*base_conditions) if base_conditions else True).group_by(
            VoiceTimbreClone.clone_status
        )
        
        status_result = await self.db.execute(status_stmt)
        status_distribution = {row.clone_status: row.count for row in status_result}
        
        # 成功率
        completed_count = status_distribution.get("completed", 0)
        failed_count = status_distribution.get("failed", 0)
        total_finished = completed_count + failed_count
        
        success_rate = completed_count / total_finished if total_finished > 0 else 0
        
        return {
            "total_clones": total_clones,
            "status_distribution": status_distribution,
            "success_rate": success_rate
        }


class VoiceTimbreTemplateRepository(RepositoryBase[VoiceTimbreTemplate]):
    """
    音色模板数据访问层
    [repositories][voice_timbre][template]
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        初始化音色模板仓储
        [repositories][voice_timbre][template][init]
        """
        super().__init__(db_session, VoiceTimbreTemplate)
    
    async def voice_timbre_template_repository_get_by_timbre_id(
        self,
        timbre_id: int,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        根据音色ID获取模板列表
        [repositories][voice_timbre][template][get_by_timbre_id]
        """
        conditions = [
            VoiceTimbreTemplate.template_timbre_id == timbre_id,
            VoiceTimbreTemplate.template_status == "active"
        ]
        
        return await self.repository_base_paginate(
            page=page,
            size=size,
            conditions=conditions,
            order_by="template_created_time"
        )
    
    async def voice_timbre_template_repository_get_public_templates(
        self,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        获取公共音色模板
        [repositories][voice_timbre][template][get_public_templates]
        """
        conditions = [
            VoiceTimbreTemplate.template_status == "active",
            VoiceTimbreTemplate.template_is_public == True
        ]
        
        return await self.repository_base_paginate(
            page=page,
            size=size,
            conditions=conditions,
            order_by="template_usage_count"
        )
    
    async def voice_timbre_template_repository_get_user_templates(
        self,
        user_id: int,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        获取用户音色模板
        [repositories][voice_timbre][template][get_user_templates]
        """
        conditions = [
            VoiceTimbreTemplate.template_created_user_id == user_id,
            VoiceTimbreTemplate.template_status == "active"
        ]
        
        return await self.repository_base_paginate(
            page=page,
            size=size,
            conditions=conditions,
            order_by="template_updated_time"
        )
    
    async def voice_timbre_template_repository_increment_usage(
        self,
        template_id: int
    ) -> Optional[VoiceTimbreTemplate]:
        """
        增加模板使用次数
        [repositories][voice_timbre][template][increment_usage]
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
    
    async def voice_timbre_template_repository_get_popular_templates(
        self,
        limit: int = 10
    ) -> List[VoiceTimbreTemplate]:
        """
        获取热门音色模板
        [repositories][voice_timbre][template][get_popular_templates]
        """
        conditions = [
            VoiceTimbreTemplate.template_status == "active",
            VoiceTimbreTemplate.template_is_public == True
        ]
        
        return await self.repository_base_get_all(
            conditions=conditions,
            order_by="template_usage_count",
            limit=limit
        )