#!/usr/bin/env python3
"""
Database Verification Script
数据库验证脚本 - [scripts][verify_database]
"""

import asyncio
import asyncpg
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.settings import app_config_get_settings

async def verify_database():
    """验证数据库内容"""
    settings = app_config_get_settings()
    
    # 解析数据库URL
    url = settings.DATABASE_URL.replace('postgresql+asyncpg://', '')
    parts = url.split('/')
    db_name = parts[-1]
    auth_host = parts[0].split('@')
    auth_parts = auth_host[0].split(':')
    host_port = auth_host[1].split(':')
    
    conn = await asyncpg.connect(
        user=auth_parts[0],
        password=auth_parts[1],
        host=host_port[0],
        port=int(host_port[1]),
        database=db_name
    )
    
    try:
        print("🔍 数据库验证报告")
        print("=" * 50)
        
        # 查看所有表
        tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """
        tables = await conn.fetch(tables_query)
        print(f"📋 数据表 ({len(tables)}个):")
        for table in tables:
            print(f"   ✓ {table['table_name']}")
        
        print("\n📊 数据统计:")
        
        # 用户统计
        user_count = await conn.fetchval("SELECT COUNT(*) FROM user_auth_basic")
        print(f"   👥 用户数量: {user_count}")
        
        if user_count > 0:
            users = await conn.fetch("SELECT user_name, user_role, user_status FROM user_auth_basic")
            for user in users:
                print(f"      - {user['user_name']} ({user['user_role']}) - {user['user_status']}")
        
        # 模板统计
        text_template_count = await conn.fetchval("SELECT COUNT(*) FROM text_template_basic")
        voice_template_count = await conn.fetchval("SELECT COUNT(*) FROM voice_audio_template")
        image_template_count = await conn.fetchval("SELECT COUNT(*) FROM image_template")
        
        print(f"   📝 文本模板: {text_template_count}个")
        print(f"   🎵 语音模板: {voice_template_count}个")
        print(f"   🖼️  图像模板: {image_template_count}个")
        
        # 验证关系
        print("\n🔗 关系验证:")
        profile_count = await conn.fetchval("SELECT COUNT(*) FROM user_auth_profile")
        print(f"   👤 用户资料: {profile_count}个")
        
        if user_count == profile_count:
            print("   ✅ 用户-资料关系正常")
        else:
            print("   ❌ 用户-资料关系异常")
        
        print("\n🎉 数据库验证完成！")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(verify_database())