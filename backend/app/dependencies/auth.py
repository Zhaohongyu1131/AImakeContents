"""
Authentication Dependencies
认证依赖项 - [dependencies][auth]
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import jwt
from datetime import datetime

from app.models.user_auth.user_auth_basic import UserAuthBasic
from app.dependencies.db import get_db
from app.config.settings import app_config_get_settings


security = HTTPBearer()


class CurrentUser:
    """
    当前用户信息类
    [dependencies][auth][current_user]
    """
    def __init__(self, user_id: int, username: str, email: str, user_role: str = "user"):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.user_role = user_role


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> CurrentUser:
    """
    获取当前用户
    [dependencies][auth][get_current_user]
    """
    try:
        settings = app_config_get_settings()
        
        # 解码JWT令牌
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 从数据库获取用户信息
        result = await db.execute(
            select(UserAuthBasic).where(UserAuthBasic.user_id == int(user_id))
        )
        user = result.scalar_one_or_none()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return CurrentUser(
            user_id=user.user_id,
            username=user.user_name,
            email=user.user_email,
            user_role=user.user_role
        )
        
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}"
        )


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[CurrentUser]:
    """
    获取可选的当前用户（允许匿名访问）
    [dependencies][auth][get_optional_current_user]
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


def require_admin_role(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """
    要求管理员角色
    [dependencies][auth][require_admin_role]
    """
    if current_user.user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_premium_user(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """
    要求高级用户
    [dependencies][auth][require_premium_user]
    """
    if current_user.user_role not in ["premium", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Premium access required"
        )
    return current_user