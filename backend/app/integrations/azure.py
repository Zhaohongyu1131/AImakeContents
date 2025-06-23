"""
Azure Cognitive Services Integration
Azure认知服务集成 - [integrations][azure]
"""

from typing import Dict, Any, Optional, List
import base64
import json
from datetime import datetime
from app.integrations.base import IntegrationBase, IntegrationResponse, IntegrationError


class AzureIntegration(IntegrationBase):
    """
    Azure认知服务集成
    [integrations][azure]
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化Azure集成
        [integrations][azure][init]
        """
        super().__init__(config)
        
        # Azure特定配置
        self.subscription_key = config.get("subscription_key", "")
        self.region = config.get("region", "eastus")
        self.resource_name = config.get("resource_name", "")
        
        # API端点
        self.base_url = f"https://{self.region}.tts.speech.microsoft.com"
        self.tts_endpoint = "/cognitiveservices/v1"
        self.voices_endpoint = "/cognitiveservices/voices/list"
        self.custom_voice_endpoint = "/cognitiveservices/customvoice/v1.0"
        
        # 支持的语言和格式
        self.supported_languages = [
            "zh-CN", "zh-TW", "en-US", "en-GB", "ja-JP", 
            "ko-KR", "fr-FR", "de-DE", "es-ES", "it-IT"
        ]
        self.supported_formats = [
            "audio-16khz-32kbitrate-mono-mp3",
            "audio-16khz-64kbitrate-mono-mp3", 
            "audio-16khz-128kbitrate-mono-mp3",
            "audio-24khz-48kbitrate-mono-mp3",
            "audio-24khz-96kbitrate-mono-mp3",
            "audio-24khz-160kbitrate-mono-mp3",
            "riff-16khz-16bit-mono-pcm",
            "riff-24khz-16bit-mono-pcm"
        ]
    
    def _get_default_headers(self) -> Dict[str, str]:
        """
        获取Azure默认请求头
        [integrations][azure][_get_default_headers]
        """
        headers = {
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-16khz-32kbitrate-mono-mp3",
            "User-Agent": "DataSay-Azure-TTS"
        }
        return headers
    
    async def test_connection(self) -> IntegrationResponse:
        """
        测试Azure连接
        [integrations][azure][test_connection]
        """
        try:
            # 通过获取音色列表测试连接
            response = await self.azure_list_voices()
            
            if response.success:
                return IntegrationResponse.success_response({
                    "status": "connected",
                    "service": "azure_cognitive_services",
                    "message": "Connection test successful",
                    "region": self.region
                })
            else:
                return response
                
        except Exception as e:
            error = IntegrationError(
                code="CONNECTION_TEST_FAILED",
                message=f"Azure connection test failed: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
    async def get_service_info(self) -> IntegrationResponse:
        """
        获取Azure服务信息
        [integrations][azure][get_service_info]
        """
        try:
            service_info = {
                "service_name": "Azure Cognitive Services TTS",
                "provider": "Microsoft",
                "version": "v1",
                "features": [
                    "text_to_speech",
                    "neural_voices",
                    "custom_voices",
                    "ssml_support",
                    "voice_tuning"
                ],
                "supported_languages": self.supported_languages,
                "supported_formats": self.supported_formats,
                "region": self.region,
                "endpoints": {
                    "tts": f"{self.base_url}{self.tts_endpoint}",
                    "voices": f"{self.base_url}{self.voices_endpoint}",
                    "custom_voice": f"{self.base_url}{self.custom_voice_endpoint}"
                }
            }
            
            return IntegrationResponse.success_response(service_info)
            
        except Exception as e:
            error = IntegrationError(
                code="SERVICE_INFO_ERROR",
                message=f"Failed to get service info: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
    async def azure_text_to_speech(
        self,
        text: str,
        voice_name: str = "zh-CN-XiaoxiaoNeural",
        language: str = "zh-CN",
        output_format: str = "audio-16khz-32kbitrate-mono-mp3",
        **kwargs
    ) -> IntegrationResponse:
        """
        Azure文本转语音
        [integrations][azure][text_to_speech]
        """
        try:
            # 构建SSML
            ssml = self._build_ssml(text, voice_name, language, **kwargs)
            
            # 设置输出格式
            headers = self._get_default_headers()
            headers["X-Microsoft-OutputFormat"] = output_format
            
            # 发送TTS请求
            response = await self._make_request(
                "POST", 
                self.tts_endpoint,
                data=ssml,
                headers=headers
            )
            
            if response.success and response.data:
                # Azure返回的是音频数据
                audio_data = response.data.get("content", "")
                
                return IntegrationResponse.success_response({
                    "audio_data": audio_data,
                    "format": output_format,
                    "voice_name": voice_name,
                    "language": language,
                    "text_length": len(text),
                    "encoding": "base64" if isinstance(audio_data, str) else "binary"
                })
            else:
                return response
                
        except Exception as e:
            error = IntegrationError(
                code="TTS_ERROR",
                message=f"Azure TTS failed: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
    async def azure_list_voices(self, language: Optional[str] = None) -> IntegrationResponse:
        """
        获取Azure音色列表
        [integrations][azure][list_voices]
        """
        try:
            headers = {
                "Ocp-Apim-Subscription-Key": self.subscription_key
            }
            
            response = await self._make_request(
                "GET",
                self.voices_endpoint,
                headers=headers
            )
            
            if response.success and response.data:
                voices = response.data
                
                # 过滤指定语言的音色
                if language:
                    voices = [
                        voice for voice in voices 
                        if voice.get("Locale", "").startswith(language)
                    ]
                
                return IntegrationResponse.success_response({
                    "voices": voices,
                    "total_count": len(voices),
                    "filtered_language": language
                })
            else:
                return response
                
        except Exception as e:
            error = IntegrationError(
                code="LIST_VOICES_ERROR",
                message=f"Failed to list Azure voices: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
    async def azure_create_custom_voice(
        self,
        voice_name: str,
        description: str,
        audio_files: List[Dict[str, Any]],
        language: str = "zh-CN",
        **kwargs
    ) -> IntegrationResponse:
        """
        创建自定义音色
        [integrations][azure][create_custom_voice]
        """
        try:
            # 构建自定义音色创建请求
            custom_voice_data = {
                "name": voice_name,
                "description": description,
                "locale": language,
                "kind": "TextToSpeech",
                "properties": {
                    "Gender": kwargs.get("gender", "Female"),
                    "VoiceType": kwargs.get("voice_type", "NeuralVoice")
                },
                "datasets": []
            }
            
            # 添加音频数据集
            for audio_file in audio_files:
                dataset = {
                    "name": audio_file.get("name"),
                    "description": audio_file.get("description", ""),
                    "kind": "Acoustic",
                    "data": {
                        "audioData": audio_file.get("audio_data"),
                        "script": audio_file.get("transcript", "")
                    }
                }
                custom_voice_data["datasets"].append(dataset)
            
            headers = {
                "Ocp-Apim-Subscription-Key": self.subscription_key,
                "Content-Type": "application/json"
            }
            
            response = await self._make_request(
                "POST",
                f"{self.custom_voice_endpoint}/models",
                data=custom_voice_data,
                headers=headers
            )
            
            if response.success and response.data:
                result_data = response.data
                
                return IntegrationResponse.success_response({
                    "voice_id": result_data.get("id"),
                    "voice_name": voice_name,
                    "status": result_data.get("status", "NotStarted"),
                    "created_time": result_data.get("createdDateTime"),
                    "locale": language,
                    "model_kind": result_data.get("kind")
                })
            else:
                return response
                
        except Exception as e:
            error = IntegrationError(
                code="CUSTOM_VOICE_ERROR",
                message=f"Azure custom voice creation failed: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
    async def azure_get_custom_voice_status(self, voice_id: str) -> IntegrationResponse:
        """
        获取自定义音色状态
        [integrations][azure][get_custom_voice_status]
        """
        try:
            headers = {
                "Ocp-Apim-Subscription-Key": self.subscription_key
            }
            
            response = await self._make_request(
                "GET",
                f"{self.custom_voice_endpoint}/models/{voice_id}",
                headers=headers
            )
            
            if response.success and response.data:
                result_data = response.data
                
                return IntegrationResponse.success_response({
                    "voice_id": voice_id,
                    "status": result_data.get("status"),
                    "name": result_data.get("name"),
                    "locale": result_data.get("locale"),
                    "created_time": result_data.get("createdDateTime"),
                    "last_action_time": result_data.get("lastActionDateTime"),
                    "error_message": result_data.get("error", {}).get("message")
                })
            else:
                return response
                
        except Exception as e:
            error = IntegrationError(
                code="VOICE_STATUS_ERROR",
                message=f"Failed to get custom voice status: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
    async def azure_list_custom_voices(self) -> IntegrationResponse:
        """
        获取自定义音色列表
        [integrations][azure][list_custom_voices]
        """
        try:
            headers = {
                "Ocp-Apim-Subscription-Key": self.subscription_key
            }
            
            response = await self._make_request(
                "GET",
                f"{self.custom_voice_endpoint}/models",
                headers=headers
            )
            
            if response.success and response.data:
                voices = response.data
                
                return IntegrationResponse.success_response({
                    "custom_voices": voices,
                    "total_count": len(voices)
                })
            else:
                return response
                
        except Exception as e:
            error = IntegrationError(
                code="LIST_CUSTOM_VOICES_ERROR",
                message=f"Failed to list custom voices: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
    async def azure_speech_synthesis_markup(
        self,
        ssml: str,
        output_format: str = "audio-16khz-32kbitrate-mono-mp3"
    ) -> IntegrationResponse:
        """
        使用SSML进行语音合成
        [integrations][azure][speech_synthesis_markup]
        """
        try:
            headers = self._get_default_headers()
            headers["X-Microsoft-OutputFormat"] = output_format
            headers["Content-Type"] = "application/ssml+xml"
            
            response = await self._make_request(
                "POST",
                self.tts_endpoint,
                data=ssml,
                headers=headers
            )
            
            if response.success and response.data:
                return IntegrationResponse.success_response({
                    "audio_data": response.data.get("content"),
                    "format": output_format,
                    "ssml_length": len(ssml)
                })
            else:
                return response
                
        except Exception as e:
            error = IntegrationError(
                code="SSML_SYNTHESIS_ERROR",
                message=f"SSML synthesis failed: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
    def _build_ssml(
        self,
        text: str,
        voice_name: str,
        language: str,
        **kwargs
    ) -> str:
        """
        构建SSML文档
        [integrations][azure][_build_ssml]
        """
        # 语音参数
        rate = kwargs.get("rate", "0%")
        pitch = kwargs.get("pitch", "0%")
        volume = kwargs.get("volume", "0%")
        style = kwargs.get("style", "")
        style_degree = kwargs.get("style_degree", "1.0")
        
        # 构建SSML
        ssml_parts = [
            '<speak version="1.0"',
            f' xmlns="http://www.w3.org/2001/10/synthesis"',
            f' xmlns:mstts="https://www.w3.org/2001/mstts"',
            f' xml:lang="{language}">',
            f'<voice name="{voice_name}">'
        ]
        
        # 添加风格（如果支持）
        if style and "Neural" in voice_name:
            ssml_parts.extend([
                f'<mstts:express-as style="{style}" styledegree="{style_degree}">',
            ])
        
        # 添加语音调节
        ssml_parts.extend([
            f'<prosody rate="{rate}" pitch="{pitch}" volume="{volume}">',
            text,
            '</prosody>'
        ])
        
        # 关闭标签
        if style and "Neural" in voice_name:
            ssml_parts.append('</mstts:express-as>')
        
        ssml_parts.extend([
            '</voice>',
            '</speak>'
        ])
        
        return ''.join(ssml_parts)
    
    async def azure_get_subscription_info(self) -> IntegrationResponse:
        """
        获取订阅信息
        [integrations][azure][get_subscription_info]
        """
        try:
            headers = {
                "Ocp-Apim-Subscription-Key": self.subscription_key
            }
            
            # Azure没有直接的订阅信息API，这里模拟返回基本信息
            return IntegrationResponse.success_response({
                "subscription_key": self.subscription_key[:8] + "***",
                "region": self.region,
                "service_name": "Speech Services",
                "status": "active"
            })
            
        except Exception as e:
            error = IntegrationError(
                code="SUBSCRIPTION_INFO_ERROR",
                message=f"Failed to get subscription info: {str(e)}"
            )
            return IntegrationResponse.error_response(error)