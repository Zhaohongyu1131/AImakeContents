"""
Volcano Enhanced Service
火山引擎增强服务 - [services][volcano_enhanced_service]
"""

from typing import Dict, Any, Optional, List, AsyncGenerator
from app.integrations.volcano_enhanced import VolcanoEngineEnhanced
from app.integrations.base import IntegrationResponse
from app.config.settings import settings


class VolcanoEnhancedService:
    """
    火山引擎增强服务
    [services][volcano_enhanced_service]
    """
    
    def __init__(self):
        """
        初始化火山引擎增强服务
        [services][volcano_enhanced_service][init]
        """
        self.volcano_config = {
            "appid": settings.VOLCANO_VOICE_APPID,
            "access_token": settings.VOLCANO_VOICE_ACCESS_TOKEN,
            "cluster": settings.VOLCANO_VOICE_CLUSTER
        }
        self.volcano_engine = VolcanoEngineEnhanced(self.volcano_config)
    
    async def test_connection(self) -> IntegrationResponse:
        """
        测试火山引擎连接
        [services][volcano_enhanced_service][test_connection]
        """
        return await self.volcano_engine.test_connection()
    
    async def get_service_info(self) -> IntegrationResponse:
        """
        获取服务信息
        [services][volcano_enhanced_service][get_service_info]
        """
        return await self.volcano_engine.get_service_info()
    
    async def volcano_upload_voice_clone(
        self,
        speaker_id: str,
        audio_data: bytes,
        audio_format: str = "wav",
        language: int = 0,
        model_type: int = 1,
        reference_text: Optional[str] = None
    ) -> IntegrationResponse:
        """
        上传音频进行音色克隆
        [services][volcano_enhanced_service][upload_voice_clone]
        """
        return await self.volcano_engine.volcano_upload_voice_clone(
            speaker_id=speaker_id,
            audio_data=audio_data,
            audio_format=audio_format,
            language=language,
            model_type=model_type,
            reference_text=reference_text
        )
    
    async def volcano_check_speaker_status(self, speaker_id: str) -> IntegrationResponse:
        """
        检查音色状态
        [services][volcano_enhanced_service][check_speaker_status]
        """
        return await self.volcano_engine.volcano_check_speaker_status(speaker_id)
    
    async def volcano_list_speaker_status(
        self,
        speaker_ids: Optional[List[str]] = None
    ) -> IntegrationResponse:
        """
        批量获取音色状态
        [services][volcano_enhanced_service][list_speaker_status]
        """
        return await self.volcano_engine.volcano_list_speaker_status(speaker_ids)
    
    async def volcano_text_to_speech_http(
        self,
        text: str,
        voice_type: str,
        encoding: str = "mp3",
        speed_ratio: float = 1.0,
        volume_ratio: float = 1.0,
        pitch_ratio: float = 1.0,
        sample_rate: int = 24000,
        **kwargs
    ) -> IntegrationResponse:
        """
        HTTP文本转语音
        [services][volcano_enhanced_service][text_to_speech_http]
        """
        return await self.volcano_engine.volcano_text_to_speech_http(
            text=text,
            voice_type=voice_type,
            encoding=encoding,
            speed_ratio=speed_ratio,
            volume_ratio=volume_ratio,
            pitch_ratio=pitch_ratio,
            sample_rate=sample_rate,
            **kwargs
        )
    
    async def volcano_text_to_speech_websocket(
        self,
        text: str,
        voice_type: str,
        encoding: str = "mp3",
        speed_ratio: float = 1.0,
        volume_ratio: float = 1.0,
        pitch_ratio: float = 1.0,
        sample_rate: int = 24000,
        **kwargs
    ) -> AsyncGenerator[IntegrationResponse, None]:
        """
        WebSocket流式文本转语音
        [services][volcano_enhanced_service][text_to_speech_websocket]
        """
        async for response in self.volcano_engine.volcano_text_to_speech_websocket(
            text=text,
            voice_type=voice_type,
            encoding=encoding,
            speed_ratio=speed_ratio,
            volume_ratio=volume_ratio,
            pitch_ratio=pitch_ratio,
            sample_rate=sample_rate,
            **kwargs
        ):
            yield response
    
    async def volcano_health_check(self) -> IntegrationResponse:
        """
        健康检查
        [services][volcano_enhanced_service][health_check]
        """
        return await self.volcano_engine.volcano_health_check()
    
    async def get_usage_stats(self) -> IntegrationResponse:
        """
        获取使用统计
        [services][volcano_enhanced_service][get_usage_stats]
        """
        return await self.volcano_engine.volcano_get_usage_stats()