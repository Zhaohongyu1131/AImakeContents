"""
Base Repository Class
数据访问层基类 - [repositories][base]
"""

from abc import ABC
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.orm import selectinload, joinedload
from app.models.base import ModelBase

T = TypeVar('T', bound=ModelBase)


class RepositoryBase(Generic[T], ABC):
    """
    数据访问层基类
    [repositories][base]
    """
    
    def __init__(self, db_session: AsyncSession, model_class: Type[T]):
        """
        初始化仓储基类
        [repositories][base][init]
        """
        self.db = db_session
        self.model_class = model_class
    
    async def repository_base_create(self, **kwargs) -> T:
        """
        创建记录
        [repositories][base][create]
        """
        instance = self.model_class(**kwargs)
        self.db.add(instance)
        await self.db.commit()
        await self.db.refresh(instance)
        return instance
    
    async def repository_base_get_by_id(self, id_value: Any) -> Optional[T]:
        """
        根据ID获取记录
        [repositories][base][get_by_id]
        """
        primary_key = self.repository_base_get_primary_key()
        stmt = select(self.model_class).where(getattr(self.model_class, primary_key) == id_value)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def repository_base_get_by_field(
        self, 
        field_name: str, 
        field_value: Any
    ) -> Optional[T]:
        """
        根据字段获取记录
        [repositories][base][get_by_field]
        """
        stmt = select(self.model_class).where(getattr(self.model_class, field_name) == field_value)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def repository_base_get_all(
        self,
        conditions: Optional[List] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[T]:
        """
        获取所有记录
        [repositories][base][get_all]
        """
        stmt = select(self.model_class)
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        if order_by:
            order_field = getattr(self.model_class, order_by, None)
            if order_field is not None:
                stmt = stmt.order_by(order_field)
        
        if offset is not None:
            stmt = stmt.offset(offset)
        
        if limit is not None:
            stmt = stmt.limit(limit)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def repository_base_count(
        self,
        conditions: Optional[List] = None
    ) -> int:
        """
        统计记录数量
        [repositories][base][count]
        """
        primary_key = self.repository_base_get_primary_key()
        stmt = select(func.count(getattr(self.model_class, primary_key)))
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        result = await self.db.execute(stmt)
        return result.scalar()
    
    async def repository_base_update(
        self,
        id_value: Any,
        **kwargs
    ) -> Optional[T]:
        """
        更新记录
        [repositories][base][update]
        """
        primary_key = self.repository_base_get_primary_key()
        stmt = update(self.model_class).where(
            getattr(self.model_class, primary_key) == id_value
        ).values(**kwargs).returning(self.model_class)
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        updated_instance = result.scalar_one_or_none()
        if updated_instance:
            await self.db.refresh(updated_instance)
        
        return updated_instance
    
    async def repository_base_update_by_conditions(
        self,
        conditions: List,
        **kwargs
    ) -> int:
        """
        根据条件批量更新
        [repositories][base][update_by_conditions]
        """
        stmt = update(self.model_class).where(and_(*conditions)).values(**kwargs)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount
    
    async def repository_base_delete(self, id_value: Any) -> bool:
        """
        删除记录
        [repositories][base][delete]
        """
        primary_key = self.repository_base_get_primary_key()
        stmt = delete(self.model_class).where(
            getattr(self.model_class, primary_key) == id_value
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
    
    async def repository_base_soft_delete(
        self,
        id_value: Any,
        delete_field: str = "deleted_at",
        status_field: Optional[str] = None,
        status_value: str = "deleted"
    ) -> Optional[T]:
        """
        软删除记录
        [repositories][base][soft_delete]
        """
        from datetime import datetime
        
        update_data = {delete_field: datetime.utcnow()}
        if status_field:
            update_data[status_field] = status_value
        
        return await self.repository_base_update(id_value, **update_data)
    
    async def repository_base_exists(
        self,
        conditions: List
    ) -> bool:
        """
        检查记录是否存在
        [repositories][base][exists]
        """
        primary_key = self.repository_base_get_primary_key()
        stmt = select(func.count(getattr(self.model_class, primary_key))).where(
            and_(*conditions)
        )
        result = await self.db.execute(stmt)
        count = result.scalar()
        return count > 0
    
    async def repository_base_get_with_relations(
        self,
        id_value: Any,
        relations: List[str]
    ) -> Optional[T]:
        """
        获取包含关联关系的记录
        [repositories][base][get_with_relations]
        """
        primary_key = self.repository_base_get_primary_key()
        stmt = select(self.model_class).where(
            getattr(self.model_class, primary_key) == id_value
        )
        
        # 添加关联加载
        for relation in relations:
            relation_attr = getattr(self.model_class, relation, None)
            if relation_attr is not None:
                stmt = stmt.options(selectinload(relation_attr))
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def repository_base_bulk_create(
        self,
        instances_data: List[Dict[str, Any]]
    ) -> List[T]:
        """
        批量创建记录
        [repositories][base][bulk_create]
        """
        instances = []
        for data in instances_data:
            instance = self.model_class(**data)
            instances.append(instance)
            self.db.add(instance)
        
        await self.db.commit()
        
        # 刷新所有实例
        for instance in instances:
            await self.db.refresh(instance)
        
        return instances
    
    async def repository_base_paginate(
        self,
        page: int = 1,
        size: int = 20,
        conditions: Optional[List] = None,
        order_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        分页查询
        [repositories][base][paginate]
        """
        if page < 1:
            page = 1
        if size < 1:
            size = 20
        if size > 100:
            size = 100
        
        offset = (page - 1) * size
        
        # 查询数据
        items = await self.repository_base_get_all(
            conditions=conditions,
            order_by=order_by,
            limit=size,
            offset=offset
        )
        
        # 查询总数
        total = await self.repository_base_count(conditions)
        
        pages = (total + size - 1) // size
        
        return {
            "items": items,
            "pagination": {
                "page": page,
                "size": size,
                "total": total,
                "pages": pages,
                "has_next": page < pages,
                "has_prev": page > 1
            }
        }
    
    def repository_base_get_primary_key(self) -> str:
        """
        获取主键字段名
        [repositories][base][get_primary_key]
        """
        for column in self.model_class.__table__.columns:
            if column.primary_key:
                return column.name
        raise ValueError(f"No primary key found for {self.model_class.__name__}")
    
    async def repository_base_search(
        self,
        search_fields: List[str],
        search_term: str,
        conditions: Optional[List] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        搜索记录
        [repositories][base][search]
        """
        search_conditions = []
        
        # 构建搜索条件
        for field in search_fields:
            field_attr = getattr(self.model_class, field, None)
            if field_attr is not None:
                search_conditions.append(field_attr.like(f"%{search_term}%"))
        
        # 组合搜索条件
        all_conditions = conditions or []
        if search_conditions:
            all_conditions.append(or_(*search_conditions))
        
        return await self.repository_base_paginate(
            page=page,
            size=size,
            conditions=all_conditions
        )