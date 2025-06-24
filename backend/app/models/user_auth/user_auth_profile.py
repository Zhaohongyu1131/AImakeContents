"""
User Authentication Profile Model
用户认证档案模型 - [user][auth][profile]
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean, func
from sqlalchemy.orm import relationship
from app.models.base import ModelBase

class UserAuthProfile(ModelBase):
    """
    用户认证档案表 - 扩展用户信息
    [user][auth][profile]
    """
    __tablename__ = "user_auth_profile"
    
    # 主键
    profile_id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="档案ID")
    
    # 关联用户
    user_id = Column(Integer, ForeignKey("user_auth_basic.user_id"), nullable=False, unique=True, index=True, comment="用户ID")
    
    # 用户档案信息
    profile_nickname = Column(String(100), nullable=True, comment="昵称")
    profile_avatar = Column(String(500), nullable=True, comment="头像URL")
    profile_bio = Column(Text, nullable=True, comment="个人简介")
    profile_location = Column(String(100), nullable=True, comment="位置")
    profile_website = Column(String(200), nullable=True, comment="个人网站")
    
    # 联系信息
    profile_phone = Column(String(20), nullable=True, comment="电话号码")
    profile_wechat = Column(String(50), nullable=True, comment="微信号")
    profile_qq = Column(String(20), nullable=True, comment="QQ号")
    
    # 偏好设置
    profile_language = Column(String(10), nullable=False, default="zh-CN", comment="语言偏好")
    profile_timezone = Column(String(50), nullable=False, default="Asia/Shanghai", comment="时区")
    profile_theme = Column(String(20), nullable=False, default="light", comment="主题偏好")
    
    # 隐私设置
    profile_privacy_settings = Column(JSON, nullable=True, comment="隐私设置JSON")
    profile_notification_settings = Column(JSON, nullable=True, comment="通知设置JSON")
    
    # 验证状态
    profile_phone_verified = Column(Boolean, nullable=False, default=False, comment="电话是否验证")
    profile_email_verified = Column(Boolean, nullable=False, default=False, comment="邮箱是否验证")
    profile_identity_verified = Column(Boolean, nullable=False, default=False, comment="身份是否验证")
    
    # 统计信息
    profile_login_count = Column(Integer, nullable=False, default=0, comment="登录次数")
    profile_last_login_time = Column(DateTime(timezone=True), nullable=True, comment="最后登录时间")
    profile_last_login_ip = Column(String(45), nullable=True, comment="最后登录IP")
    
    # 时间信息
    profile_created_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    profile_updated_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    
    # 状态
    profile_status = Column(String(20), nullable=False, default="active", index=True, comment="档案状态")
    
    # 关系映射
    user = relationship("UserAuthBasic", back_populates="profile")
    
    def __repr__(self) -> str:
        return f"<UserAuthProfile(profile_id={self.profile_id}, user_id={self.user_id}, nickname='{self.profile_nickname}')>"
    
    def profile_get_display_name(self) -> str:
        """
        获取显示名称
        [user][auth][profile][get_display_name]
        """
        if self.profile_nickname:
            return self.profile_nickname
        elif hasattr(self.user, 'user_username'):
            return self.user.user_username
        else:
            return f"用户{self.user_id}"
    
    def profile_privacy_get(self, key: str, default=None):
        """
        获取隐私设置
        [user][auth][profile][privacy_get]
        """
        if not self.profile_privacy_settings:
            return default
        return self.profile_privacy_settings.get(key, default)
    
    def profile_privacy_set(self, key: str, value):
        """
        设置隐私设置
        [user][auth][profile][privacy_set]
        """
        if not self.profile_privacy_settings:
            self.profile_privacy_settings = {}
        self.profile_privacy_settings[key] = value
    
    def profile_notification_get(self, key: str, default=None):
        """
        获取通知设置
        [user][auth][profile][notification_get]
        """
        if not self.profile_notification_settings:
            return default
        return self.profile_notification_settings.get(key, default)
    
    def profile_notification_set(self, key: str, value):
        """
        设置通知设置
        [user][auth][profile][notification_set]
        """
        if not self.profile_notification_settings:
            self.profile_notification_settings = {}
        self.profile_notification_settings[key] = value
    
    def profile_update_login_info(self, ip_address: str = None):
        """
        更新登录信息
        [user][auth][profile][update_login_info]
        """
        from datetime import datetime
        self.profile_login_count += 1
        self.profile_last_login_time = datetime.now()
        if ip_address:
            self.profile_last_login_ip = ip_address
    
    def profile_is_complete(self) -> bool:
        """
        检查档案是否完整
        [user][auth][profile][is_complete]
        """
        required_fields = [
            self.profile_nickname,
            self.profile_phone or (hasattr(self.user, 'user_email') and self.user.user_email)
        ]
        return all(field for field in required_fields)
    
    def profile_get_verification_status(self) -> dict:
        """
        获取验证状态
        [user][auth][profile][get_verification_status]
        """
        return {
            "phone_verified": self.profile_phone_verified,
            "email_verified": self.profile_email_verified,
            "identity_verified": self.profile_identity_verified,
            "overall_verified": all([
                self.profile_phone_verified,
                self.profile_email_verified
            ])
        }