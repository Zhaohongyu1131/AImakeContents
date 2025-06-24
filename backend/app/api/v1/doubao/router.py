"""
Doubao API Router
豆包API路由 - [api][v1][doubao][router]
"""

from fastapi import APIRouter, Depends
from .voice import doubao_voice_router_get
from .text import doubao_text_router_get
from .image import doubao_image_router_get
from app.dependencies.db import get_db


def doubao_router_get() -> APIRouter:
    """
    获取豆包API主路由
    [api][v1][doubao][router][get]
    """
    router = APIRouter()
    
    # 健康检查
    @router.get(
        "/health",
        summary="豆包API健康检查",
        description="检查豆包API服务状态"
    )
    async def doubao_health_check(db = Depends(get_db)):
        """
        豆包API健康检查
        [api][v1][doubao][health_check]
        """
        try:
            from app.services.doubao_service import DoubaoService
            doubao_service = DoubaoService(db)
            
            result = await doubao_service.doubao_service_health_check()
            
            if result["success"]:
                return {
                    "success": True,
                    "message": "Doubao API is healthy",
                    "service": "volcano_engine",
                    "details": result["data"]
                }
            else:
                return {
                    "success": False,
                    "message": "Doubao API health check failed",
                    "service": "volcano_engine",
                    "error": result["message"]
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Doubao API health check error: {str(e)}",
                "service": "volcano_engine"
            }
    
    # 包含子模块路由
    router.include_router(
        doubao_voice_router_get(),
        prefix="/voice",
        tags=["豆包-语音服务"]
    )
    
    router.include_router(
        doubao_text_router_get(),
        prefix="/text",
        tags=["豆包-文本服务"]
    )
    
    router.include_router(
        doubao_image_router_get(),
        prefix="/image",
        tags=["豆包-图像服务"]
    )
    
    return router