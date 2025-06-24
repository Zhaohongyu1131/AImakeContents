#!/usr/bin/env python3
"""
Database Initialization Script
数据库初始化脚本 - [scripts][init_database]
"""

import asyncio
import logging
from typing import Dict, Any
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.settings import app_config_get_settings
from app.models.base import ModelBase
from app.models.user_auth.user_auth_basic import UserAuthBasic
from app.models.user_auth.user_auth_session import UserAuthSession
from app.models.user_auth.user_auth_profile import UserAuthProfile
from app.models.file_storage.file_storage_basic import FileStorageBasic
from app.models.file_storage.file_storage_meta import FileStorageMeta
from app.models.text_content.text_content_basic import TextContentBasic
from app.models.text_content.text_analyse_result import TextAnalyseResult
from app.models.text_content.text_template_basic import TextTemplateBasic
from app.models.voice_audio.voice_audio_basic import VoiceAudioBasic
from app.models.voice_audio.voice_audio_analyse import VoiceAudioAnalyse
from app.models.voice_audio.voice_audio_template import VoiceAudioTemplate
from app.models.voice_timbre.voice_timbre_basic import VoiceTimbreBasic
from app.models.voice_timbre.voice_timbre_clone import VoiceTimbreClone
from app.models.voice_timbre.voice_timbre_template import VoiceTimbreTemplate
from app.models.image_video.image_basic import ImageBasic
from app.models.image_video.image_analyse import ImageAnalyse
from app.models.image_video.image_template import ImageTemplate
from app.models.image_video.video_basic import VideoBasic
from app.models.image_video.video_analyse import VideoAnalyse
from app.models.image_video.video_template import VideoTemplate
from app.models.mixed_content.mixed_content_basic import MixedContentBasic
from app.models.mixed_content.mixed_content_analyse import MixedContentAnalyse
from app.models.mixed_content.mixed_content_template import MixedContentTemplate

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseInitializer:
    """
    数据库初始化器
    [scripts][init_database][initializer]
    """
    
    def __init__(self):
        self.settings = app_config_get_settings()
        self.db_config = self._parse_database_url()
        
    def _parse_database_url(self) -> Dict[str, str]:
        """解析数据库连接URL"""
        url = self.settings.DATABASE_URL
        # postgresql+asyncpg://datasayai:datasayai123@localhost:5433/datasay
        
        if not url.startswith('postgresql+asyncpg://'):
            raise ValueError("Invalid database URL format")
        
        # 移除协议部分
        url_parts = url.replace('postgresql+asyncpg://', '').split('/')
        db_name = url_parts[-1]
        
        auth_host = url_parts[0].split('@')
        auth_parts = auth_host[0].split(':')
        host_port = auth_host[1].split(':')
        
        return {
            'user': auth_parts[0],
            'password': auth_parts[1],
            'host': host_port[0],
            'port': int(host_port[1]),
            'database': db_name
        }
    
    async def create_database_if_not_exists(self) -> bool:
        """创建数据库（如果不存在）"""
        try:
            # 连接到postgres数据库来创建新数据库
            postgres_config = self.db_config.copy()
            postgres_config['database'] = 'postgres'
            
            conn = await asyncpg.connect(
                user=postgres_config['user'],
                password=postgres_config['password'],
                host=postgres_config['host'],
                port=postgres_config['port'],
                database=postgres_config['database']
            )
            
            try:
                # 检查数据库是否存在
                check_query = "SELECT 1 FROM pg_database WHERE datname = $1"
                result = await conn.fetchval(check_query, self.db_config['database'])
                
                if result:
                    logger.info(f"数据库 '{self.db_config['database']}' 已存在")
                    return True
                
                # 创建数据库
                create_query = f"CREATE DATABASE {self.db_config['database']}"
                await conn.execute(create_query)
                logger.info(f"数据库 '{self.db_config['database']}' 创建成功")
                return True
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"创建数据库失败: {str(e)}")
            return False
    
    async def create_tables(self) -> bool:
        """创建所有数据表"""
        try:
            # 创建异步引擎
            engine = create_async_engine(
                self.settings.DATABASE_URL,
                echo=self.settings.DATABASE_ECHO
            )
            
            # 创建所有表
            async with engine.begin() as conn:
                logger.info("开始创建数据表...")
                
                # 删除所有表（如果存在）- 谨慎使用
                await conn.run_sync(ModelBase.metadata.drop_all)
                logger.info("已删除所有现有表")
                
                # 创建所有表
                await conn.run_sync(ModelBase.metadata.create_all)
                logger.info("所有数据表创建成功")
                
            await engine.dispose()
            return True
            
        except Exception as e:
            logger.error(f"创建数据表失败: {str(e)}")
            return False
    
    async def create_initial_data(self) -> bool:
        """创建初始数据"""
        try:
            # 创建异步引擎和会话
            engine = create_async_engine(self.settings.DATABASE_URL)
            async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
            
            async with async_session() as session:
                logger.info("开始创建初始数据...")
                
                # 创建管理员用户
                await self._create_admin_user(session)
                
                # 创建测试用户
                await self._create_test_users(session)
                
                # 创建默认模板
                await self._create_default_templates(session)
                
                await session.commit()
                logger.info("初始数据创建成功")
                
            await engine.dispose()
            return True
            
        except Exception as e:
            logger.error(f"创建初始数据失败: {str(e)}")
            return False
    
    async def _create_admin_user(self, session: AsyncSession):
        """创建管理员用户"""
        from app.core.security import security_password_hash_create
        
        admin_user = UserAuthBasic(
            user_name="admin",
            user_email="admin@datasay.com",
            user_password_hash=security_password_hash_create("admin123"),
            user_role="admin",
            user_status="active"
        )
        
        session.add(admin_user)
        await session.flush()  # 获取用户ID
        
        # 创建管理员资料
        admin_profile = UserAuthProfile(
            user_id=admin_user.user_id,
            profile_nickname="系统管理员",
            profile_phone="",
            profile_avatar="",
            profile_bio="DataSay系统管理员账户"
        )
        
        session.add(admin_profile)
        logger.info("管理员用户创建成功: admin / admin123")
    
    async def _create_test_users(self, session: AsyncSession):
        """创建测试用户"""
        from app.core.security import security_password_hash_create
        
        test_users = [
            {
                "username": "testuser1",
                "email": "test1@datasay.com",
                "password": "test123",
                "role": "user",
                "real_name": "测试用户1"
            },
            {
                "username": "testuser2", 
                "email": "test2@datasay.com",
                "password": "test123",
                "role": "user",
                "real_name": "测试用户2"
            },
            {
                "username": "moderator",
                "email": "mod@datasay.com", 
                "password": "mod123",
                "role": "moderator",
                "real_name": "协调员"
            }
        ]
        
        for user_data in test_users:
            user = UserAuthBasic(
                user_name=user_data["username"],
                user_email=user_data["email"],
                user_password_hash=security_password_hash_create(user_data["password"]),
                user_role=user_data["role"],
                user_status="active"
            )
            
            session.add(user)
            await session.flush()
            
            # 创建用户资料
            profile = UserAuthProfile(
                user_id=user.user_id,
                profile_nickname=user_data["real_name"],
                profile_phone="",
                profile_avatar="",
                profile_bio=f"{user_data['real_name']}的个人资料"
            )
            
            session.add(profile)
            
        logger.info("测试用户创建成功")
    
    async def _create_default_templates(self, session: AsyncSession):
        """创建默认模板"""
        # 创建文本模板
        text_templates = [
            {
                "template_name": "新闻文章",
                "template_description": "新闻文章写作模板",
                "template_content": "标题: {title}\n\n导语: {lead}\n\n正文: {content}\n\n结语: {conclusion}",
                "template_variables": ["title", "lead", "content", "conclusion"],
                "template_type": "news"
            },
            {
                "template_name": "产品介绍",
                "template_description": "产品介绍文案模板", 
                "template_content": "产品名称: {product_name}\n\n主要功能: {features}\n\n优势特点: {advantages}\n\n适用场景: {use_cases}",
                "template_variables": ["product_name", "features", "advantages", "use_cases"],
                "template_type": "marketing"
            }
        ]
        
        for template_data in text_templates:
            template = TextTemplateBasic(
                template_name=template_data["template_name"],
                template_description=template_data["template_description"],
                template_content=template_data["template_content"],
                template_variables=template_data["template_variables"],
                template_type=template_data["template_type"],
                template_created_user_id=1,  # 管理员用户ID
                template_status="active"
            )
            session.add(template)
        
        # 创建语音模板
        voice_templates = [
            {
                "template_name": "新闻播报",
                "template_description": "新闻播报语音模板",
                "template_synthesis_params": {"voice_id": "news_anchor", "speed": 1.0, "volume": 1.0, "style": "news"},
                "template_type": "news"
            },
            {
                "template_name": "广告配音",
                "template_description": "广告配音模板",
                "template_synthesis_params": {"voice_id": "commercial", "speed": 0.9, "volume": 1.2, "style": "commercial"},
                "template_type": "commercial"
            }
        ]
        
        for template_data in voice_templates:
            template = VoiceAudioTemplate(
                template_name=template_data["template_name"],
                template_description=template_data["template_description"],
                template_synthesis_params=template_data["template_synthesis_params"],
                template_type=template_data["template_type"],
                template_created_user_id=1,
                template_status="active"
            )
            session.add(template)
        
        # 创建图像模板
        image_templates = [
            {
                "template_name": "产品海报",
                "template_description": "产品宣传海报模板",
                "template_generation_params": {"style": "commercial", "quality": "high"},
                "template_output_width": 1024,
                "template_output_height": 1024,
                "template_type": "marketing"
            },
            {
                "template_name": "社交媒体",
                "template_description": "社交媒体图片模板",
                "template_generation_params": {"style": "social", "quality": "standard"},
                "template_output_width": 1080,
                "template_output_height": 1080,
                "template_type": "social"
            }
        ]
        
        for template_data in image_templates:
            template = ImageTemplate(
                template_name=template_data["template_name"],
                template_description=template_data["template_description"],
                template_generation_params=template_data["template_generation_params"],
                template_output_width=template_data["template_output_width"],
                template_output_height=template_data["template_output_height"],
                template_type=template_data["template_type"],
                template_created_user_id=1,
                template_status="active"
            )
            session.add(template)
        
        logger.info("默认模板创建成功")
    
    async def verify_installation(self) -> bool:
        """验证数据库安装"""
        try:
            engine = create_async_engine(self.settings.DATABASE_URL)
            async_session = sessionmaker(engine, class_=AsyncSession)
            
            async with async_session() as session:
                # 检查表是否存在
                result = await session.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                tables = [row[0] for row in result.fetchall()]
                
                expected_tables = [
                    'user_auth_basic',
                    'user_auth_session', 
                    'user_auth_profile',
                    'file_storage_basic',
                    'file_storage_meta',
                    'text_content_basic',
                    'text_analyse_result',
                    'text_template_basic',
                    'voice_audio_basic',
                    'voice_audio_analyse',
                    'voice_audio_template',
                    'voice_timbre_basic',
                    'voice_timbre_clone',
                    'voice_timbre_template',
                    'image_basic',
                    'image_analyse',
                    'image_template',
                    'video_basic',
                    'video_analyse',
                    'video_template',
                    'mixed_content_basic',
                    'mixed_content_analyse',
                    'mixed_content_template'
                ]
                
                missing_tables = set(expected_tables) - set(tables)
                if missing_tables:
                    logger.error(f"缺少数据表: {missing_tables}")
                    return False
                
                # 检查用户数据
                result = await session.execute(text("SELECT COUNT(*) FROM user_auth_basic"))
                user_count = result.scalar()
                
                if user_count == 0:
                    logger.error("未找到用户数据")
                    return False
                
                logger.info(f"数据库验证成功 - 表数量: {len(tables)}, 用户数量: {user_count}")
                return True
                
            await engine.dispose()
            
        except Exception as e:
            logger.error(f"数据库验证失败: {str(e)}")
            return False


