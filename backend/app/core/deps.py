"""
Dependencies Module
依赖注入模块 - [deps]
"""

from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import database_session_get_async
from app.core.security import security_jwt_token_verify
from app.core.exceptions import AppExceptionUnauthorized

# HTTP Bearer 认证
deps_security_bearer = HTTPBearer()

async def deps_database_session_get() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话依赖
    [deps][database][session_get]
    """
    async for session in database_session_get_async():
        yield session

async def deps_auth_token_get(
    credentials: HTTPAuthorizationCredentials = Depends(deps_security_bearer)
) -> str:
    """
    获取认证令牌依赖
    [deps][auth][token_get]
    """
    if not credentials:
        raise AppExceptionUnauthorized("认证令牌缺失")
    
    return credentials.credentials

async def deps_auth_user_current_get(
    token: str = Depends(deps_auth_token_get)
) -> dict:
    """
    获取当前用户依赖
    [deps][auth][user_current_get]
    """
    try:
        payload = security_jwt_token_verify(token, "access")
        user_id: int = payload.get("sub")
        if user_id is None:
            raise AppExceptionUnauthorized("无效的认证令牌")
        return {"user_id": user_id, "payload": payload}
    except Exception:
        raise AppExceptionUnauthorized("认证令牌验证失败")

async def deps_auth_user_admin_get(
    current_user: dict = Depends(deps_auth_user_current_get)
) -> dict:
    """
    获取管理员用户依赖
    [deps][auth][user_admin_get]
    """
    user_role = current_user["payload"].get("role", "user")
    if user_role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    return current_user

class DepsAuthOptional:
    """
    可选认证依赖类
    [deps][auth][optional]
    """
    def __init__(self, auto_error: bool = True):
        self.auto_error = auto_error
    
    async def __call__(
        self, 
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
    ) -> Optional[dict]:
        """
        可选的用户认证
        """
        if not credentials:
            return None
        
        try:
            payload = security_jwt_token_verify(credentials.credentials, "access")
            user_id: int = payload.get("sub")
            if user_id is None:
                return None
            return {"user_id": user_id, "payload": payload}
        except Exception:
            if self.auto_error:
                raise AppExceptionUnauthorized("认证令牌验证失败")
            return None

# 可选认证依赖实例
deps_auth_optional = DepsAuthOptional(auto_error=False)