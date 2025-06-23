"""
Volcano Engine Integration
火山引擎集成服务 - [integrations][volcano]
"""

from typing import Dict, Any, Optional, List
import base64
import hashlib
import hmac
import json
from datetime import datetime
from app.integrations.base import IntegrationBase, IntegrationResponse, IntegrationError


class VolcanoEngineIntegration(IntegrationBase):
    """
    火山引擎集成服务
    [integrations][volcano]
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化火山引擎集成
        [integrations][volcano][init]
        """
        super().__init__(config)
        
        # 火山引擎特定配置
        self.app_id = config.get("app_id", "")
        self.access_token = config.get("access_token", "")
        self.cluster = config.get("cluster", "volcano_icl")
        self.secret_key = config.get("secret_key", "")
        
        # API端点
        self.voice_clone_url = "https://openspeech.bytedance.com/api/v1/mega_tts/audio/upload"
        self.tts_url = "https://openspeech.bytedance.com/api/v1/tts"
        self.websocket_url = "wss://openspeech.bytedance.com/api/v1/tts/ws_binary"
        
        # 支持的语言和音色
        self.supported_languages = ["zh", "en", "ja", "ko"]
        self.supported_formats = ["mp3", "wav", "pcm"]
    
    def _get_default_headers(self) -> Dict[str, str]:
        """
        获取火山引擎默认请求头
        [integrations][volcano][_get_default_headers]
        """
        headers = super()._get_default_headers()
        headers.update({
            "Authorization": f"Bearer; {self.access_token}",
            "X-App-Id": self.app_id,
            "X-Cluster": self.cluster
        })
        return headers
    
    async def test_connection(self) -> IntegrationResponse:
        """
        测试火山引擎连接
        [integrations][volcano][test_connection]
        """
        try:
            # 使用简单的TTS请求测试连接
            test_data = {
                "app": {
                    "appid": self.app_id,
                    "token": self.access_token,
                    "cluster": self.cluster
                },
                "user": {
                    "uid": "test_user"
                },
                "audio": {
                    "voice_type": "BV001_streaming",
                    "encoding": "mp3",
                    "rate": 24000
                },
                "request": {
                    "reqid": "test_connection",
                    "text": "测试连接",
                    "text_type": "plain",
                    "operation": "query"
                }
            }
            
            response = await self._make_request("POST", "", data=test_data)
            
            if response.success:
                return IntegrationResponse.success_response({
                    "status": "connected",
                    "service": "volcano_engine",
                    "message": "Connection test successful"
                })
            else:
                return response
                
        except Exception as e:
            error = IntegrationError(
                code="CONNECTION_TEST_FAILED",
                message=f"Volcano Engine connection test failed: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
    async def get_service_info(self) -> IntegrationResponse:
        """
        获取火山引擎服务信息
        [integrations][volcano][get_service_info]
        """
        try:
            service_info = {
                "service_name": "Volcano Engine TTS",
                "provider": "ByteDance",
                "version": "v1",
                "features": [
                    "text_to_speech",
                    "voice_cloning",
                    "streaming_synthesis",
                    "multi_language_support"
                ],
                "supported_languages": self.supported_languages,
                "supported_formats": self.supported_formats,
                "cluster": self.cluster,
                "endpoints": {
                    "tts": self.tts_url,
                    "voice_clone": self.voice_clone_url,
                    "websocket": self.websocket_url
                }
            }
            
            return IntegrationResponse.success_response(service_info)
            
        except Exception as e:
            error = IntegrationError(
                code="SERVICE_INFO_ERROR",
                message=f"Failed to get service info: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
    async def volcano_text_to_speech(
        self,
        text: str,
        voice_type: str = "BV001_streaming",
        encoding: str = "mp3",
        rate: int = 24000,
        **kwargs
    ) -> IntegrationResponse:
        """
        文本转语音
        [integrations][volcano][text_to_speech]
        """
        try:
            # 构建请求数据
            request_data = {
                "app": {
                    "appid": self.app_id,
                    "token": self.access_token,
                    "cluster": self.cluster
                },
                "user": {
                    "uid": kwargs.get("user_id", "default_user")
                },
                "audio": {
                    "voice_type": voice_type,
                    "encoding": encoding,
                    "rate": rate,
                    "speed_ratio": kwargs.get("speed", 1.0),
                    "volume_ratio": kwargs.get("volume", 1.0),
                    "pitch_ratio": kwargs.get("pitch", 1.0)
                },
                "request": {
                    "reqid": kwargs.get("request_id", f"tts_{datetime.now().timestamp()}"),
                    "text": text,
                    "text_type": "plain",
                    "operation": "submit"
                }
            }
            
            # 发送请求
            response = await self._make_request("POST", self.tts_url, data=request_data)
            
            if response.success and response.data:
                # 处理响应数据
                result_data = response.data
                
                return IntegrationResponse.success_response({
                    "task_id": result_data.get("reqid"),
                    "audio_data": result_data.get("data"),
                    "format": encoding,
                    "sample_rate": rate,
                    "duration": result_data.get("duration"),
                    "size": result_data.get("size")
                })
            else:
                return response
                
        except Exception as e:
            error = IntegrationError(
                code="TTS_ERROR",
                message=f"Volcano TTS failed: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
    async def volcano_voice_clone(
        self,
        audio_file_data: bytes,
        voice_name: str,
        audio_format: str = "wav",
        **kwargs
    ) -> IntegrationResponse:
        """
        音色克隆
        [integrations][volcano][voice_clone]
        """
        try:
            # 准备上传数据
            audio_base64 = base64.b64encode(audio_file_data).decode('utf-8')
            
            clone_data = {
                "app": {
                    "appid": self.app_id,
                    "token": self.access_token,
                    "cluster": self.cluster
                },
                "user": {
                    "uid": kwargs.get("user_id", "default_user")
                },
                "audio": {
                    "audio_data": audio_base64,
                    "format": audio_format,
                    "voice_name": voice_name,
                    "language": kwargs.get("language", "zh"),
                    "gender": kwargs.get("gender", "female"),
                    "age": kwargs.get("age", "adult")
                },
                "request": {
                    "reqid": kwargs.get("request_id", f"clone_{datetime.now().timestamp()}"),
                    "operation": "create_voice"
                },
                "training": {
                    "epochs": kwargs.get("epochs", 100),
                    "batch_size": kwargs.get("batch_size", 32),
                    "learning_rate": kwargs.get("learning_rate", 0.001)
                }
            }
            
            # 发送克隆请求
            response = await self._make_request("POST", self.voice_clone_url, data=clone_data)
            
            if response.success and response.data:
                result_data = response.data
                
                return IntegrationResponse.success_response({
                    "voice_id": result_data.get("voice_id"),
                    "task_id": result_data.get("task_id"),
                    "status": result_data.get("status", "pending"),
                    "voice_name": voice_name,
                    "estimated_time": result_data.get("estimated_time"),
                    "progress": result_data.get("progress", 0)
                })
            else:
                return response
                
        except Exception as e:
            error = IntegrationError(
                code="VOICE_CLONE_ERROR",
                message=f"Volcano voice clone failed: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
    async def volcano_get_clone_status(self, task_id: str) -> IntegrationResponse:
        """
        获取克隆任务状态
        [integrations][volcano][get_clone_status]
        """
        try:
            status_data = {
                "app": {
                    "appid": self.app_id,
                    "token": self.access_token,
                    "cluster": self.cluster
                },
                "request": {
                    "reqid": f"status_{datetime.now().timestamp()}",
                    "task_id": task_id,
                    "operation": "query_status"
                }
            }
            
            response = await self._make_request("POST", "/api/v1/mega_tts/task/status", data=status_data)
            
            if response.success and response.data:
                result_data = response.data
                
                return IntegrationResponse.success_response({
                    "task_id": task_id,
                    "status": result_data.get("status"),
                    "progress": result_data.get("progress", 0),
                    "voice_id": result_data.get("voice_id"),
                    "error_message": result_data.get("error_message"),
                    "completed_time": result_data.get("completed_time")
                })
            else:
                return response
                
        except Exception as e:
            error = IntegrationError(
                code="STATUS_QUERY_ERROR",
                message=f"Failed to get clone status: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
    async def volcano_list_voices(self) -> IntegrationResponse:
        """
        获取可用音色列表
        [integrations][volcano][list_voices]
        """
        try:
            list_data = {
                "app": {
                    "appid": self.app_id,
                    "token": self.access_token,
                    "cluster": self.cluster
                },
                "request": {
                    "reqid": f"list_{datetime.now().timestamp()}",
                    "operation": "list_voices"
                }
            }
            
            response = await self._make_request("POST", "/api/v1/mega_tts/voice/list", data=list_data)
            
            if response.success and response.data:
                result_data = response.data
                
                return IntegrationResponse.success_response({
                    "voices": result_data.get("voices", []),
                    "total_count": result_data.get("total_count", 0),
                    "system_voices": result_data.get("system_voices", []),
                    "custom_voices": result_data.get("custom_voices", [])
                })
            else:
                return response
                
        except Exception as e:
            error = IntegrationError(
                code="LIST_VOICES_ERROR",
                message=f"Failed to list voices: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
    async def volcano_streaming_tts(
        self,
        text: str,
        voice_type: str = "BV001_streaming",
        **kwargs
    ) -> IntegrationResponse:
        """
        流式TTS（WebSocket）
        [integrations][volcano][streaming_tts]
        """
        try:
            # 这里需要实现WebSocket连接
            # 由于复杂性，这里提供基本框架
            
            streaming_config = {
                "app": {
                    "appid": self.app_id,
                    "token": self.access_token,
                    "cluster": self.cluster
                },
                "user": {
                    "uid": kwargs.get("user_id", "default_user")
                },
                "audio": {
                    "voice_type": voice_type,
                    "encoding": kwargs.get("encoding", "mp3"),
                    "rate": kwargs.get("rate", 24000)
                },
                "request": {
                    "reqid": kwargs.get("request_id", f"stream_{datetime.now().timestamp()}"),
                    "text": text,
                    "text_type": "plain",
                    "operation": "stream"
                }
            }
            
            # TODO: 实现WebSocket流式连接
            # 这里返回配置信息，实际实现需要WebSocket客户端
            
            return IntegrationResponse.success_response({
                "stream_url": self.websocket_url,
                "config": streaming_config,
                "message": "Streaming TTS configuration prepared"
            })
            
        except Exception as e:
            error = IntegrationError(
                code="STREAMING_TTS_ERROR",
                message=f"Volcano streaming TTS failed: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """
        生成API签名
        [integrations][volcano][_generate_signature]
        """
        if not self.secret_key:
            return ""
        
        # 对参数进行排序
        sorted_params = sorted(params.items())
        query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
        
        # 生成签名
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    async def volcano_get_quota(self) -> IntegrationResponse:
        """
        获取配额信息
        [integrations][volcano][get_quota]
        """
        try:
            quota_data = {
                "app": {
                    "appid": self.app_id,
                    "token": self.access_token,
                    "cluster": self.cluster
                },
                "request": {
                    "reqid": f"quota_{datetime.now().timestamp()}",
                    "operation": "query_quota"
                }
            }
            
            response = await self._make_request("POST", "/api/v1/quota", data=quota_data)
            
            if response.success and response.data:
                result_data = response.data
                
                return IntegrationResponse.success_response({
                    "total_quota": result_data.get("total_quota"),
                    "used_quota": result_data.get("used_quota"),
                    "remaining_quota": result_data.get("remaining_quota"),
                    "quota_type": result_data.get("quota_type"),
                    "reset_time": result_data.get("reset_time")
                })
            else:
                return response
                
        except Exception as e:
            error = IntegrationError(
                code="QUOTA_QUERY_ERROR",
                message=f"Failed to get quota info: {str(e)}"
            )
            return IntegrationResponse.error_response(error)