"""
User Authentication Service
用户认证业务逻辑服务 - [services][user_auth]
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.services.base import ServiceBase
from app.models.user_auth.user_auth_basic import UserAuthBasic
from app.models.user_auth.user_auth_session import UserAuthSession
from app.config.settings import app_config_get_settings


class UserAuthService(ServiceBase):
    """
    用户认证业务逻辑服务
    [services][user_auth]
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        初始化用户认证服务
        [services][user_auth][init]
        """
        super().__init__(db_session)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.settings = app_config_get_settings()
    
    async def user_auth_service_register(
        self,
        username: str,
        email: str,
        password: str,
        user_type: str = "user",
        **kwargs
    ) -> Dict[str, Any]:
        """
        用户注册
        [services][user_auth][register]
        """
        try:
            # 检查用户名是否已存在
            existing_user = await self.user_auth_service_get_by_username(username)
            if existing_user:
                return {
                    "success": False,
                    "error": "用户名已存在"
                }
            
            # 检查邮箱是否已存在
            existing_email = await self.user_auth_service_get_by_email(email)
            if existing_email:
                return {
                    "success": False,
                    "error": "邮箱已被注册"
                }
            
            # 创建新用户
            hashed_password = self.user_auth_service_hash_password(password)
            new_user = UserAuthBasic(
                user_username=username,
                user_email=email,
                user_password_hash=hashed_password,
                user_type=user_type,
                user_status="active",
                user_created_time=datetime.utcnow(),
                user_updated_time=datetime.utcnow()
            )
            
            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)
            
            # 记录操作日志
            await self.service_base_log_operation(
                "register",
                "user",
                new_user.user_id,
                new_user.user_id
            )
            
            return {
                "success": True,
                "data": {
                    "user_id": new_user.user_id,
                    "username": new_user.user_username,
                    "email": new_user.user_email,
                    "user_type": new_user.user_type
                }
            }
            
        except Exception as e:
            await self.db.rollback()
            return {
                "success": False,
                "error": f"注册失败: {str(e)}"
            }
    
    async def user_auth_service_login(
        self,
        username: str,
        password: str,
        login_ip: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        用户登录
        [services][user_auth][login]
        """
        try:
            # 验证用户凭据
            user = await self.user_auth_service_authenticate(username, password)
            if not user:
                return {
                    "success": False,
                    "error": "用户名或密码错误"
                }
            
            # 检查用户状态
            if user.user_status != "active":
                return {
                    "success": False,
                    "error": "账户已被禁用"
                }
            
            # 生成访问令牌
            access_token = self.user_auth_service_create_access_token(
                data={"sub": str(user.user_id), "username": user.user_username}
            )
            
            # 创建会话记录
            session = UserAuthSession(
                user_id=user.user_id,
                session_token=access_token,
                session_login_ip=login_ip,
                session_login_time=datetime.utcnow(),
                session_expires_at=datetime.utcnow() + timedelta(
                    minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES
                ),
                session_status="active"
            )
            
            self.db.add(session)
            await self.db.commit()
            
            # 记录操作日志
            await self.service_base_log_operation(
                "login",
                "user",
                user.user_id,
                user.user_id,
                {"login_ip": login_ip}
            )
            
            return {
                "success": True,
                "data": {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "expires_in": self.settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                    "user": {
                        "user_id": user.user_id,
                        "username": user.user_username,
                        "email": user.user_email,
                        "user_type": user.user_type
                    }
                }
            }
            
        except Exception as e:
            await self.db.rollback()
            return {
                "success": False,
                "error": f"登录失败: {str(e)}"
            }
    
    async def user_auth_service_logout(
        self,
        token: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        用户登出
        [services][user_auth][logout]
        """
        try:
            # 查找会话记录
            stmt = select(UserAuthSession).where(
                and_(
                    UserAuthSession.session_token == token,
                    UserAuthSession.user_id == user_id,
                    UserAuthSession.session_status == "active"
                )
            )
            result = await self.db.execute(stmt)
            session = result.scalar_one_or_none()
            
            if session:
                # 标记会话为已登出
                session.session_status = "logged_out"
                session.session_logout_time = datetime.utcnow()
                await self.db.commit()
            
            # 记录操作日志
            await self.service_base_log_operation(
                "logout",
                "user",
                user_id,
                user_id
            )
            
            return {
                "success": True,
                "message": "登出成功"
            }
            
        except Exception as e:
            await self.db.rollback()
            return {
                "success": False,
                "error": f"登出失败: {str(e)}"
            }
    
    async def user_auth_service_get_by_username(
        self,
        username: str
    ) -> Optional[UserAuthBasic]:
        """
        根据用户名获取用户
        [services][user_auth][get_by_username]
        """
        stmt = select(UserAuthBasic).where(UserAuthBasic.user_username == username)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def user_auth_service_get_by_email(
        self,
        email: str
    ) -> Optional[UserAuthBasic]:
        """
        根据邮箱获取用户
        [services][user_auth][get_by_email]
        """
        stmt = select(UserAuthBasic).where(UserAuthBasic.user_email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def user_auth_service_authenticate(
        self,
        username: str,
        password: str
    ) -> Optional[UserAuthBasic]:
        """
        验证用户凭据
        [services][user_auth][authenticate]
        """
        user = await self.user_auth_service_get_by_username(username)
        if not user:
            return None
        
        if not self.user_auth_service_verify_password(password, user.user_password_hash):
            return None
        
        return user
    
    def user_auth_service_hash_password(self, password: str) -> str:
        """
        密码哈希
        [services][user_auth][hash_password]
        """
        return self.pwd_context.hash(password)
    
    def user_auth_service_verify_password(
        self,
        plain_password: str,
        hashed_password: str
    ) -> bool:
        """
        验证密码
        [services][user_auth][verify_password]
        """
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def user_auth_service_create_access_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        创建访问令牌
        [services][user_auth][create_access_token]
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            self.settings.SECRET_KEY,
            algorithm=self.settings.ALGORITHM
        )
        return encoded_jwt
    
    async def user_auth_service_verify_token(
        self,
        token: str
    ) -> Optional[Dict[str, Any]]:
        """
        验证访问令牌
        [services][user_auth][verify_token]
        """
        try:
            payload = jwt.decode(
                token,
                self.settings.SECRET_KEY,
                algorithms=[self.settings.ALGORITHM]
            )
            user_id: str = payload.get("sub")
            username: str = payload.get("username")
            
            if user_id is None or username is None:
                return None
            
            return {
                "user_id": int(user_id),
                "username": username
            }
            
        except JWTError:
            return None