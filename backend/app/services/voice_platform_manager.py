"""
Voice Platform Manager Service
语音平台统一管理服务 - [services][voice_platform][manager]
"""

from typing import Dict, Any, Optional, List, Union
from enum import Enum
from dataclasses import dataclass
import asyncio
import logging
from datetime import datetime, timedelta

from app.integrations.base import IntegrationBase, IntegrationResponse, IntegrationError
from app.integrations.volcano_enhanced import VolcanoEngineEnhanced
from app.integrations.azure import AzureIntegration
from app.integrations.openai import OpenAIIntegration


class VoicePlatformType(Enum):
    """
    语音平台类型枚举
    [services][voice_platform][manager][platform_type]
    """
    VOLCANO = "volcano"  # 火山引擎（豆包）
    AZURE = "azure"      # 微软Azure
    OPENAI = "openai"    # OpenAI
    ALIBABA = "alibaba"  # 阿里云
    BAIDU = "baidu"      # 百度
    TENCENT = "tencent"  # 腾讯云


@dataclass
class VoicePlatformConfig:
    """
    语音平台配置
    [services][voice_platform][manager][platform_config]
    """
    platform_type: VoicePlatformType
    platform_name: str
    platform_description: str
    is_enabled: bool
    api_config: Dict[str, Any]
    feature_support: Dict[str, bool]
    priority: int  # 优先级，数字越小优先级越高
    cost_per_minute: float  # 每分钟费用（用于成本优化）
    max_daily_requests: int  # 每日最大请求数


@dataclass
class VoicePlatformStatus:
    """
    语音平台状态
    [services][voice_platform][manager][platform_status]
    """
    platform_type: VoicePlatformType
    is_healthy: bool
    last_health_check: datetime
    response_time_ms: float
    error_rate: float
    daily_requests_used: int
    daily_requests_limit: int
    current_load: float  # 当前负载百分比


