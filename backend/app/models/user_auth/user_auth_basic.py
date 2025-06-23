"""
User Authentication Basic Model
用户基础信息模型 - [user][auth][basic]
"""

from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.models.base import ModelBase

class UserAuthBasic(ModelBase):
    """
    用户基础信息表
    [user][auth][basic]
    """
    __tablename__ = "user_auth_basic"
    
    # 主键
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="用户ID")
    
    # 基础信息
    user_name = Column(String(50), nullable=False, unique=True, index=True, comment="用户名")
    user_email = Column(String(100), nullable=False, unique=True, index=True, comment="邮箱地址")
    user_phone = Column(String(20), nullable=True, comment="手机号码")
    user_password_hash = Column(String(255), nullable=False, comment="密码哈希")
    
    # 状态和角色
    user_status = Column(String(20), nullable=False, default="active", index=True, comment="用户状态")
    user_role = Column(String(20), nullable=False, default="user", index=True, comment="用户角色")
    
    # 时间记录
    user_created_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    user_updated_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    user_last_login_time = Column(DateTime(timezone=True), nullable=True, comment="最后登录时间")
    
    # 个人资料
    user_profile_avatar = Column(String(500), nullable=True, comment="头像URL")
    user_profile_nickname = Column(String(100), nullable=True, comment="昵称")
    
    # 关系映射
    sessions = relationship("UserAuthSession", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<UserAuthBasic(user_id={self.user_id}, user_name='{self.user_name}', user_email='{self.user_email}')>"
    
    @property
    def user_display_name(self) -> str:
        """
        获取用户显示名称
        [user][display_name]
        """
        return self.user_profile_nickname or self.user_name
    
    def user_status_is_active(self) -> bool:
        """
        检查用户是否激活
        [user][status][is_active]
        """
        return self.user_status == "active"
    
    def user_role_is_admin(self) -> bool:
        """
        检查用户是否为管理员
        [user][role][is_admin]
        """
        return self.user_role in ["admin", "super_admin"]