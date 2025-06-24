"""
Image Content Create API Router
图像内容创建API路由 - [api][v1][image_video][image_content_create]
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.services.image_content_service import ImageContentService
from app.models.user_auth.user_auth_basic import UserAuthBasic


class ImageContentCreateRequest(BaseModel):
    """
    图像内容创建请求模型
    [api][v1][image_video][image_content_create][request]
    """
    model_config = {"protected_namespaces": ()}
    
    title: str = Field(..., description="图像标题", min_length=1, max_length=100)
    prompt: str = Field(..., description="生成提示词", min_length=1, max_length=2000)
    width: int = Field(512, description="图像宽度", ge=256, le=2048)
    height: int = Field(512, description="图像高度", ge=256, le=2048)
    style: Optional[str] = Field(None, description="图像风格")
    quality: str = Field("standard", description="图像质量")
    model_provider: str = Field("doubao", description="AI模型提供商")
    model_name: Optional[str] = Field(None, description="具体模型名称")
    template_id: Optional[int] = Field(None, description="模板ID")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    save_file: bool = Field(True, description="是否保存文件")


class ImageContentCreateResponse(BaseModel):
    """
    图像内容创建响应模型
    [api][v1][image_video][image_content_create][response]
    """
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: Optional[str] = None


class ImageContentBatchCreateRequest(BaseModel):
    """
    图像内容批量创建请求模型
    [api][v1][image_video][image_content_create][batch_request]
    """
    requests: List[ImageContentCreateRequest] = Field(..., description="批量创建请求列表", min_items=1, max_items=10)


def image_content_create_router_get() -> APIRouter:
    """
    获取图像内容创建API路由
    [api][v1][image_video][image_content_create][router_get]
    """
    router = APIRouter()
    
    @router.post(
        "/create",
        response_model=ImageContentCreateResponse,
        summary="创建图像内容",
        description="根据提示词生成图像并保存内容记录"
    )
    async def image_content_create(
        request: ImageContentCreateRequest,
        current_user: UserAuthBasic = Depends(get_current_user),
        db_session = Depends(get_db)
    ):
        """
        创建图像内容
        [api][v1][image_video][image_content_create][create]
        """
        try:
            service = ImageContentService(db_session)
            
            result = await service.image_content_service_create(
                title=request.title,
                prompt=request.prompt,
                width=request.width,
                height=request.height,
                style=request.style,
                quality=request.quality,
                model_provider=request.model_provider,
                model_name=request.model_name,
                user_id=current_user.user_id,
                template_id=request.template_id,
                tags=request.tags,
                save_file=request.save_file
            )
            
            if not result["success"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result["error"]
                )
            
            return ImageContentCreateResponse(
                success=True,
                data=result["data"],
                message="图像内容创建成功"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"图像内容创建失败: {str(e)}"
            )
    
    @router.post(
        "/create-batch",
        response_model=ImageContentCreateResponse,
        summary="批量创建图像内容",
        description="批量根据提示词生成图像并保存内容记录"
    )
    async def image_content_create_batch(
        request: ImageContentBatchCreateRequest,
        current_user: UserAuthBasic = Depends(get_current_user),
        db_session = Depends(get_db)
    ):
        """
        批量创建图像内容
        [api][v1][image_video][image_content_create][create_batch]
        """
        try:
            service = ImageContentService(db_session)
            
            # 收集所有创建任务
            results = []
            failed_count = 0
            
            for idx, create_request in enumerate(request.requests):
                try:
                    result = await service.image_content_service_create(
                        title=create_request.title,
                        prompt=create_request.prompt,
                        width=create_request.width,
                        height=create_request.height,
                        style=create_request.style,
                        quality=create_request.quality,
                        model_provider=create_request.model_provider,
                        model_name=create_request.model_name,
                        user_id=current_user.user_id,
                        template_id=create_request.template_id,
                        tags=create_request.tags,
                        save_file=create_request.save_file
                    )
                    
                    results.append({
                        "index": idx,
                        "success": result["success"],
                        "data": result.get("data") if result["success"] else None,
                        "error": result.get("error") if not result["success"] else None
                    })
                    
                    if not result["success"]:
                        failed_count += 1
                        
                except Exception as e:
                    results.append({
                        "index": idx,
                        "success": False,
                        "error": str(e)
                    })
                    failed_count += 1
            
            return ImageContentCreateResponse(
                success=failed_count == 0,
                data={
                    "results": results,
                    "total": len(request.requests),
                    "succeeded": len(request.requests) - failed_count,
                    "failed": failed_count
                },
                message=f"批量创建完成，成功 {len(request.requests) - failed_count}/{len(request.requests)} 个"
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"批量图像内容创建失败: {str(e)}"
            )
    
    @router.post(
        "/create-with-template/{template_type}",
        response_model=ImageContentCreateResponse,
        summary="使用模板创建图像内容",
        description="使用预定义模板创建图像内容"
    )
    async def image_content_create_with_template(
        template_type: str,
        variables: Dict[str, Any],
        model_provider: str = "doubao",
        model_name: Optional[str] = None,
        current_user: UserAuthBasic = Depends(get_current_user),
        db_session = Depends(get_db)
    ):
        """
        使用模板创建图像内容
        [api][v1][image_video][image_content_create][create_with_template]
        """
        try:
            from app.services.image_generation_service import image_generation_service
            
            # 使用图像生成服务的模板功能
            generation_result = await image_generation_service.image_generation_service_generate_with_template(
                template_type=template_type,
                variables=variables,
                model_provider=model_provider,
                model_name=model_name
            )
            
            if not generation_result["success"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=generation_result["error"]
                )
            
            # 创建图像内容记录
            service = ImageContentService(db_session)
            
            # 从模板生成标题
            title = f"{template_type.title()} - {variables.get('subject', variables.get('topic', 'Generated'))}"
            prompt = generation_result["data"]["original_prompt"]
            
            result = await service.image_content_service_create(
                title=title,
                prompt=prompt,
                width=generation_result["data"]["generation_params"]["width"],
                height=generation_result["data"]["generation_params"]["height"],
                style=generation_result["data"]["generation_params"].get("style"),
                quality=generation_result["data"]["generation_params"]["quality"],
                model_provider=model_provider,
                model_name=model_name,
                user_id=current_user.user_id,
                tags=[template_type, "template_generated"]
            )
            
            if not result["success"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result["error"]
                )
            
            return ImageContentCreateResponse(
                success=True,
                data={
                    **result["data"],
                    "template_type": template_type,
                    "template_variables": variables
                },
                message="模板图像内容创建成功"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"模板图像内容创建失败: {str(e)}"
            )
    
    return router