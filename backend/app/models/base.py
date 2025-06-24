"""
Base Model Classes
基础模型类 - [models][base]
"""

from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declared_attr
from app.config.database import DatabaseBase

class ModelBase(DatabaseBase):
    """
    基础模型类
    [model][base]
    """
    __abstract__ = True
    
    @declared_attr
    def __tablename__(cls) -> str:
        """
        自动生成表名
        遵循 [business_module][data_object][attribute] 命名规范
        """
        return cls.__name__.lower()

class ModelBaseWithTimestamp(ModelBase):
    """
    包含时间戳的基础模型类
    [model][base][with_timestamp]
    """
    __abstract__ = True
    
    created_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class ModelBaseWithUser(ModelBase):
    """
    包含用户关联的基础模型类
    [model][base][with_user]
    """
    __abstract__ = True
    
    created_user_id = Column(Integer, nullable=False, index=True, comment="创建用户ID")
    
class ModelBaseWithStatus(ModelBase):
    """
    包含状态的基础模型类
    [model][base][with_status]
    """
    __abstract__ = True
    
    status = Column(String(20), nullable=False, default="active", index=True, comment="状态")

class ModelBaseComplete(ModelBase):
    """
    完整的基础模型类（包含用户和状态）
    [model][base][complete]
    """
    __abstract__ = True
    
    created_user_id = Column(Integer, nullable=False, index=True, comment="创建用户ID")
    status = Column(String(20), nullable=False, default="active", index=True, comment="状态")