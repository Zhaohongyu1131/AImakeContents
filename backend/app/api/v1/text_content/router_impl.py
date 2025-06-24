"""
Text Content API Router Implementation
文本内容API路由实现 - [api][v1][text_content][router_impl]
"""

from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import deps_get_current_user, deps_get_db
from app.services.text_content import TextContentService
from app.schemas.base import ResponseBaseSchema, PaginatedResponseSchema
from app.schemas.text_content import (
    TextContentBasicSchema,
    TextContentBasicCreateSchema,
    TextContentBasicUpdateSchema,
    TextContentAnalyseSchema,
    TextContentAnalyseCreateSchema,
    TextTemplateBasicSchema,
    TextTemplateBasicCreateSchema,
    TextTemplateBasicUpdateSchema,
    TextContentGenerateSchema,
    TextContentBatchGenerateSchema,
    TextContentStatsSchema,
    TextContentCompleteSchema
)
from app.models.user_auth.user_auth_basic import UserAuthBasic


def text_content_router_impl_get() -> APIRouter:
    """
    获取文本内容API路由（实现版）
    [api][v1][text_content][router_impl][get]
    """
    router = APIRouter()
    
    # ==================== 文本内容管理 ====================
    
    @router.post(
        "/contents",
        response_model=ResponseBaseSchema[TextContentBasicSchema],
        status_code=status.HTTP_201_CREATED,
        summary="创建文本内容",
        description="创建新的文本内容"
    )
    async def text_content_create(
        content_data: TextContentBasicCreateSchema,
        current_user: UserAuthBasic = Depends(deps_get_current_user),
        db: AsyncSession = Depends(deps_get_db)
    ):
        """
        创建文本内容
        [api][v1][text_content][create]
        """
        service = TextContentService(db)
        
        result = await service.text_content_service_create(
            content=content_data.content_text,
            title=content_data.content_title,
            content_type=content_data.content_type,
            user_id=current_user.user_id,
            template_id=content_data.content_template_id,
            source_prompt=content_data.content_source_prompt,
            generation_params=content_data.content_generation_params,
            tags=content_data.content_tags,
            language=content_data.content_language
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return ResponseBaseSchema(
            success=True,
            message="文本内容创建成功",
            data=result["data"]
        )
    
    @router.get(
        "/contents/{content_id}",
        response_model=ResponseBaseSchema[TextContentCompleteSchema],
        summary="获取文本内容",
        description="根据内容ID获取完整文本信息"
    )
    async def text_content_get(
        content_id: int,
        current_user: UserAuthBasic = Depends(deps_get_current_user),
        db: AsyncSession = Depends(deps_get_db)
    ):
        """
        获取文本内容
        [api][v1][text_content][get]
        """
        service = TextContentService(db)
        
        result = await service.text_content_service_get(
            text_id=content_id,
            user_id=current_user.user_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        
        return ResponseBaseSchema(
            success=True,
            message="获取文本内容成功",
            data={
                "content": result["data"],
                "template": None,  # TODO: 获取模板信息
                "analyses": result["data"].get("analyses", [])
            }
        )
    
    @router.put(
        "/contents/{content_id}",
        response_model=ResponseBaseSchema[TextContentBasicSchema],
        summary="更新文本内容",
        description="更新文本内容信息"
    )
    async def text_content_update(
        content_id: int,
        content_data: TextContentBasicUpdateSchema,
        current_user: UserAuthBasic = Depends(deps_get_current_user),
        db: AsyncSession = Depends(deps_get_db)
    ):
        """
        更新文本内容
        [api][v1][text_content][update]
        """
        service = TextContentService(db)
        
        result = await service.text_content_service_update(
            text_id=content_id,
            content=content_data.content_text,
            title=content_data.content_title,
            user_id=current_user.user_id,
            tags=content_data.content_tags,
            language=content_data.content_language
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return ResponseBaseSchema(
            success=True,
            message="文本内容更新成功",
            data=result["data"]
        )
    
    @router.delete(
        "/contents/{content_id}",
        response_model=ResponseBaseSchema[None],
        summary="删除文本内容",
        description="删除指定的文本内容"
    )
    async def text_content_delete(
        content_id: int,
        current_user: UserAuthBasic = Depends(deps_get_current_user),
        db: AsyncSession = Depends(deps_get_db)
    ):
        """
        删除文本内容
        [api][v1][text_content][delete]
        """
        service = TextContentService(db)
        
        result = await service.text_content_service_delete(
            text_id=content_id,
            user_id=current_user.user_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return ResponseBaseSchema(
            success=True,
            message="文本内容删除成功",
            data=None
        )
    
    @router.get(
        "/contents",
        response_model=PaginatedResponseSchema[TextContentBasicSchema],
        summary="获取文本内容列表",
        description="分页获取文本内容列表"
    )
    async def text_content_list(
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=100),
        content_type: Optional[str] = None,
        language: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        current_user: UserAuthBasic = Depends(deps_get_current_user),
        db: AsyncSession = Depends(deps_get_db)
    ):
        """
        获取文本内容列表
        [api][v1][text_content][list]
        """
        service = TextContentService(db)
        
        result = await service.text_content_service_list(
            user_id=current_user.user_id,
            content_type=content_type,
            keyword=search,
            page=page,
            size=size
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return PaginatedResponseSchema(
            success=True,
            message="获取文本内容列表成功",
            data=result["data"],
            pagination=result["pagination"]
        )
    
    # ==================== 文本生成 ====================
    
    @router.post(
        "/generate",
        response_model=ResponseBaseSchema[TextContentBasicSchema],
        status_code=status.HTTP_201_CREATED,
        summary="生成文本内容",
        description="使用AI生成文本内容"
    )
    async def text_content_generate(
        generate_data: TextContentGenerateSchema,
        current_user: UserAuthBasic = Depends(deps_get_current_user),
        db: AsyncSession = Depends(deps_get_db)
    ):
        """
        生成文本内容
        [api][v1][text_content][generate]
        """
        service = TextContentService(db)
        
        result = await service.text_content_service_generate(
            prompt=generate_data.prompt,
            template_type=generate_data.template_type,
            model_provider=generate_data.model_provider,
            user_id=current_user.user_id,
            save_result=generate_data.save_result,
            title=generate_data.title,
            content_type=generate_data.content_type,
            temperature=generate_data.generation_params.get("temperature", 0.7) if generate_data.generation_params else 0.7,
            max_tokens=generate_data.generation_params.get("max_tokens", 2000) if generate_data.generation_params else 2000,
            system_prompt=generate_data.generation_params.get("system_prompt") if generate_data.generation_params else None,
            variables=generate_data.template_variables
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return ResponseBaseSchema(
            success=True,
            message="文本生成成功",
            data=result["data"]
        )
    
    @router.post(
        "/generate/batch",
        response_model=ResponseBaseSchema[Dict[str, Any]],
        status_code=status.HTTP_201_CREATED,
        summary="批量生成文本内容",
        description="批量使用AI生成多个文本内容"
    )
    async def text_content_batch_generate(
        generate_data: TextContentBatchGenerateSchema,
        current_user: UserAuthBasic = Depends(deps_get_current_user),
        db: AsyncSession = Depends(deps_get_db)
    ):
        """
        批量生成文本内容
        [api][v1][text_content][batch_generate]
        """
        service = TextContentService(db)
        
        result = await service.text_content_service_generate_batch(
            prompts=generate_data.prompts,
            model_provider=generate_data.model_provider,
            user_id=current_user.user_id,
            save_results=generate_data.save_results,
            temperature=generate_data.common_params.get("temperature", 0.7) if generate_data.common_params else 0.7,
            max_tokens=generate_data.common_params.get("max_tokens", 2000) if generate_data.common_params else 2000,
            system_prompt=generate_data.common_params.get("system_prompt") if generate_data.common_params else None
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return ResponseBaseSchema(
            success=True,
            message=f"批量生成完成，成功 {result['data']['succeeded']} 个，失败 {result['data']['failed']} 个",
            data=result["data"]
        )
    
    # ==================== 文本分析 ====================
    
    @router.post(
        "/contents/{content_id}/analyse",
        response_model=ResponseBaseSchema[TextContentAnalyseSchema],
        status_code=status.HTTP_201_CREATED,
        summary="创建文本分析",
        description="对文本内容进行分析"
    )
    async def text_content_create_analyse(
        content_id: int,
        analyse_data: TextContentAnalyseCreateSchema,
        current_user: UserAuthBasic = Depends(deps_get_current_user),
        db: AsyncSession = Depends(deps_get_db)
    ):
        """
        创建文本分析
        [api][v1][text_content][create_analyse]
        """
        service = TextContentService(db)
        
        result = await service.text_content_service_analyse(
            text_id=content_id,
            analyse_type=analyse_data.analyse_type,
            user_id=current_user.user_id,
            custom_params=analyse_data.analyse_params
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return ResponseBaseSchema(
            success=True,
            message="文本分析创建成功",
            data=result["data"]
        )
    
    @router.get(
        "/contents/{content_id}/analyses",
        response_model=ResponseBaseSchema[List[TextContentAnalyseSchema]],
        summary="获取文本分析列表",
        description="获取文本内容的所有分析结果"
    )
    async def text_content_get_analyses(
        content_id: int,
        current_user: UserAuthBasic = Depends(deps_get_current_user),
        db: AsyncSession = Depends(deps_get_db)
    ):
        """
        获取文本分析列表
        [api][v1][text_content][get_analyses]
        """
        service = TextContentService(db)
        
        analyses = await service.text_content_service_get_analyses(
            text_id=content_id
        )
        
        return ResponseBaseSchema(
            success=True,
            message="获取文本分析列表成功",
            data=analyses
        )
    
    # ==================== 文本模板管理 ====================
    
    # TODO: 实现模板管理相关API
    
    # ==================== 统计信息 ====================
    
    @router.get(
        "/stats",
        response_model=ResponseBaseSchema[TextContentStatsSchema],
        summary="获取文本统计信息",
        description="获取文本内容的统计数据"
    )
    async def text_content_get_stats(
        current_user: UserAuthBasic = Depends(deps_get_current_user),
        db: AsyncSession = Depends(deps_get_db)
    ):
        """
        获取文本统计信息
        [api][v1][text_content][get_stats]
        """
        # TODO: 实现统计逻辑
        return ResponseBaseSchema(
            success=True,
            message="获取文本统计信息成功",
            data={
                "total_contents": 0,
                "total_words": 0,
                "content_types": {},
                "language_distribution": {},
                "creation_trends": [],
                "popular_templates": []
            }
        )
    
    return router