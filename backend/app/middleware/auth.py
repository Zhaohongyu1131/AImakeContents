"""
Authentication Middleware
认证中间件 - [middleware][auth]
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
import logging
from app.config.settings import app_config_get_settings
from app.middleware.error import AuthenticationException, AuthorizationException

logger = logging.getLogger(__name__)

# JWT Bearer Token 安全方案
security = HTTPBearer(auto_error=False)

class AuthMiddleware:
    """
    认证中间件类
    [middleware][auth][middleware]
    """
    
    def __init__(self):
        self.settings = app_config_get_settings()
    
    def auth_token_decode(self, token: str) -> dict:
        """
        解码JWT令牌
        [middleware][auth][token_decode]
        """
        try:
            payload = jwt.decode(
                token,
                self.settings.JWT_SECRET_KEY,
                algorithms=[self.settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError as e:
            logger.warning(f"JWT解码失败: {e}")
            raise AuthenticationException("无效的认证令牌")
    
    def auth_token_verify(self, token: str) -> dict:
        """
        验证JWT令牌
        [middleware][auth][token_verify]
        """
        payload = self.auth_token_decode(token)
        
        # 检查令牌是否包含必要字段
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationException("令牌缺少用户信息")
        
        # 检查令牌是否过期
        exp = payload.get("exp")
        if not exp:
            raise AuthenticationException("令牌缺少过期时间")
        
        return payload
    
    def auth_permission_check(self, user_payload: dict, required_role: str = None) -> bool:
        """
        检查用户权限
        [middleware][auth][permission_check]
        """
        if not required_role:
            return True
        
        user_role = user_payload.get("role", "user")
        
        # 角色层级检查
        role_hierarchy = {
            "admin": 3,
            "moderator": 2,
            "user": 1,
            "guest": 0
        }
        
        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 1)
        
        return user_level >= required_level

# 全局认证中间件实例
auth_middleware = AuthMiddleware()

def auth_current_user_get(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """
    获取当前用户信息（可选认证）
    [middleware][auth][current_user_get]
    """
    if not credentials:
        return None
    
    try:
        payload = auth_middleware.auth_token_verify(credentials.credentials)
        return payload
    except AuthenticationException:
        return None

def auth_current_user_require(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    获取当前用户信息（必须认证）
    [middleware][auth][current_user_require]
    """
    if not credentials:
        raise AuthenticationException("缺少认证令牌")
    
    payload = auth_middleware.auth_token_verify(credentials.credentials)
    return payload

def auth_admin_require(
    current_user: dict = Depends(auth_current_user_require)
) -> dict:
    """
    要求管理员权限
    [middleware][auth][admin_require]
    """
    if not auth_middleware.auth_permission_check(current_user, "admin"):
        raise AuthorizationException("需要管理员权限")
    
    return current_user

def auth_moderator_require(
    current_user: dict = Depends(auth_current_user_require)
) -> dict:
    """
    要求版主权限
    [middleware][auth][moderator_require]
    """
    if not auth_middleware.auth_permission_check(current_user, "moderator"):
        raise AuthorizationException("需要版主权限")
    
    return current_user

def auth_user_require(
    current_user: dict = Depends(auth_current_user_require)
) -> dict:
    """
    要求用户权限
    [middleware][auth][user_require]
    """
    if not auth_middleware.auth_permission_check(current_user, "user"):
        raise AuthorizationException("需要用户权限")
    
    return current_user

def auth_owner_or_admin_require(
    resource_user_id: int,
    current_user: dict = Depends(auth_current_user_require)
) -> dict:
    """
    要求资源所有者或管理员权限
    [middleware][auth][owner_or_admin_require]
    """
    user_id = int(current_user.get("sub", 0))
    user_role = current_user.get("role", "user")
    
    # 检查是否为资源所有者或管理员
    if user_id != resource_user_id and user_role != "admin":
        raise AuthorizationException("只有资源所有者或管理员可以执行此操作")
    
    return current_user

def auth_middleware_add(app: FastAPI) -> None:
    """
    添加认证中间件
    [middleware][auth][add]
    """
    # 添加认证相关的异常处理
    @app.exception_handler(AuthenticationException)
    async def authentication_exception_handler(request: Request, exc: AuthenticationException):
        """
        认证异常处理器
        [middleware][auth][authentication_exception_handler]
        """
        from fastapi.responses import JSONResponse
        from app.schemas.base import ErrorSchema
        
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorSchema(
                success=False,
                message=exc.message,
                error_code=exc.error_code,
                error_detail={
                    "path": str(request.url.path),
                    "method": request.method
                }
            ).dict()
        )
    
    @app.exception_handler(AuthorizationException)
    async def authorization_exception_handler(request: Request, exc: AuthorizationException):
        """
        授权异常处理器
        [middleware][auth][authorization_exception_handler]
        """
        from fastapi.responses import JSONResponse
        from app.schemas.base import ErrorSchema
        
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorSchema(
                success=False,
                message=exc.message,
                error_code=exc.error_code,
                error_detail={
                    "path": str(request.url.path),
                    "method": request.method
                }
            ).dict()
        )