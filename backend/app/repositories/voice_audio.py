"""
Voice Audio Repository
音频管理数据访问层 - [repositories][voice_audio]
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.repositories.base import RepositoryBase
from app.models.voice_audio.voice_audio_basic import VoiceAudioBasic
from app.models.voice_audio.voice_audio_analyse import VoiceAudioAnalyse
from app.models.voice_audio.voice_audio_template import VoiceAudioTemplate


class VoiceAudioRepository(RepositoryBase[VoiceAudioBasic]):
    """
    音频管理数据访问层
    [repositories][voice_audio]
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        初始化音频管理仓储
        [repositories][voice_audio][init]
        """
        super().__init__(db_session, VoiceAudioBasic)
    
    async def voice_audio_repository_get_by_timbre_id(
        self,
        timbre_id: int,
        user_id: Optional[int] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        根据音色ID获取音频列表
        [repositories][voice_audio][get_by_timbre_id]
        """
        conditions = [
            VoiceAudioBasic.audio_timbre_id == timbre_id,
            VoiceAudioBasic.audio_status != "deleted"
        ]
        
        if user_id:
            conditions.append(VoiceAudioBasic.audio_created_user_id == user_id)
        
        return await self.repository_base_paginate(
            page=page,
            size=size,
            conditions=conditions,
            order_by="audio_created_time"
        )
    
    async def voice_audio_repository_get_by_platform(
        self,
        platform: str,
        user_id: Optional[int] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        根据平台获取音频列表
        [repositories][voice_audio][get_by_platform]
        """
        conditions = [
            VoiceAudioBasic.audio_platform == platform,
            VoiceAudioBasic.audio_status != "deleted"
        ]
        
        if user_id:
            conditions.append(VoiceAudioBasic.audio_created_user_id == user_id)
        
        return await self.repository_base_paginate(
            page=page,
            size=size,
            conditions=conditions,
            order_by="audio_created_time"
        )
    
    async def voice_audio_repository_get_by_status(
        self,
        status: str,
        user_id: Optional[int] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        根据状态获取音频列表
        [repositories][voice_audio][get_by_status]
        """
        conditions = [VoiceAudioBasic.audio_status == status]
        
        if user_id:
            conditions.append(VoiceAudioBasic.audio_created_user_id == user_id)
        
        return await self.repository_base_paginate(
            page=page,
            size=size,
            conditions=conditions,
            order_by="audio_created_time"
        )
    
    async def voice_audio_repository_get_user_audios(
        self,
        user_id: int,
        status: Optional[str] = None,
        platform: Optional[str] = None,
        timbre_id: Optional[int] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        获取用户音频列表
        [repositories][voice_audio][get_user_audios]
        """
        conditions = [
            VoiceAudioBasic.audio_created_user_id == user_id,
            VoiceAudioBasic.audio_status != "deleted"
        ]
        
        if status:
            conditions.append(VoiceAudioBasic.audio_status == status)
        
        if platform:
            conditions.append(VoiceAudioBasic.audio_platform == platform)
        
        if timbre_id:
            conditions.append(VoiceAudioBasic.audio_timbre_id == timbre_id)
        
        return await self.repository_base_paginate(
            page=page,
            size=size,
            conditions=conditions,
            order_by="audio_updated_time"
        )
    
    async def voice_audio_repository_search_audios(
        self,
        search_term: str,
        user_id: Optional[int] = None,
        platform: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        搜索音频
        [repositories][voice_audio][search_audios]
        """
        conditions = [VoiceAudioBasic.audio_status != "deleted"]
        
        if user_id:
            conditions.append(VoiceAudioBasic.audio_created_user_id == user_id)
        
        if platform:
            conditions.append(VoiceAudioBasic.audio_platform == platform)
        
        if status:
            conditions.append(VoiceAudioBasic.audio_status == status)
        
        return await self.repository_base_search(
            search_fields=["audio_name", "audio_description"],
            search_term=search_term,
            conditions=conditions,
            page=page,
            size=size
        )
    
    async def voice_audio_repository_get_processing_audios(
        self,
        user_id: Optional[int] = None
    ) -> List[VoiceAudioBasic]:
        """
        获取处理中的音频列表
        [repositories][voice_audio][get_processing_audios]
        """
        conditions = [VoiceAudioBasic.audio_status == "processing"]
        
        if user_id:
            conditions.append(VoiceAudioBasic.audio_created_user_id == user_id)
        
        return await self.repository_base_get_all(
            conditions=conditions,
            order_by="audio_created_time"
        )
    
    async def voice_audio_repository_get_completed_audios(
        self,
        user_id: Optional[int] = None,
        days: int = 7,
        limit: int = 50
    ) -> List[VoiceAudioBasic]:
        """
        获取最近完成的音频列表
        [repositories][voice_audio][get_completed_audios]
        """
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        conditions = [
            VoiceAudioBasic.audio_status == "completed",
            VoiceAudioBasic.audio_updated_time >= cutoff_date
        ]
        
        if user_id:
            conditions.append(VoiceAudioBasic.audio_created_user_id == user_id)
        
        return await self.repository_base_get_all(
            conditions=conditions,
            order_by="audio_updated_time",
            limit=limit
        )
    
    async def voice_audio_repository_update_status(
        self,
        audio_id: int,
        status: str,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> Optional[VoiceAudioBasic]:
        """
        更新音频状态
        [repositories][voice_audio][update_status]
        """
        update_data = {
            "audio_status": status,
            "audio_updated_time": datetime.utcnow()
        }
        
        if additional_data:
            update_data.update(additional_data)
        
        return await self.repository_base_update(audio_id, **update_data)
    
    async def voice_audio_repository_soft_delete_audio(
        self,
        audio_id: int,
        deleted_user_id: int
    ) -> Optional[VoiceAudioBasic]:
        """
        软删除音频
        [repositories][voice_audio][soft_delete_audio]
        """
        return await self.repository_base_update(
            audio_id,
            audio_status="deleted",
            audio_deleted_time=datetime.utcnow(),
            audio_deleted_user_id=deleted_user_id
        )
    
    async def voice_audio_repository_get_audio_stats(
        self,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        获取音频统计信息
        [repositories][voice_audio][get_audio_stats]
        """
        conditions = [VoiceAudioBasic.audio_status != "deleted"]
        
        if user_id:
            conditions.append(VoiceAudioBasic.audio_created_user_id == user_id)
        
        # 音频总数
        total_audios = await self.repository_base_count(conditions)
        
        # 总时长
        duration_stmt = select(func.sum(VoiceAudioBasic.audio_duration)).where(
            and_(*conditions, VoiceAudioBasic.audio_duration.isnot(None))
        )
        duration_result = await self.db.execute(duration_stmt)
        total_duration = float(duration_result.scalar() or 0)
        
        # 按平台统计
        platform_stmt = select(
            VoiceAudioBasic.audio_platform,
            func.count(VoiceAudioBasic.audio_id).label("count"),
            func.sum(VoiceAudioBasic.audio_duration).label("duration")
        ).where(and_(*conditions)).group_by(VoiceAudioBasic.audio_platform)
        
        platform_result = await self.db.execute(platform_stmt)
        platform_distribution = {
            row.audio_platform: {
                "count": row.count,
                "duration": float(row.duration or 0)
            }
            for row in platform_result
        }
        
        # 按格式统计
        format_stmt = select(
            VoiceAudioBasic.audio_format,
            func.count(VoiceAudioBasic.audio_id).label("count")
        ).where(and_(*conditions)).group_by(VoiceAudioBasic.audio_format)
        
        format_result = await self.db.execute(format_stmt)
        format_distribution = {
            row.audio_format or "unknown": row.count 
            for row in format_result
        }
        
        # 按状态统计
        status_stmt = select(
            VoiceAudioBasic.audio_status,
            func.count(VoiceAudioBasic.audio_id).label("count")
        ).where(and_(*conditions)).group_by(VoiceAudioBasic.audio_status)
        
        status_result = await self.db.execute(status_stmt)
        status_distribution = {row.audio_status: row.count for row in status_result}
        
        return {
            "total_audios": total_audios,
            "total_duration": total_duration,
            "platform_distribution": platform_distribution,
            "format_distribution": format_distribution,
            "status_distribution": status_distribution
        }
    
    async def voice_audio_repository_get_long_audios(
        self,
        min_duration: float = 300.0,  # 5分钟
        user_id: Optional[int] = None,
        limit: int = 20
    ) -> List[VoiceAudioBasic]:
        """
        获取长音频列表
        [repositories][voice_audio][get_long_audios]
        """
        conditions = [
            VoiceAudioBasic.audio_duration >= min_duration,
            VoiceAudioBasic.audio_status == "completed"
        ]
        
        if user_id:
            conditions.append(VoiceAudioBasic.audio_created_user_id == user_id)
        
        return await self.repository_base_get_all(
            conditions=conditions,
            order_by="audio_duration",
            limit=limit
        )
    
    async def voice_audio_repository_cleanup_failed_audios(
        self,
        days_old: int = 7
    ) -> int:
        """
        清理失败的音频记录
        [repositories][voice_audio][cleanup_failed_audios]
        """
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        conditions = [
            VoiceAudioBasic.audio_status == "failed",
            VoiceAudioBasic.audio_updated_time <= cutoff_date
        ]
        
        return await self.repository_base_update_by_conditions(
            conditions,
            audio_status="cleanup_pending"
        )


class VoiceAudioAnalyseRepository(RepositoryBase[VoiceAudioAnalyse]):
    """
    音频分析数据访问层
    [repositories][voice_audio][analyse]
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        初始化音频分析仓储
        [repositories][voice_audio][analyse][init]
        """
        super().__init__(db_session, VoiceAudioAnalyse)
    
    async def voice_audio_analyse_repository_get_by_audio_id(
        self,
        audio_id: int
    ) -> List[VoiceAudioAnalyse]:
        """
        根据音频ID获取所有分析结果
        [repositories][voice_audio][analyse][get_by_audio_id]
        """
        return await self.repository_base_get_all(
            conditions=[VoiceAudioAnalyse.audio_id == audio_id],
            order_by="analyse_created_time"
        )
    
    async def voice_audio_analyse_repository_get_by_type(
        self,
        audio_id: int,
        analyse_type: str
    ) -> List[VoiceAudioAnalyse]:
        """
        根据音频ID和分析类型获取分析结果
        [repositories][voice_audio][analyse][get_by_type]
        """
        conditions = [
            VoiceAudioAnalyse.audio_id == audio_id,
            VoiceAudioAnalyse.analyse_type == analyse_type
        ]
        
        return await self.repository_base_get_all(
            conditions=conditions,
            order_by="analyse_created_time"
        )
    
    async def voice_audio_analyse_repository_get_latest_analysis(
        self,
        audio_id: int,
        analyse_type: str
    ) -> Optional[VoiceAudioAnalyse]:
        """
        获取最新的分析结果
        [repositories][voice_audio][analyse][get_latest_analysis]
        """
        stmt = select(VoiceAudioAnalyse).where(
            and_(
                VoiceAudioAnalyse.audio_id == audio_id,
                VoiceAudioAnalyse.analyse_type == analyse_type,
                VoiceAudioAnalyse.analyse_status == "completed"
            )
        ).order_by(VoiceAudioAnalyse.analyse_created_time.desc()).limit(1)
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def voice_audio_analyse_repository_get_quality_analyses(
        self,
        min_score: float = 80.0,
        user_id: Optional[int] = None,
        limit: int = 20
    ) -> List[VoiceAudioAnalyse]:
        """
        获取高质量分析结果
        [repositories][voice_audio][analyse][get_quality_analyses]
        """
        conditions = [
            VoiceAudioAnalyse.analyse_quality_score >= min_score,
            VoiceAudioAnalyse.analyse_status == "completed"
        ]
        
        if user_id:
            conditions.append(VoiceAudioAnalyse.analyse_created_user_id == user_id)
        
        return await self.repository_base_get_all(
            conditions=conditions,
            order_by="analyse_quality_score",
            limit=limit
        )
    
    async def voice_audio_analyse_repository_get_analysis_stats(
        self,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        获取分析统计信息
        [repositories][voice_audio][analyse][get_analysis_stats]
        """
        base_conditions = [VoiceAudioAnalyse.analyse_status == "completed"]
        
        if user_id:
            base_conditions.append(VoiceAudioAnalyse.analyse_created_user_id == user_id)
        
        # 总分析数
        total_analyses = await self.repository_base_count(base_conditions)
        
        # 按类型统计
        type_stmt = select(
            VoiceAudioAnalyse.analyse_type,
            func.count(VoiceAudioAnalyse.analyse_id).label("count"),
            func.avg(VoiceAudioAnalyse.analyse_quality_score).label("avg_quality"),
            func.avg(VoiceAudioAnalyse.analyse_confidence_score).label("avg_confidence")
        ).where(and_(*base_conditions)).group_by(VoiceAudioAnalyse.analyse_type)
        
        type_result = await self.db.execute(type_stmt)
        type_distribution = {
            row.analyse_type: {
                "count": row.count,
                "avg_quality": float(row.avg_quality or 0),
                "avg_confidence": float(row.avg_confidence or 0)
            }
            for row in type_result
        }
        
        # 整体平均分数
        avg_stmt = select(
            func.avg(VoiceAudioAnalyse.analyse_quality_score).label("avg_quality"),
            func.avg(VoiceAudioAnalyse.analyse_confidence_score).label("avg_confidence"),
            func.avg(VoiceAudioAnalyse.analyse_clarity_score).label("avg_clarity")
        ).where(and_(*base_conditions))
        
        avg_result = await self.db.execute(avg_stmt)
        avg_row = avg_result.first()
        
        return {
            "total_analyses": total_analyses,
            "type_distribution": type_distribution,
            "average_scores": {
                "quality": float(avg_row.avg_quality or 0),
                "confidence": float(avg_row.avg_confidence or 0),
                "clarity": float(avg_row.avg_clarity or 0)
            }
        }


class VoiceAudioTemplateRepository(RepositoryBase[VoiceAudioTemplate]):
    """
    音频模板数据访问层
    [repositories][voice_audio][template]
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        初始化音频模板仓储
        [repositories][voice_audio][template][init]
        """
        super().__init__(db_session, VoiceAudioTemplate)
    
    async def voice_audio_template_repository_get_by_type(
        self,
        template_type: str,
        user_id: Optional[int] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        根据模板类型获取模板列表
        [repositories][voice_audio][template][get_by_type]
        """
        conditions = [
            VoiceAudioTemplate.template_type == template_type,
            VoiceAudioTemplate.template_status == "active"
        ]
        
        if user_id:
            conditions.append(VoiceAudioTemplate.template_created_user_id == user_id)
        
        return await self.repository_base_paginate(
            page=page,
            size=size,
            conditions=conditions,
            order_by="template_created_time"
        )
    
    async def voice_audio_template_repository_get_by_timbre_id(
        self,
        timbre_id: int,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        根据音色ID获取模板列表
        [repositories][voice_audio][template][get_by_timbre_id]
        """
        conditions = [
            VoiceAudioTemplate.template_timbre_id == timbre_id,
            VoiceAudioTemplate.template_status == "active"
        ]
        
        return await self.repository_base_paginate(
            page=page,
            size=size,
            conditions=conditions,
            order_by="template_created_time"
        )
    
    async def voice_audio_template_repository_get_public_templates(
        self,
        template_type: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        获取公共音频模板
        [repositories][voice_audio][template][get_public_templates]
        """
        conditions = [
            VoiceAudioTemplate.template_status == "active",
            VoiceAudioTemplate.template_is_public == True
        ]
        
        if template_type:
            conditions.append(VoiceAudioTemplate.template_type == template_type)
        
        return await self.repository_base_paginate(
            page=page,
            size=size,
            conditions=conditions,
            order_by="template_usage_count"
        )
    
    async def voice_audio_template_repository_get_user_templates(
        self,
        user_id: int,
        template_type: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        获取用户音频模板
        [repositories][voice_audio][template][get_user_templates]
        """
        conditions = [
            VoiceAudioTemplate.template_created_user_id == user_id,
            VoiceAudioTemplate.template_status == "active"
        ]
        
        if template_type:
            conditions.append(VoiceAudioTemplate.template_type == template_type)
        
        return await self.repository_base_paginate(
            page=page,
            size=size,
            conditions=conditions,
            order_by="template_updated_time"
        )
    
    async def voice_audio_template_repository_increment_usage(
        self,
        template_id: int
    ) -> Optional[VoiceAudioTemplate]:
        """
        增加模板使用次数
        [repositories][voice_audio][template][increment_usage]
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
    
    async def voice_audio_template_repository_get_popular_templates(
        self,
        template_type: Optional[str] = None,
        limit: int = 10
    ) -> List[VoiceAudioTemplate]:
        """
        获取热门音频模板
        [repositories][voice_audio][template][get_popular_templates]
        """
        conditions = [
            VoiceAudioTemplate.template_status == "active",
            VoiceAudioTemplate.template_is_public == True
        ]
        
        if template_type:
            conditions.append(VoiceAudioTemplate.template_type == template_type)
        
        return await self.repository_base_get_all(
            conditions=conditions,
            order_by="template_usage_count",
            limit=limit
        )