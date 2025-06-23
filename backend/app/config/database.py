"""
Database Configuration
数据库配置管理 - [database][config]
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
import asyncio

from app.config.settings import app_config_get_settings

# 获取配置
settings = app_config_get_settings()

# 创建异步数据库引擎
database_engine_async = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    future=True,
    pool_pre_ping=True,
    pool_recycle=300,
)

# 创建异步会话工厂
database_session_async_factory = async_sessionmaker(
    database_engine_async,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# 创建声明式基类
DatabaseBase = declarative_base()

async def database_session_get_async() -> AsyncGenerator[AsyncSession, None]:
    """
    获取异步数据库会话
    [database][session][get_async]
    """
    async with database_session_async_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def database_connection_test_async() -> bool:
    """
    测试数据库连接
    [database][connection][test_async]
    """
    try:
        async with database_engine_async.begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

async def database_tables_create_async():
    """
    创建所有数据库表
    [database][tables][create_async]
    """
    async with database_engine_async.begin() as conn:
        await conn.run_sync(DatabaseBase.metadata.create_all)

async def database_tables_drop_async():
    """
    删除所有数据库表
    [database][tables][drop_async]
    """
    async with database_engine_async.begin() as conn:
        await conn.run_sync(DatabaseBase.metadata.drop_all)