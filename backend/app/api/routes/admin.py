"""
Admin API Routes
管理员API路由 - [api][routes][admin]
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user, require_admin_role, CurrentUser
from app.services.user_auth import UserAuthService
from app.services.permission_service import PermissionService, UserRole
from app.models.user_auth.user_auth_basic import UserAuthBasic
from sqlalchemy import select, and_, or_, func

router = APIRouter(prefix="/admin", tags=["admin"])


# Pydantic模型
class AdminUserCreateRequest(BaseModel):
    """
    管理员创建用户请求模型
    [api][routes][admin][user_create_request]
    """
    username: str
    email: EmailStr
    password: str
    user_role: str = "user"
    user_status: str = "active"
    
    model_config = {"protected_namespaces": ()}


class AdminUserUpdateRequest(BaseModel):
    """
    管理员更新用户请求模型
    [api][routes][admin][user_update_request]
    """
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    user_role: Optional[str] = None
    user_status: Optional[str] = None
    
    model_config = {"protected_namespaces": ()}


class AdminUserRoleAssignRequest(BaseModel):
    """
    角色分配请求模型
    [api][routes][admin][role_assign_request]
    """
    user_id: int
    new_role: str
    
    model_config = {"protected_namespaces": ()}


@router.get("/users", summary="获取用户列表")
async def admin_get_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: CurrentUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取用户列表（分页）
    [api][routes][admin][get_users]
    """
    try:
        # 构建查询条件
        conditions = []
        
        if search:
            conditions.append(
                or_(
                    UserAuthBasic.user_name.ilike(f"%{search}%"),
                    UserAuthBasic.user_email.ilike(f"%{search}%")
                )
            )
        
        if role:
            conditions.append(UserAuthBasic.user_role == role)
        
        if status:
            conditions.append(UserAuthBasic.user_status == status)
        
        # 计算总数
        count_stmt = select(func.count(UserAuthBasic.user_id))
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        
        count_result = await db.execute(count_stmt)
        total = count_result.scalar()
        
        # 获取分页数据
        offset = (page - 1) * size
        stmt = select(UserAuthBasic).offset(offset).limit(size)
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        stmt = stmt.order_by(UserAuthBasic.user_created_time.desc())
        
        result = await db.execute(stmt)
        users = result.scalars().all()
        
        # 转换为字典格式
        users_data = []
        for user in users:
            users_data.append({
                "user_id": user.user_id,
                "username": user.user_name,
                "email": user.user_email,
                "user_role": user.user_role,
                "user_status": user.user_status,
                "created_time": user.user_created_time.isoformat() if user.user_created_time else None,
                "updated_time": user.user_updated_time.isoformat() if user.user_updated_time else None
            })
        
        return {
            "success": True,
            "data": {
                "users": users_data,
                "pagination": {
                    "page": page,
                    "size": size,
                    "total": total,
                    "pages": (total + size - 1) // size
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户列表失败: {str(e)}"
        )


@router.post("/users", summary="创建用户")
async def admin_create_user(
    request: AdminUserCreateRequest,
    current_user: CurrentUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    管理员创建用户
    [api][routes][admin][create_user]
    """
    try:
        # 验证角色
        try:
            UserRole(request.user_role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的用户角色"
            )
        
        auth_service = UserAuthService(db)
        result = await auth_service.user_auth_service_register(
            username=request.username,
            email=request.email,
            password=request.password,
            user_type=request.user_role
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        # 如果需要，更新用户状态
        if request.user_status != "active":
            user_id = result["data"]["user_id"]
            stmt = select(UserAuthBasic).where(UserAuthBasic.user_id == user_id)
            user_result = await db.execute(stmt)
            user = user_result.scalar_one()
            user.user_status = request.user_status
            await db.commit()
        
        return {
            "success": True,
            "message": "用户创建成功",
            "data": result["data"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建用户失败: {str(e)}"
        )


@router.get("/users/{user_id}", summary="获取用户详情")
async def admin_get_user(
    user_id: int,
    current_user: CurrentUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取用户详细信息
    [api][routes][admin][get_user]
    """
    try:
        stmt = select(UserAuthBasic).where(UserAuthBasic.user_id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 获取用户权限
        permission_service = PermissionService(db)
        permissions_result = await permission_service.permission_service_get_user_permissions(user_id)
        
        return {
            "success": True,
            "data": {
                "user_id": user.user_id,
                "username": user.user_name,
                "email": user.user_email,
                "user_role": user.user_role,
                "user_status": user.user_status,
                "created_time": user.user_created_time.isoformat() if user.user_created_time else None,
                "updated_time": user.user_updated_time.isoformat() if user.user_updated_time else None,
                "permissions": permissions_result.get("data", {})
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户信息失败: {str(e)}"
        )


@router.put("/users/{user_id}", summary="更新用户信息")
async def admin_update_user(
    user_id: int,
    request: AdminUserUpdateRequest,
    current_user: CurrentUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    更新用户信息
    [api][routes][admin][update_user]
    """
    try:
        stmt = select(UserAuthBasic).where(UserAuthBasic.user_id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 更新字段
        if request.username is not None:
            # 检查用户名是否已被使用
            existing_stmt = select(UserAuthBasic).where(
                and_(
                    UserAuthBasic.user_name == request.username,
                    UserAuthBasic.user_id != user_id
                )
            )
            existing_result = await db.execute(existing_stmt)
            if existing_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户名已被使用"
                )
            user.user_name = request.username
        
        if request.email is not None:
            # 检查邮箱是否已被使用
            existing_stmt = select(UserAuthBasic).where(
                and_(
                    UserAuthBasic.user_email == request.email,
                    UserAuthBasic.user_id != user_id
                )
            )
            existing_result = await db.execute(existing_stmt)
            if existing_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已被使用"
                )
            user.user_email = request.email
        
        if request.user_role is not None:
            # 验证角色
            try:
                UserRole(request.user_role)
                user.user_role = request.user_role
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="无效的用户角色"
                )
        
        if request.user_status is not None:
            user.user_status = request.user_status
        
        user.user_updated_time = func.now()
        await db.commit()
        
        return {
            "success": True,
            "message": "用户信息更新成功",
            "data": {
                "user_id": user.user_id,
                "username": user.user_name,
                "email": user.user_email,
                "user_role": user.user_role,
                "user_status": user.user_status
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户失败: {str(e)}"
        )


@router.post("/assign-role", summary="分配用户角色")
async def admin_assign_role(
    request: AdminUserRoleAssignRequest,
    current_user: CurrentUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    分配用户角色
    [api][routes][admin][assign_role]
    """
    try:
        permission_service = PermissionService(db)
        result = await permission_service.permission_service_assign_role(
            user_id=request.user_id,
            new_role=request.new_role,
            operator_user_id=current_user.user_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "success": True,
            "message": "角色分配成功",
            "data": result["data"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"角色分配失败: {str(e)}"
        )


@router.get("/roles", summary="获取角色列表")
async def admin_get_roles(
    current_user: CurrentUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取系统角色列表和权限
    [api][routes][admin][get_roles]
    """
    try:
        permission_service = PermissionService(db)
        roles_data = []
        
        for role in UserRole:
            role_result = await permission_service.permission_service_get_role_permissions(role.value)
            if role_result["success"]:
                roles_data.append(role_result["data"])
        
        return {
            "success": True,
            "data": {
                "roles": roles_data
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取角色列表失败: {str(e)}"
        )


@router.delete("/users/{user_id}", summary="删除用户")
async def admin_delete_user(
    user_id: int,
    current_user: CurrentUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    删除用户（软删除）
    [api][routes][admin][delete_user]
    """
    try:
        if user_id == current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能删除自己的账户"
            )
        
        stmt = select(UserAuthBasic).where(UserAuthBasic.user_id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 软删除：更改状态为deleted
        user.user_status = "deleted"
        user.user_updated_time = func.now()
        await db.commit()
        
        return {
            "success": True,
            "message": "用户删除成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除用户失败: {str(e)}"
        )


@router.get("/statistics", summary="获取系统统计")
async def admin_get_statistics(
    current_user: CurrentUser = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取系统统计信息
    [api][routes][admin][get_statistics]
    """
    try:
        # 用户总数
        total_users_stmt = select(func.count(UserAuthBasic.user_id))
        total_users_result = await db.execute(total_users_stmt)
        total_users = total_users_result.scalar()
        
        # 活跃用户数
        active_users_stmt = select(func.count(UserAuthBasic.user_id)).where(
            UserAuthBasic.user_status == "active"
        )
        active_users_result = await db.execute(active_users_stmt)
        active_users = active_users_result.scalar()
        
        # 按角色统计
        role_stats = {}
        for role in UserRole:
            role_stmt = select(func.count(UserAuthBasic.user_id)).where(
                UserAuthBasic.user_role == role.value
            )
            role_result = await db.execute(role_stmt)
            role_stats[role.value] = role_result.scalar()
        
        return {
            "success": True,
            "data": {
                "total_users": total_users,
                "active_users": active_users,
                "role_statistics": role_stats
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )