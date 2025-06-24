"""
Image Generation Service
图像生成服务 - 集成多AI平台图像生成API - [services][image_generation]
"""

from typing import Dict, Any, Optional, List, Union
import base64
import json
import logging
from datetime import datetime
import aiohttp
import asyncio
from app.config.settings import app_config_get_settings
from app.integrations.base import IntegrationResponse, IntegrationError


class ImageGenerationService:
    """
    图像生成服务
    支持多个AI图像生成平台
    [services][image_generation]
    """
    
    def __init__(self):
        """
        初始化图像生成服务
        [services][image_generation][init]
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.settings = app_config_get_settings()
        
        # 豆包图像API配置
        self.doubao_image_endpoint = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
        self.doubao_api_key = getattr(self.settings, 'DOUBAO_API_KEY', '')
        
        # Stable Diffusion配置（未来扩展）
        self.sd_endpoint = ""
        self.sd_api_key = ""
        
        # DALL-E配置（未来扩展）
        self.dalle_endpoint = "https://api.openai.com/v1/images/generations"
        self.dalle_api_key = getattr(self.settings, 'OPENAI_API_KEY', '')
        
        # Midjourney配置（未来扩展）
        self.midjourney_endpoint = ""
        self.midjourney_api_key = ""
    
    async def image_generation_service_generate(
        self,
        prompt: str,
        model_provider: str = "doubao",
        model_name: Optional[str] = None,
        width: int = 512,
        height: int = 512,
        num_images: int = 1,
        style: Optional[str] = None,
        quality: str = "standard",
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成图像
        [services][image_generation][generate]
        """
        try:
            if model_provider == "doubao":
                return await self._image_generation_service_doubao_generate(
                    prompt, model_name, width, height, num_images, style, quality, **kwargs
                )
            elif model_provider == "dalle":
                return await self._image_generation_service_dalle_generate(
                    prompt, model_name, width, height, num_images, style, quality, **kwargs
                )
            elif model_provider == "stable_diffusion":
                return await self._image_generation_service_sd_generate(
                    prompt, model_name, width, height, num_images, style, quality, **kwargs
                )
            elif model_provider == "midjourney":
                return await self._image_generation_service_midjourney_generate(
                    prompt, model_name, width, height, num_images, style, quality, **kwargs
                )
            else:
                return {
                    "success": False,
                    "error": f"不支持的图像生成平台: {model_provider}"
                }
                
        except Exception as e:
            self.logger.error(f"Image generation failed: {str(e)}")
            return {
                "success": False,
                "error": f"图像生成失败: {str(e)}"
            }
    
    async def _image_generation_service_doubao_generate(
        self,
        prompt: str,
        model_name: Optional[str] = None,
        width: int = 512,
        height: int = 512,
        num_images: int = 1,
        style: Optional[str] = None,
        quality: str = "standard",
        **kwargs
    ) -> Dict[str, Any]:
        """
        使用豆包API生成图像
        [services][image_generation][doubao_generate]
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.doubao_api_key}"
            }
            
            data = {
                "prompt": prompt,
                "model": model_name or "doubao-image-v1",
                "n": num_images,
                "size": f"{width}x{height}",
                "quality": quality,
                "response_format": "b64_json"
            }
            
            # 添加风格参数
            if style:
                data["style"] = style
            
            # 添加其他参数
            if kwargs.get("negative_prompt"):
                data["negative_prompt"] = kwargs["negative_prompt"]
            
            if kwargs.get("steps"):
                data["steps"] = kwargs["steps"]
            
            if kwargs.get("guidance_scale"):
                data["guidance_scale"] = kwargs["guidance_scale"]
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.doubao_image_endpoint,
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if "data" in result and len(result["data"]) > 0:
                            generated_images = []
                            
                            for item in result["data"]:
                                image_data = {
                                    "image_data": item.get("b64_json"),
                                    "url": item.get("url"),
                                    "revised_prompt": item.get("revised_prompt", prompt)
                                }
                                generated_images.append(image_data)
                            
                            return {
                                "success": True,
                                "data": {
                                    "images": generated_images,
                                    "model": model_name or "doubao-image-v1",
                                    "provider": "doubao",
                                    "original_prompt": prompt,
                                    "generation_params": {
                                        "width": width,
                                        "height": height,
                                        "num_images": num_images,
                                        "style": style,
                                        "quality": quality
                                    }
                                }
                            }
                        else:
                            return {
                                "success": False,
                                "error": "豆包API返回了空的图像数据"
                            }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"豆包图像API请求失败: {response.status} - {error_text}"
                        }
                        
        except Exception as e:
            self.logger.error(f"Doubao image generation error: {str(e)}")
            return {
                "success": False,
                "error": f"豆包图像生成失败: {str(e)}"
            }
    
    async def _image_generation_service_dalle_generate(
        self,
        prompt: str,
        model_name: Optional[str] = None,
        width: int = 512,
        height: int = 512,
        num_images: int = 1,
        style: Optional[str] = None,
        quality: str = "standard",
        **kwargs
    ) -> Dict[str, Any]:
        """
        使用DALL-E API生成图像
        [services][image_generation][dalle_generate]
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.dalle_api_key}"
            }
            
            # DALL-E支持的尺寸
            size_mapping = {
                (1024, 1024): "1024x1024",
                (1792, 1024): "1792x1024", 
                (1024, 1792): "1024x1792",
                (512, 512): "1024x1024"  # 默认映射到最接近的支持尺寸
            }
            
            size = size_mapping.get((width, height), "1024x1024")
            
            data = {
                "prompt": prompt,
                "model": model_name or "dall-e-3",
                "n": min(num_images, 1),  # DALL-E 3只支持单张
                "size": size,
                "quality": quality,
                "response_format": "b64_json"
            }
            
            if style:
                data["style"] = style
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.dalle_endpoint,
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        generated_images = []
                        for item in result.get("data", []):
                            image_data = {
                                "image_data": item.get("b64_json"),
                                "url": item.get("url"),
                                "revised_prompt": item.get("revised_prompt", prompt)
                            }
                            generated_images.append(image_data)
                        
                        return {
                            "success": True,
                            "data": {
                                "images": generated_images,
                                "model": model_name or "dall-e-3",
                                "provider": "dalle",
                                "original_prompt": prompt,
                                "generation_params": {
                                    "width": width,
                                    "height": height,
                                    "num_images": len(generated_images),
                                    "style": style,
                                    "quality": quality
                                }
                            }
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"DALL-E API请求失败: {response.status} - {error_text}"
                        }
                        
        except Exception as e:
            self.logger.error(f"DALL-E image generation error: {str(e)}")
            return {
                "success": False,
                "error": f"DALL-E图像生成失败: {str(e)}"
            }
    
    async def _image_generation_service_sd_generate(
        self,
        prompt: str,
        model_name: Optional[str] = None,
        width: int = 512,
        height: int = 512,
        num_images: int = 1,
        style: Optional[str] = None,
        quality: str = "standard",
        **kwargs
    ) -> Dict[str, Any]:
        """
        使用Stable Diffusion生成图像
        [services][image_generation][sd_generate]
        """
        # TODO: 实现Stable Diffusion集成
        return {
            "success": False,
            "error": "Stable Diffusion集成尚未实现"
        }
    
    async def _image_generation_service_midjourney_generate(
        self,
        prompt: str,
        model_name: Optional[str] = None,
        width: int = 512,
        height: int = 512,
        num_images: int = 1,
        style: Optional[str] = None,
        quality: str = "standard",
        **kwargs
    ) -> Dict[str, Any]:
        """
        使用Midjourney生成图像
        [services][image_generation][midjourney_generate]
        """
        # TODO: 实现Midjourney集成
        return {
            "success": False,
            "error": "Midjourney集成尚未实现"
        }
    
    async def image_generation_service_generate_batch(
        self,
        prompts: List[str],
        model_provider: str = "doubao",
        model_name: Optional[str] = None,
        width: int = 512,
        height: int = 512,
        style: Optional[str] = None,
        quality: str = "standard",
        **kwargs
    ) -> Dict[str, Any]:
        """
        批量生成图像
        [services][image_generation][generate_batch]
        """
        try:
            tasks = []
            for prompt in prompts:
                task = self.image_generation_service_generate(
                    prompt=prompt,
                    model_provider=model_provider,
                    model_name=model_name,
                    width=width,
                    height=height,
                    num_images=1,
                    style=style,
                    quality=quality,
                    **kwargs
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_results = []
            failed_results = []
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failed_results.append({
                        "index": i,
                        "prompt": prompts[i],
                        "error": str(result)
                    })
                elif result.get("success"):
                    successful_results.append({
                        "index": i,
                        "prompt": prompts[i],
                        "images": result["data"]["images"],
                        "model": result["data"]["model"]
                    })
                else:
                    failed_results.append({
                        "index": i,
                        "prompt": prompts[i],
                        "error": result.get("error", "未知错误")
                    })
            
            return {
                "success": len(failed_results) == 0,
                "data": {
                    "successful_results": successful_results,
                    "failed_results": failed_results,
                    "total": len(prompts),
                    "succeeded": len(successful_results),
                    "failed": len(failed_results)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Batch image generation failed: {str(e)}")
            return {
                "success": False,
                "error": f"批量图像生成失败: {str(e)}"
            }
    
    async def image_generation_service_generate_with_template(
        self,
        template_type: str,
        variables: Dict[str, Any],
        model_provider: str = "doubao",
        model_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        使用模板生成图像
        [services][image_generation][generate_with_template]
        """
        try:
            # 获取模板
            template = self._image_generation_service_get_template(template_type)
            if not template:
                return {
                    "success": False,
                    "error": f"未找到模板类型: {template_type}"
                }
            
            # 渲染模板
            prompt = template["prompt_template"]
            for key, value in variables.items():
                prompt = prompt.replace(f"{{{key}}}", str(value))
            
            # 生成图像
            return await self.image_generation_service_generate(
                prompt=prompt,
                model_provider=model_provider,
                model_name=model_name,
                width=template.get("width", 512),
                height=template.get("height", 512),
                style=template.get("style"),
                quality=template.get("quality", "standard"),
                **kwargs
            )
            
        except Exception as e:
            self.logger.error(f"Template image generation failed: {str(e)}")
            return {
                "success": False,
                "error": f"模板图像生成失败: {str(e)}"
            }
    
    def _image_generation_service_get_template(self, template_type: str) -> Optional[Dict[str, Any]]:
        """
        获取预定义模板
        [services][image_generation][get_template]
        """
        templates = {
            "portrait": {
                "prompt_template": "a professional portrait of {subject}, {style}, high quality, detailed",
                "width": 512,
                "height": 768,
                "style": "photographic",
                "quality": "hd"
            },
            "landscape": {
                "prompt_template": "a beautiful landscape of {location}, {weather}, {time_of_day}, cinematic lighting",
                "width": 768,
                "height": 512,
                "style": "natural",
                "quality": "hd"
            },
            "product": {
                "prompt_template": "professional product photo of {product}, {background}, studio lighting, commercial photography",
                "width": 512,
                "height": 512,
                "style": "photographic",
                "quality": "hd"
            },
            "logo": {
                "prompt_template": "minimalist logo design for {company}, {industry}, {style}, vector art, clean",
                "width": 512,
                "height": 512,
                "style": "vector",
                "quality": "standard"
            },
            "artwork": {
                "prompt_template": "artistic illustration of {subject}, {art_style}, {mood}, detailed artwork",
                "width": 512,
                "height": 512,
                "style": "artistic",
                "quality": "hd"
            },
            "social_media": {
                "prompt_template": "eye-catching social media post about {topic}, {style}, vibrant colors, engaging",
                "width": 512,
                "height": 512,
                "style": "vivid",
                "quality": "standard"
            }
        }
        
        return templates.get(template_type)
    
    def image_generation_service_get_available_models(self, provider: str) -> List[Dict[str, str]]:
        """
        获取可用的模型列表
        [services][image_generation][get_available_models]
        """
        models = {
            "doubao": [
                {"id": "doubao-image-v1", "name": "豆包图像生成", "description": "豆包标准图像生成模型"},
                {"id": "doubao-image-hd", "name": "豆包高清图像", "description": "豆包高清图像生成模型"}
            ],
            "dalle": [
                {"id": "dall-e-3", "name": "DALL-E 3", "description": "最新的DALL-E模型"},
                {"id": "dall-e-2", "name": "DALL-E 2", "description": "经典的DALL-E模型"}
            ],
            "stable_diffusion": [
                {"id": "sd-xl", "name": "Stable Diffusion XL", "description": "高质量图像生成"},
                {"id": "sd-2.1", "name": "Stable Diffusion 2.1", "description": "稳定版本"}
            ],
            "midjourney": [
                {"id": "mj-v5", "name": "Midjourney V5", "description": "最新Midjourney模型"},
                {"id": "mj-v4", "name": "Midjourney V4", "description": "经典Midjourney模型"}
            ]
        }
        
        return models.get(provider, [])
    
    def image_generation_service_get_supported_sizes(self, provider: str) -> List[Dict[str, Any]]:
        """
        获取支持的图像尺寸
        [services][image_generation][get_supported_sizes]
        """
        sizes = {
            "doubao": [
                {"width": 512, "height": 512, "name": "正方形 512x512"},
                {"width": 768, "height": 512, "name": "横版 768x512"},
                {"width": 512, "height": 768, "name": "竖版 512x768"},
                {"width": 1024, "height": 1024, "name": "大正方形 1024x1024"}
            ],
            "dalle": [
                {"width": 1024, "height": 1024, "name": "正方形 1024x1024"},
                {"width": 1792, "height": 1024, "name": "横版 1792x1024"},
                {"width": 1024, "height": 1792, "name": "竖版 1024x1792"}
            ],
            "stable_diffusion": [
                {"width": 512, "height": 512, "name": "标准 512x512"},
                {"width": 768, "height": 768, "name": "中等 768x768"},
                {"width": 1024, "height": 1024, "name": "高清 1024x1024"}
            ]
        }
        
        return sizes.get(provider, [])


# 创建全局服务实例
image_generation_service = ImageGenerationService()