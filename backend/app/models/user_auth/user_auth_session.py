"""
User Authentication Session Model
用户会话信息模型 - [user][auth][session]
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import INET
from app.models.base import ModelBase

class UserAuthSession(ModelBase):
    """
    用户会话信息表
    [user][auth][session]
    """
    __tablename__ = "user_auth_session"
    
    # 主键
    session_id = Column(String(128), primary_key=True, comment="会话ID")
    
    # 用户关联
    user_id = Column(Integer, ForeignKey("user_auth_basic.user_id"), nullable=False, index=True, comment="用户ID")
    
    # 会话信息
    session_token_hash = Column(String(255), nullable=False, comment="会话令牌哈希")
    session_expire_time = Column(DateTime(timezone=True), nullable=False, index=True, comment="过期时间")
    session_created_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    
    # 客户端信息
    session_ip_address = Column(INET, nullable=True, comment="IP地址")
    session_user_agent = Column(String(500), nullable=True, comment="用户代理")
    
    # 关系映射
    user = relationship("UserAuthBasic", back_populates="sessions")
    
    def __repr__(self) -> str:
        return f"<UserAuthSession(session_id='{self.session_id}', user_id={self.user_id})>"
    
    def session_is_expired(self) -> bool:
        """
        检查会话是否过期
        [session][is_expired]
        """
        from datetime import datetime
        return datetime.utcnow() > self.session_expire_time.replace(tzinfo=None)
    
    def session_ip_address_get(self) -> str:
        """
        获取IP地址字符串
        [session][ip_address][get]
        """
        return str(self.session_ip_address) if self.session_ip_address else "unknown"