"""
Voice Service Unified
统一语音服务接口 - [services][voice_service][unified]
"""

from typing import Dict, Any, Optional, List, Union, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
from datetime import datetime
import uuid

from app.services.voice_platform_manager import (
    VoicePlatformManager, 
    VoicePlatformType, 
    voice_platform_manager
)
from app.integrations.base import IntegrationResponse, IntegrationError


class VoiceOperationType(Enum):
    """
    语音操作类型枚举
    [services][voice_service][unified][operation_type]
    """
    VOICE_CLONE = "voice_clone"          # 音色克隆
    TTS_SYNTHESIS = "tts_synthesis"      # 文本转语音
    TTS_STREAM = "tts_stream"           # 流式TTS
    VOICE_ANALYSIS = "voice_analysis"    # 音色分析
    VOICE_TEST = "voice_test"           # 音色测试


@dataclass
class VoiceCloneRequest:
    """
    音色克隆请求
    [services][voice_service][unified][voice_clone_request]
    """
    user_id: int
    timbre_name: str
    timbre_description: Optional[str]
    audio_data: bytes
    audio_format: str
    language: str
    model_type: Optional[str] = None
    reference_text: Optional[str] = None
    advanced_params: Optional[Dict[str, Any]] = None
    preferred_platform: Optional[VoicePlatformType] = None


@dataclass
class TTSRequest:
    """
    TTS合成请求
    [services][voice_service][unified][tts_request]
    """
    user_id: int
    text: str
    voice_id: str  # 可以是平台音色ID或自定义音色ID
    language: Optional[str] = None
    speed_ratio: float = 1.0
    volume_ratio: float = 1.0
    pitch_ratio: float = 1.0
    audio_format: str = "mp3"
    sample_rate: int = 24000
    use_ssml: bool = False
    streaming: bool = False
    advanced_params: Optional[Dict[str, Any]] = None
    preferred_platform: Optional[VoicePlatformType] = None


@dataclass
class VoiceOperationResult:
    """
    语音操作结果
    [services][voice_service][unified][operation_result]
    """
    success: bool
    operation_id: str
    operation_type: VoiceOperationType
    platform_used: VoicePlatformType
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_time_ms: float = 0.0
    metadata: Optional[Dict[str, Any]] = None


