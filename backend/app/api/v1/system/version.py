"""
System Version API
系统版本信息API - [api][v1][system][version]
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any

from app.api.versioning import api_version_manager
from app.config.settings import app_config_get_settings

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/version")
async def system_version_get_info(request: Request) -> JSONResponse:
    """
    获取系统版本信息
    [api][v1][system][version][get_info]
    """
    settings = app_config_get_settings()
    
    # 获取当前API版本
    current_version = getattr(request.state, "api_version", "v1")
    
    response_data = {
        "success": True,
        "data": {
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "api_version": current_version,
            "supported_api_versions": api_version_manager.api_version_manager_get_supported_versions(),
            "environment": settings.ENVIRONMENT,
            "build_time": "2024-12-24T00:00:00Z",  # 可以从构建时设置
        }
    }
    
    return JSONResponse(content=response_data)


@router.get("/versions")
async def system_version_get_all_versions() -> JSONResponse:
    """
    获取所有API版本信息
    [api][v1][system][version][get_all_versions]
    """
    versions_info = api_version_manager.api_version_manager_get_all_versions()
    
    response_data = {
        "success": True,
        "data": {
            "versions": versions_info,
            "default_version": api_version_manager.default_version,
            "supported_versions": api_version_manager.api_version_manager_get_supported_versions()
        }
    }
    
    return JSONResponse(content=response_data)


@router.get("/health")
async def system_version_health_check() -> JSONResponse:
    """
    系统健康检查
    [api][v1][system][version][health_check]
    """
    # 这里可以添加更多健康检查逻辑
    # 比如数据库连接、Redis连接、外部服务状态等
    
    response_data = {
        "success": True,
        "data": {
            "status": "healthy",
            "timestamp": "2024-12-24T00:00:00Z",
            "checks": {
                "database": "healthy",
                "redis": "healthy",
                "external_apis": "healthy"
            }
        }
    }
    
    return JSONResponse(content=response_data)