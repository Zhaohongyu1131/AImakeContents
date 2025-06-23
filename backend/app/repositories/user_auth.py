"""
User Authentication Repository
用户认证数据访问层 - [repositories][user_auth]
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from app.repositories.base import RepositoryBase
from app.models.user_auth.user_auth_basic import UserAuthBasic
from app.models.user_auth.user_auth_session import UserAuthSession
from app.models.user_auth.user_auth_profile import UserAuthProfile


class UserAuthRepository(RepositoryBase[UserAuthBasic]):
    """
    用户认证数据访问层
    [repositories][user_auth]
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        初始化用户认证仓储
        [repositories][user_auth][init]
        """
        super().__init__(db_session, UserAuthBasic)
    
    async def user_auth_repository_get_by_username(
        self,
        username: str
    ) -> Optional[UserAuthBasic]:
        """
        根据用户名获取用户
        [repositories][user_auth][get_by_username]
        """
        return await self.repository_base_get_by_field("user_username", username)
    
    async def user_auth_repository_get_by_email(
        self,
        email: str
    ) -> Optional[UserAuthBasic]:
        """
        根据邮箱获取用户
        [repositories][user_auth][get_by_email]
        """
        return await self.repository_base_get_by_field("user_email", email)
    
    async def user_auth_repository_check_username_exists(
        self,
        username: str,
        exclude_user_id: Optional[int] = None
    ) -> bool:
        """
        检查用户名是否存在
        [repositories][user_auth][check_username_exists]
        """
        conditions = [UserAuthBasic.user_username == username]
        
        if exclude_user_id:
            conditions.append(UserAuthBasic.user_id != exclude_user_id)
        
        return await self.repository_base_exists(conditions)
    
    async def user_auth_repository_check_email_exists(
        self,
        email: str,
        exclude_user_id: Optional[int] = None
    ) -> bool:
        """
        检查邮箱是否存在
        [repositories][user_auth][check_email_exists]
        """
        conditions = [UserAuthBasic.user_email == email]
        
        if exclude_user_id:
            conditions.append(UserAuthBasic.user_id != exclude_user_id)
        
        return await self.repository_base_exists(conditions)
    
    async def user_auth_repository_get_active_users(
        self,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        获取活跃用户列表
        [repositories][user_auth][get_active_users]
        """
        conditions = [UserAuthBasic.user_status == "active"]
        
        return await self.repository_base_paginate(
            page=page,
            size=size,
            conditions=conditions,
            order_by="user_created_time"
        )
    
    async def user_auth_repository_search_users(
        self,
        search_term: str,
        user_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        搜索用户
        [repositories][user_auth][search_users]
        """
        conditions = []
        
        if user_type:
            conditions.append(UserAuthBasic.user_type == user_type)
        
        if status:
            conditions.append(UserAuthBasic.user_status == status)
        
        return await self.repository_base_search(
            search_fields=["user_username", "user_email", "user_full_name"],
            search_term=search_term,
            conditions=conditions,
            page=page,
            size=size
        )
    
    async def user_auth_repository_update_last_login(
        self,
        user_id: int,
        login_time: datetime,
        login_ip: Optional[str] = None
    ) -> Optional[UserAuthBasic]:
        """
        更新最后登录时间
        [repositories][user_auth][update_last_login]
        """
        update_data = {
            "user_last_login_time": login_time,
            "user_updated_time": login_time
        }
        
        if login_ip:
            update_data["user_last_login_ip"] = login_ip
        
        return await self.repository_base_update(user_id, **update_data)
    
    async def user_auth_repository_get_users_by_type(
        self,
        user_type: str,
        active_only: bool = True
    ) -> List[UserAuthBasic]:
        """
        根据用户类型获取用户列表
        [repositories][user_auth][get_users_by_type]
        """
        conditions = [UserAuthBasic.user_type == user_type]
        
        if active_only:
            conditions.append(UserAuthBasic.user_status == "active")
        
        return await self.repository_base_get_all(
            conditions=conditions,
            order_by="user_created_time"
        )
    
    async def user_auth_repository_get_user_stats(self) -> Dict[str, Any]:
        """
        获取用户统计信息
        [repositories][user_auth][get_user_stats]
        """
        # 总用户数
        total_users = await self.repository_base_count()
        
        # 活跃用户数
        active_users = await self.repository_base_count([
            UserAuthBasic.user_status == "active"
        ])
        
        # 按类型统计
        type_stats_stmt = select(
            UserAuthBasic.user_type,
            func.count(UserAuthBasic.user_id).label("count")
        ).group_by(UserAuthBasic.user_type)
        
        type_result = await self.db.execute(type_stats_stmt)
        type_distribution = {row.user_type: row.count for row in type_result}
        
        # 按状态统计
        status_stats_stmt = select(
            UserAuthBasic.user_status,
            func.count(UserAuthBasic.user_id).label("count")
        ).group_by(UserAuthBasic.user_status)
        
        status_result = await self.db.execute(status_stats_stmt)
        status_distribution = {row.user_status: row.count for row in status_result}
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "type_distribution": type_distribution,
            "status_distribution": status_distribution
        }


class UserAuthSessionRepository(RepositoryBase[UserAuthSession]):
    """
    用户会话数据访问层
    [repositories][user_auth][session]
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        初始化用户会话仓储
        [repositories][user_auth][session][init]
        """
        super().__init__(db_session, UserAuthSession)
    
    async def user_auth_session_repository_get_by_token(
        self,
        token: str
    ) -> Optional[UserAuthSession]:
        """
        根据令牌获取会话
        [repositories][user_auth][session][get_by_token]
        """
        return await self.repository_base_get_by_field("session_token", token)
    
    async def user_auth_session_repository_get_active_session(
        self,
        token: str
    ) -> Optional[UserAuthSession]:
        """
        获取活跃会话
        [repositories][user_auth][session][get_active_session]
        """
        stmt = select(UserAuthSession).where(
            and_(
                UserAuthSession.session_token == token,
                UserAuthSession.session_status == "active",
                UserAuthSession.session_expires_at > datetime.utcnow()
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def user_auth_session_repository_get_user_sessions(
        self,
        user_id: int,
        active_only: bool = True
    ) -> List[UserAuthSession]:
        """
        获取用户会话列表
        [repositories][user_auth][session][get_user_sessions]
        """
        conditions = [UserAuthSession.user_id == user_id]
        
        if active_only:
            conditions.extend([
                UserAuthSession.session_status == "active",
                UserAuthSession.session_expires_at > datetime.utcnow()
            ])
        
        return await self.repository_base_get_all(
            conditions=conditions,
            order_by="session_login_time"
        )
    
    async def user_auth_session_repository_logout_session(
        self,
        token: str,
        logout_time: datetime
    ) -> Optional[UserAuthSession]:
        """
        登出会话
        [repositories][user_auth][session][logout_session]
        """
        session = await self.user_auth_session_repository_get_by_token(token)
        if session:
            return await self.repository_base_update(
                session.session_id,
                session_status="logged_out",
                session_logout_time=logout_time
            )
        return None
    
    async def user_auth_session_repository_logout_all_user_sessions(
        self,
        user_id: int,
        logout_time: datetime
    ) -> int:
        """
        登出用户所有会话
        [repositories][user_auth][session][logout_all_user_sessions]
        """
        conditions = [
            UserAuthSession.user_id == user_id,
            UserAuthSession.session_status == "active"
        ]
        
        return await self.repository_base_update_by_conditions(
            conditions,
            session_status="logged_out",
            session_logout_time=logout_time
        )
    
    async def user_auth_session_repository_cleanup_expired_sessions(self) -> int:
        """
        清理过期会话
        [repositories][user_auth][session][cleanup_expired_sessions]
        """
        conditions = [
            UserAuthSession.session_status == "active",
            UserAuthSession.session_expires_at <= datetime.utcnow()
        ]
        
        return await self.repository_base_update_by_conditions(
            conditions,
            session_status="expired",
            session_logout_time=datetime.utcnow()
        )


class UserAuthProfileRepository(RepositoryBase[UserAuthProfile]):
    """
    用户资料数据访问层
    [repositories][user_auth][profile]
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        初始化用户资料仓储
        [repositories][user_auth][profile][init]
        """
        super().__init__(db_session, UserAuthProfile)
    
    async def user_auth_profile_repository_get_by_user_id(
        self,
        user_id: int
    ) -> Optional[UserAuthProfile]:
        """
        根据用户ID获取资料
        [repositories][user_auth][profile][get_by_user_id]
        """
        return await self.repository_base_get_by_field("user_id", user_id)
    
    async def user_auth_profile_repository_create_or_update(
        self,
        user_id: int,
        **profile_data
    ) -> UserAuthProfile:
        """
        创建或更新用户资料
        [repositories][user_auth][profile][create_or_update]
        """
        existing_profile = await self.user_auth_profile_repository_get_by_user_id(user_id)
        
        if existing_profile:
            # 更新现有资料
            profile_data["profile_updated_time"] = datetime.utcnow()
            updated_profile = await self.repository_base_update(
                existing_profile.profile_id,
                **profile_data
            )
            return updated_profile
        else:
            # 创建新资料
            profile_data.update({
                "user_id": user_id,
                "profile_created_time": datetime.utcnow(),
                "profile_updated_time": datetime.utcnow()
            })
            return await self.repository_base_create(**profile_data)