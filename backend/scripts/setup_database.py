"""
Database Setup Script
数据库设置脚本 - [scripts][setup_database]
"""

import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from app.models.base import ModelBase
from app.config.settings import app_config_get_settings

# 导入所有模型以确保它们被注册到元数据中
from app.models.user_auth import *
from app.models.file_storage import *
from app.models.text_content import *
from app.models.voice_timbre import *
from app.models.voice_audio import *
from app.models.image_video import *
from app.models.mixed_content import *

async def setup_database_create_database():
    """
    创建数据库
    [scripts][setup_database][create_database]
    """
    settings = app_config_get_settings()
    
    # 连接到默认的postgres数据库来创建新数据库
    engine = create_async_engine(
        "postgresql+asyncpg://datasayai:datasayai123@localhost:5433/postgres",
        echo=True
    )
    
    try:
        async with engine.begin() as conn:
            # 检查数据库是否存在
            result = await conn.execute(
                "SELECT 1 FROM pg_database WHERE datname = 'datasay'"
            )
            if not result.fetchone():
                # 创建数据库
                await conn.execute("CREATE DATABASE datasay")
                print("✅ Database 'datasay' created successfully")
            else:
                print("ℹ️ Database 'datasay' already exists")
                
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        # 如果连接失败，我们将生成SQL文件供手动执行
        await setup_database_generate_sql_script()
    finally:
        await engine.dispose()

async def setup_database_create_tables():
    """
    创建数据表
    [scripts][setup_database][create_tables]
    """
    settings = app_config_get_settings()
    
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True
    )
    
    try:
        async with engine.begin() as conn:
            # 创建所有表
            await conn.run_sync(ModelBase.metadata.create_all)
            print("✅ All database tables created successfully")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise
    finally:
        await engine.dispose()

async def setup_database_generate_sql_script():
    """
    生成SQL脚本文件
    [scripts][setup_database][generate_sql_script]
    """
    from sqlalchemy import create_engine
    from sqlalchemy.dialects import postgresql
    
    print("📝 Generating SQL script for manual database setup...")
    
    # 创建一个虚拟引擎来生成SQL
    engine = create_engine("postgresql://", strategy='mock', executor=lambda sql, *_: None)
    
    sql_script = []
    
    # 添加数据库创建语句
    sql_script.append("-- DataSay Database Setup Script")
    sql_script.append("-- Run this script to set up the DataSay database\n")
    sql_script.append("-- 1. Create database")
    sql_script.append("CREATE DATABASE datasay;")
    sql_script.append("\\c datasay;\n")
    sql_script.append("-- 2. Create extensions")
    sql_script.append('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    sql_script.append('CREATE EXTENSION IF NOT EXISTS "pg_trgm";\n')
    sql_script.append("-- 3. Create all tables")
    
    # 生成创建表的SQL
    def dump(sql, *multiparams, **params):
        statement = str(sql.compile(dialect=postgresql.dialect()))
        sql_script.append(statement + ";")
    
    engine.execute = dump
    ModelBase.metadata.create_all(engine, checkfirst=False)
    
    # 写入SQL文件
    sql_content = "\n".join(sql_script)
    
    with open("scripts/database_setup.sql", "w", encoding="utf-8") as f:
        f.write(sql_content)
    
    print("✅ SQL script generated at: scripts/database_setup.sql")
    print("📋 To set up the database manually, run:")
    print("   psql -h localhost -p 5433 -U datasayai -f scripts/database_setup.sql")

async def setup_database_insert_test_data():
    """
    插入测试数据
    [scripts][setup_database][insert_test_data]
    """
    from datetime import datetime
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
    from app.models.user_auth.user_auth_basic import UserAuthBasic
    from app.models.user_auth.user_auth_profile import UserAuthProfile
    
    settings = app_config_get_settings()
    
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(engine, class_=AsyncSession)
    
    try:
        async with async_session() as session:
            # 创建默认用户
            test_user = UserAuthBasic(
                user_name="admin",
                user_email="admin@datasay.ai",
                user_password_hash="$2b$12$placeholder",  # 需要实际的hash
                user_is_active=True,
                user_is_admin=True,
                user_created_time=datetime.utcnow()
            )
            
            session.add(test_user)
            await session.commit()
            await session.refresh(test_user)
            
            # 创建用户配置
            user_profile = UserAuthProfile(
                user_id=test_user.user_id,
                profile_display_name="DataSay Administrator",
                profile_avatar_url="/static/default_avatar.png",
                profile_bio="DataSay platform administrator",
                profile_created_time=datetime.utcnow()
            )
            
            session.add(user_profile)
            await session.commit()
            
            print("✅ Test data inserted successfully")
            print(f"   Default user: admin (ID: {test_user.user_id})")
            
    except Exception as e:
        print(f"❌ Error inserting test data: {e}")
    finally:
        await engine.dispose()

async def main():
    """
    主函数
    [scripts][setup_database][main]
    """
    print("🚀 Starting DataSay database setup...")
    
    try:
        # 1. 创建数据库
        await setup_database_create_database()
        
        # 2. 创建表结构
        await setup_database_create_tables()
        
        # 3. 插入测试数据
        await setup_database_insert_test_data()
        
        print("\n✅ Database setup completed successfully!")
        print("🎯 Next steps:")
        print("   1. Run: alembic stamp head")
        print("   2. For future migrations: alembic revision --autogenerate")
        print("   3. Apply migrations: alembic upgrade head")
        
    except Exception as e:
        print(f"\n❌ Database setup failed: {e}")
        print("📝 Generating SQL script for manual setup...")
        await setup_database_generate_sql_script()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())