"""
Permission Middleware
权限检查中间件 - [middleware][permission]
"""

from typing import Optional, Callable, Dict, Any
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user, CurrentUser
from app.services.permission_service import PermissionService

logger = logging.getLogger(__name__)


class PermissionMiddleware:
    """
    权限检查中间件
    [middleware][permission]
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        """
        ASGI应用调用
        [middleware][permission][call]
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # 检查是否需要权限验证的路径
        if not self._needs_permission_check(request.url.path):
            await self.app(scope, receive, send)
            return
        
        try:
            # 执行权限检查
            await self._check_permissions(request)
            await self.app(scope, receive, send)
            
        except HTTPException as exc:
            response = JSONResponse(
                status_code=exc.status_code,
                content={
                    "success": False,
                    "error": exc.detail,
                    "error_code": "PERMISSION_DENIED"
                }
            )
            await response(scope, receive, send)
        except Exception as e:
            logger.error(f"Permission middleware error: {str(e)}")
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "error": "权限检查失败",
                    "error_code": "PERMISSION_CHECK_ERROR"
                }
            )
            await response(scope, receive, send)
    
    def _needs_permission_check(self, path: str) -> bool:
        """
        检查路径是否需要权限验证
        [middleware][permission][needs_permission_check]
        """
        # 不需要权限检查的路径
        skip_paths = [
            "/api/v1/auth/register",
            "/api/v1/auth/login", 
            "/api/v1/auth/refresh",
            "/api/v1/auth/verify",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health"
        ]
        
        for skip_path in skip_paths:
            if path.startswith(skip_path):
                return False
        
        # 需要权限检查的API路径
        protected_patterns = [
            "/api/v1/admin",
            "/api/v1/voice",
            "/api/v1/text", 
            "/api/v1/image",
            "/api/v1/files"
        ]
        
        for pattern in protected_patterns:
            if path.startswith(pattern):
                return True
        
        return False
    
    async def _check_permissions(self, request: Request):
        """
        执行权限检查
        [middleware][permission][check_permissions]
        """
        # 获取路径和方法
        path = request.url.path
        method = request.method.lower()
        
        # 获取权限配置
        permission_config = self._get_permission_config(path, method)
        if not permission_config:
            return  # 无需特殊权限检查
        
        # 这里应该从请求中获取用户信息
        # 由于中间件无法直接使用Depends，需要手动实现认证逻辑
        # 实际应用中建议使用装饰器或依赖注入方式进行权限检查
        pass
    
    def _get_permission_config(self, path: str, method: str) -> Optional[Dict[str, Any]]:
        """
        获取路径的权限配置
        [middleware][permission][get_permission_config]
        """
        # 权限配置映射
        permission_map = {
            # 管理员路径
            "/api/v1/admin": {
                "resource": "admin",
                "action": "admin",
                "require_admin": True
            },
            
            # 语音相关
            "/api/v1/voice/create": {
                "resource": "voice_audio",
                "action": "create"
            },
            "/api/v1/voice/manage": {
                "resource": "voice_audio", 
                "action": "update"
            },
            
            # 文本相关
            "/api/v1/text/create": {
                "resource": "text_content",
                "action": "create"
            },
            "/api/v1/text/manage": {
                "resource": "text_content",
                "action": "update"
            },
            
            # 图像相关
            "/api/v1/image/create": {
                "resource": "image_content",
                "action": "create"
            },
            "/api/v1/image/manage": {
                "resource": "image_content",
                "action": "update"
            }
        }
        
        # 查找匹配的权限配置
        for pattern, config in permission_map.items():
            if path.startswith(pattern):
                return config
        
        return None


def require_permission_decorator(resource: str, action: str):
    """
    权限装饰器工厂
    [middleware][permission][require_permission_decorator]
    """
    def decorator(func):
        """权限装饰器"""
        async def wrapper(*args, **kwargs):
            # 从kwargs中获取当前用户和数据库会话
            current_user = kwargs.get('current_user')
            db = kwargs.get('db')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="需要登录"
                )
            
            if not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="数据库会话不可用"
                )
            
            # 执行权限检查
            permission_service = PermissionService(db)
            
            # 检查资源所有者（如果提供）
            resource_owner_id = kwargs.get('resource_owner_id')
            
            has_permission = await permission_service.permission_service_check_permission(
                current_user.user_id,
                resource,
                action,
                resource_owner_id
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"无权限执行操作: {resource}:{action}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# 预定义的权限装饰器
require_voice_create = require_permission_decorator("voice_audio", "create")
require_voice_read = require_permission_decorator("voice_audio", "read") 
require_voice_update = require_permission_decorator("voice_audio", "update")
require_voice_delete = require_permission_decorator("voice_audio", "delete")

require_text_create = require_permission_decorator("text_content", "create")
require_text_read = require_permission_decorator("text_content", "read")
require_text_update = require_permission_decorator("text_content", "update")
require_text_delete = require_permission_decorator("text_content", "delete")

require_image_create = require_permission_decorator("image_content", "create")
require_image_read = require_permission_decorator("image_content", "read")
require_image_update = require_permission_decorator("image_content", "update")
require_image_delete = require_permission_decorator("image_content", "delete")

require_file_create = require_permission_decorator("file_storage", "create")
require_file_read = require_permission_decorator("file_storage", "read")
require_file_update = require_permission_decorator("file_storage", "update")
require_file_delete = require_permission_decorator("file_storage", "delete")

require_admin_access = require_permission_decorator("system", "admin")