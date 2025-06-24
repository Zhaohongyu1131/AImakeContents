"""
Image Content Manage API Router
图像内容管理API路由 - [api][v1][image_video][image_content_manage]
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.services.image_content_service import ImageContentService
from app.models.user_auth.user_auth_basic import UserAuthBasic


class ImageContentGetResponse(BaseModel):
    """
    图像内容获取响应模型
    [api][v1][image_video][image_content_manage][get_response]
    """
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ImageContentListResponse(BaseModel):
    """
    图像内容列表响应模型
    [api][v1][image_video][image_content_manage][list_response]
    """
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    pagination: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ImageContentUpdateRequest(BaseModel):
    """
    图像内容更新请求模型
    [api][v1][image_video][image_content_manage][update_request]
    """
    title: Optional[str] = Field(None, description="图像标题", max_length=100)
    description: Optional[str] = Field(None, description="图像描述", max_length=2000)
    tags: Optional[List[str]] = Field(None, description="标签列表")


class ImageContentUpdateResponse(BaseModel):
    """
    图像内容更新响应模型
    [api][v1][image_video][image_content_manage][update_response]
    """
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: Optional[str] = None


class ImageContentDeleteResponse(BaseModel):
    """
    图像内容删除响应模型
    [api][v1][image_video][image_content_manage][delete_response]
    """
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None


class ImageContentAnalyseRequest(BaseModel):
    """
    图像内容分析请求模型
    [api][v1][image_video][image_content_manage][analyse_request]
    """
    analyse_type: str = Field(..., description="分析类型", pattern="^(quality|content|style|emotion|objects)$")
    custom_params: Optional[Dict[str, Any]] = Field(None, description="自定义分析参数")


class ImageContentAnalyseResponse(BaseModel):
    """
    图像内容分析响应模型
    [api][v1][image_video][image_content_manage][analyse_response]
    """
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: Optional[str] = None


def image_content_manage_router_get() -> APIRouter:
    """
    获取图像内容管理API路由
    [api][v1][image_video][image_content_manage][router_get]
    """
    router = APIRouter()
    
    @router.get(
        "/{image_id}",
        response_model=ImageContentGetResponse,
        summary="获取图像内容详情",
        description="根据图像ID获取图像内容的详细信息"
    )
    async def image_content_get(
        image_id: int,
        current_user: UserAuthBasic = Depends(get_current_user),
        db_session = Depends(get_db)
    ):
        """
        获取图像内容详情
        [api][v1][image_video][image_content_manage][get]
        """
        try:
            service = ImageContentService(db_session)
            
            result = await service.image_content_service_get(
                image_id=image_id,
                user_id=current_user.user_id
            )
            
            if not result["success"]:
                if "不存在" in result["error"]:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=result["error"]
                    )
                elif "无权限" in result["error"]:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=result["error"]
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=result["error"]
                    )
            
            return ImageContentGetResponse(
                success=True,
                data=result["data"]
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取图像内容失败: {str(e)}"
            )
    
    @router.get(
        "/",
        response_model=ImageContentListResponse,
        summary="获取图像内容列表",
        description="分页获取图像内容列表，支持多种过滤条件"
    )
    async def image_content_list(
        status_filter: Optional[str] = Query(None, description="状态过滤"),
        format_filter: Optional[str] = Query(None, description="格式过滤"),
        model_provider: Optional[str] = Query(None, description="模型提供商过滤"),
        keyword: Optional[str] = Query(None, description="关键词搜索"),
        page: int = Query(1, description="页码", ge=1),
        size: int = Query(20, description="每页数量", ge=1, le=100),
        current_user: UserAuthBasic = Depends(get_current_user),
        db_session = Depends(get_db)
    ):
        """
        获取图像内容列表
        [api][v1][image_video][image_content_manage][list]
        """
        try:
            service = ImageContentService(db_session)
            
            result = await service.image_content_service_list(
                user_id=current_user.user_id,
                status=status_filter,
                format_filter=format_filter,
                model_provider=model_provider,
                keyword=keyword,
                page=page,
                size=size
            )
            
            if not result["success"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result["error"]
                )
            
            return ImageContentListResponse(
                success=True,
                data=result["data"],
                pagination=result["pagination"]
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取图像内容列表失败: {str(e)}"
            )
    
    @router.put(
        "/{image_id}",
        response_model=ImageContentUpdateResponse,
        summary="更新图像内容",
        description="更新图像内容的标题、描述和标签等信息"
    )
    async def image_content_update(
        image_id: int,
        request: ImageContentUpdateRequest,
        current_user: UserAuthBasic = Depends(get_current_user),
        db_session = Depends(get_db)
    ):
        """
        更新图像内容
        [api][v1][image_video][image_content_manage][update]
        """
        try:
            service = ImageContentService(db_session)
            
            result = await service.image_content_service_update(
                image_id=image_id,
                title=request.title,
                description=request.description,
                tags=request.tags,
                user_id=current_user.user_id
            )
            
            if not result["success"]:
                if "不存在" in result["error"]:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=result["error"]
                    )
                elif "无权限" in result["error"]:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=result["error"]
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=result["error"]
                    )
            
            return ImageContentUpdateResponse(
                success=True,
                data=result["data"],
                message="图像内容更新成功"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"更新图像内容失败: {str(e)}"
            )
    
    @router.delete(
        "/{image_id}",
        response_model=ImageContentDeleteResponse,
        summary="删除图像内容",
        description="软删除图像内容记录"
    )
    async def image_content_delete(
        image_id: int,
        current_user: UserAuthBasic = Depends(get_current_user),
        db_session = Depends(get_db)
    ):
        """
        删除图像内容
        [api][v1][image_video][image_content_manage][delete]
        """
        try:
            service = ImageContentService(db_session)
            
            result = await service.image_content_service_delete(
                image_id=image_id,
                user_id=current_user.user_id
            )
            
            if not result["success"]:
                if "不存在" in result["error"]:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=result["error"]
                    )
                elif "无权限" in result["error"]:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=result["error"]
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=result["error"]
                    )
            
            return ImageContentDeleteResponse(
                success=True,
                message=result["message"]
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"删除图像内容失败: {str(e)}"
            )
    
    @router.post(
        "/{image_id}/analyse",
        response_model=ImageContentAnalyseResponse,
        summary="分析图像内容",
        description="对图像进行AI分析，支持质量、内容、风格等多种分析类型"
    )
    async def image_content_analyse(
        image_id: int,
        request: ImageContentAnalyseRequest,
        current_user: UserAuthBasic = Depends(get_current_user),
        db_session = Depends(get_db)
    ):
        """
        分析图像内容
        [api][v1][image_video][image_content_manage][analyse]
        """
        try:
            service = ImageContentService(db_session)
            
            result = await service.image_content_service_analyse(
                image_id=image_id,
                analyse_type=request.analyse_type,
                user_id=current_user.user_id,
                custom_params=request.custom_params
            )
            
            if not result["success"]:
                if "不存在" in result["error"]:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=result["error"]
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=result["error"]
                    )
            
            return ImageContentAnalyseResponse(
                success=True,
                data=result["data"],
                message="图像分析完成"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"图像分析失败: {str(e)}"
            )
    
    @router.get(
        "/{image_id}/analyses",
        summary="获取图像分析历史",
        description="获取图像的所有分析结果历史记录"
    )
    async def image_content_analyses_get(
        image_id: int,
        current_user: UserAuthBasic = Depends(get_current_user),
        db_session = Depends(get_db)
    ):
        """
        获取图像分析历史
        [api][v1][image_video][image_content_manage][analyses_get]
        """
        try:
            service = ImageContentService(db_session)
            
            # 先验证图像是否存在和权限
            image_result = await service.image_content_service_get(
                image_id=image_id,
                user_id=current_user.user_id
            )
            
            if not image_result["success"]:
                if "不存在" in image_result["error"]:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=image_result["error"]
                    )
                elif "无权限" in image_result["error"]:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=image_result["error"]
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=image_result["error"]
                    )
            
            # 获取分析历史
            analyses = await service.image_content_service_get_analyses(image_id)
            
            return {
                "success": True,
                "data": analyses,
                "message": f"获取到 {len(analyses)} 条分析记录"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取图像分析历史失败: {str(e)}"
            )
    
    return router