class VoicePlatformManager:
    """
    语音平台统一管理器
    [services][voice_platform][manager]
    """
    
    def __init__(self):
        """
        初始化平台管理器
        [services][voice_platform][manager][init]
        """
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        
        # 平台配置存储
        self.platform_configs: Dict[VoicePlatformType, VoicePlatformConfig] = {}
        self.platform_instances: Dict[VoicePlatformType, IntegrationBase] = {}
        self.platform_status: Dict[VoicePlatformType, VoicePlatformStatus] = {}
        
        # 负载均衡和故障转移配置
        self.health_check_interval = 300  # 5分钟健康检查
        self.auto_failover_enabled = True
        self.load_balance_enabled = True
        self.cost_optimization_enabled = True
        
        # 初始化默认配置
        self._voice_platform_manager_initialize_default_configs()
    
    def _voice_platform_manager_initialize_default_configs(self):
        """
        初始化默认平台配置
        [services][voice_platform][manager][initialize_default_configs]
        """
        # 火山引擎（豆包）配置
        volcano_config = VoicePlatformConfig(
            platform_type=VoicePlatformType.VOLCANO,
            platform_name="火山引擎（豆包）",
            platform_description="字节跳动火山引擎语音服务，支持高质量音色克隆和TTS",
            is_enabled=True,
            api_config={
                "app_id": "",
                "access_token": "",
                "cluster": "volcano_icl",
                "base_url": "https://openspeech.bytedance.com"
            },
            feature_support={
                "voice_clone": True,
                "tts_synthesis": True,
                "stream_tts": True,
                "ssml_support": True,
                "custom_voice": True,
                "batch_processing": True
            },
            priority=1,
            cost_per_minute=0.002,  # 假设费用
            max_daily_requests=10000
        )
        self.platform_configs[VoicePlatformType.VOLCANO] = volcano_config
        
        # Azure配置
        azure_config = VoicePlatformConfig(
            platform_type=VoicePlatformType.AZURE,
            platform_name="Microsoft Azure",
            platform_description="微软Azure认知服务语音功能",
            is_enabled=False,
            api_config={
                "subscription_key": "",
                "region": "eastus",
                "resource_name": "",
                "base_url": ""
            },
            feature_support={
                "voice_clone": True,
                "tts_synthesis": True,
                "stream_tts": True,
                "ssml_support": True,
                "custom_voice": True,
                "batch_processing": False
            },
            priority=2,
            cost_per_minute=0.004,
            max_daily_requests=5000
        )
        self.platform_configs[VoicePlatformType.AZURE] = azure_config
        
        # OpenAI配置
        openai_config = VoicePlatformConfig(
            platform_type=VoicePlatformType.OPENAI,
            platform_name="OpenAI",
            platform_description="OpenAI语音合成服务",
            is_enabled=False,
            api_config={
                "api_key": "",
                "base_url": "https://api.openai.com/v1",
                "model": "tts-1"
            },
            feature_support={
                "voice_clone": False,
                "tts_synthesis": True,
                "stream_tts": True,
                "ssml_support": False,
                "custom_voice": False,
                "batch_processing": False
            },
            priority=3,
            cost_per_minute=0.015,
            max_daily_requests=1000
        )
        self.platform_configs[VoicePlatformType.OPENAI] = openai_config
    
    async def voice_platform_manager_initialize_platform(
        self, 
        platform_type: VoicePlatformType
    ) -> bool:
        """
        初始化指定平台
        [services][voice_platform][manager][initialize_platform]
        """
        try:
            config = self.platform_configs.get(platform_type)
            if not config or not config.is_enabled:
                self.logger.warning(f"Platform {platform_type.value} is not enabled or configured")
                return False
            
            # 创建平台实例
            if platform_type == VoicePlatformType.VOLCANO:
                instance = VolcanoEngineEnhanced(config.api_config)
            elif platform_type == VoicePlatformType.AZURE:
                instance = AzureIntegration(config.api_config)
            elif platform_type == VoicePlatformType.OPENAI:
                instance = OpenAIIntegration(config.api_config)
            else:
                self.logger.error(f"Unsupported platform type: {platform_type.value}")
                return False
            
            # 初始化实例
            if await instance.integration_base_initialize():
                self.platform_instances[platform_type] = instance
                
                # 初始化状态
                self.platform_status[platform_type] = VoicePlatformStatus(
                    platform_type=platform_type,
                    is_healthy=True,
                    last_health_check=datetime.now(),
                    response_time_ms=0.0,
                    error_rate=0.0,
                    daily_requests_used=0,
                    daily_requests_limit=config.max_daily_requests,
                    current_load=0.0
                )
                
                self.logger.info(f"Platform {platform_type.value} initialized successfully")
                return True
            else:
                self.logger.error(f"Failed to initialize platform {platform_type.value}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error initializing platform {platform_type.value}: {str(e)}")
            return False
    
    async def voice_platform_manager_get_available_platforms(self) -> List[VoicePlatformConfig]:
        """
        获取可用平台列表
        [services][voice_platform][manager][get_available_platforms]
        """
        available_platforms = []
        
        for platform_type, config in self.platform_configs.items():
            if config.is_enabled and platform_type in self.platform_instances:
                status = self.platform_status.get(platform_type)
                if status and status.is_healthy:
                    available_platforms.append(config)
        
        # 按优先级排序
        available_platforms.sort(key=lambda x: x.priority)
        return available_platforms
    
    async def voice_platform_manager_select_best_platform(
        self,
        required_features: List[str],
        preferred_platform: Optional[VoicePlatformType] = None
    ) -> Optional[VoicePlatformType]:
        """
        选择最佳平台
        [services][voice_platform][manager][select_best_platform]
        """
        available_platforms = await self.voice_platform_manager_get_available_platforms()
        
        if not available_platforms:
            self.logger.warning("No available platforms found")
            return None
        
        # 如果指定了首选平台且可用，优先使用
        if preferred_platform:
            for config in available_platforms:
                if (config.platform_type == preferred_platform and 
                    self._voice_platform_manager_platform_supports_features(config, required_features)):
                    return preferred_platform
        
        # 筛选支持所需功能的平台
        suitable_platforms = [
            config for config in available_platforms
            if self._voice_platform_manager_platform_supports_features(config, required_features)
        ]
        
        if not suitable_platforms:
            self.logger.warning(f"No platforms support required features: {required_features}")
            return None
        
        # 智能选择逻辑
        if self.cost_optimization_enabled:
            # 成本优化：选择最便宜的平台
            return min(suitable_platforms, key=lambda x: x.cost_per_minute).platform_type
        elif self.load_balance_enabled:
            # 负载均衡：选择负载最低的平台
            return self._voice_platform_manager_select_lowest_load_platform(suitable_platforms)
        else:
            # 默认：按优先级选择
            return suitable_platforms[0].platform_type
    
    def _voice_platform_manager_platform_supports_features(
        self, 
        config: VoicePlatformConfig, 
        required_features: List[str]
    ) -> bool:
        """
        检查平台是否支持所需功能
        [services][voice_platform][manager][platform_supports_features]
        """
        for feature in required_features:
            if not config.feature_support.get(feature, False):
                return False
        return True
    
    def _voice_platform_manager_select_lowest_load_platform(
        self, 
        platforms: List[VoicePlatformConfig]
    ) -> VoicePlatformType:
        """
        选择负载最低的平台
        [services][voice_platform][manager][select_lowest_load_platform]
        """
        min_load = float('inf')
        selected_platform = platforms[0].platform_type
        
        for config in platforms:
            status = self.platform_status.get(config.platform_type)
            if status:
                load = status.current_load
                if load < min_load:
                    min_load = load
                    selected_platform = config.platform_type
        
        return selected_platform
    
    async def voice_platform_manager_get_platform_instance(
        self, 
        platform_type: VoicePlatformType
    ) -> Optional[IntegrationBase]:
        """
        获取平台实例
        [services][voice_platform][manager][get_platform_instance]
        """
        return self.platform_instances.get(platform_type)
    
    async def voice_platform_manager_health_check_all_platforms(self):
        """
        检查所有平台健康状态
        [services][voice_platform][manager][health_check_all_platforms]
        """
        tasks = []
        for platform_type in self.platform_instances.keys():
            task = asyncio.create_task(
                self._voice_platform_manager_health_check_single_platform(platform_type)
            )
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _voice_platform_manager_health_check_single_platform(
        self, 
        platform_type: VoicePlatformType
    ):
        """
        检查单个平台健康状态
        [services][voice_platform][manager][health_check_single_platform]
        """
        try:
            instance = self.platform_instances.get(platform_type)
            status = self.platform_status.get(platform_type)
            
            if not instance or not status:
                return
            
            start_time = datetime.now()
            health_response = await instance.integration_base_health_check()
            end_time = datetime.now()
            
            # 更新状态
            status.is_healthy = health_response
            status.last_health_check = end_time
            status.response_time_ms = (end_time - start_time).total_seconds() * 1000
            
            self.logger.debug(f"Health check for {platform_type.value}: {health_response}")
            
        except Exception as e:
            self.logger.error(f"Health check failed for {platform_type.value}: {str(e)}")
            if platform_type in self.platform_status:
                self.platform_status[platform_type].is_healthy = False
    
    async def voice_platform_manager_update_platform_config(
        self,
        platform_type: VoicePlatformType,
        new_config: Dict[str, Any]
    ) -> bool:
        """
        更新平台配置
        [services][voice_platform][manager][update_platform_config]
        """
        try:
            if platform_type not in self.platform_configs:
                self.logger.error(f"Platform {platform_type.value} not found")
                return False
            
            # 更新配置
            config = self.platform_configs[platform_type]
            for key, value in new_config.items():
                if hasattr(config, key):
                    setattr(config, key, value)
                elif key in config.api_config:
                    config.api_config[key] = value
            
            # 如果平台已初始化，重新初始化
            if platform_type in self.platform_instances:
                await self._voice_platform_manager_cleanup_platform(platform_type)
                await self.voice_platform_manager_initialize_platform(platform_type)
            
            self.logger.info(f"Platform {platform_type.value} config updated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update config for {platform_type.value}: {str(e)}")
            return False
    
    async def _voice_platform_manager_cleanup_platform(self, platform_type: VoicePlatformType):
        """
        清理平台实例
        [services][voice_platform][manager][cleanup_platform]
        """
        if platform_type in self.platform_instances:
            instance = self.platform_instances[platform_type]
            await instance.integration_base_cleanup()
            del self.platform_instances[platform_type]
        
        if platform_type in self.platform_status:
            del self.platform_status[platform_type]
    
    async def voice_platform_manager_get_platform_status_summary(self) -> Dict[str, Any]:
        """
        获取平台状态摘要
        [services][voice_platform][manager][get_platform_status_summary]
        """
        summary = {
            "total_platforms": len(self.platform_configs),
            "enabled_platforms": len([c for c in self.platform_configs.values() if c.is_enabled]),
            "healthy_platforms": len([s for s in self.platform_status.values() if s.is_healthy]),
            "platform_details": {}
        }
        
        for platform_type, config in self.platform_configs.items():
            status = self.platform_status.get(platform_type)
            
            summary["platform_details"][platform_type.value] = {
                "name": config.platform_name,
                "enabled": config.is_enabled,
                "healthy": status.is_healthy if status else False,
                "response_time_ms": status.response_time_ms if status else None,
                "features": list(config.feature_support.keys()),
                "priority": config.priority,
                "cost_per_minute": config.cost_per_minute
            }
        
        return summary
    
    async def voice_platform_manager_cleanup_all_platforms(self):
        """
        清理所有平台
        [services][voice_platform][manager][cleanup_all_platforms]
        """
        tasks = []
        for platform_type in list(self.platform_instances.keys()):
            task = asyncio.create_task(
                self._voice_platform_manager_cleanup_platform(platform_type)
            )
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        self.logger.info("All platforms cleaned up")


# 创建全局平台管理器实例
voice_platform_manager = VoicePlatformManager()