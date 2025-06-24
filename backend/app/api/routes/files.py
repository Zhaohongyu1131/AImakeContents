"""
File Storage API Routes
文件存储API路由 - [api][routes][files]
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_
from pydantic import BaseModel
import io

from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user, get_optional_current_user, CurrentUser
from app.services.file_storage_service import FileStorageService, FileCategory
from app.middleware.permission import require_file_create, require_file_read, require_file_delete

router = APIRouter(prefix="/files", tags=["files"])


# Pydantic模型
class FileUploadResponse(BaseModel):
    """
    文件上传响应模型
    [api][routes][files][upload_response]
    """
    file_id: int
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    mime_type: str
    file_url: str
    upload_time: str
    
    model_config = {"protected_namespaces": ()}


class FileListRequest(BaseModel):
    """
    文件列表请求模型
    [api][routes][files][list_request]
    """
    file_type: Optional[str] = None
    search: Optional[str] = None
    page: int = 1
    size: int = 20
    
    model_config = {"protected_namespaces": ()}


@router.post("/upload", summary="上传文件")
async def files_upload(
    file: UploadFile = File(...),
    file_category: Optional[str] = Form(None),
    custom_metadata: Optional[str] = Form(None),  # JSON字符串
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    上传文件
    [api][routes][files][upload]
    """
    try:
        # 读取文件内容
        file_content = await file.read()
        
        # 解析自定义元数据
        metadata_dict = None
        if custom_metadata:
            import json
            try:
                metadata_dict = json.loads(custom_metadata)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="自定义元数据格式错误"
                )
        
        # 验证文件类别
        if file_category and file_category not in [cat.value for cat in FileCategory]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的文件类别"
            )
        
        # 创建文件存储服务
        file_service = FileStorageService(db)
        
        # 上传文件
        result = await file_service.file_storage_service_upload(
            file_data=file_content,
            original_filename=file.filename,
            user_id=current_user.user_id,
            file_category=file_category,
            custom_metadata=metadata_dict
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "success": True,
            "message": "文件上传成功",
            "data": result["data"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {str(e)}"
        )


@router.get("/download/{file_id}", summary="下载文件")
async def files_download(
    file_id: int,
    current_user: Optional[CurrentUser] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    下载文件
    [api][routes][files][download]
    """
    try:
        file_service = FileStorageService(db)
        
        # 下载文件
        result = await file_service.file_storage_service_download(
            file_id=file_id,
            user_id=current_user.user_id if current_user else None
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        
        file_data = result["data"]
        
        # 创建文件流响应
        file_stream = io.BytesIO(file_data["file_content"])
        
        headers = {
            "Content-Disposition": f"attachment; filename=\"{file_data['filename']}\""
        }
        
        return StreamingResponse(
            io.BytesIO(file_data["file_content"]),
            media_type=file_data["mime_type"],
            headers=headers
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件下载失败: {str(e)}"
        )


@router.get("/list", summary="获取文件列表")
async def files_list(
    file_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取用户文件列表
    [api][routes][files][list]
    """
    try:
        file_service = FileStorageService(db)
        
        result = await file_service.file_storage_service_list(
            user_id=current_user.user_id,
            file_type=file_type,
            page=page,
            size=size,
            search=search
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        return {
            "success": True,
            "data": result["data"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文件列表失败: {str(e)}"
        )


@router.get("/admin/list", summary="管理员获取所有文件列表")
async def files_admin_list(
    file_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    管理员获取所有文件列表
    [api][routes][files][admin_list]
    """
    try:
        # 检查管理员权限
        if current_user.user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理员权限"
            )
        
        file_service = FileStorageService(db)
        
        result = await file_service.file_storage_service_list(
            user_id=user_id,
            file_type=file_type,
            page=page,
            size=size,
            search=search
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        return {
            "success": True,
            "data": result["data"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文件列表失败: {str(e)}"
        )


@router.get("/{file_id}/metadata", summary="获取文件元数据")
async def files_get_metadata(
    file_id: int,
    current_user: Optional[CurrentUser] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取文件元数据
    [api][routes][files][get_metadata]
    """
    try:
        file_service = FileStorageService(db)
        
        result = await file_service.file_storage_service_get_metadata(file_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        
        return {
            "success": True,
            "data": result["data"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文件元数据失败: {str(e)}"
        )


@router.delete("/{file_id}", summary="删除文件")
async def files_delete(
    file_id: int,
    permanent: bool = Query(False),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    删除文件
    [api][routes][files][delete]
    """
    try:
        file_service = FileStorageService(db)
        
        result = await file_service.file_storage_service_delete(
            file_id=file_id,
            user_id=current_user.user_id,
            permanent=permanent
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "success": True,
            "message": result["message"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除文件失败: {str(e)}"
        )


@router.get("/categories", summary="获取文件类别列表")
async def files_get_categories() -> Dict[str, Any]:
    """
    获取支持的文件类别列表
    [api][routes][files][get_categories]
    """
    try:
        categories = [
            {
                "value": category.value,
                "label": {
                    "image": "图像",
                    "audio": "音频", 
                    "video": "视频",
                    "text": "文本",
                    "document": "文档",
                    "other": "其他"
                }.get(category.value, category.value)
            }
            for category in FileCategory
        ]
        
        return {
            "success": True,
            "data": {
                "categories": categories
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文件类别失败: {str(e)}"
        )


@router.post("/batch-upload", summary="批量上传文件")
async def files_batch_upload(
    files: List[UploadFile] = File(...),
    file_category: Optional[str] = Form(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    批量上传文件
    [api][routes][files][batch_upload]
    """
    try:
        if len(files) > 10:  # 限制一次最多上传10个文件
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="一次最多上传10个文件"
            )
        
        file_service = FileStorageService(db)
        results = []
        
        for file in files:
            try:
                file_content = await file.read()
                
                result = await file_service.file_storage_service_upload(
                    file_data=file_content,
                    original_filename=file.filename,
                    user_id=current_user.user_id,
                    file_category=file_category
                )
                
                results.append({
                    "filename": file.filename,
                    "success": result["success"],
                    "data": result.get("data"),
                    "error": result.get("error")
                })
                
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": str(e)
                })
        
        # 统计结果
        success_count = sum(1 for r in results if r["success"])
        
        return {
            "success": True,
            "message": f"批量上传完成，成功: {success_count}/{len(files)}",
            "data": {
                "results": results,
                "summary": {
                    "total": len(files),
                    "success": success_count,
                    "failed": len(files) - success_count
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量上传失败: {str(e)}"
        )


@router.get("/statistics", summary="获取文件统计信息")
async def files_get_statistics(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取用户文件统计信息
    [api][routes][files][get_statistics]
    """
    try:
        from sqlalchemy import select, func
        from app.models.file_storage.file_storage_basic import FileStorageBasic
        
        # 用户文件总数
        total_stmt = select(func.count(FileStorageBasic.file_id)).where(
            and_(
                FileStorageBasic.file_created_user_id == current_user.user_id,
                FileStorageBasic.file_status == "active"
            )
        )
        total_result = await db.execute(total_stmt)
        total_files = total_result.scalar()
        
        # 用户文件总大小
        size_stmt = select(func.sum(FileStorageBasic.file_size)).where(
            and_(
                FileStorageBasic.file_created_user_id == current_user.user_id,
                FileStorageBasic.file_status == "active"
            )
        )
        size_result = await db.execute(size_stmt)
        total_size = size_result.scalar() or 0
        
        # 按类型统计
        type_stats = {}
        for category in FileCategory:
            type_stmt = select(func.count(FileStorageBasic.file_id)).where(
                and_(
                    FileStorageBasic.file_created_user_id == current_user.user_id,
                    FileStorageBasic.file_type == category.value,
                    FileStorageBasic.file_status == "active"
                )
            )
            type_result = await db.execute(type_stmt)
            type_stats[category.value] = type_result.scalar()
        
        return {
            "success": True,
            "data": {
                "total_files": total_files,
                "total_size": total_size,
                "total_size_human": f"{total_size / (1024*1024):.1f} MB" if total_size else "0 B",
                "type_statistics": type_stats
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )