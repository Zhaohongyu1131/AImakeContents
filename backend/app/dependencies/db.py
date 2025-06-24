"""
Database Dependencies
数据库依赖项 - [dependencies][db]
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.config.settings import settings


# 创建异步数据库引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=20,
    max_overflow=30
)

# 创建异步会话工厂
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话
    [dependencies][db][get_db]
    """
    async with async_session_factory() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


async def get_db_transaction() -> AsyncGenerator[AsyncSession, None]:
    """
    获取事务性数据库会话
    [dependencies][db][get_db_transaction]
    """
    async with async_session_factory() as session:
        async with session.begin():
            try:
                yield session
            except Exception as e:
                await session.rollback()
                raise e