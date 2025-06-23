"""
Base Service Class
业务逻辑服务基类 - [services][base]
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import ModelBase


class ServiceBase(ABC):
    """
    业务逻辑服务基类
    [services][base]
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        初始化服务基类
        [services][base][init]
        """
        self.db = db_session
    
    async def service_base_validate_business_rules(
        self, 
        entity: ModelBase, 
        operation: str
    ) -> Dict[str, Any]:
        """
        验证业务规则
        [services][base][validate_business_rules]
        """
        return {
            "valid": True,
            "errors": [],
            "warnings": []
        }
    
    async def service_base_apply_business_logic(
        self,
        entity: ModelBase,
        operation: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        应用业务逻辑
        [services][base][apply_business_logic]
        """
        context = context or {}
        
        # 验证业务规则
        validation_result = await self.service_base_validate_business_rules(
            entity, operation
        )
        
        if not validation_result["valid"]:
            return {
                "success": False,
                "errors": validation_result["errors"]
            }
        
        return {
            "success": True,
            "data": entity,
            "warnings": validation_result["warnings"]
        }
    
    async def service_base_log_operation(
        self,
        operation: str,
        entity_type: str,
        entity_id: Optional[int] = None,
        user_id: Optional[int] = None,
        details: Dict[str, Any] = None
    ) -> None:
        """
        记录操作日志
        [services][base][log_operation]
        """
        # TODO: 实现操作日志记录
        pass
    
    async def service_base_send_notification(
        self,
        notification_type: str,
        recipient_id: int,
        content: Dict[str, Any]
    ) -> None:
        """
        发送通知
        [services][base][send_notification]
        """
        # TODO: 实现通知发送
        pass