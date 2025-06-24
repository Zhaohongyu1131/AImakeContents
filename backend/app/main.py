"""
DataSay Main Application Entry Point
FastAPI主应用入口，遵循[业务模块][数据对象][操作]命名规范
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
import logging

from app.config.settings import app_config_get_settings
from app.api.main import api_router
from app.middleware import (
    cors_middleware_add,
    error_handler_add,
    logging_middleware_add,
    auth_middleware_add
)
from app.services.voice_platform_manager import voice_platform_manager
from app.services.voice_platform_manager import VoicePlatformType

async def app_main_initialize_platforms():
    """
    初始化语音平台管理器
    [app][main][initialize_platforms]
    """
    logger = logging.getLogger(__name__)
    
    try:
        # 获取配置
        settings = app_config_get_settings()
        
        # 更新Volcano平台配置
        volcano_config = {
            "is_enabled": True,
            "api_config": {
                "appid": getattr(settings, 'VOLCANO_VOICE_APPID', ''),
                "access_token": getattr(settings, 'VOLCANO_VOICE_ACCESS_TOKEN', ''),
                "cluster": getattr(settings, 'VOLCANO_VOICE_CLUSTER', 'volcano_icl'),
                "base_url": "https://openspeech.bytedance.com"
            }
        }
        
        # 更新平台配置
        await voice_platform_manager.voice_platform_manager_update_platform_config(
            VoicePlatformType.VOLCANO, 
            volcano_config
        )
        
        # 初始化已启用的平台
        for platform_type in [VoicePlatformType.VOLCANO, VoicePlatformType.AZURE, VoicePlatformType.OPENAI]:
            try:
                success = await voice_platform_manager.voice_platform_manager_initialize_platform(platform_type)
                if success:
                    logger.info(f"Platform {platform_type.value} initialized successfully")
                else:
                    logger.warning(f"Platform {platform_type.value} initialization failed")
            except Exception as e:
                logger.error(f"Error initializing platform {platform_type.value}: {str(e)}")
        
        # 启动健康检查任务
        asyncio.create_task(app_main_platform_health_monitor())
        
        logger.info("Voice platform manager initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize voice platform manager: {str(e)}")

async def app_main_platform_health_monitor():
    """
    平台健康监控任务
    [app][main][platform_health_monitor]
    """
    logger = logging.getLogger(__name__)
    
    while True:
        try:
            await voice_platform_manager.voice_platform_manager_health_check_all_platforms()
            logger.debug("Platform health check completed")
        except Exception as e:
            logger.error(f"Platform health check failed: {str(e)}")
        
        # 每5分钟检查一次
        await asyncio.sleep(300)

def app_main_create() -> FastAPI:
    """
    创建FastAPI应用实例
    [app][main][create]
    """
    settings = app_config_get_settings()
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="DataSay - 企业级多模态内容创作平台",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    )
    
    # 添加中间件（注意顺序很重要）
    cors_middleware_add(app)
    logging_middleware_add(app)
    auth_middleware_add(app)
    error_handler_add(app)
    
    # 注册API路由
    app.include_router(api_router)
    
    # 添加启动事件
    @app.on_event("startup")
    async def startup_event():
        """应用启动事件"""
        await app_main_initialize_platforms()
    
    # 添加关闭事件
    @app.on_event("shutdown")
    async def shutdown_event():
        """应用关闭事件"""
        await voice_platform_manager.voice_platform_manager_cleanup_all_platforms()
    
    return app

# 创建应用实例
app = app_main_create()

@app.get("/")
async def app_main_health_check():
    """
    应用健康检查接口
    [app][main][health_check]
    """
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "DataSay API is running",
            "version": "1.0.0"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )