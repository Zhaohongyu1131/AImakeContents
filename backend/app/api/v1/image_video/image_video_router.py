"""
Image Video Main Router
图像视频主路由 - [api][v1][image_video][router]
"""

from fastapi import APIRouter
from app.api.v1.image_video.image_content_create import image_content_create_router_get
from app.api.v1.image_video.image_content_manage import image_content_manage_router_get


def image_video_router_get() -> APIRouter:
    """
    获取图像视频主路由
    [api][v1][image_video][router_get]
    """
    router = APIRouter()
    
    # 图像内容创建路由
    router.include_router(
        image_content_create_router_get(),
        prefix="/image/content",
        tags=["图像内容创建"]
    )
    
    # 图像内容管理路由
    router.include_router(
        image_content_manage_router_get(),
        prefix="/image/content",
        tags=["图像内容管理"]
    )
    
    # 健康检查
    @router.get(
        "/health",
        summary="图像视频模块健康检查",
        description="检查图像视频模块状态"
    )
    async def image_video_health_check():
        """
        图像视频模块健康检查
        [api][v1][image_video][health_check]
        """
        return {
            "success": True,
            "message": "Image Video module is healthy",
            "modules": {
                "image_content": "active",
                "video_content": "planned",
                "image_generation": "active",
                "video_generation": "planned"
            }
        }
    
    # 获取支持的平台和模型
    @router.get(
        "/platforms",
        summary="获取支持的AI平台",
        description="获取支持的图像/视频生成AI平台列表"
    )
    async def image_video_platforms_get():
        """
        获取支持的AI平台
        [api][v1][image_video][platforms_get]
        """
        from app.services.image_generation_service import image_generation_service
        
        platforms = {
            "doubao": {
                "name": "豆包AI",
                "description": "字节跳动豆包AI图像生成",
                "status": "active",
                "models": image_generation_service.image_generation_service_get_available_models("doubao"),
                "supported_sizes": image_generation_service.image_generation_service_get_supported_sizes("doubao")
            },
            "dalle": {
                "name": "DALL-E",
                "description": "OpenAI DALL-E图像生成",
                "status": "active",
                "models": image_generation_service.image_generation_service_get_available_models("dalle"),
                "supported_sizes": image_generation_service.image_generation_service_get_supported_sizes("dalle")
            },
            "stable_diffusion": {
                "name": "Stable Diffusion",
                "description": "开源Stable Diffusion模型",
                "status": "planned",
                "models": image_generation_service.image_generation_service_get_available_models("stable_diffusion"),
                "supported_sizes": image_generation_service.image_generation_service_get_supported_sizes("stable_diffusion")
            },
            "midjourney": {
                "name": "Midjourney",
                "description": "Midjourney艺术图像生成",
                "status": "planned",
                "models": image_generation_service.image_generation_service_get_available_models("midjourney"),
                "supported_sizes": []
            }
        }
        
        return {
            "success": True,
            "data": platforms,
            "message": "获取AI平台信息成功"
        }
    
    # 获取模板列表
    @router.get(
        "/templates",
        summary="获取图像生成模板",
        description="获取预定义的图像生成模板列表"
    )
    async def image_video_templates_get():
        """
        获取图像生成模板
        [api][v1][image_video][templates_get]
        """
        templates = {
            "portrait": {
                "name": "人像摄影",
                "description": "专业人像照片生成",
                "variables": ["subject", "style"],
                "example": "a professional portrait of {subject}, {style}, high quality, detailed"
            },
            "landscape": {
                "name": "风景摄影",
                "description": "自然风景图像生成",
                "variables": ["location", "weather", "time_of_day"],
                "example": "a beautiful landscape of {location}, {weather}, {time_of_day}, cinematic lighting"
            },
            "product": {
                "name": "产品摄影",
                "description": "商业产品图像生成",
                "variables": ["product", "background"],
                "example": "professional product photo of {product}, {background}, studio lighting"
            },
            "logo": {
                "name": "标志设计",
                "description": "企业标志设计生成",
                "variables": ["company", "industry", "style"],
                "example": "minimalist logo design for {company}, {industry}, {style}, vector art"
            },
            "artwork": {
                "name": "艺术插画",
                "description": "艺术风格插画生成",
                "variables": ["subject", "art_style", "mood"],
                "example": "artistic illustration of {subject}, {art_style}, {mood}, detailed artwork"
            },
            "social_media": {
                "name": "社交媒体",
                "description": "社交媒体内容图像",
                "variables": ["topic", "style"],
                "example": "eye-catching social media post about {topic}, {style}, vibrant colors"
            }
        }
        
        return {
            "success": True,
            "data": templates,
            "message": "获取模板列表成功"
        }
    
    return router