class VoiceServiceUnified:
    """
    统一语音服务接口
    [services][voice_service][unified]
    """
    
    def __init__(self, platform_manager: VoicePlatformManager):
        """
        初始化统一语音服务
        [services][voice_service][unified][init]
        """
        self.platform_manager = platform_manager
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        
        # 操作历史记录（简单内存存储，生产环境应使用数据库）
        self.operation_history: Dict[str, VoiceOperationResult] = {}
        
        # 平台功能映射
        self.operation_required_features = {
            VoiceOperationType.VOICE_CLONE: ["voice_clone"],
            VoiceOperationType.TTS_SYNTHESIS: ["tts_synthesis"],
            VoiceOperationType.TTS_STREAM: ["stream_tts"],
            VoiceOperationType.VOICE_ANALYSIS: ["voice_clone"],
            VoiceOperationType.VOICE_TEST: ["tts_synthesis"]
        }
    
    async def voice_service_unified_clone_voice(
        self, 
        request: VoiceCloneRequest
    ) -> VoiceOperationResult:
        """
        统一音色克隆接口
        [services][voice_service][unified][clone_voice]
        """
        operation_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # 选择最佳平台
            required_features = self.operation_required_features[VoiceOperationType.VOICE_CLONE]
            selected_platform = await self.platform_manager.voice_platform_manager_select_best_platform(
                required_features=required_features,
                preferred_platform=request.preferred_platform
            )
            
            if not selected_platform:
                error_msg = "No available platform supports voice cloning"
                self.logger.error(error_msg)
                return VoiceOperationResult(
                    success=False,
                    operation_id=operation_id,
                    operation_type=VoiceOperationType.VOICE_CLONE,
                    platform_used=selected_platform or VoicePlatformType.VOLCANO,
                    error_message=error_msg
                )
            
            # 获取平台实例
            platform_instance = await self.platform_manager.voice_platform_manager_get_platform_instance(
                selected_platform
            )
            
            if not platform_instance:
                error_msg = f"Platform {selected_platform.value} instance not available"
                self.logger.error(error_msg)
                return VoiceOperationResult(
                    success=False,
                    operation_id=operation_id,
                    operation_type=VoiceOperationType.VOICE_CLONE,
                    platform_used=selected_platform,
                    error_message=error_msg
                )
            
            # 执行音色克隆
            clone_result = await self._voice_service_unified_execute_voice_clone(
                platform_instance, request, selected_platform
            )
            
            # 计算处理时间
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds() * 1000
            
            # 创建结果对象
            result = VoiceOperationResult(
                success=clone_result.success,
                operation_id=operation_id,
                operation_type=VoiceOperationType.VOICE_CLONE,
                platform_used=selected_platform,
                result_data=clone_result.data if clone_result.success else None,
                error_message=clone_result.error.message if clone_result.error else None,
                processing_time_ms=processing_time,
                metadata={
                    "user_id": request.user_id,
                    "timbre_name": request.timbre_name,
                    "audio_format": request.audio_format,
                    "language": request.language
                }
            )
            
            # 记录操作历史
            self.operation_history[operation_id] = result
            
            return result
            
        except Exception as e:
            self.logger.error(f"Voice clone operation failed: {str(e)}")
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds() * 1000
            
            return VoiceOperationResult(
                success=False,
                operation_id=operation_id,
                operation_type=VoiceOperationType.VOICE_CLONE,
                platform_used=selected_platform or VoicePlatformType.VOLCANO,
                error_message=f"Internal error: {str(e)}",
                processing_time_ms=processing_time
            )
    
    async def _voice_service_unified_execute_voice_clone(
        self,
        platform_instance,
        request: VoiceCloneRequest,
        platform_type: VoicePlatformType
    ) -> IntegrationResponse:
        """
        执行平台特定的音色克隆
        [services][voice_service][unified][execute_voice_clone]
        """
        try:
            if platform_type == VoicePlatformType.VOLCANO:
                # 火山引擎音色克隆
                return await platform_instance.volcano_upload_voice_clone(
                    speaker_id=f"user_{request.user_id}_{request.timbre_name}",
                    audio_data=request.audio_data,
                    audio_format=request.audio_format,
                    language=self._voice_service_unified_convert_language_code(request.language, platform_type),
                    model_type=int(request.model_type) if request.model_type else 1,
                    reference_text=request.reference_text
                )
            elif platform_type == VoicePlatformType.AZURE:
                # Azure音色克隆（需要实现）
                return await platform_instance.azure_create_custom_voice(
                    voice_name=request.timbre_name,
                    audio_data=request.audio_data,
                    language=request.language,
                    description=request.timbre_description
                )
            elif platform_type == VoicePlatformType.OPENAI:
                # OpenAI不支持音色克隆
                return IntegrationResponse.error_response(
                    IntegrationError(
                        code="FEATURE_NOT_SUPPORTED",
                        message="OpenAI does not support voice cloning"
                    )
                )
            else:
                return IntegrationResponse.error_response(
                    IntegrationError(
                        code="PLATFORM_NOT_SUPPORTED",
                        message=f"Platform {platform_type.value} not supported for voice cloning"
                    )
                )
                
        except Exception as e:
            return IntegrationResponse.error_response(
                IntegrationError(
                    code="PLATFORM_EXECUTION_ERROR",
                    message=f"Platform execution failed: {str(e)}"
                )
            )
    
    async def voice_service_unified_synthesize_speech(
        self, 
        request: TTSRequest
    ) -> VoiceOperationResult:
        """
        统一TTS合成接口
        [services][voice_service][unified][synthesize_speech]
        """
        operation_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # 选择最佳平台
            operation_type = VoiceOperationType.TTS_STREAM if request.streaming else VoiceOperationType.TTS_SYNTHESIS
            required_features = self.operation_required_features[operation_type]
            
            selected_platform = await self.platform_manager.voice_platform_manager_select_best_platform(
                required_features=required_features,
                preferred_platform=request.preferred_platform
            )
            
            if not selected_platform:
                error_msg = "No available platform supports TTS synthesis"
                self.logger.error(error_msg)
                return VoiceOperationResult(
                    success=False,
                    operation_id=operation_id,
                    operation_type=operation_type,
                    platform_used=selected_platform or VoicePlatformType.VOLCANO,
                    error_message=error_msg
                )
            
            # 获取平台实例
            platform_instance = await self.platform_manager.voice_platform_manager_get_platform_instance(
                selected_platform
            )
            
            if not platform_instance:
                error_msg = f"Platform {selected_platform.value} instance not available"
                self.logger.error(error_msg)
                return VoiceOperationResult(
                    success=False,
                    operation_id=operation_id,
                    operation_type=operation_type,
                    platform_used=selected_platform,
                    error_message=error_msg
                )
            
            # 执行TTS合成
            if request.streaming:
                tts_result = await self._voice_service_unified_execute_stream_tts(
                    platform_instance, request, selected_platform
                )
            else:
                tts_result = await self._voice_service_unified_execute_tts_synthesis(
                    platform_instance, request, selected_platform
                )
            
            # 计算处理时间
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds() * 1000
            
            # 创建结果对象
            result = VoiceOperationResult(
                success=tts_result.success,
                operation_id=operation_id,
                operation_type=operation_type,
                platform_used=selected_platform,
                result_data=tts_result.data if tts_result.success else None,
                error_message=tts_result.error.message if tts_result.error else None,
                processing_time_ms=processing_time,
                metadata={
                    "user_id": request.user_id,
                    "text_length": len(request.text),
                    "voice_id": request.voice_id,
                    "audio_format": request.audio_format,
                    "streaming": request.streaming
                }
            )
            
            # 记录操作历史
            self.operation_history[operation_id] = result
            
            return result
            
        except Exception as e:
            self.logger.error(f"TTS synthesis operation failed: {str(e)}")
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds() * 1000
            
            return VoiceOperationResult(
                success=False,
                operation_id=operation_id,
                operation_type=operation_type,
                platform_used=selected_platform or VoicePlatformType.VOLCANO,
                error_message=f"Internal error: {str(e)}",
                processing_time_ms=processing_time
            )
    
    async def _voice_service_unified_execute_tts_synthesis(
        self,
        platform_instance,
        request: TTSRequest,
        platform_type: VoicePlatformType
    ) -> IntegrationResponse:
        """
        执行平台特定的TTS合成
        [services][voice_service][unified][execute_tts_synthesis]
        """
        try:
            if platform_type == VoicePlatformType.VOLCANO:
                # 火山引擎TTS
                return await platform_instance.volcano_text_to_speech(
                    text=request.text,
                    voice_type=request.voice_id,
                    encoding=request.audio_format,
                    speed_ratio=request.speed_ratio,
                    volume_ratio=request.volume_ratio,
                    pitch_ratio=request.pitch_ratio,
                    sample_rate=request.sample_rate,
                    language=self._voice_service_unified_convert_language_code(request.language, platform_type),
                    text_type="ssml" if request.use_ssml else "plain"
                )
            elif platform_type == VoicePlatformType.AZURE:
                # Azure TTS
                return await platform_instance.azure_synthesize_speech(
                    text=request.text,
                    voice_name=request.voice_id,
                    output_format=request.audio_format,
                    rate=request.speed_ratio,
                    volume=request.volume_ratio,
                    pitch=request.pitch_ratio
                )
            elif platform_type == VoicePlatformType.OPENAI:
                # OpenAI TTS
                return await platform_instance.openai_create_speech(
                    text=request.text,
                    voice=request.voice_id,
                    model="tts-1",
                    response_format=request.audio_format,
                    speed=request.speed_ratio
                )
            else:
                return IntegrationResponse.error_response(
                    IntegrationError(
                        code="PLATFORM_NOT_SUPPORTED",
                        message=f"Platform {platform_type.value} not supported for TTS"
                    )
                )
                
        except Exception as e:
            return IntegrationResponse.error_response(
                IntegrationError(
                    code="PLATFORM_EXECUTION_ERROR",
                    message=f"Platform execution failed: {str(e)}"
                )
            )
    
    async def _voice_service_unified_execute_stream_tts(
        self,
        platform_instance,
        request: TTSRequest,
        platform_type: VoicePlatformType
    ) -> IntegrationResponse:
        """
        执行平台特定的流式TTS
        [services][voice_service][unified][execute_stream_tts]
        """
        try:
            if platform_type == VoicePlatformType.VOLCANO:
                # 火山引擎流式TTS
                stream_generator = platform_instance.volcano_text_to_speech_websocket(
                    text=request.text,
                    voice_type=request.voice_id,
                    encoding=request.audio_format,
                    speed_ratio=request.speed_ratio,
                    volume_ratio=request.volume_ratio,
                    pitch_ratio=request.pitch_ratio,
                    sample_rate=request.sample_rate
                )
                
                # 收集流式数据
                audio_chunks = []
                async for chunk in stream_generator:
                    if chunk.success and chunk.data:
                        audio_chunks.append(chunk.data.get('audio_data', b''))
                
                # 合并音频数据
                complete_audio = b''.join(audio_chunks)
                return IntegrationResponse.success_response({
                    "audio_data": complete_audio,
                    "format": request.audio_format,
                    "sample_rate": request.sample_rate,
                    "streaming": True
                })
                
            else:
                # 对于不支持流式的平台，降级到普通TTS
                return await self._voice_service_unified_execute_tts_synthesis(
                    platform_instance, request, platform_type
                )
                
        except Exception as e:
            return IntegrationResponse.error_response(
                IntegrationError(
                    code="STREAM_EXECUTION_ERROR",
                    message=f"Stream TTS execution failed: {str(e)}"
                )
            )
    
    def _voice_service_unified_convert_language_code(
        self, 
        language: Optional[str], 
        platform_type: VoicePlatformType
    ) -> str:
        """
        转换语言代码适配不同平台
        [services][voice_service][unified][convert_language_code]
        """
        if not language:
            return "zh-CN"  # 默认中文
        
        # 标准化语言代码映射
        language_mapping = {
            VoicePlatformType.VOLCANO: {
                "zh": "zh-CN",
                "zh-CN": "zh-CN",
                "en": "en-US",
                "en-US": "en-US",
                "ja": "ja-JP",
                "ja-JP": "ja-JP"
            },
            VoicePlatformType.AZURE: {
                "zh": "zh-CN",
                "zh-CN": "zh-CN",
                "en": "en-US",
                "en-US": "en-US",
                "ja": "ja-JP",
                "ja-JP": "ja-JP"
            },
            VoicePlatformType.OPENAI: {
                "zh": "zh",
                "zh-CN": "zh",
                "en": "en",
                "en-US": "en",
                "ja": "ja",
                "ja-JP": "ja"
            }
        }
        
        platform_mapping = language_mapping.get(platform_type, {})
        return platform_mapping.get(language, language)
    
    async def voice_service_unified_get_operation_status(
        self, 
        operation_id: str
    ) -> Optional[VoiceOperationResult]:
        """
        获取操作状态
        [services][voice_service][unified][get_operation_status]
        """
        return self.operation_history.get(operation_id)
    
    async def voice_service_unified_get_available_voices(
        self, 
        platform_type: Optional[VoicePlatformType] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取可用音色列表
        [services][voice_service][unified][get_available_voices]
        """
        result = {}
        
        if platform_type:
            platforms = [platform_type]
        else:
            # 获取所有可用平台
            available_configs = await self.platform_manager.voice_platform_manager_get_available_platforms()
            platforms = [config.platform_type for config in available_configs]
        
        for platform in platforms:
            platform_instance = await self.platform_manager.voice_platform_manager_get_platform_instance(platform)
            if platform_instance:
                try:
                    # 这里需要各平台实现获取音色列表的方法
                    voices_response = await platform_instance.get_available_voices()
                    if voices_response.success:
                        result[platform.value] = voices_response.data.get("voices", [])
                    else:
                        result[platform.value] = []
                except Exception as e:
                    self.logger.error(f"Failed to get voices from {platform.value}: {str(e)}")
                    result[platform.value] = []
        
        return result
    
    async def voice_service_unified_get_platform_statistics(self) -> Dict[str, Any]:
        """
        获取平台使用统计
        [services][voice_service][unified][get_platform_statistics]
        """
        total_operations = len(self.operation_history)
        successful_operations = len([op for op in self.operation_history.values() if op.success])
        
        platform_usage = {}
        operation_type_counts = {}
        
        for operation in self.operation_history.values():
            # 平台使用统计
            platform = operation.platform_used.value
            if platform not in platform_usage:
                platform_usage[platform] = {"total": 0, "successful": 0, "failed": 0}
            
            platform_usage[platform]["total"] += 1
            if operation.success:
                platform_usage[platform]["successful"] += 1
            else:
                platform_usage[platform]["failed"] += 1
            
            # 操作类型统计
            op_type = operation.operation_type.value
            if op_type not in operation_type_counts:
                operation_type_counts[op_type] = 0
            operation_type_counts[op_type] += 1
        
        return {
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "success_rate": successful_operations / total_operations if total_operations > 0 else 0,
            "platform_usage": platform_usage,
            "operation_type_counts": operation_type_counts,
            "platform_status": await self.platform_manager.voice_platform_manager_get_platform_status_summary()
        }


# 创建全局统一语音服务实例
voice_service_unified = VoiceServiceUnified(voice_platform_manager)