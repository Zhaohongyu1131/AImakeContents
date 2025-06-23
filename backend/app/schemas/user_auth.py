"""
User Auth Schemas
用户认证响应模型 - [schemas][user_auth]
"""

from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

# ==================== 用户基础信息 ====================

class UserAuthBasicSchema(BaseModel):
    """
    用户基础信息响应模型
    [schemas][user_auth][basic]
    """
    user_id: int = Field(..., description="用户ID")
    user_username: str = Field(..., description="用户名")
    user_email: EmailStr = Field(..., description="邮箱地址")
    user_role: str = Field(..., description="用户角色")
    user_is_active: bool = Field(..., description="是否激活")
    user_is_verified: bool = Field(..., description="是否验证")
    user_created_time: datetime = Field(..., description="创建时间")
    user_last_login_time: Optional[datetime] = Field(None, description="最后登录时间")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserAuthBasicCreateSchema(BaseModel):
    """
    用户创建请求模型
    [schemas][user_auth][basic_create]
    """
    user_username: str = Field(..., min_length=3, max_length=50, description="用户名")
    user_email: EmailStr = Field(..., description="邮箱地址")
    user_password: str = Field(..., min_length=8, description="密码")
    user_role: str = Field("user", description="用户角色")

class UserAuthBasicUpdateSchema(BaseModel):
    """
    用户更新请求模型
    [schemas][user_auth][basic_update]
    """
    user_email: Optional[EmailStr] = Field(None, description="邮箱地址")
    user_role: Optional[str] = Field(None, description="用户角色")
    user_is_active: Optional[bool] = Field(None, description="是否激活")

# ==================== 用户档案信息 ====================

class UserAuthProfileSchema(BaseModel):
    """
    用户档案信息响应模型
    [schemas][user_auth][profile]
    """
    profile_id: int = Field(..., description="档案ID")
    user_id: int = Field(..., description="用户ID")
    profile_display_name: Optional[str] = Field(None, description="显示名称")
    profile_avatar_url: Optional[str] = Field(None, description="头像URL")
    profile_bio: Optional[str] = Field(None, description="个人简介")
    profile_phone: Optional[str] = Field(None, description="联系电话")
    profile_address: Optional[str] = Field(None, description="联系地址")
    profile_preferences: Optional[dict] = Field(None, description="用户偏好设置")
    profile_created_time: datetime = Field(..., description="创建时间")
    profile_updated_time: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserAuthProfileCreateSchema(BaseModel):
    """
    用户档案创建请求模型
    [schemas][user_auth][profile_create]
    """
    profile_display_name: Optional[str] = Field(None, max_length=100, description="显示名称")
    profile_avatar_url: Optional[str] = Field(None, description="头像URL")
    profile_bio: Optional[str] = Field(None, max_length=500, description="个人简介")
    profile_phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    profile_address: Optional[str] = Field(None, max_length=200, description="联系地址")
    profile_preferences: Optional[dict] = Field(None, description="用户偏好设置")

class UserAuthProfileUpdateSchema(BaseModel):
    """
    用户档案更新请求模型
    [schemas][user_auth][profile_update]
    """
    profile_display_name: Optional[str] = Field(None, max_length=100, description="显示名称")
    profile_avatar_url: Optional[str] = Field(None, description="头像URL")
    profile_bio: Optional[str] = Field(None, max_length=500, description="个人简介")
    profile_phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    profile_address: Optional[str] = Field(None, max_length=200, description="联系地址")
    profile_preferences: Optional[dict] = Field(None, description="用户偏好设置")

# ==================== 用户会话信息 ====================

class UserAuthSessionSchema(BaseModel):
    """
    用户会话信息响应模型
    [schemas][user_auth][session]
    """
    session_id: int = Field(..., description="会话ID")
    user_id: int = Field(..., description="用户ID")
    session_token: str = Field(..., description="会话令牌")
    session_device_info: Optional[str] = Field(None, description="设备信息")
    session_ip_address: Optional[str] = Field(None, description="IP地址")
    session_user_agent: Optional[str] = Field(None, description="用户代理")
    session_created_time: datetime = Field(..., description="创建时间")
    session_last_activity_time: datetime = Field(..., description="最后活动时间")
    session_expires_at: datetime = Field(..., description="过期时间")
    session_is_active: bool = Field(..., description="是否活跃")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# ==================== 登录认证 ====================

class UserAuthLoginSchema(BaseModel):
    """
    用户登录请求模型
    [schemas][user_auth][login]
    """
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")
    device_info: Optional[str] = Field(None, description="设备信息")

class UserAuthTokenSchema(BaseModel):
    """
    认证令牌响应模型
    [schemas][user_auth][token]
    """
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field("bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")
    user_info: UserAuthBasicSchema = Field(..., description="用户信息")

class UserAuthRefreshTokenSchema(BaseModel):
    """
    刷新令牌请求模型
    [schemas][user_auth][refresh_token]
    """
    refresh_token: str = Field(..., description="刷新令牌")

class UserAuthPasswordChangeSchema(BaseModel):
    """
    密码修改请求模型
    [schemas][user_auth][password_change]
    """
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=8, description="新密码")

class UserAuthPasswordResetSchema(BaseModel):
    """
    密码重置请求模型
    [schemas][user_auth][password_reset]
    """
    email: EmailStr = Field(..., description="邮箱地址")

class UserAuthPasswordResetConfirmSchema(BaseModel):
    """
    密码重置确认请求模型
    [schemas][user_auth][password_reset_confirm]
    """
    token: str = Field(..., description="重置令牌")
    new_password: str = Field(..., min_length=8, description="新密码")

# ==================== 完整用户信息 ====================

class UserAuthCompleteSchema(BaseModel):
    """
    完整用户信息响应模型
    [schemas][user_auth][complete]
    """
    user: UserAuthBasicSchema = Field(..., description="用户基础信息")
    profile: Optional[UserAuthProfileSchema] = Field(None, description="用户档案信息")
    active_sessions: List[UserAuthSessionSchema] = Field([], description="活跃会话列表")
    
    class Config:
        from_attributes = True