"""
File Storage Service
文件存储业务逻辑服务 - [services][file_storage]
"""

import os
import uuid
import mimetypes
from typing import Dict, Any, Optional, List, BinaryIO
from datetime import datetime
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.services.base import ServiceBase
from app.models.file_storage.file_storage_basic import FileStorageBasic
from app.models.file_storage.file_storage_meta import FileStorageMeta
from app.config.settings import app_config_get_settings


class FileStorageService(ServiceBase):
    """
    文件存储业务逻辑服务
    [services][file_storage]
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        初始化文件存储服务
        [services][file_storage][init]
        """
        super().__init__(db_session)
        self.settings = app_config_get_settings()
        self.upload_path = Path(self.settings.UPLOAD_DIR)
        self.upload_path.mkdir(parents=True, exist_ok=True)
    
    async def file_storage_service_upload(
        self,
        file_content: BinaryIO,
        filename: str,
        user_id: int,
        file_category: str = "general",
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        上传文件
        [services][file_storage][upload]
        """
        try:
            # 生成唯一文件名
            file_extension = Path(filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # 确定文件类型
            content_type, _ = mimetypes.guess_type(filename)
            if not content_type:
                content_type = "application/octet-stream"
            
            # 计算文件大小
            file_content.seek(0, 2)  # 移动到文件末尾
            file_size = file_content.tell()
            file_content.seek(0)  # 回到文件开头
            
            # 验证文件大小
            max_size = self.settings.MAX_FILE_SIZE
            if file_size > max_size:
                return {
                    "success": False,
                    "error": f"文件大小超过限制 ({max_size} bytes)"
                }
            
            # 创建存储目录
            today = datetime.now().strftime("%Y/%m/%d")
            storage_dir = self.upload_path / today
            storage_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存文件
            file_path = storage_dir / unique_filename
            with open(file_path, "wb") as f:
                f.write(file_content.read())
            
            # 创建文件记录
            file_record = FileStorageBasic(
                file_original_name=filename,
                file_stored_name=unique_filename,
                file_path=str(file_path.relative_to(self.upload_path)),
                file_size=file_size,
                file_type=content_type,
                file_category=file_category,
                file_description=description,
                file_upload_user_id=user_id,
                file_created_time=datetime.utcnow(),
                file_status="active"
            )
            
            self.db.add(file_record)
            await self.db.commit()
            await self.db.refresh(file_record)
            
            # 创建文件元数据
            await self.file_storage_service_create_metadata(
                file_record.file_id,
                file_path,
                content_type
            )
            
            # 记录操作日志
            await self.service_base_log_operation(
                "upload",
                "file",
                file_record.file_id,
                user_id,
                {
                    "filename": filename,
                    "size": file_size,
                    "category": file_category
                }
            )
            
            return {
                "success": True,
                "data": {
                    "file_id": file_record.file_id,
                    "filename": filename,
                    "file_size": file_size,
                    "file_type": content_type,
                    "file_url": self.file_storage_service_get_file_url(file_record.file_id)
                }
            }
            
        except Exception as e:
            await self.db.rollback()
            return {
                "success": False,
                "error": f"文件上传失败: {str(e)}"
            }
    
    async def file_storage_service_get_file(
        self,
        file_id: int,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        获取文件信息
        [services][file_storage][get_file]
        """
        try:
            stmt = select(FileStorageBasic).where(FileStorageBasic.file_id == file_id)
            result = await self.db.execute(stmt)
            file_record = result.scalar_one_or_none()
            
            if not file_record:
                return {
                    "success": False,
                    "error": "文件不存在"
                }
            
            # 检查访问权限
            if user_id and not await self.file_storage_service_check_access(file_id, user_id):
                return {
                    "success": False,
                    "error": "无权限访问此文件"
                }
            
            return {
                "success": True,
                "data": {
                    "file_id": file_record.file_id,
                    "original_name": file_record.file_original_name,
                    "file_size": file_record.file_size,
                    "file_type": file_record.file_type,
                    "file_category": file_record.file_category,
                    "description": file_record.file_description,
                    "created_time": file_record.file_created_time,
                    "file_url": self.file_storage_service_get_file_url(file_record.file_id),
                    "download_url": self.file_storage_service_get_download_url(file_record.file_id)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"获取文件信息失败: {str(e)}"
            }
    
    async def file_storage_service_delete_file(
        self,
        file_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        删除文件
        [services][file_storage][delete_file]
        """
        try:
            # 获取文件记录
            stmt = select(FileStorageBasic).where(FileStorageBasic.file_id == file_id)
            result = await self.db.execute(stmt)
            file_record = result.scalar_one_or_none()
            
            if not file_record:
                return {
                    "success": False,
                    "error": "文件不存在"
                }
            
            # 检查删除权限
            if not await self.file_storage_service_check_delete_permission(file_id, user_id):
                return {
                    "success": False,
                    "error": "无权限删除此文件"
                }
            
            # 标记文件为已删除
            file_record.file_status = "deleted"
            file_record.file_deleted_time = datetime.utcnow()
            file_record.file_deleted_user_id = user_id
            
            await self.db.commit()
            
            # 记录操作日志
            await self.service_base_log_operation(
                "delete",
                "file",
                file_id,
                user_id
            )
            
            return {
                "success": True,
                "message": "文件删除成功"
            }
            
        except Exception as e:
            await self.db.rollback()
            return {
                "success": False,
                "error": f"文件删除失败: {str(e)}"
            }
    
    async def file_storage_service_list_files(
        self,
        user_id: Optional[int] = None,
        file_category: Optional[str] = None,
        file_type: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        获取文件列表
        [services][file_storage][list_files]
        """
        try:
            # 构建查询条件
            conditions = [FileStorageBasic.file_status == "active"]
            
            if user_id:
                conditions.append(FileStorageBasic.file_upload_user_id == user_id)
            
            if file_category:
                conditions.append(FileStorageBasic.file_category == file_category)
            
            if file_type:
                conditions.append(FileStorageBasic.file_type.like(f"{file_type}%"))
            
            # 查询文件列表
            stmt = select(FileStorageBasic).where(
                and_(*conditions)
            ).offset((page - 1) * size).limit(size)
            
            result = await self.db.execute(stmt)
            files = result.scalars().all()
            
            # 查询总数
            count_stmt = select(func.count(FileStorageBasic.file_id)).where(
                and_(*conditions)
            )
            count_result = await self.db.execute(count_stmt)
            total = count_result.scalar()
            
            # 构建响应数据
            file_list = []
            for file_record in files:
                file_list.append({
                    "file_id": file_record.file_id,
                    "original_name": file_record.file_original_name,
                    "file_size": file_record.file_size,
                    "file_type": file_record.file_type,
                    "file_category": file_record.file_category,
                    "created_time": file_record.file_created_time,
                    "file_url": self.file_storage_service_get_file_url(file_record.file_id)
                })
            
            return {
                "success": True,
                "data": file_list,
                "pagination": {
                    "page": page,
                    "size": size,
                    "total": total,
                    "pages": (total + size - 1) // size
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"获取文件列表失败: {str(e)}"
            }
    
    async def file_storage_service_create_metadata(
        self,
        file_id: int,
        file_path: Path,
        content_type: str
    ) -> None:
        """
        创建文件元数据
        [services][file_storage][create_metadata]
        """
        try:
            metadata = {}
            
            # 根据文件类型提取元数据
            if content_type.startswith('image/'):
                metadata = await self.file_storage_service_extract_image_metadata(file_path)
            elif content_type.startswith('audio/'):
                metadata = await self.file_storage_service_extract_audio_metadata(file_path)
            elif content_type.startswith('video/'):
                metadata = await self.file_storage_service_extract_video_metadata(file_path)
            
            # 保存元数据
            if metadata:
                file_meta = FileStorageMeta(
                    file_id=file_id,
                    meta_key="file_info",
                    meta_value=metadata,
                    meta_created_time=datetime.utcnow()
                )
                self.db.add(file_meta)
                await self.db.commit()
                
        except Exception as e:
            # 元数据提取失败不影响文件上传
            pass
    
    async def file_storage_service_extract_image_metadata(
        self,
        file_path: Path
    ) -> Dict[str, Any]:
        """
        提取图像元数据
        [services][file_storage][extract_image_metadata]
        """
        # TODO: 使用PIL等库提取图像元数据
        return {}
    
    async def file_storage_service_extract_audio_metadata(
        self,
        file_path: Path
    ) -> Dict[str, Any]:
        """
        提取音频元数据
        [services][file_storage][extract_audio_metadata]
        """
        # TODO: 使用librosa等库提取音频元数据
        return {}
    
    async def file_storage_service_extract_video_metadata(
        self,
        file_path: Path
    ) -> Dict[str, Any]:
        """
        提取视频元数据
        [services][file_storage][extract_video_metadata]
        """
        # TODO: 使用ffmpeg等工具提取视频元数据
        return {}
    
    def file_storage_service_get_file_url(self, file_id: int) -> str:
        """
        获取文件访问URL
        [services][file_storage][get_file_url]
        """
        return f"{self.settings.BASE_URL}/api/v1/files/{file_id}"
    
    def file_storage_service_get_download_url(self, file_id: int) -> str:
        """
        获取文件下载URL
        [services][file_storage][get_download_url]
        """
        return f"{self.settings.BASE_URL}/api/v1/files/{file_id}/download"
    
    async def file_storage_service_check_access(
        self,
        file_id: int,
        user_id: int
    ) -> bool:
        """
        检查文件访问权限
        [services][file_storage][check_access]
        """
        # TODO: 实现文件访问权限检查逻辑
        return True
    
    async def file_storage_service_check_delete_permission(
        self,
        file_id: int,
        user_id: int
    ) -> bool:
        """
        检查文件删除权限
        [services][file_storage][check_delete_permission]
        """
        # TODO: 实现文件删除权限检查逻辑
        return True