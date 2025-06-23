#!/usr/bin/env python3
"""
Database Initialization Script
数据库初始化脚本 - [scripts][database][init]
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine
from app.config.settings import app_config_get_settings
from app.models.base import ModelBase

async def database_init_create_tables():
    """
    创建所有数据库表
    [database][init][create_tables]
    """
    settings = app_config_get_settings()
    
    # 创建异步引擎
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        future=True,
        pool_pre_ping=True,
        pool_recycle=300
    )
    
    try:
        print("🚀 开始创建数据库表...")
        
        # 创建所有表
        async with engine.begin() as conn:
            await conn.run_sync(ModelBase.metadata.create_all)
        
        print("✅ 数据库表创建成功！")
        
        # 显示创建的表
        async with engine.begin() as conn:
            tables = await conn.run_sync(
                lambda sync_conn: sync_conn.execute(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
                ).fetchall()
            )
            
            print(f"\n📋 创建的表 ({len(tables)} 个):")
            for table in sorted(tables):
                print(f"   - {table[0]}")
                
    except Exception as e:
        print(f"❌ 创建数据库表失败: {e}")
        raise
    
    finally:
        await engine.dispose()

async def database_init_drop_tables():
    """
    删除所有数据库表
    [database][init][drop_tables]
    """
    settings = app_config_get_settings()
    
    # 创建异步引擎
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        future=True,
        pool_pre_ping=True,
        pool_recycle=300
    )
    
    try:
        print("🗑️  开始删除数据库表...")
        
        # 删除所有表
        async with engine.begin() as conn:
            await conn.run_sync(ModelBase.metadata.drop_all)
        
        print("✅ 数据库表删除成功！")
                
    except Exception as e:
        print(f"❌ 删除数据库表失败: {e}")
        raise
    
    finally:
        await engine.dispose()

async def database_init_reset_tables():
    """
    重置数据库表（删除后重新创建）
    [database][init][reset_tables]
    """
    print("🔄 开始重置数据库表...")
    await database_init_drop_tables()
    await database_init_create_tables()
    print("✅ 数据库表重置完成！")

def main():
    """
    主函数
    [scripts][database][init][main]
    """
    if len(sys.argv) != 2:
        print("用法: python database_init.py <command>")
        print("命令:")
        print("  create  - 创建数据库表")
        print("  drop    - 删除数据库表")
        print("  reset   - 重置数据库表")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    try:
        if command == "create":
            asyncio.run(database_init_create_tables())
        elif command == "drop":
            asyncio.run(database_init_drop_tables())
        elif command == "reset":
            asyncio.run(database_init_reset_tables())
        else:
            print(f"❌ 未知命令: {command}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()