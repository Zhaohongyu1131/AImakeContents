"""
API V1 Main Router
API V1主路由 - [api][v1][router]
"""

from fastapi import APIRouter
from app.schemas.base import HealthCheckSchema
from app.api.v1.user_auth import user_auth_router_get
from app.api.v1.file_storage import file_storage_router_get
from app.api.v1.text_content import text_content_router_get
from app.api.v1.voice_timbre import voice_timbre_router_get
from app.api.v1.voice_audio import voice_audio_router_get

def api_v1_router_get() -> APIRouter:
    """
    获取API V1主路由
    [api][v1][router][get]
    """
    router = APIRouter()
    
    # 健康检查路由
    @router.get(
        "/health",
        response_model=HealthCheckSchema,
        summary="健康检查",
        description="检查API服务状态"
    )
    async def api_v1_health_check():
        """
        API健康检查
        [api][v1][health_check]
        """
        return HealthCheckSchema(
            success=True,
            message="DataSay API V1 is healthy",
            version="1.0.0"
        )
    
    # 包含业务模块路由
    router.include_router(
        user_auth_router_get(),
        prefix="/auth",
        tags=["用户认证"]
    )
    
    router.include_router(
        file_storage_router_get(),
        prefix="/files",
        tags=["文件存储"]
    )
    
    router.include_router(
        text_content_router_get(),
        prefix="/text",
        tags=["文本内容"]
    )
    
    router.include_router(
        voice_timbre_router_get(),
        prefix="/voice/timbre",
        tags=["音色管理"]
    )
    
    router.include_router(
        voice_audio_router_get(),
        prefix="/voice/audio",
        tags=["音频管理"]
    )
    
    # TODO: 添加其他业务模块路由
    # router.include_router(image_video_router_get(), prefix="/image", tags=["图像视频"])
    # router.include_router(mixed_content_router_get(), prefix="/mixed", tags=["混合内容"])
    
    return router