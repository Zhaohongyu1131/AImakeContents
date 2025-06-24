"""
File Storage Service
文件存储管理服务 - [services][file_storage]
"""

from typing import Dict, Any, Optional, List, Union, BinaryIO
from pathlib import Path
from datetime import datetime
import hashlib
import mimetypes
import shutil
import os
import asyncio
from enum import Enum
import aiofiles
import magic
from PIL import Image
import mutagen
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from app.services.base import ServiceBase
from app.models.file_storage.file_storage_basic import FileStorageBasic
from app.models.file_storage.file_storage_meta import FileStorageMeta
from app.config.settings import app_config_get_settings


class FileStorageType(Enum):
    """文件存储类型枚举"""
    LOCAL = "local"
    S3 = "s3"
    OSS = "oss"
    COS = "cos"


class FileCategory(Enum):
    """文件类别枚举"""
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    TEXT = "text"
    DOCUMENT = "document"
    OTHER = "other"


class FileStorageService(ServiceBase):
    """
    文件存储管理服务
    [services][file_storage]
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        初始化文件存储服务
        [services][file_storage][init]
        """
        super().__init__(db_session)
        self.settings = app_config_get_settings()
        self.storage_path = Path(self.settings.FILE_STORAGE_PATH)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    async def file_storage_service_upload(
        self,
        file_data: Union[BinaryIO, bytes],
        original_filename: str,
        user_id: int,
        file_category: Optional[str] = None,
        storage_type: str = "local",
        custom_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        上传文件
        [services][file_storage][upload]
        """
        try:
            # 准备文件数据
            if hasattr(file_data, 'read'):
                file_content = await asyncio.to_thread(file_data.read)
            else:
                file_content = file_data
            
            # 文件验证
            validation_result = await self._validate_file(file_content, original_filename)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"]
                }
            
            # 计算文件哈希
            file_hash = hashlib.md5(file_content).hexdigest()
            
            # 检查文件是否已存在
            existing_file = await self._check_file_exists(file_hash)
            if existing_file:
                return {
                    "success": True,
                    "data": {
                        "file_id": existing_file.file_id,
                        "message": "文件已存在，返回现有文件",
                        "file_url": existing_file.file_url_generate(),
                        "file_size": existing_file.file_size
                    }
                }
            
            # 生成文件名和路径
            file_info = await self._generate_file_path(original_filename, file_hash)
            
            # 存储文件
            storage_result = await self._store_file(
                file_content, 
                file_info["file_path"], 
                storage_type
            )
            
            if not storage_result["success"]:
                return storage_result
            
            # 确定文件类别
            if not file_category:
                file_category = await self._determine_file_category(file_content, original_filename)
            
            # 创建数据库记录
            file_record = FileStorageBasic(
                file_name=file_info["filename"],
                file_original_name=original_filename,
                file_path=file_info["file_path"],
                file_size=len(file_content),
                file_type=file_category,
                file_mime_type=validation_result["mime_type"],
                file_hash_md5=file_hash,
                file_storage_type=storage_type,
                file_created_user_id=user_id,
                file_status="active"
            )
            
            self.db.add(file_record)
            await self.db.commit()
            await self.db.refresh(file_record)
            
            # 生成文件元数据
            await self._generate_file_metadata(
                file_record.file_id, 
                file_content, 
                file_category, 
                user_id,
                custom_metadata
            )
            
            # 记录操作日志
            await self.service_base_log_operation(
                "upload",
                "file",
                file_record.file_id,
                user_id,
                {"filename": original_filename, "size": len(file_content)}
            )
            
            return {
                "success": True,
                "data": {
                    "file_id": file_record.file_id,
                    "filename": file_record.file_name,
                    "original_filename": file_record.file_original_name,
                    "file_size": file_record.file_size,
                    "file_type": file_record.file_type,
                    "mime_type": file_record.file_mime_type,
                    "file_url": file_record.file_url_generate(),
                    "upload_time": file_record.file_created_time.isoformat()
                }
            }
            
        except Exception as e:
            await self.db.rollback()
            return {
                "success": False,
                "error": f"文件上传失败: {str(e)}"
            }
    
    async def file_storage_service_download(
        self,
        file_id: int,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        下载文件
        [services][file_storage][download]
        """
        try:
            # 获取文件记录
            file_record = await self._get_file_by_id(file_id)
            if not file_record:
                return {
                    "success": False,
                    "error": "文件不存在"
                }
            
            # 检查文件状态
            if file_record.file_status != "active":
                return {
                    "success": False,
                    "error": "文件不可用"
                }
            
            # 读取文件内容
            file_content = await self._read_file(file_record.file_path, file_record.file_storage_type)
            if file_content is None:
                return {
                    "success": False,
                    "error": "文件读取失败"
                }
            
            # 记录下载日志
            if user_id:
                await self.service_base_log_operation(
                    "download",
                    "file",
                    file_id,
                    user_id
                )
            
            return {
                "success": True,
                "data": {
                    "file_content": file_content,
                    "filename": file_record.file_original_name,
                    "mime_type": file_record.file_mime_type,
                    "file_size": file_record.file_size
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"文件下载失败: {str(e)}"
            }
    
    async def file_storage_service_delete(
        self,
        file_id: int,
        user_id: int,
        permanent: bool = False
    ) -> Dict[str, Any]:
        """
        删除文件
        [services][file_storage][delete]
        """
        try:
            # 获取文件记录
            file_record = await self._get_file_by_id(file_id)
            if not file_record:
                return {
                    "success": False,
                    "error": "文件不存在"
                }
            
            # 权限检查 - 只有创建者或管理员可以删除
            # 这里简化处理，实际应该调用权限服务
            if file_record.file_created_user_id != user_id:
                return {
                    "success": False,
                    "error": "无权限删除此文件"
                }
            
            if permanent:
                # 永久删除 - 删除物理文件和数据库记录
                await self._delete_physical_file(file_record.file_path, file_record.file_storage_type)
                
                # 删除元数据
                await self.db.execute(
                    select(FileStorageMeta).where(FileStorageMeta.file_id == file_id)
                )
                
                # 删除文件记录
                await self.db.delete(file_record)
            else:
                # 软删除 - 仅标记为已删除
                file_record.file_status = "deleted"
                file_record.file_updated_time = datetime.utcnow()
            
            await self.db.commit()
            
            # 记录操作日志
            await self.service_base_log_operation(
                "delete_permanent" if permanent else "delete_soft",
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
    
    async def file_storage_service_list(
        self,
        user_id: Optional[int] = None,
        file_type: Optional[str] = None,
        page: int = 1,
        size: int = 20,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取文件列表
        [services][file_storage][list]
        """
        try:
            # 构建查询条件
            conditions = [FileStorageBasic.file_status == "active"]
            
            if user_id:
                conditions.append(FileStorageBasic.file_created_user_id == user_id)
            
            if file_type:
                conditions.append(FileStorageBasic.file_type == file_type)
            
            if search:
                conditions.append(
                    or_(
                        FileStorageBasic.file_name.ilike(f"%{search}%"),
                        FileStorageBasic.file_original_name.ilike(f"%{search}%")
                    )
                )
            
            # 计算总数
            count_stmt = select(func.count(FileStorageBasic.file_id)).where(and_(*conditions))
            count_result = await self.db.execute(count_stmt)
            total = count_result.scalar()
            
            # 获取分页数据
            offset = (page - 1) * size
            stmt = (
                select(FileStorageBasic)
                .where(and_(*conditions))
                .order_by(FileStorageBasic.file_created_time.desc())
                .offset(offset)
                .limit(size)
            )
            
            result = await self.db.execute(stmt)
            files = result.scalars().all()
            
            # 转换为字典格式
            files_data = []
            for file_record in files:
                files_data.append({
                    "file_id": file_record.file_id,
                    "filename": file_record.file_name,
                    "original_filename": file_record.file_original_name,
                    "file_size": file_record.file_size,
                    "file_size_human": file_record.file_size_human_readable,
                    "file_type": file_record.file_type,
                    "mime_type": file_record.file_mime_type,
                    "file_url": file_record.file_url_generate(),
                    "created_time": file_record.file_created_time.isoformat(),
                    "storage_type": file_record.file_storage_type
                })
            
            return {
                "success": True,
                "data": {
                    "files": files_data,
                    "pagination": {
                        "page": page,
                        "size": size,
                        "total": total,
                        "pages": (total + size - 1) // size
                    }
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"获取文件列表失败: {str(e)}"
            }
    
    async def file_storage_service_get_metadata(
        self,
        file_id: int
    ) -> Dict[str, Any]:
        """
        获取文件元数据
        [services][file_storage][get_metadata]
        """
        try:
            # 获取文件记录
            file_record = await self._get_file_by_id(file_id)
            if not file_record:
                return {
                    "success": False,
                    "error": "文件不存在"
                }
            
            # 获取元数据
            stmt = select(FileStorageMeta).where(
                and_(
                    FileStorageMeta.file_id == file_id,
                    FileStorageMeta.meta_status == "active"
                )
            )
            result = await self.db.execute(stmt)
            metadata_records = result.scalars().all()
            
            # 组织元数据
            metadata = {}
            for meta in metadata_records:
                category = meta.meta_category
                if category not in metadata:
                    metadata[category] = {}
                
                metadata[category][meta.meta_key] = {
                    "value": meta.meta_value_get_typed(),
                    "type": meta.meta_type,
                    "description": meta.meta_description,
                    "created_time": meta.meta_created_time.isoformat()
                }
            
            return {
                "success": True,
                "data": {
                    "file_info": {
                        "file_id": file_record.file_id,
                        "filename": file_record.file_original_name,
                        "file_size": file_record.file_size,
                        "file_type": file_record.file_type,
                        "mime_type": file_record.file_mime_type,
                        "created_time": file_record.file_created_time.isoformat()
                    },
                    "metadata": metadata
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"获取文件元数据失败: {str(e)}"
            }
    
    async def _validate_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """验证文件"""
        try:
            # 检查文件大小
            if len(file_content) > self.settings.FILE_UPLOAD_MAX_SIZE:
                return {
                    "valid": False,
                    "error": f"文件大小超过限制 ({self.settings.FILE_UPLOAD_MAX_SIZE} bytes)"
                }
            
            # 检查文件扩展名
            file_ext = Path(filename).suffix.lower()
            if file_ext not in self.settings.FILE_ALLOWED_EXTENSIONS:
                return {
                    "valid": False,
                    "error": f"不支持的文件类型: {file_ext}"
                }
            
            # 检测MIME类型
            try:
                mime_type = magic.from_buffer(file_content, mime=True)
            except Exception:
                mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
            
            return {
                "valid": True,
                "mime_type": mime_type
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"文件验证失败: {str(e)}"
            }
    
    async def _check_file_exists(self, file_hash: str) -> Optional[FileStorageBasic]:
        """检查文件是否已存在"""
        stmt = select(FileStorageBasic).where(
            and_(
                FileStorageBasic.file_hash_md5 == file_hash,
                FileStorageBasic.file_status == "active"
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _generate_file_path(self, original_filename: str, file_hash: str) -> Dict[str, str]:
        """生成文件路径"""
        file_ext = Path(original_filename).suffix.lower()
        
        # 按日期组织目录结构
        now = datetime.utcnow()
        date_path = f"{now.year:04d}/{now.month:02d}/{now.day:02d}"
        
        # 使用哈希前缀避免同一目录文件过多
        hash_prefix = file_hash[:2]
        
        # 生成唯一文件名
        filename = f"{file_hash}{file_ext}"
        relative_path = f"{date_path}/{hash_prefix}/{filename}"
        full_path = self.storage_path / relative_path
        
        # 确保目录存在
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        return {
            "filename": filename,
            "file_path": str(full_path),
            "relative_path": relative_path
        }
    
    async def _store_file(self, file_content: bytes, file_path: str, storage_type: str) -> Dict[str, Any]:
        """存储文件"""
        try:
            if storage_type == "local":
                async with aiofiles.open(file_path, 'wb') as f:
                    await f.write(file_content)
            else:
                # 其他存储类型的实现
                return {
                    "success": False,
                    "error": f"不支持的存储类型: {storage_type}"
                }
            
            return {"success": True}
            
        except Exception as e:
            return {
                "success": False,
                "error": f"文件存储失败: {str(e)}"
            }
    
    async def _determine_file_category(self, file_content: bytes, filename: str) -> str:
        """确定文件类别"""
        try:
            mime_type = magic.from_buffer(file_content, mime=True)
        except Exception:
            mime_type = mimetypes.guess_type(filename)[0] or ""
        
        if mime_type.startswith("image/"):
            return FileCategory.IMAGE.value
        elif mime_type.startswith("audio/"):
            return FileCategory.AUDIO.value
        elif mime_type.startswith("video/"):
            return FileCategory.VIDEO.value
        elif mime_type.startswith("text/"):
            return FileCategory.TEXT.value
        elif mime_type in ["application/pdf", "application/msword"]:
            return FileCategory.DOCUMENT.value
        else:
            return FileCategory.OTHER.value
    
    async def _generate_file_metadata(
        self, 
        file_id: int, 
        file_content: bytes, 
        file_category: str, 
        user_id: int,
        custom_metadata: Optional[Dict[str, Any]] = None
    ):
        """生成文件元数据"""
        try:
            metadata_records = []
            
            if file_category == FileCategory.IMAGE.value:
                metadata_records.extend(await self._generate_image_metadata(file_id, file_content, user_id))
            elif file_category == FileCategory.AUDIO.value:
                metadata_records.extend(await self._generate_audio_metadata(file_id, file_content, user_id))
            
            # 添加自定义元数据
            if custom_metadata:
                for key, value in custom_metadata.items():
                    metadata_records.append(
                        FileStorageMeta(
                            file_id=file_id,
                            meta_key=key,
                            meta_value=str(value),
                            meta_type="string",
                            meta_category="custom",
                            meta_created_user_id=user_id
                        )
                    )
            
            # 批量添加元数据
            if metadata_records:
                self.db.add_all(metadata_records)
                await self.db.commit()
                
        except Exception as e:
            self.logger.error(f"Generate file metadata failed: {str(e)}")
    
    async def _generate_image_metadata(self, file_id: int, file_content: bytes, user_id: int) -> List[FileStorageMeta]:
        """生成图像元数据"""
        try:
            from io import BytesIO
            image = Image.open(BytesIO(file_content))
            
            return [
                FileStorageMeta.meta_create_image_metadata(
                    file_id=file_id,
                    width=image.width,
                    height=image.height,
                    format_name=image.format,
                    user_id=user_id
                )
            ]
        except Exception:
            return []
    
    async def _generate_audio_metadata(self, file_id: int, file_content: bytes, user_id: int) -> List[FileStorageMeta]:
        """生成音频元数据"""
        try:
            from io import BytesIO
            audio_file = mutagen.File(BytesIO(file_content))
            
            if audio_file:
                duration = audio_file.info.length if hasattr(audio_file.info, 'length') else 0
                bitrate = audio_file.info.bitrate if hasattr(audio_file.info, 'bitrate') else 0
                
                return [
                    FileStorageMeta.meta_create_audio_metadata(
                        file_id=file_id,
                        duration=duration,
                        sample_rate=0,  # 需要更详细的音频库来获取
                        channels=0,     # 需要更详细的音频库来获取
                        bitrate=bitrate,
                        user_id=user_id
                    )
                ]
        except Exception:
            return []
    
    async def _get_file_by_id(self, file_id: int) -> Optional[FileStorageBasic]:
        """根据ID获取文件记录"""
        stmt = select(FileStorageBasic).where(FileStorageBasic.file_id == file_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _read_file(self, file_path: str, storage_type: str) -> Optional[bytes]:
        """读取文件内容"""
        try:
            if storage_type == "local":
                if not os.path.exists(file_path):
                    return None
                
                async with aiofiles.open(file_path, 'rb') as f:
                    return await f.read()
            else:
                # 其他存储类型的实现
                return None
                
        except Exception:
            return None
    
    async def _delete_physical_file(self, file_path: str, storage_type: str):
        """删除物理文件"""
        try:
            if storage_type == "local":
                if os.path.exists(file_path):
                    os.remove(file_path)
            else:
                # 其他存储类型的实现
                pass
        except Exception:
            pass