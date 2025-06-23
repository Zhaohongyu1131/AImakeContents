#!/usr/bin/env python3
"""
Database Test Data Script
数据库测试数据脚本 - [scripts][database][test_data]
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config.settings import app_config_get_settings
from app.models.user_auth import UserAuthBasic, UserAuthProfile
from app.models.text_content import TextContentBasic, TextTemplateBasic
from app.models.voice_timbre import VoiceTimbreBasic
from app.models.file_storage import FileStorageBasic

async def database_test_data_create_users(session: AsyncSession):
    """
    创建测试用户数据
    [database][test_data][create_users]
    """
    print("👤 创建测试用户...")
    
    # 创建管理员用户
    admin_user = UserAuthBasic(
        user_username="admin",
        user_email="admin@datasay.com",
        user_password_hash="$2b$12$example_hash_for_admin_user",  # 实际应该使用真正的哈希
        user_role="admin",
        user_is_active=True,
        user_is_verified=True
    )
    session.add(admin_user)
    await session.flush()  # 获取ID
    
    # 创建管理员档案
    admin_profile = UserAuthProfile(
        user_id=admin_user.user_id,
        profile_display_name="系统管理员",
        profile_bio="DataSay平台管理员",
        profile_phone="13800138000"
    )
    session.add(admin_profile)
    
    # 创建普通用户
    demo_user = UserAuthBasic(
        user_username="demo_user",
        user_email="demo@datasay.com", 
        user_password_hash="$2b$12$example_hash_for_demo_user",
        user_role="user",
        user_is_active=True,
        user_is_verified=True
    )
    session.add(demo_user)
    await session.flush()
    
    # 创建普通用户档案
    demo_profile = UserAuthProfile(
        user_id=demo_user.user_id,
        profile_display_name="演示用户",
        profile_bio="DataSay平台演示用户",
        profile_phone="13900139000"
    )
    session.add(demo_profile)
    
    print(f"   ✅ 创建了 {admin_user.user_username} (管理员)")
    print(f"   ✅ 创建了 {demo_user.user_username} (普通用户)")
    
    return admin_user, demo_user

async def database_test_data_create_text_templates(session: AsyncSession, admin_user: UserAuthBasic):
    """
    创建测试文本模板
    [database][test_data][create_text_templates]
    """
    print("📝 创建测试文本模板...")
    
    templates = [
        {
            "name": "营销文案模板",
            "description": "用于生成营销推广文案的模板",
            "content": "【{product_name}】限时优惠！{discount}折起，{features}，立即购买享受{benefit}！",
            "type": "prompt",
            "variables": {
                "product_name": "产品名称",
                "discount": "折扣",
                "features": "产品特色",
                "benefit": "购买好处"
            }
        },
        {
            "name": "新闻稿模板",
            "description": "用于生成新闻稿的结构化模板",
            "content": "标题：{title}\n\n导语：{lead}\n\n正文：{body}\n\n结语：{conclusion}",
            "type": "structure",
            "variables": {
                "title": "新闻标题",
                "lead": "新闻导语",
                "body": "新闻正文",
                "conclusion": "新闻结语"
            }
        },
        {
            "name": "故事创作模板",
            "description": "用于创作故事的提示词模板",
            "content": "请创作一个关于{theme}的{genre}故事，主角是{protagonist}，故事发生在{setting}，核心冲突是{conflict}。",
            "type": "prompt",
            "variables": {
                "theme": "故事主题",
                "genre": "故事类型",
                "protagonist": "主角",
                "setting": "故事背景",
                "conflict": "核心冲突"
            }
        }
    ]
    
    for template_data in templates:
        template = TextTemplateBasic(
            template_name=template_data["name"],
            template_description=template_data["description"],
            template_content=template_data["content"],
            template_type=template_data["type"],
            template_variables=template_data["variables"],
            template_created_user_id=admin_user.user_id
        )
        session.add(template)
        print(f"   ✅ 创建了模板: {template_data['name']}")

async def database_test_data_create_text_contents(session: AsyncSession, demo_user: UserAuthBasic):
    """
    创建测试文本内容
    [database][test_data][create_text_contents]
    """
    print("📄 创建测试文本内容...")
    
    contents = [
        {
            "title": "AI技术发展趋势分析",
            "content": "随着人工智能技术的快速发展，我们正在见证一个全新的技术革命。从自然语言处理到计算机视觉，AI正在改变我们的生活和工作方式。",
            "type": "article"
        },
        {
            "title": "DataSay平台介绍",
            "content": "DataSay是一个创新的多媒体内容创作平台，集成了文本生成、语音合成、图像创作和视频制作功能，为用户提供一站式的内容创作解决方案。",
            "type": "description"
        },
        {
            "title": "环保生活小贴士",
            "content": "保护环境从我做起：1. 减少一次性用品使用 2. 选择绿色出行方式 3. 节约水电资源 4. 垃圾分类回收。让我们共同为地球的未来努力！",
            "type": "guide"
        }
    ]
    
    for content_data in contents:
        content = TextContentBasic(
            content_title=content_data["title"],
            content_text=content_data["content"],
            content_type=content_data["type"],
            content_created_user_id=demo_user.user_id
        )
        session.add(content)
        print(f"   ✅ 创建了内容: {content_data['title']}")

async def database_test_data_create_voice_timbres(session: AsyncSession, demo_user: UserAuthBasic):
    """
    创建测试音色数据
    [database][test_data][create_voice_timbres]
    """
    print("🎙️ 创建测试音色...")
    
    timbres = [
        {
            "name": "温暖女声",
            "description": "温柔亲切的女性音色，适合朗读和讲解",
            "platform": "volcano",
            "platform_id": "zh_female_warm_001",
            "language": "zh-CN",
            "gender": "female",
            "age_range": "25-35",
            "style": "温暖亲切",
            "quality_score": 85.5
        },
        {
            "name": "专业男声",
            "description": "成熟稳重的男性音色，适合新闻播报",
            "platform": "volcano",
            "platform_id": "zh_male_professional_001",
            "language": "zh-CN",
            "gender": "male",
            "age_range": "30-45",
            "style": "专业稳重",
            "quality_score": 88.2
        },
        {
            "name": "活泼童声",
            "description": "活泼可爱的儿童音色，适合儿童内容",
            "platform": "volcano",
            "platform_id": "zh_child_lively_001", 
            "language": "zh-CN",
            "gender": "neutral",
            "age_range": "8-12",
            "style": "活泼可爱",
            "quality_score": 82.0
        }
    ]
    
    for timbre_data in timbres:
        timbre = VoiceTimbreBasic(
            timbre_name=timbre_data["name"],
            timbre_description=timbre_data["description"],
            timbre_platform=timbre_data["platform"],
            timbre_platform_id=timbre_data["platform_id"],
            timbre_language=timbre_data["language"],
            timbre_gender=timbre_data["gender"],
            timbre_age_range=timbre_data["age_range"],
            timbre_style=timbre_data["style"],
            timbre_quality_score=timbre_data["quality_score"],
            timbre_status="ready",
            timbre_created_user_id=demo_user.user_id
        )
        session.add(timbre)
        print(f"   ✅ 创建了音色: {timbre_data['name']}")

async def database_test_data_insert_all():
    """
    插入所有测试数据
    [database][test_data][insert_all]
    """
    settings = app_config_get_settings()
    
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        future=True,
        pool_pre_ping=True,
        pool_recycle=300
    )
    
    # 创建异步会话工厂
    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    try:
        async with async_session_factory() as session:
            print("📦 开始插入测试数据...")
            
            # 创建用户
            admin_user, demo_user = await database_test_data_create_users(session)
            
            # 创建文本模板
            await database_test_data_create_text_templates(session, admin_user)
            
            # 创建文本内容
            await database_test_data_create_text_contents(session, demo_user)
            
            # 创建音色
            await database_test_data_create_voice_timbres(session, demo_user)
            
            # 提交所有更改
            await session.commit()
            print("✅ 所有测试数据插入成功！")
            
    except Exception as e:
        print(f"❌ 插入测试数据失败: {e}")
        raise
    
    finally:
        await engine.dispose()

async def database_test_data_clear_all():
    """
    清除所有测试数据
    [database][test_data][clear_all]
    """
    settings = app_config_get_settings()
    
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        future=True,
        pool_pre_ping=True,
        pool_recycle=300
    )
    
    try:
        async with engine.begin() as conn:
            print("🗑️  开始清除测试数据...")
            
            # 清除所有表的数据（按照依赖关系的逆序）
            tables = [
                "user_auth_session",
                "user_auth_profile", 
                "voice_timbre_clone",
                "voice_timbre_template",
                "voice_audio_analyse",
                "voice_audio_template",
                "voice_audio_basic",
                "voice_timbre_basic",
                "image_analyse",
                "image_template",
                "image_basic",
                "video_analyse", 
                "video_template",
                "video_basic",
                "mixed_content_analyse",
                "mixed_content_template",
                "mixed_content_basic",
                "text_content_analyse",
                "text_content_basic",
                "text_template_basic",
                "file_storage_analyse",
                "file_storage_basic",
                "user_auth_basic"
            ]
            
            for table in tables:
                await conn.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE")
                print(f"   ✅ 清除了表: {table}")
            
            print("✅ 所有测试数据清除成功！")
            
    except Exception as e:
        print(f"❌ 清除测试数据失败: {e}")
        raise
    
    finally:
        await engine.dispose()

def main():
    """
    主函数
    [scripts][database][test_data][main]
    """
    if len(sys.argv) != 2:
        print("用法: python database_test_data.py <command>")
        print("命令:")
        print("  insert  - 插入测试数据")
        print("  clear   - 清除测试数据")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    try:
        if command == "insert":
            asyncio.run(database_test_data_insert_all())
        elif command == "clear":
            asyncio.run(database_test_data_clear_all())
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