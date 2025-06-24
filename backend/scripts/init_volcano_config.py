"""
Initialize Volcano API Configuration Data
初始化火山引擎API配置数据
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings
from app.models.base import Base


async def init_volcano_config_data():
    """初始化火山引擎API配置数据"""
    
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # 音色克隆基础设置配置
            voice_clone_basic_configs = [
                {
                    'config_name': '音色名称',
                    'config_type': 'voice_clone',
                    'config_category': 'basic',
                    'config_key': 'timbre_name',
                    'config_label': '音色名称',
                    'config_description': '为您的音色起一个易识别的名称',
                    'config_data_type': 'string',
                    'config_default_value': '',
                    'config_validation_rules': '{"min_length": 1, "max_length": 50}',
                    'config_display_order': 1,
                    'config_is_required': True,
                    'config_group_name': '基本信息'
                },
                {
                    'config_name': '音色描述',
                    'config_type': 'voice_clone',
                    'config_category': 'basic',
                    'config_key': 'timbre_description',
                    'config_label': '音色描述',
                    'config_description': '描述音色的特点和用途',
                    'config_data_type': 'string',
                    'config_default_value': '',
                    'config_validation_rules': '{"max_length": 200}',
                    'config_display_order': 2,
                    'config_is_required': False,
                    'config_group_name': '基本信息'
                },
                {
                    'config_name': '语言类型',
                    'config_type': 'voice_clone',
                    'config_category': 'basic',
                    'config_key': 'language',
                    'config_label': '语言类型',
                    'config_description': '选择音色主要支持的语言',
                    'config_data_type': 'select',
                    'config_default_value': '0',
                    'config_options': '{"options": [{"value": "0", "label": "中文"}, {"value": "1", "label": "英文"}, {"value": "2", "label": "日语"}, {"value": "3", "label": "西班牙语"}, {"value": "4", "label": "印尼语"}, {"value": "5", "label": "葡萄牙语"}]}',
                    'config_display_order': 3,
                    'config_is_required': True,
                    'config_group_name': '基本信息'
                },
                {
                    'config_name': '模型类型',
                    'config_type': 'voice_clone',
                    'config_category': 'basic',
                    'config_key': 'model_type',
                    'config_label': '模型类型',
                    'config_description': '选择音色训练使用的模型版本',
                    'config_data_type': 'select',
                    'config_default_value': '1',
                    'config_options': '{"options": [{"value": "1", "label": "2.0效果(ICL) - 推荐"}, {"value": "0", "label": "1.0效果"}, {"value": "2", "label": "DiT标准版(音色)"}, {"value": "3", "label": "DiT还原版(音色+风格)"}]}',
                    'config_display_order': 4,
                    'config_is_required': True,
                    'config_group_name': '训练设置'
                }
            ]
            
            # 音色克隆高级设置配置
            voice_clone_advanced_configs = [
                {
                    'config_name': '参考文本',
                    'config_type': 'voice_clone',
                    'config_category': 'advanced',
                    'config_key': 'reference_text',
                    'config_label': '参考文本',
                    'config_description': '提供参考文本可提高训练质量，音频内容应与此文本一致',
                    'config_data_type': 'string',
                    'config_default_value': '',
                    'config_validation_rules': '{"max_length": 1000}',
                    'config_display_order': 1,
                    'config_is_required': False,
                    'config_group_name': '质量优化'
                },
                {
                    'config_name': '音频格式',
                    'config_type': 'voice_clone',
                    'config_category': 'advanced',
                    'config_key': 'audio_format',
                    'config_label': '音频格式',
                    'config_description': '源音频文件格式',
                    'config_data_type': 'select',
                    'config_default_value': 'wav',
                    'config_options': '{"options": [{"value": "wav", "label": "WAV"}, {"value": "mp3", "label": "MP3"}, {"value": "ogg", "label": "OGG"}, {"value": "m4a", "label": "M4A"}, {"value": "aac", "label": "AAC"}, {"value": "pcm", "label": "PCM"}]}',
                    'config_display_order': 2,
                    'config_is_required': False,
                    'config_group_name': '音频设置'
                }
            ]
            
            # TTS合成基础设置配置
            tts_basic_configs = [
                {
                    'config_name': '语速',
                    'config_type': 'tts_basic',
                    'config_category': 'basic',
                    'config_key': 'speed_ratio',
                    'config_label': '语速',
                    'config_description': '调整语音播放速度',
                    'config_data_type': 'float',
                    'config_default_value': '1.0',
                    'config_validation_rules': '{"min": 0.2, "max": 3.0, "step": 0.1}',
                    'config_display_order': 1,
                    'config_is_required': False,
                    'config_group_name': '语音控制'
                },
                {
                    'config_name': '音量',
                    'config_type': 'tts_basic',
                    'config_category': 'basic',
                    'config_key': 'volume_ratio',
                    'config_label': '音量',
                    'config_description': '调整语音音量大小',
                    'config_data_type': 'float',
                    'config_default_value': '1.0',
                    'config_validation_rules': '{"min": 0.1, "max": 2.0, "step": 0.1}',
                    'config_display_order': 2,
                    'config_is_required': False,
                    'config_group_name': '语音控制'
                },
                {
                    'config_name': '音调',
                    'config_type': 'tts_basic',
                    'config_category': 'basic',
                    'config_key': 'pitch_ratio',
                    'config_label': '音调',
                    'config_description': '调整语音音调高低',
                    'config_data_type': 'float',
                    'config_default_value': '1.0',
                    'config_validation_rules': '{"min": 0.5, "max": 2.0, "step": 0.1}',
                    'config_display_order': 3,
                    'config_is_required': False,
                    'config_group_name': '语音控制'
                },
                {
                    'config_name': '音频格式',
                    'config_type': 'tts_basic',
                    'config_category': 'basic',
                    'config_key': 'encoding',
                    'config_label': '音频格式',
                    'config_description': '选择输出音频格式',
                    'config_data_type': 'select',
                    'config_default_value': 'mp3',
                    'config_options': '{"options": [{"value": "mp3", "label": "MP3 - 推荐"}, {"value": "wav", "label": "WAV - 高质量"}, {"value": "ogg_opus", "label": "OGG Opus - 压缩"}, {"value": "pcm", "label": "PCM - 原始"}]}',
                    'config_display_order': 4,
                    'config_is_required': False,
                    'config_group_name': '输出设置'
                },
                {
                    'config_name': '采样率',
                    'config_type': 'tts_basic',
                    'config_category': 'basic',
                    'config_key': 'sample_rate',
                    'config_label': '采样率',
                    'config_description': '音频采样率，影响音质',
                    'config_data_type': 'select',
                    'config_default_value': '24000',
                    'config_options': '{"options": [{"value": "8000", "label": "8kHz - 电话质量"}, {"value": "16000", "label": "16kHz - 标准质量"}, {"value": "24000", "label": "24kHz - 高质量"}]}',
                    'config_display_order': 5,
                    'config_is_required': False,
                    'config_group_name': '输出设置'
                }
            ]
            
            # TTS合成高级设置配置
            tts_advanced_configs = [
                {
                    'config_name': '语种控制',
                    'config_type': 'tts_basic',
                    'config_category': 'advanced',
                    'config_key': 'explicit_language',
                    'config_label': '语种控制',
                    'config_description': '精确控制文本语种识别',
                    'config_data_type': 'select',
                    'config_default_value': 'zh',
                    'config_options': '{"options": [{"value": "", "label": "自动检测"}, {"value": "crosslingual", "label": "多语种混合"}, {"value": "zh", "label": "中文为主"}, {"value": "en", "label": "仅英文"}, {"value": "ja", "label": "仅日文"}, {"value": "es-mx", "label": "仅墨西哥语"}, {"value": "id", "label": "仅印尼语"}, {"value": "pt-br", "label": "仅巴西葡萄牙语"}]}',
                    'config_display_order': 1,
                    'config_is_required': False,
                    'config_group_name': '语言设置'
                },
                {
                    'config_name': '参考语种',
                    'config_type': 'tts_basic',
                    'config_category': 'advanced',
                    'config_key': 'context_language',
                    'config_label': '参考语种',
                    'config_description': '为西欧语种提供参考语言',
                    'config_data_type': 'select',
                    'config_default_value': '',
                    'config_options': '{"options": [{"value": "", "label": "默认(英语)"}, {"value": "id", "label": "印尼语参考"}, {"value": "es", "label": "西班牙语参考"}, {"value": "pt", "label": "葡萄牙语参考"}]}',
                    'config_display_order': 2,
                    'config_is_required': False,
                    'config_group_name': '语言设置'
                },
                {
                    'config_name': '文本类型',
                    'config_type': 'tts_basic',
                    'config_category': 'advanced',
                    'config_key': 'text_type',
                    'config_label': '文本类型',
                    'config_description': '文本标记语言类型',
                    'config_data_type': 'select',
                    'config_default_value': 'plain',
                    'config_options': '{"options": [{"value": "plain", "label": "纯文本"}, {"value": "ssml", "label": "SSML标记语言"}]}',
                    'config_display_order': 3,
                    'config_is_required': False,
                    'config_group_name': '文本处理'
                },
                {
                    'config_name': '时间戳',
                    'config_type': 'tts_basic',
                    'config_category': 'advanced',
                    'config_key': 'with_timestamp',
                    'config_label': '时间戳',
                    'config_description': '返回原文本的时间戳信息',
                    'config_data_type': 'boolean',
                    'config_default_value': 'false',
                    'config_display_order': 4,
                    'config_is_required': False,
                    'config_group_name': '输出选项'
                },
                {
                    'config_name': '分句处理',
                    'config_type': 'tts_basic',
                    'config_category': 'advanced',
                    'config_key': 'split_sentence',
                    'config_label': '分句处理',
                    'config_description': '针对1.0音色的语速优化(解决语速过快问题)',
                    'config_data_type': 'boolean',
                    'config_default_value': 'false',
                    'config_display_order': 5,
                    'config_is_required': False,
                    'config_group_name': '1.0音色优化'
                },
                {
                    'config_name': '启用缓存',
                    'config_type': 'tts_basic',
                    'config_category': 'advanced',
                    'config_key': 'cache_enabled',
                    'config_label': '启用缓存',
                    'config_description': '缓存相同文本的合成结果，提高响应速度',
                    'config_data_type': 'boolean',
                    'config_default_value': 'false',
                    'config_display_order': 6,
                    'config_is_required': False,
                    'config_group_name': '性能优化'
                },
                {
                    'config_name': '集群选择',
                    'config_type': 'tts_basic',
                    'config_category': 'advanced',
                    'config_key': 'cluster',
                    'config_label': '集群选择',
                    'config_description': '选择处理集群类型',
                    'config_data_type': 'select',
                    'config_default_value': 'volcano_icl',
                    'config_options': '{"options": [{"value": "volcano_icl", "label": "标准集群"}, {"value": "volcano_icl_concurr", "label": "并发集群"}]}',
                    'config_display_order': 7,
                    'config_is_required': False,
                    'config_group_name': '系统设置'
                }
            ]
            
            # 合并所有配置
            all_configs = (
                voice_clone_basic_configs + 
                voice_clone_advanced_configs + 
                tts_basic_configs + 
                tts_advanced_configs
            )
            
            # 插入配置数据
            for config in all_configs:
                insert_sql = """
                INSERT INTO volcano_api_config (
                    config_name, config_type, config_category, config_key, config_label,
                    config_description, config_data_type, config_default_value, config_options,
                    config_validation_rules, config_display_order, config_is_required,
                    config_is_visible, config_group_name
                ) VALUES (
                    :config_name, :config_type, :config_category, :config_key, :config_label,
                    :config_description, :config_data_type, :config_default_value, 
                    CAST(:config_options AS JSONB), CAST(:config_validation_rules AS JSONB),
                    :config_display_order, :config_is_required, :config_is_visible, :config_group_name
                )
                ON CONFLICT (config_key, config_type, config_category) DO NOTHING
                """
                
                await session.execute(insert_sql, {
                    **config,
                    'config_is_visible': True,
                    'config_options': config.get('config_options'),
                    'config_validation_rules': config.get('config_validation_rules')
                })
            
            await session.commit()
            print(f"Successfully initialized {len(all_configs)} Volcano API configuration entries.")
            
        except Exception as e:
            await session.rollback()
            print(f"Error initializing Volcano API configuration: {str(e)}")
            raise e
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_volcano_config_data())