"""
Permission Service
权限管理服务 - [services][permission]
"""

from typing import Dict, Any, Optional, List, Set
from enum import Enum
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.services.base import ServiceBase
from app.models.user_auth.user_auth_basic import UserAuthBasic


class PermissionAction(Enum):
    """权限操作枚举"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    ADMIN = "admin"


class PermissionResource(Enum):
    """权限资源枚举"""
    USER = "user"
    TEXT_CONTENT = "text_content"
    VOICE_AUDIO = "voice_audio"
    VOICE_TIMBRE = "voice_timbre"
    IMAGE_CONTENT = "image_content"
    VIDEO_CONTENT = "video_content"
    FILE_STORAGE = "file_storage"
    MIXED_CONTENT = "mixed_content"
    SYSTEM = "system"


class UserRole(Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    GUEST = "guest"


class PermissionService(ServiceBase):
    """
    权限管理服务
    [services][permission]
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        初始化权限服务
        [services][permission][init]
        """
        super().__init__(db_session)
        
        # 定义角色权限映射
        self.role_permissions = {
            UserRole.ADMIN: self._get_admin_permissions(),
            UserRole.MODERATOR: self._get_moderator_permissions(),
            UserRole.USER: self._get_user_permissions(),
            UserRole.GUEST: self._get_guest_permissions()
        }
    
    def _get_admin_permissions(self) -> Set[str]:
        """获取管理员权限"""
        return {
            f"{resource.value}:{action.value}"
            for resource in PermissionResource
            for action in PermissionAction
        }
    
    def _get_moderator_permissions(self) -> Set[str]:
        """获取协调员权限"""
        return {
            f"{resource.value}:{action.value}"
            for resource in [
                PermissionResource.TEXT_CONTENT,
                PermissionResource.VOICE_AUDIO,
                PermissionResource.VOICE_TIMBRE,
                PermissionResource.IMAGE_CONTENT,
                PermissionResource.VIDEO_CONTENT,
                PermissionResource.FILE_STORAGE,
                PermissionResource.MIXED_CONTENT
            ]
            for action in [
                PermissionAction.CREATE,
                PermissionAction.READ,
                PermissionAction.UPDATE,
                PermissionAction.DELETE
            ]
        } | {
            f"{PermissionResource.USER.value}:{PermissionAction.READ.value}",
            f"{PermissionResource.USER.value}:{PermissionAction.UPDATE.value}"
        }
    
    def _get_user_permissions(self) -> Set[str]:
        """获取普通用户权限"""
        return {
            f"{resource.value}:{action.value}"
            for resource in [
                PermissionResource.TEXT_CONTENT,
                PermissionResource.VOICE_AUDIO,
                PermissionResource.VOICE_TIMBRE,
                PermissionResource.IMAGE_CONTENT,
                PermissionResource.VIDEO_CONTENT,
                PermissionResource.FILE_STORAGE,
                PermissionResource.MIXED_CONTENT
            ]
            for action in [
                PermissionAction.CREATE,
                PermissionAction.READ,
                PermissionAction.UPDATE
            ]
        } | {
            f"{PermissionResource.USER.value}:{PermissionAction.READ.value}",
            f"{PermissionResource.USER.value}:{PermissionAction.UPDATE.value}"
        }
    
    def _get_guest_permissions(self) -> Set[str]:
        """获取访客权限"""
        return {
            f"{resource.value}:{PermissionAction.READ.value}"
            for resource in [
                PermissionResource.TEXT_CONTENT,
                PermissionResource.VOICE_AUDIO,
                PermissionResource.IMAGE_CONTENT,
                PermissionResource.VIDEO_CONTENT
            ]
        }
    
    async def permission_service_check_permission(
        self,
        user_id: int,
        resource: str,
        action: str,
        resource_owner_id: Optional[int] = None
    ) -> bool:
        """
        检查用户权限
        [services][permission][check_permission]
        """
        try:
            # 获取用户信息
            user = await self._get_user_by_id(user_id)
            if not user:
                return False
            
            # 检查用户状态
            if user.user_status != "active":
                return False
            
            # 获取用户角色
            user_role = UserRole(user.user_role)
            
            # 获取权限字符串
            permission_key = f"{resource}:{action}"
            
            # 检查角色权限
            role_permissions = self.role_permissions.get(user_role, set())
            
            # 管理员拥有所有权限
            if user_role == UserRole.ADMIN:
                return True
            
            # 检查基础权限
            if permission_key not in role_permissions:
                return False
            
            # 资源所有者检查
            if resource_owner_id is not None:
                # 用户可以操作自己的资源
                if user_id == resource_owner_id:
                    return True
                
                # 协调员可以操作他人资源
                if user_role == UserRole.MODERATOR:
                    return True
                
                # 普通用户只能操作自己的资源（除了读取权限）
                if action != PermissionAction.READ.value:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Permission check failed: {str(e)}")
            return False
    
    async def permission_service_check_multiple_permissions(
        self,
        user_id: int,
        permissions: List[Dict[str, Any]]
    ) -> Dict[str, bool]:
        """
        批量检查权限
        [services][permission][check_multiple_permissions]
        """
        results = {}
        
        for perm in permissions:
            resource = perm.get("resource")
            action = perm.get("action")
            resource_owner_id = perm.get("resource_owner_id")
            
            if resource and action:
                key = f"{resource}:{action}"
                results[key] = await self.permission_service_check_permission(
                    user_id, resource, action, resource_owner_id
                )
        
        return results
    
    async def permission_service_get_user_permissions(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        获取用户权限列表
        [services][permission][get_user_permissions]
        """
        try:
            user = await self._get_user_by_id(user_id)
            if not user:
                return {
                    "success": False,
                    "error": "用户不存在"
                }
            
            user_role = UserRole(user.user_role)
            permissions = self.role_permissions.get(user_role, set())
            
            # 按资源分组权限
            grouped_permissions = {}
            for perm in permissions:
                resource, action = perm.split(":", 1)
                if resource not in grouped_permissions:
                    grouped_permissions[resource] = []
                grouped_permissions[resource].append(action)
            
            return {
                "success": True,
                "data": {
                    "user_id": user_id,
                    "role": user_role.value,
                    "permissions": list(permissions),
                    "grouped_permissions": grouped_permissions
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"获取用户权限失败: {str(e)}"
            }
    
    async def permission_service_assign_role(
        self,
        user_id: int,
        new_role: str,
        operator_user_id: int
    ) -> Dict[str, Any]:
        """
        分配用户角色
        [services][permission][assign_role]
        """
        try:
            # 检查操作者权限
            if not await self.permission_service_check_permission(
                operator_user_id, PermissionResource.USER.value, PermissionAction.ADMIN.value
            ):
                return {
                    "success": False,
                    "error": "无权限执行此操作"
                }
            
            # 验证新角色
            try:
                role = UserRole(new_role)
            except ValueError:
                return {
                    "success": False,
                    "error": "无效的角色类型"
                }
            
            # 获取目标用户
            user = await self._get_user_by_id(user_id)
            if not user:
                return {
                    "success": False,
                    "error": "目标用户不存在"
                }
            
            # 更新用户角色
            old_role = user.user_role
            user.user_role = new_role
            user.user_updated_time = datetime.utcnow()
            
            await self.db.commit()
            
            # 记录操作日志
            await self.service_base_log_operation(
                "assign_role",
                "user",
                user_id,
                operator_user_id,
                {
                    "old_role": old_role,
                    "new_role": new_role
                }
            )
            
            return {
                "success": True,
                "data": {
                    "user_id": user_id,
                    "old_role": old_role,
                    "new_role": new_role
                }
            }
            
        except Exception as e:
            await self.db.rollback()
            return {
                "success": False,
                "error": f"角色分配失败: {str(e)}"
            }
    
    async def permission_service_get_role_permissions(
        self,
        role: str
    ) -> Dict[str, Any]:
        """
        获取角色权限定义
        [services][permission][get_role_permissions]
        """
        try:
            user_role = UserRole(role)
            permissions = self.role_permissions.get(user_role, set())
            
            return {
                "success": True,
                "data": {
                    "role": role,
                    "permissions": list(permissions),
                    "permission_count": len(permissions)
                }
            }
            
        except ValueError:
            return {
                "success": False,
                "error": "无效的角色类型"
            }
    
    async def _get_user_by_id(self, user_id: int) -> Optional[UserAuthBasic]:
        """获取用户信息"""
        stmt = select(UserAuthBasic).where(UserAuthBasic.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


# 权限装饰器函数
def require_permission(resource: str, action: str):
    """
    权限检查装饰器
    [services][permission][require_permission]
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 从参数中获取current_user和db_session
            current_user = kwargs.get('current_user')
            db_session = kwargs.get('db_session')
            
            if not current_user or not db_session:
                raise Exception("Missing authentication or database session")
            
            # 检查权限
            permission_service = PermissionService(db_session)
            
            # 检查资源所有者ID（如果存在）
            resource_owner_id = kwargs.get('resource_owner_id')
            
            has_permission = await permission_service.permission_service_check_permission(
                current_user.user_id,
                resource,
                action,
                resource_owner_id
            )
            
            if not has_permission:
                raise Exception(f"Permission denied: {resource}:{action}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# 创建全局权限服务实例
permission_service = PermissionService