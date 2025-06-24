"""
Simple Database Creation Script
简单数据库创建脚本 - [scripts][create_database]
"""

import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def create_database():
    """
    创建数据库
    [scripts][create_database][main]
    """
    try:
        # 连接到 postgres 数据库（默认数据库）
        engine = create_async_engine(
            "postgresql+asyncpg://datasayai:datasayai123@localhost:5433/postgres",
            echo=True
        )
        
        async with engine.begin() as conn:
            # 检查数据库是否存在
            result = await conn.execute(text(
                "SELECT 1 FROM pg_database WHERE datname = 'datasay'"
            ))
            exists = result.fetchone()
            
            if not exists:
                # 创建数据库
                await conn.execute(text("CREATE DATABASE datasay"))
                print("✅ Database 'datasay' created successfully")
            else:
                print("ℹ️ Database 'datasay' already exists")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("📝 Database creation failed. Manual setup required:")
        print("   1. Start PostgreSQL server")
        print("   2. Run: createdb -h localhost -p 5433 -U datasayai datasay")
        print("   3. Or use SQL: CREATE DATABASE datasay;")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = asyncio.run(create_database())
    if success:
        print("🎯 Next step: Run alembic migrations")
        print("   alembic upgrade head")