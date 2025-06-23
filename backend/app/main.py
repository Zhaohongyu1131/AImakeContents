"""
DataSay Main Application Entry Point
FastAPI主应用入口，遵循[业务模块][数据对象][操作]命名规范
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

from app.config.settings import app_config_get_settings
from app.api.v1.router import api_v1_router_get
from app.middleware import (
    cors_middleware_add,
    error_handler_add,
    logging_middleware_add,
    auth_middleware_add
)

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
    app.include_router(api_v1_router_get(), prefix=settings.API_V1_PREFIX)
    
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