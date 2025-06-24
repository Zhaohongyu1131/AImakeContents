"""
Enhanced Volcano Engine Integration
增强版火山引擎集成服务 - [integrations][volcano_enhanced]
"""

from typing import Dict, Any, Optional, List, Union, AsyncGenerator
import base64
import json
import uuid
import asyncio
import websockets
import aiohttp
import gzip
import struct
from datetime import datetime
import logging
from app.integrations.base import IntegrationBase, IntegrationResponse, IntegrationError


class VolcanoEngineEnhanced(IntegrationBase):
    """
    增强版火山引擎集成服务
    支持完整的豆包API功能
    [integrations][volcano_enhanced]
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化火山引擎增强集成
        [integrations][volcano_enhanced][init]
        """
        super().__init__(config)
        
        # 火山引擎配置
        self.appid = config.get("appid", "")
        self.access_token = config.get("access_token", "")
        self.cluster = config.get("cluster", "volcano_icl")
        
        # API端点
        self.base_url = "https://openspeech.bytedance.com"
        self.upload_endpoint = "/api/v1/mega_tts/audio/upload"
        self.status_endpoint = "/api/v1/mega_tts/status"
        self.tts_http_endpoint = "/api/v1/tts"
        self.tts_ws_endpoint = "wss://openspeech.bytedance.com/api/v1/tts/ws_binary"
        
        # 支持的语言映射
        self.language_map = {
            "zh-CN": 0,  # 中文
            "en-US": 1,  # 英文
            "ja-JP": 2,  # 日语
            "es-ES": 3,  # 西班牙语
            "id-ID": 4,  # 印尼语
            "pt-PT": 5   # 葡萄牙语
        }
        
        # 模型类型说明
        self.model_types = {
            0: "1.0效果",
            1: "2.0效果(ICL)",
            2: "DiT标准版(音色)",
            3: "DiT还原版(音色+风格)"
        }
        
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _get_default_headers(self) -> Dict[str, str]:
        """
        获取默认请求头
        [integrations][volcano_enhanced][_get_default_headers]
        """
        return {
            "Authorization": f"Bearer;{self.access_token}",
            "Content-Type": "application/json",
            "Resource-Id": "volc.megatts.voiceclone"
        }
    
    async def test_connection(self) -> IntegrationResponse:
        """
        测试火山引擎连接
        [integrations][volcano_enhanced][test_connection]
        """
        try:
            # 通过获取音色状态测试连接
            response = await self.volcano_list_speaker_status()
            
            if response.success:
                return IntegrationResponse.success_response({
                    "status": "connected",
                    "service": "volcano_engine",
                    "message": "Connection test successful",
                    "appid": self.appid
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
        [integrations][volcano_enhanced][get_service_info]
        """
        try:
            service_info = {
                "service_name": "火山引擎语音技术",
                "provider": "字节跳动",
                "version": "v1",
                "features": [
                    "voice_cloning",
                    "text_to_speech_http",
                    "text_to_speech_websocket",
                    "multi_language_support",
                    "streaming_synthesis"
                ],
                "supported_languages": list(self.language_map.keys()),
                "model_types": self.model_types,
                "clusters": ["volcano_icl", "volcano_icl_concurr"],
                "endpoints": {
                    "voice_clone": f"{self.base_url}{self.upload_endpoint}",
                    "status_check": f"{self.base_url}{self.status_endpoint}",
                    "tts_http": f"{self.base_url}{self.tts_http_endpoint}",
                    "tts_websocket": self.tts_ws_endpoint
                }
            }
            
            return IntegrationResponse.success_response(service_info)
            
        except Exception as e:
            error = IntegrationError(
                code="SERVICE_INFO_ERROR",
                message=f"Failed to get service info: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
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
        上传音频进行音色克隆训练
        [integrations][volcano_enhanced][upload_voice_clone]
        """
        try:
            # 编码音频数据
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # 构建请求数据
            upload_data = {
                "appid": self.appid,
                "speaker_id": speaker_id,
                "audios": [{
                    "audio_bytes": audio_base64,
                    "audio_format": audio_format
                }],
                "source": 2,
                "language": language,
                "model_type": model_type
            }
            
            # 添加参考文本（如果提供）
            if reference_text:
                upload_data["audios"][0]["text"] = reference_text
            
            # 发送上传请求
            response = await self._make_request(
                "POST",
                self.upload_endpoint,
                data=upload_data,
                headers=self._get_default_headers()
            )
            
            if response.success and response.data:
                return IntegrationResponse.success_response({
                    "speaker_id": response.data.get("speaker_id"),
                    "upload_status": "submitted",
                    "model_type": model_type,
                    "language": language,
                    "audio_format": audio_format,
                    "reference_text": reference_text
                })
            else:
                return response
                
        except Exception as e:
            error = IntegrationError(
                code="VOICE_CLONE_UPLOAD_ERROR",
                message=f"Voice clone upload failed: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
    async def volcano_check_speaker_status(
        self,
        speaker_id: str
    ) -> IntegrationResponse:
        """
        检查音色训练状态
        [integrations][volcano_enhanced][check_speaker_status]
        """
        try:
            status_data = {
                "appid": self.appid,
                "speaker_id": speaker_id
            }
            
            response = await self._make_request(
                "POST",
                self.status_endpoint,
                data=status_data,
                headers=self._get_default_headers()
            )
            
            if response.success and response.data:
                status_info = response.data
                
                return IntegrationResponse.success_response({
                    "speaker_id": status_info.get("speaker_id"),
                    "status": status_info.get("status"),  # 0=NotFound, 1=Training, 2=Success, 3=Failed, 4=Active
                    "create_time": status_info.get("create_time"),
                    "version": status_info.get("version", "V1"),
                    "demo_audio": status_info.get("demo_audio"),
                    "is_ready": status_info.get("status") in [2, 4]  # Success or Active
                })
            else:
                return response
                
        except Exception as e:
            error = IntegrationError(
                code="STATUS_CHECK_ERROR",
                message=f"Speaker status check failed: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
    async def volcano_list_speaker_status(
        self,
        speaker_ids: Optional[List[str]] = None
    ) -> IntegrationResponse:
        """
        批量获取音色状态
        [integrations][volcano_enhanced][list_speaker_status]
        """
        try:
            status_data = {"appid": self.appid}
            
            if speaker_ids:
                status_data["speaker_ids"] = speaker_ids
            
            response = await self._make_request(
                "POST",
                self.status_endpoint,
                data=status_data,
                headers=self._get_default_headers()
            )
            
            if response.success and response.data:
                return IntegrationResponse.success_response({
                    "speakers": response.data.get("speakers", []),
                    "total_count": len(response.data.get("speakers", []))
                })
            else:
                return response
                
        except Exception as e:
            error = IntegrationError(
                code="LIST_STATUS_ERROR",
                message=f"List speaker status failed: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
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
        HTTP方式文本转语音
        [integrations][volcano_enhanced][text_to_speech_http]
        """
        try:
            # 生成唯一请求ID
            reqid = str(uuid.uuid4())
            
            # 构建请求数据
            tts_data = {
                "app": {
                    "appid": self.appid,
                    "token": "access_token",
                    "cluster": kwargs.get("cluster", self.cluster)
                },
                "user": {
                    "uid": kwargs.get("user_id", "default_user")
                },
                "audio": {
                    "voice_type": voice_type,
                    "encoding": encoding,
                    "rate": sample_rate,
                    "speed_ratio": speed_ratio,
                    "volume_ratio": volume_ratio,
                    "pitch_ratio": pitch_ratio
                },
                "request": {
                    "reqid": reqid,
                    "text": text,
                    "text_type": kwargs.get("text_type", "plain"),
                    "operation": "query"
                }
            }
            
            # 添加高级参数
            if kwargs.get("explicit_language"):
                tts_data["audio"]["explicit_language"] = kwargs["explicit_language"]
            
            if kwargs.get("context_language"):
                tts_data["audio"]["context_language"] = kwargs["context_language"]
            
            if kwargs.get("with_timestamp"):
                tts_data["request"]["with_timestamp"] = kwargs["with_timestamp"]
            
            if kwargs.get("split_sentence"):
                tts_data["request"]["split_sentence"] = kwargs["split_sentence"]
            
            # 缓存配置
            if kwargs.get("cache_enabled"):
                cache_config = {
                    "text_type": 1,
                    "use_cache": True
                }
                tts_data["request"]["extra_param"] = json.dumps({"cache_config": cache_config})
            
            # 发送TTS请求
            headers = {
                "Authorization": f"Bearer;{self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = await self._make_request(
                "POST",
                self.tts_http_endpoint,
                data=tts_data,
                headers=headers
            )
            
            if response.success and response.data:
                result_data = response.data
                
                # 解码音频数据
                audio_data = None
                if result_data.get("data"):
                    audio_data = base64.b64decode(result_data["data"])
                
                return IntegrationResponse.success_response({
                    "reqid": result_data.get("reqid"),
                    "audio_data": audio_data,
                    "encoding": encoding,
                    "sample_rate": sample_rate,
                    "duration": result_data.get("addition", {}).get("duration"),
                    "sequence": result_data.get("sequence"),
                    "voice_type": voice_type,
                    "text_length": len(text)
                })
            else:
                return response
                
        except Exception as e:
            error = IntegrationError(
                code="TTS_HTTP_ERROR",
                message=f"HTTP TTS failed: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
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
        [integrations][volcano_enhanced][text_to_speech_websocket]
        """
        try:
            # 生成唯一请求ID
            reqid = str(uuid.uuid4())
            
            # 构建请求数据
            request_json = {
                "app": {
                    "appid": self.appid,
                    "token": "access_token",
                    "cluster": kwargs.get("cluster", self.cluster)
                },
                "user": {
                    "uid": kwargs.get("user_id", "default_user")
                },
                "audio": {
                    "voice_type": voice_type,
                    "encoding": encoding,
                    "rate": sample_rate,
                    "speed_ratio": speed_ratio,
                    "volume_ratio": volume_ratio,
                    "pitch_ratio": pitch_ratio
                },
                "request": {
                    "reqid": reqid,
                    "text": text,
                    "text_type": kwargs.get("text_type", "plain"),
                    "operation": "submit"
                }
            }
            
            # 添加高级参数
            if kwargs.get("explicit_language"):
                request_json["audio"]["explicit_language"] = kwargs["explicit_language"]
            
            # 构建WebSocket消息
            payload_bytes = json.dumps(request_json).encode('utf-8')
            payload_bytes = gzip.compress(payload_bytes)
            
            # 构建消息头 (version=1, header_size=1, message_type=1, flags=0, serialization=1, compression=1, reserved=0)
            header = bytearray(b'\x11\x10\x11\x00')
            
            # 添加payload大小
            full_message = bytearray(header)
            full_message.extend(len(payload_bytes).to_bytes(4, 'big'))
            full_message.extend(payload_bytes)
            
            # WebSocket连接和通信
            headers = {"Authorization": f"Bearer;{self.access_token}"}
            
            async with websockets.connect(self.tts_ws_endpoint, extra_headers=headers) as websocket:
                # 发送请求
                await websocket.send(full_message)
                
                audio_chunks = []
                
                # 接收响应
                while True:
                    try:
                        response = await websocket.recv()
                        
                        # 解析响应
                        result = self._parse_websocket_response(response)
                        
                        if result["type"] == "audio":
                            audio_chunks.append(result["data"])
                            
                            yield IntegrationResponse.success_response({
                                "type": "audio_chunk",
                                "audio_data": result["data"],
                                "sequence": result["sequence"],
                                "is_final": result["is_final"]
                            })
                            
                            if result["is_final"]:
                                # 发送完整音频数据
                                complete_audio = b''.join(audio_chunks)
                                yield IntegrationResponse.success_response({
                                    "type": "complete",
                                    "audio_data": complete_audio,
                                    "reqid": reqid,
                                    "encoding": encoding,
                                    "total_chunks": len(audio_chunks)
                                })
                                break
                                
                        elif result["type"] == "error":
                            yield IntegrationResponse.error_response(
                                IntegrationError(
                                    code="WEBSOCKET_TTS_ERROR",
                                    message=result["error_message"]
                                )
                            )
                            break
                            
                    except websockets.exceptions.ConnectionClosed:
                        break
                    except Exception as e:
                        yield IntegrationResponse.error_response(
                            IntegrationError(
                                code="WEBSOCKET_STREAM_ERROR",
                                message=f"WebSocket stream error: {str(e)}"
                            )
                        )
                        break
                        
        except Exception as e:
            yield IntegrationResponse.error_response(
                IntegrationError(
                    code="WEBSOCKET_TTS_ERROR",
                    message=f"WebSocket TTS failed: {str(e)}"
                )
            )
    
    def _parse_websocket_response(self, response: bytes) -> Dict[str, Any]:
        """
        解析WebSocket响应
        [integrations][volcano_enhanced][_parse_websocket_response]
        """
        try:
            # 解析消息头
            protocol_version = response[0] >> 4
            header_size = response[0] & 0x0f
            message_type = response[1] >> 4
            message_type_specific_flags = response[1] & 0x0f
            serialization_method = response[2] >> 4
            message_compression = response[2] & 0x0f
            
            header_end = header_size * 4
            payload = response[header_end:]
            
            if message_type == 0xb:  # Audio-only server response
                if message_type_specific_flags == 0:  # ACK without data
                    return {"type": "ack", "data": None}
                else:
                    # Extract sequence number and payload size
                    sequence_number = int.from_bytes(payload[:4], "big", signed=True)
                    payload_size = int.from_bytes(payload[4:8], "big", signed=False)
                    audio_data = payload[8:]
                    
                    return {
                        "type": "audio",
                        "data": audio_data,
                        "sequence": sequence_number,
                        "is_final": sequence_number < 0
                    }
                    
            elif message_type == 0xf:  # Error message
                error_code = int.from_bytes(payload[:4], "big", signed=False)
                msg_size = int.from_bytes(payload[4:8], "big", signed=False)
                error_msg = payload[8:]
                
                if message_compression == 1:
                    error_msg = gzip.decompress(error_msg)
                
                return {
                    "type": "error",
                    "error_code": error_code,
                    "error_message": error_msg.decode('utf-8')
                }
            
            return {"type": "unknown", "data": None}
            
        except Exception as e:
            return {
                "type": "error",
                "error_code": -1,
                "error_message": f"Response parsing error: {str(e)}"
            }
    
    async def volcano_get_usage_stats(self) -> IntegrationResponse:
        """
        获取使用统计信息
        [integrations][volcano_enhanced][get_usage_stats]
        """
        try:
            # 火山引擎没有直接的使用统计API
            # 这里返回基本信息
            return IntegrationResponse.success_response({
                "message": "Usage stats not directly available from Volcano Engine API",
                "suggestion": "Track usage locally or use Volcano Console",
                "appid": self.appid,
                "cluster": self.cluster
            })
            
        except Exception as e:
            error = IntegrationError(
                code="USAGE_STATS_ERROR",
                message=f"Failed to get usage stats: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
    async def volcano_health_check(self) -> IntegrationResponse:
        """
        火山引擎健康检查
        [integrations][volcano_enhanced][health_check]
        """
        try:
            # 通过简单的状态查询检查健康状态
            health_data = {
                "appid": self.appid
            }
            
            response = await self._make_request(
                "POST",
                self.status_endpoint,
                data=health_data,
                headers=self._get_default_headers(),
                timeout=10  # 10秒超时
            )
            
            return IntegrationResponse.success_response({
                "status": "healthy" if response.success else "unhealthy",
                "response_time": response.metadata.get("response_time", 0),
                "appid": self.appid,
                "cluster": self.cluster
            })
            
        except Exception as e:
            return IntegrationResponse.error_response(
                IntegrationError(
                    code="HEALTH_CHECK_FAILED",
                    message=f"Volcano Engine health check failed: {str(e)}"
                )
            )