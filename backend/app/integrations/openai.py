"""
OpenAI Integration
OpenAI集成服务 - [integrations][openai]
"""

from typing import Dict, Any, Optional, List
import json
from datetime import datetime
from app.integrations.base import IntegrationBase, IntegrationResponse, IntegrationError


class OpenAIIntegration(IntegrationBase):
    """
    OpenAI集成服务
    [integrations][openai]
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化OpenAI集成
        [integrations][openai][init]
        """
        super().__init__(config)
        
        # OpenAI特定配置
        self.api_key = config.get("api_key", "")
        self.organization = config.get("organization", "")
        self.base_url = config.get("base_url", "https://api.openai.com/v1")
        
        # API端点
        self.chat_endpoint = "/chat/completions"
        self.audio_speech_endpoint = "/audio/speech"
        self.audio_transcriptions_endpoint = "/audio/transcriptions"
        self.models_endpoint = "/models"
        
        # 支持的模型
        self.text_models = [
            "gpt-4", "gpt-4-32k", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"
        ]
        self.audio_models = ["tts-1", "tts-1-hd"]
        self.speech_models = ["whisper-1"]
        
        # 支持的TTS音色
        self.tts_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        self.tts_formats = ["mp3", "opus", "aac", "flac"]
    
    def _get_default_headers(self) -> Dict[str, str]:
        """
        获取OpenAI默认请求头
        [integrations][openai][_get_default_headers]
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if self.organization:
            headers["OpenAI-Organization"] = self.organization
        
        return headers
    
    async def test_connection(self) -> IntegrationResponse:
        """
        测试OpenAI连接
        [integrations][openai][test_connection]
        """
        try:
            # 通过获取模型列表测试连接
            response = await self.openai_list_models()
            
            if response.success:
                return IntegrationResponse.success_response({
                    "status": "connected",
                    "service": "openai",
                    "message": "Connection test successful"
                })
            else:
                return response
                
        except Exception as e:
            error = IntegrationError(
                code="CONNECTION_TEST_FAILED",
                message=f"OpenAI connection test failed: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
    async def get_service_info(self) -> IntegrationResponse:
        """
        获取OpenAI服务信息
        [integrations][openai][get_service_info]
        """
        try:
            service_info = {
                "service_name": "OpenAI API",
                "provider": "OpenAI",
                "version": "v1",
                "features": [
                    "text_generation",
                    "text_to_speech",
                    "speech_to_text",
                    "chat_completion"
                ],
                "text_models": self.text_models,
                "audio_models": self.audio_models,
                "speech_models": self.speech_models,
                "tts_voices": self.tts_voices,
                "tts_formats": self.tts_formats,
                "endpoints": {
                    "chat": f"{self.base_url}{self.chat_endpoint}",
                    "audio_speech": f"{self.base_url}{self.audio_speech_endpoint}",
                    "audio_transcriptions": f"{self.base_url}{self.audio_transcriptions_endpoint}",
                    "models": f"{self.base_url}{self.models_endpoint}"
                }
            }
            
            return IntegrationResponse.success_response(service_info)
            
        except Exception as e:
            error = IntegrationError(
                code="SERVICE_INFO_ERROR",
                message=f"Failed to get service info: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
    async def openai_text_to_speech(
        self,
        text: str,
        voice: str = "alloy",
        model: str = "tts-1",
        response_format: str = "mp3",
        speed: float = 1.0
    ) -> IntegrationResponse:
        """
        OpenAI文本转语音
        [integrations][openai][text_to_speech]
        """
        try:
            # 验证参数
            if voice not in self.tts_voices:
                error = IntegrationError(
                    code="INVALID_VOICE",
                    message=f"Voice '{voice}' not supported. Available: {self.tts_voices}"
                )
                return IntegrationResponse.error_response(error)
            
            if response_format not in self.tts_formats:
                error = IntegrationError(
                    code="INVALID_FORMAT",
                    message=f"Format '{response_format}' not supported. Available: {self.tts_formats}"
                )
                return IntegrationResponse.error_response(error)
            
            # 构建请求数据
            tts_data = {
                "model": model,
                "input": text,
                "voice": voice,
                "response_format": response_format,
                "speed": speed
            }
            
            # 发送TTS请求
            response = await self._make_request(
                "POST",
                self.audio_speech_endpoint,
                data=tts_data
            )
            
            if response.success and response.data:
                return IntegrationResponse.success_response({
                    "audio_data": response.data.get("content"),
                    "format": response_format,
                    "voice": voice,
                    "model": model,
                    "speed": speed,
                    "text_length": len(text)
                })
            else:
                return response
                
        except Exception as e:
            error = IntegrationError(
                code="TTS_ERROR",
                message=f"OpenAI TTS failed: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
    async def openai_speech_to_text(
        self,
        audio_data: bytes,
        model: str = "whisper-1",
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: str = "json",
        temperature: float = 0.0
    ) -> IntegrationResponse:
        """
        OpenAI语音转文本
        [integrations][openai][speech_to_text]
        """
        try:
            # 构建请求数据
            transcription_data = {
                "model": model,
                "response_format": response_format,
                "temperature": temperature
            }
            
            if language:
                transcription_data["language"] = language
            
            if prompt:
                transcription_data["prompt"] = prompt
            
            # 这里需要处理文件上传，简化实现
            # 实际应该使用multipart/form-data格式
            
            response = await self._make_request(
                "POST",
                self.audio_transcriptions_endpoint,
                data=transcription_data
            )
            
            if response.success and response.data:
                result_data = response.data
                
                return IntegrationResponse.success_response({
                    "text": result_data.get("text", ""),
                    "language": result_data.get("language"),
                    "duration": result_data.get("duration"),
                    "segments": result_data.get("segments", []),
                    "model": model
                })
            else:
                return response
                
        except Exception as e:
            error = IntegrationError(
                code="STT_ERROR",
                message=f"OpenAI STT failed: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
    async def openai_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> IntegrationResponse:
        """
        OpenAI聊天完成
        [integrations][openai][chat_completion]
        """
        try:
            # 构建请求数据
            chat_data = {
                "model": model,
                "messages": messages,
                "temperature": temperature
            }
            
            if max_tokens:
                chat_data["max_tokens"] = max_tokens
            
            # 添加其他可选参数
            optional_params = [
                "top_p", "n", "stream", "stop", "presence_penalty", 
                "frequency_penalty", "logit_bias", "user"
            ]
            
            for param in optional_params:
                if param in kwargs:
                    chat_data[param] = kwargs[param]
            
            # 发送聊天请求
            response = await self._make_request(
                "POST",
                self.chat_endpoint,
                data=chat_data
            )
            
            if response.success and response.data:
                result_data = response.data
                
                return IntegrationResponse.success_response({
                    "id": result_data.get("id"),
                    "choices": result_data.get("choices", []),
                    "usage": result_data.get("usage", {}),
                    "model": result_data.get("model"),
                    "created": result_data.get("created"),
                    "message_count": len(messages)
                })
            else:
                return response
                
        except Exception as e:
            error = IntegrationError(
                code="CHAT_ERROR",
                message=f"OpenAI chat completion failed: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
    async def openai_list_models(self) -> IntegrationResponse:
        """
        获取OpenAI模型列表
        [integrations][openai][list_models]
        """
        try:
            response = await self._make_request("GET", self.models_endpoint)
            
            if response.success and response.data:
                models = response.data.get("data", [])
                
                # 分类模型
                text_models = [m for m in models if any(tm in m.get("id", "") for tm in ["gpt", "text"])]
                audio_models = [m for m in models if any(am in m.get("id", "") for am in ["tts", "whisper"])]
                
                return IntegrationResponse.success_response({
                    "models": models,
                    "total_count": len(models),
                    "text_models": text_models,
                    "audio_models": audio_models
                })
            else:
                return response
                
        except Exception as e:
            error = IntegrationError(
                code="LIST_MODELS_ERROR",
                message=f"Failed to list OpenAI models: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
    async def openai_text_analysis(
        self,
        text: str,
        analysis_type: str = "sentiment",
        model: str = "gpt-3.5-turbo"
    ) -> IntegrationResponse:
        """
        OpenAI文本分析
        [integrations][openai][text_analysis]
        """
        try:
            # 构建分析提示
            analysis_prompts = {
                "sentiment": "请分析以下文本的情感倾向，返回正面、负面或中性，并给出置信度分数：",
                "keywords": "请提取以下文本的关键词，返回最重要的5-10个关键词：",
                "summary": "请总结以下文本的主要内容，控制在100字以内：",
                "toxicity": "请分析以下文本是否包含有害内容，返回风险等级和具体说明：",
                "language": "请识别以下文本的语言类型：",
                "readability": "请评估以下文本的可读性，包括难度等级和改进建议："
            }
            
            prompt = analysis_prompts.get(analysis_type, "请分析以下文本：")
            
            messages = [
                {"role": "system", "content": "你是一个专业的文本分析助手。"},
                {"role": "user", "content": f"{prompt}\n\n{text}"}
            ]
            
            # 调用聊天完成API
            response = await self.openai_chat_completion(
                messages=messages,
                model=model,
                temperature=0.3,
                max_tokens=500
            )
            
            if response.success and response.data:
                choices = response.data.get("choices", [])
                if choices:
                    analysis_result = choices[0].get("message", {}).get("content", "")
                    
                    return IntegrationResponse.success_response({
                        "analysis_type": analysis_type,
                        "result": analysis_result,
                        "model": model,
                        "text_length": len(text),
                        "usage": response.data.get("usage", {})
                    })
            
            return response
            
        except Exception as e:
            error = IntegrationError(
                code="TEXT_ANALYSIS_ERROR",
                message=f"OpenAI text analysis failed: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
    async def openai_content_generation(
        self,
        prompt: str,
        content_type: str = "article",
        model: str = "gpt-3.5-turbo",
        max_tokens: int = 1000,
        **kwargs
    ) -> IntegrationResponse:
        """
        OpenAI内容生成
        [integrations][openai][content_generation]
        """
        try:
            # 构建内容生成提示
            system_prompts = {
                "article": "你是一个专业的文章写作助手，请根据用户的要求创作高质量的文章。",
                "story": "你是一个创意写作助手，请根据用户的要求创作引人入胜的故事。",
                "marketing": "你是一个营销文案专家，请根据用户的要求创作有说服力的营销内容。",
                "technical": "你是一个技术写作专家，请根据用户的要求创作准确的技术文档。",
                "creative": "你是一个创意写作助手，请根据用户的要求创作富有想象力的内容。"
            }
            
            system_prompt = system_prompts.get(content_type, system_prompts["article"])
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            # 调用聊天完成API
            response = await self.openai_chat_completion(
                messages=messages,
                model=model,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=max_tokens,
                **kwargs
            )
            
            if response.success and response.data:
                choices = response.data.get("choices", [])
                if choices:
                    generated_content = choices[0].get("message", {}).get("content", "")
                    
                    return IntegrationResponse.success_response({
                        "content": generated_content,
                        "content_type": content_type,
                        "prompt": prompt,
                        "model": model,
                        "usage": response.data.get("usage", {}),
                        "word_count": len(generated_content.split())
                    })
            
            return response
            
        except Exception as e:
            error = IntegrationError(
                code="CONTENT_GENERATION_ERROR",
                message=f"OpenAI content generation failed: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
    async def openai_get_usage_stats(self) -> IntegrationResponse:
        """
        获取使用统计（模拟实现）
        [integrations][openai][get_usage_stats]
        """
        try:
            # OpenAI不提供直接的使用统计API
            # 这里返回模拟数据或从本地记录中获取
            
            return IntegrationResponse.success_response({
                "message": "Usage stats not directly available from OpenAI API",
                "suggestion": "Track usage locally or use OpenAI dashboard",
                "api_key": self.api_key[:8] + "***",
                "organization": self.organization or "default"
            })
            
        except Exception as e:
            error = IntegrationError(
                code="USAGE_STATS_ERROR",
                message=f"Failed to get usage stats: {str(e)}"
            )
            return IntegrationResponse.error_response(error)