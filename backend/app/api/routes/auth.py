"""
Authentication API Routes
用户认证API路由 - [api][routes][auth]
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user, get_optional_current_user, CurrentUser
from app.services.user_auth import UserAuthService
from app.services.permission_service import PermissionService
from app.core.security import security_jwt_token_create, security_jwt_token_verify
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


# Pydantic模型
class UserAuthRegisterRequest(BaseModel):
    """
    用户注册请求模型
    [api][routes][auth][register_request]
    """
    username: str
    email: EmailStr
    password: str
    user_type: str = "user"
    
    model_config = {"protected_namespaces": ()}


class UserAuthLoginRequest(BaseModel):
    """
    用户登录请求模型
    [api][routes][auth][login_request]
    """
    username: str
    password: str
    
    model_config = {"protected_namespaces": ()}


class UserAuthPasswordChangeRequest(BaseModel):
    """
    密码修改请求模型
    [api][routes][auth][password_change_request]
    """
    current_password: str
    new_password: str
    
    model_config = {"protected_namespaces": ()}


class UserAuthTokenRefreshRequest(BaseModel):
    """
    令牌刷新请求模型
    [api][routes][auth][token_refresh_request]
    """
    refresh_token: str
    
    model_config = {"protected_namespaces": ()}


@router.post("/register", summary="用户注册")
async def auth_register(
    request: UserAuthRegisterRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    用户注册
    [api][routes][auth][register]
    """
    try:
        auth_service = UserAuthService(db)
        result = await auth_service.user_auth_service_register(
            username=request.username,
            email=request.email,
            password=request.password,
            user_type=request.user_type
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "success": True,
            "message": "注册成功",
            "data": result["data"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )


@router.post("/login", summary="用户登录")
async def auth_login(
    request: UserAuthLoginRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    用户登录
    [api][routes][auth][login]
    """
    try:
        auth_service = UserAuthService(db)
        result = await auth_service.user_auth_service_login(
            username=request.username,
            password=request.password
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result["error"]
            )
        
        # 生成刷新令牌
        refresh_token = security_jwt_token_create(
            data={
                "sub": str(result["data"]["user"]["user_id"]),
                "username": result["data"]["user"]["username"]
            },
            expires_delta=timedelta(minutes=60 * 24 * 7),  # 7天
            token_type="refresh"
        )
        
        result["data"]["refresh_token"] = refresh_token
        
        return {
            "success": True,
            "message": "登录成功",
            "data": result["data"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )


@router.post("/logout", summary="用户登出")
async def auth_logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    用户登出
    [api][routes][auth][logout]
    """
    try:
        auth_service = UserAuthService(db)
        result = await auth_service.user_auth_service_logout(
            token=credentials.credentials,
            user_id=current_user.user_id
        )
        
        return {
            "success": True,
            "message": "登出成功"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登出失败: {str(e)}"
        )


@router.post("/refresh", summary="刷新访问令牌")
async def auth_refresh_token(
    request: UserAuthTokenRefreshRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    刷新访问令牌
    [api][routes][auth][refresh_token]
    """
    try:
        # 验证刷新令牌
        payload = security_jwt_token_verify(request.refresh_token, "refresh")
        
        user_id = payload.get("sub")
        username = payload.get("username")
        
        if not user_id or not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌"
            )
        
        # 生成新的访问令牌
        access_token = security_jwt_token_create(
            data={"sub": user_id, "username": username},
            token_type="access"
        )
        
        return {
            "success": True,
            "message": "令牌刷新成功",
            "data": {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": 60 * 60 * 24  # 24小时
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"令牌刷新失败: {str(e)}"
        )


@router.get("/profile", summary="获取用户信息")
async def auth_get_profile(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取当前用户信息
    [api][routes][auth][get_profile]
    """
    try:
        # 获取用户权限信息
        permission_service = PermissionService(db)
        permissions_result = await permission_service.permission_service_get_user_permissions(
            current_user.user_id
        )
        
        return {
            "success": True,
            "data": {
                "user_id": current_user.user_id,
                "username": current_user.username,
                "email": current_user.email,
                "user_role": current_user.user_role,
                "permissions": permissions_result.get("data", {}).get("permissions", [])
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户信息失败: {str(e)}"
        )


@router.put("/password", summary="修改密码")
async def auth_change_password(
    request: UserAuthPasswordChangeRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    修改用户密码
    [api][routes][auth][change_password]
    """
    try:
        auth_service = UserAuthService(db)
        
        # 验证当前密码
        user = await auth_service.user_auth_service_authenticate(
            current_user.username,
            request.current_password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="当前密码错误"
            )
        
        # 更新密码
        new_password_hash = auth_service.user_auth_service_hash_password(request.new_password)
        user.user_password_hash = new_password_hash
        
        await db.commit()
        
        return {
            "success": True,
            "message": "密码修改成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"密码修改失败: {str(e)}"
        )


@router.get("/permissions", summary="获取用户权限")
async def auth_get_permissions(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取当前用户权限列表
    [api][routes][auth][get_permissions]
    """
    try:
        permission_service = PermissionService(db)
        result = await permission_service.permission_service_get_user_permissions(
            current_user.user_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        return {
            "success": True,
            "data": result["data"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取权限失败: {str(e)}"
        )


@router.post("/check-permission", summary="检查权限")
async def auth_check_permission(
    resource: str = Body(...),
    action: str = Body(...),
    resource_owner_id: Optional[int] = Body(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    检查用户是否有指定权限
    [api][routes][auth][check_permission]
    """
    try:
        permission_service = PermissionService(db)
        has_permission = await permission_service.permission_service_check_permission(
            current_user.user_id,
            resource,
            action,
            resource_owner_id
        )
        
        return {
            "success": True,
            "data": {
                "has_permission": has_permission,
                "resource": resource,
                "action": action,
                "resource_owner_id": resource_owner_id
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"权限检查失败: {str(e)}"
        )


@router.get("/verify", summary="验证令牌")
async def auth_verify_token(
    current_user: CurrentUser = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    验证访问令牌有效性
    [api][routes][auth][verify_token]
    """
    return {
        "success": True,
        "message": "令牌有效",
        "data": {
            "user_id": current_user.user_id,
            "username": current_user.username,
            "user_role": current_user.user_role
        }
    }