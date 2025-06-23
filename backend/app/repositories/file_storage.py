"""
File Storage Repository
文件存储数据访问层 - [repositories][file_storage]
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.repositories.base import RepositoryBase
from app.models.file_storage.file_storage_basic import FileStorageBasic
from app.models.file_storage.file_storage_meta import FileStorageMeta


class FileStorageRepository(RepositoryBase[FileStorageBasic]):
    """
    文件存储数据访问层
    [repositories][file_storage]
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        初始化文件存储仓储
        [repositories][file_storage][init]
        """
        super().__init__(db_session, FileStorageBasic)
    
    async def file_storage_repository_get_by_stored_name(
        self,
        stored_name: str
    ) -> Optional[FileStorageBasic]:
        """
        根据存储文件名获取文件
        [repositories][file_storage][get_by_stored_name]
        """
        return await self.repository_base_get_by_field("file_stored_name", stored_name)
    
    async def file_storage_repository_get_by_category(
        self,
        category: str,
        user_id: Optional[int] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        根据分类获取文件列表
        [repositories][file_storage][get_by_category]
        """
        conditions = [
            FileStorageBasic.file_category == category,
            FileStorageBasic.file_status == "active"
        ]
        
        if user_id:
            conditions.append(FileStorageBasic.file_upload_user_id == user_id)
        
        return await self.repository_base_paginate(
            page=page,
            size=size,
            conditions=conditions,
            order_by="file_created_time"
        )
    
    async def file_storage_repository_get_by_type(
        self,
        file_type: str,
        user_id: Optional[int] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        根据文件类型获取文件列表
        [repositories][file_storage][get_by_type]
        """
        conditions = [
            FileStorageBasic.file_type.like(f"{file_type}%"),
            FileStorageBasic.file_status == "active"
        ]
        
        if user_id:
            conditions.append(FileStorageBasic.file_upload_user_id == user_id)
        
        return await self.repository_base_paginate(
            page=page,
            size=size,
            conditions=conditions,
            order_by="file_created_time"
        )
    
    async def file_storage_repository_get_user_files(
        self,
        user_id: int,
        category: Optional[str] = None,
        file_type: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        获取用户文件列表
        [repositories][file_storage][get_user_files]
        """
        conditions = [
            FileStorageBasic.file_upload_user_id == user_id,
            FileStorageBasic.file_status == "active"
        ]
        
        if category:
            conditions.append(FileStorageBasic.file_category == category)
        
        if file_type:
            conditions.append(FileStorageBasic.file_type.like(f"{file_type}%"))
        
        return await self.repository_base_paginate(
            page=page,
            size=size,
            conditions=conditions,
            order_by="file_created_time"
        )
    
    async def file_storage_repository_search_files(
        self,
        search_term: str,
        user_id: Optional[int] = None,
        category: Optional[str] = None,
        file_type: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        搜索文件
        [repositories][file_storage][search_files]
        """
        conditions = [FileStorageBasic.file_status == "active"]
        
        if user_id:
            conditions.append(FileStorageBasic.file_upload_user_id == user_id)
        
        if category:
            conditions.append(FileStorageBasic.file_category == category)
        
        if file_type:
            conditions.append(FileStorageBasic.file_type.like(f"{file_type}%"))
        
        return await self.repository_base_search(
            search_fields=["file_original_name", "file_description"],
            search_term=search_term,
            conditions=conditions,
            page=page,
            size=size
        )
    
    async def file_storage_repository_soft_delete_file(
        self,
        file_id: int,
        deleted_user_id: int
    ) -> Optional[FileStorageBasic]:
        """
        软删除文件
        [repositories][file_storage][soft_delete_file]
        """
        return await self.repository_base_update(
            file_id,
            file_status="deleted",
            file_deleted_time=datetime.utcnow(),
            file_deleted_user_id=deleted_user_id
        )
    
    async def file_storage_repository_get_file_stats(
        self,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        获取文件统计信息
        [repositories][file_storage][get_file_stats]
        """
        conditions = [FileStorageBasic.file_status == "active"]
        
        if user_id:
            conditions.append(FileStorageBasic.file_upload_user_id == user_id)
        
        # 文件总数
        total_files = await self.repository_base_count(conditions)
        
        # 总文件大小
        size_stmt = select(func.sum(FileStorageBasic.file_size)).where(
            and_(*conditions)
        )
        size_result = await self.db.execute(size_stmt)
        total_size = size_result.scalar() or 0
        
        # 按分类统计
        category_stmt = select(
            FileStorageBasic.file_category,
            func.count(FileStorageBasic.file_id).label("count"),
            func.sum(FileStorageBasic.file_size).label("size")
        ).where(and_(*conditions)).group_by(FileStorageBasic.file_category)
        
        category_result = await self.db.execute(category_stmt)
        category_distribution = {
            row.file_category: {"count": row.count, "size": row.size or 0}
            for row in category_result
        }
        
        # 按类型统计（主要类型）
        type_stmt = select(
            func.substring(FileStorageBasic.file_type, 1, 
                          func.strpos(FileStorageBasic.file_type, "/") - 1).label("main_type"),
            func.count(FileStorageBasic.file_id).label("count")
        ).where(and_(*conditions)).group_by("main_type")
        
        type_result = await self.db.execute(type_stmt)
        type_distribution = {
            row.main_type or "unknown": row.count 
            for row in type_result
        }
        
        return {
            "total_files": total_files,
            "total_size": total_size,
            "category_distribution": category_distribution,
            "type_distribution": type_distribution
        }
    
    async def file_storage_repository_get_large_files(
        self,
        min_size: int = 10485760,  # 10MB
        user_id: Optional[int] = None,
        limit: int = 50
    ) -> List[FileStorageBasic]:
        """
        获取大文件列表
        [repositories][file_storage][get_large_files]
        """
        conditions = [
            FileStorageBasic.file_size >= min_size,
            FileStorageBasic.file_status == "active"
        ]
        
        if user_id:
            conditions.append(FileStorageBasic.file_upload_user_id == user_id)
        
        return await self.repository_base_get_all(
            conditions=conditions,
            order_by="file_size",
            limit=limit
        )
    
    async def file_storage_repository_cleanup_orphaned_files(
        self,
        days_old: int = 30
    ) -> int:
        """
        清理孤立文件（标记为删除但未实际删除的文件）
        [repositories][file_storage][cleanup_orphaned_files]
        """
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        conditions = [
            FileStorageBasic.file_status == "deleted",
            FileStorageBasic.file_deleted_time <= cutoff_date
        ]
        
        # 这里只是标记清理，实际文件删除应该由后台任务处理
        return await self.repository_base_update_by_conditions(
            conditions,
            file_status="cleanup_pending"
        )


class FileStorageMetaRepository(RepositoryBase[FileStorageMeta]):
    """
    文件元数据数据访问层
    [repositories][file_storage][meta]
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        初始化文件元数据仓储
        [repositories][file_storage][meta][init]
        """
        super().__init__(db_session, FileStorageMeta)
    
    async def file_storage_meta_repository_get_by_file_id(
        self,
        file_id: int
    ) -> List[FileStorageMeta]:
        """
        根据文件ID获取所有元数据
        [repositories][file_storage][meta][get_by_file_id]
        """
        return await self.repository_base_get_all(
            conditions=[FileStorageMeta.file_id == file_id],
            order_by="meta_created_time"
        )
    
    async def file_storage_meta_repository_get_by_key(
        self,
        file_id: int,
        meta_key: str
    ) -> Optional[FileStorageMeta]:
        """
        根据文件ID和键获取元数据
        [repositories][file_storage][meta][get_by_key]
        """
        stmt = select(FileStorageMeta).where(
            and_(
                FileStorageMeta.file_id == file_id,
                FileStorageMeta.meta_key == meta_key
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def file_storage_meta_repository_set_meta(
        self,
        file_id: int,
        meta_key: str,
        meta_value: Any,
        meta_type: str = "json"
    ) -> FileStorageMeta:
        """
        设置或更新文件元数据
        [repositories][file_storage][meta][set_meta]
        """
        existing_meta = await self.file_storage_meta_repository_get_by_key(
            file_id, meta_key
        )
        
        if existing_meta:
            # 更新现有元数据
            return await self.repository_base_update(
                existing_meta.meta_id,
                meta_value=meta_value,
                meta_type=meta_type,
                meta_updated_time=datetime.utcnow()
            )
        else:
            # 创建新元数据
            return await self.repository_base_create(
                file_id=file_id,
                meta_key=meta_key,
                meta_value=meta_value,
                meta_type=meta_type,
                meta_created_time=datetime.utcnow(),
                meta_updated_time=datetime.utcnow()
            )
    
    async def file_storage_meta_repository_delete_by_file_id(
        self,
        file_id: int
    ) -> int:
        """
        删除文件的所有元数据
        [repositories][file_storage][meta][delete_by_file_id]
        """
        from sqlalchemy import delete
        
        stmt = delete(FileStorageMeta).where(FileStorageMeta.file_id == file_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount
    
    async def file_storage_meta_repository_bulk_set_meta(
        self,
        file_id: int,
        metadata_dict: Dict[str, Any]
    ) -> List[FileStorageMeta]:
        """
        批量设置文件元数据
        [repositories][file_storage][meta][bulk_set_meta]
        """
        results = []
        
        for meta_key, meta_value in metadata_dict.items():
            meta_record = await self.file_storage_meta_repository_set_meta(
                file_id=file_id,
                meta_key=meta_key,
                meta_value=meta_value
            )
            results.append(meta_record)
        
        return results