"""
Text Generation Service
文本生成服务 - 集成大语言模型API - [services][text_generation]
"""

from typing import Dict, Any, Optional, List, AsyncGenerator
import json
import logging
from datetime import datetime
import aiohttp
from app.config.settings import app_config_get_settings
from app.integrations.base import IntegrationResponse, IntegrationError


class TextGenerationService:
    """
    文本生成服务
    支持多个大语言模型平台
    [services][text_generation]
    """
    
    def __init__(self):
        """
        初始化文本生成服务
        [services][text_generation][init]
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.settings = app_config_get_settings()
        
        # 豆包API配置
        self.doubao_endpoint = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        self.doubao_api_key = getattr(self.settings, 'DOUBAO_API_KEY', '')
        self.doubao_model = getattr(self.settings, 'DOUBAO_MODEL', 'ep-20241223025957-d2x2r')
        
        # 其他平台配置（未来扩展）
        self.openai_api_key = getattr(self.settings, 'OPENAI_API_KEY', '')
        self.azure_api_key = getattr(self.settings, 'AZURE_API_KEY', '')
    
    async def text_generation_service_generate(
        self,
        prompt: str,
        model_provider: str = "doubao",
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成文本内容
        [services][text_generation][generate]
        """
        try:
            if model_provider == "doubao":
                return await self._text_generation_service_doubao_generate(
                    prompt, model_name, temperature, max_tokens, system_prompt, **kwargs
                )
            elif model_provider == "openai":
                return await self._text_generation_service_openai_generate(
                    prompt, model_name, temperature, max_tokens, system_prompt, **kwargs
                )
            elif model_provider == "azure":
                return await self._text_generation_service_azure_generate(
                    prompt, model_name, temperature, max_tokens, system_prompt, **kwargs
                )
            else:
                return {
                    "success": False,
                    "error": f"不支持的模型提供商: {model_provider}"
                }
                
        except Exception as e:
            self.logger.error(f"Text generation failed: {str(e)}")
            return {
                "success": False,
                "error": f"文本生成失败: {str(e)}"
            }
    
    async def _text_generation_service_doubao_generate(
        self,
        prompt: str,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        使用豆包API生成文本
        [services][text_generation][doubao_generate]
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.doubao_api_key}"
            }
            
            messages = []
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            data = {
                "model": model_name or self.doubao_model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": kwargs.get("top_p", 0.9),
                "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
                "presence_penalty": kwargs.get("presence_penalty", 0.0),
                "stream": False
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.doubao_endpoint,
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if "choices" in result and len(result["choices"]) > 0:
                            generated_text = result["choices"][0]["message"]["content"]
                            
                            return {
                                "success": True,
                                "data": {
                                    "generated_text": generated_text,
                                    "model": model_name or self.doubao_model,
                                    "provider": "doubao",
                                    "usage": result.get("usage", {}),
                                    "finish_reason": result["choices"][0].get("finish_reason", "complete")
                                }
                            }
                        else:
                            return {
                                "success": False,
                                "error": "豆包API返回了空的响应"
                            }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"豆包API请求失败: {response.status} - {error_text}"
                        }
                        
        except Exception as e:
            self.logger.error(f"Doubao generation error: {str(e)}")
            return {
                "success": False,
                "error": f"豆包文本生成失败: {str(e)}"
            }
    
    async def _text_generation_service_openai_generate(
        self,
        prompt: str,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        使用OpenAI API生成文本
        [services][text_generation][openai_generate]
        """
        # TODO: 实现OpenAI集成
        return {
            "success": False,
            "error": "OpenAI集成尚未实现"
        }
    
    async def _text_generation_service_azure_generate(
        self,
        prompt: str,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        使用Azure OpenAI生成文本
        [services][text_generation][azure_generate]
        """
        # TODO: 实现Azure集成
        return {
            "success": False,
            "error": "Azure集成尚未实现"
        }
    
    async def text_generation_service_generate_batch(
        self,
        prompts: List[str],
        model_provider: str = "doubao",
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        批量生成文本内容
        [services][text_generation][generate_batch]
        """
        try:
            results = []
            errors = []
            
            for i, prompt in enumerate(prompts):
                result = await self.text_generation_service_generate(
                    prompt=prompt,
                    model_provider=model_provider,
                    model_name=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    system_prompt=system_prompt,
                    **kwargs
                )
                
                if result["success"]:
                    results.append({
                        "index": i,
                        "prompt": prompt,
                        "generated_text": result["data"]["generated_text"],
                        "usage": result["data"].get("usage", {})
                    })
                else:
                    errors.append({
                        "index": i,
                        "prompt": prompt,
                        "error": result["error"]
                    })
            
            return {
                "success": len(errors) == 0,
                "data": {
                    "results": results,
                    "errors": errors,
                    "total": len(prompts),
                    "succeeded": len(results),
                    "failed": len(errors)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Batch generation failed: {str(e)}")
            return {
                "success": False,
                "error": f"批量生成失败: {str(e)}"
            }
    
    async def text_generation_service_generate_with_template(
        self,
        template_type: str,
        variables: Dict[str, Any],
        model_provider: str = "doubao",
        model_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        使用模板生成文本
        [services][text_generation][generate_with_template]
        """
        try:
            # 获取模板
            template = self._text_generation_service_get_template(template_type)
            if not template:
                return {
                    "success": False,
                    "error": f"未找到模板类型: {template_type}"
                }
            
            # 渲染模板
            prompt = template["prompt_template"]
            system_prompt = template.get("system_prompt", "")
            
            for key, value in variables.items():
                prompt = prompt.replace(f"{{{key}}}", str(value))
                system_prompt = system_prompt.replace(f"{{{key}}}", str(value))
            
            # 生成文本
            return await self.text_generation_service_generate(
                prompt=prompt,
                model_provider=model_provider,
                model_name=model_name,
                system_prompt=system_prompt,
                temperature=template.get("temperature", 0.7),
                max_tokens=template.get("max_tokens", 2000),
                **kwargs
            )
            
        except Exception as e:
            self.logger.error(f"Template generation failed: {str(e)}")
            return {
                "success": False,
                "error": f"模板生成失败: {str(e)}"
            }
    
    def _text_generation_service_get_template(self, template_type: str) -> Optional[Dict[str, Any]]:
        """
        获取预定义模板
        [services][text_generation][get_template]
        """
        templates = {
            "article": {
                "prompt_template": "请根据以下主题写一篇文章：\n主题：{topic}\n要求：{requirements}\n字数：{word_count}字左右",
                "system_prompt": "你是一位专业的文章写作助手，擅长创作高质量的文章内容。",
                "temperature": 0.7,
                "max_tokens": 3000
            },
            "product_description": {
                "prompt_template": "请为以下产品编写详细的产品描述：\n产品名称：{product_name}\n产品特点：{features}\n目标用户：{target_audience}",
                "system_prompt": "你是一位专业的产品文案撰写专家，擅长创作吸引人的产品描述。",
                "temperature": 0.6,
                "max_tokens": 1500
            },
            "social_media": {
                "prompt_template": "请创作一条关于{topic}的社交媒体文案，要求：{requirements}",
                "system_prompt": "你是一位社交媒体运营专家，擅长创作吸引人的社交媒体内容。",
                "temperature": 0.8,
                "max_tokens": 500
            },
            "email": {
                "prompt_template": "请帮我写一封{email_type}邮件：\n收件人：{recipient}\n主题：{subject}\n要点：{key_points}",
                "system_prompt": "你是一位专业的商务邮件撰写助手。",
                "temperature": 0.5,
                "max_tokens": 1000
            },
            "story": {
                "prompt_template": "请创作一个关于{theme}的故事，要求：{requirements}",
                "system_prompt": "你是一位富有创意的故事创作者。",
                "temperature": 0.9,
                "max_tokens": 4000
            }
        }
        
        return templates.get(template_type)
    
    def text_generation_service_get_available_models(self, provider: str) -> List[Dict[str, str]]:
        """
        获取可用的模型列表
        [services][text_generation][get_available_models]
        """
        models = {
            "doubao": [
                {"id": "ep-20241223025957-d2x2r", "name": "豆包通用模型", "description": "适合各种文本生成任务"},
                {"id": "ep-20241223-advanced", "name": "豆包高级模型", "description": "更强大的生成能力"}
            ],
            "openai": [
                {"id": "gpt-4", "name": "GPT-4", "description": "最强大的通用模型"},
                {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "快速且成本效益高"}
            ],
            "azure": [
                {"id": "gpt-4", "name": "Azure GPT-4", "description": "Azure托管的GPT-4"},
                {"id": "gpt-35-turbo", "name": "Azure GPT-3.5", "description": "Azure托管的GPT-3.5"}
            ]
        }
        
        return models.get(provider, [])


# 创建全局服务实例
text_generation_service = TextGenerationService()