async def main():
    """主函数"""
    print("=" * 60)
    print("DataSay 数据库初始化工具")
    print("=" * 60)
    
    initializer = DatabaseInitializer()
    
    try:
        # 步骤1: 创建数据库
        print("\n🔧 步骤1: 创建数据库...")
        if not await initializer.create_database_if_not_exists():
            print("❌ 数据库创建失败")
            return False
        print("✅ 数据库创建成功")
        
        # 步骤2: 创建数据表
        print("\n🔧 步骤2: 创建数据表...")
        if not await initializer.create_tables():
            print("❌ 数据表创建失败")
            return False
        print("✅ 数据表创建成功")
        
        # 步骤3: 创建初始数据
        print("\n🔧 步骤3: 创建初始数据...")
        if not await initializer.create_initial_data():
            print("❌ 初始数据创建失败")
            return False
        print("✅ 初始数据创建成功")
        
        # 步骤4: 验证安装
        print("\n🔧 步骤4: 验证安装...")
        if not await initializer.verify_installation():
            print("❌ 数据库验证失败")
            return False
        print("✅ 数据库验证成功")
        
        print("\n" + "=" * 60)
        print("🎉 数据库初始化完成！")
        print("\n📝 默认账户信息:")
        print("   管理员: admin / admin123")
        print("   测试用户1: testuser1 / test123")
        print("   测试用户2: testuser2 / test123")
        print("   协调员: moderator / mod123")
        print("\n🔗 数据库连接: postgresql+asyncpg://datasayai:datasayai123@localhost:5433/datasay")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 初始化过程中发生错误: {str(e)}")
        return False


if __name__ == "__main__":
    asyncio.run(main())