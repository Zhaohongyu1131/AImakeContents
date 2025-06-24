"""
Image Generation Tasks
图像生成Celery任务 - [tasks][image]
"""

from typing import Dict, Any, Optional, List
import logging
from celery import Task
import asyncio

from app.services.task_queue_service import celery_app
from app.services.image_generation_service import ImageGenerationService
from app.dependencies.db import get_db

logger = logging.getLogger(__name__)


class ImageTask(Task):
    """
    图像任务基类
    [tasks][image][base]
    """
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败时的回调"""
        logger.error(f"Image task {task_id} failed: {exc}")


@celery_app.task(base=ImageTask, bind=True, name="app.tasks.image_tasks.generate_image")
def generate_image(self, prompt: str, image_config: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    生成图像任务
    [tasks][image][generate_image]
    """
    try:
        metadata = kwargs.get('_task_metadata', {})
        task_id = metadata.get('task_id')
        user_id = metadata.get('user_id')
        
        logger.info(f"Starting image generation task {task_id} for user {user_id}")
        
        # 更新任务状态
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': 100,
                'status': '开始图像生成...'
            }
        )
        
        # 运行异步图像生成
        result = asyncio.run(_async_generate_image(prompt, image_config, self))
        
        if result["success"]:
            logger.info(f"Image generation task {task_id} completed successfully")
            return {
                "success": True,
                "data": result["data"],
                "task_id": task_id,
                "user_id": user_id
            }
        else:
            logger.error(f"Image generation task {task_id} failed: {result['error']}")
            raise Exception(result["error"])
            
    except Exception as e:
        logger.error(f"Image generation task failed: {str(e)}")
        raise


async def _async_generate_image(prompt: str, image_config: Dict[str, Any], task_instance) -> Dict[str, Any]:
    """
    异步图像生成实现
    [tasks][image][async_generate_image]
    """
    try:
        # 获取数据库会话
        async for db in get_db():
            try:
                # 创建图像生成服务
                image_service = ImageGenerationService(db)
                
                # 更新进度
                task_instance.update_state(
                    state='PROGRESS',
                    meta={
                        'current': 20,
                        'total': 100,
                        'status': '初始化图像生成服务...'
                    }
                )
                
                # 提取配置参数
                model_provider = image_config.get("model_provider", "doubao")
                width = image_config.get("width", 512)
                height = image_config.get("height", 512)
                style = image_config.get("style")
                quality = image_config.get("quality", "standard")
                
                # 更新进度
                task_instance.update_state(
                    state='PROGRESS',
                    meta={
                        'current': 50,
                        'total': 100,
                        'status': '正在生成图像...'
                    }
                )
                
                # 调用图像生成服务
                result = await image_service.image_generation_service_generate(
                    prompt=prompt,
                    model_provider=model_provider,
                    width=width,
                    height=height,
                    style=style,
                    quality=quality
                )
                
                # 更新进度
                task_instance.update_state(
                    state='PROGRESS',
                    meta={
                        'current': 90,
                        'total': 100,
                        'status': '处理结果...'
                    }
                )
                
                return result
                    
            finally:
                await db.close()
                
    except Exception as e:
        return {
            "success": False,
            "error": f"图像生成失败: {str(e)}"
        }


@celery_app.task(base=ImageTask, bind=True, name="app.tasks.image_tasks.batch_generate_image")
def batch_generate_image(self, prompts: List[str], image_config: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    批量图像生成任务
    [tasks][image][batch_generate_image]
    """
    try:
        metadata = kwargs.get('_task_metadata', {})
        task_id = metadata.get('task_id')
        user_id = metadata.get('user_id')
        
        logger.info(f"Starting batch image generation task {task_id} for user {user_id}")
        
        results = []
        total_prompts = len(prompts)
        
        for i, prompt in enumerate(prompts):
            try:
                # 更新进度
                progress = int((i / total_prompts) * 100)
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': progress,
                        'total': 100,
                        'status': f'处理第 {i+1}/{total_prompts} 个提示...'
                    }
                )
                
                # 生成单个图像
                result = asyncio.run(_async_generate_image(prompt, image_config, self))
                results.append({
                    "prompt": prompt,
                    "result": result,
                    "index": i
                })
                
            except Exception as e:
                results.append({
                    "prompt": prompt,
                    "result": {"success": False, "error": str(e)},
                    "index": i
                })
        
        # 统计结果
        success_count = sum(1 for r in results if r["result"]["success"])
        
        logger.info(f"Batch image generation task {task_id} completed: {success_count}/{total_prompts} successful")
        
        return {
            "success": True,
            "data": {
                "results": results,
                "summary": {
                    "total": total_prompts,
                    "success": success_count,
                    "failed": total_prompts - success_count
                }
            },
            "task_id": task_id,
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Batch image generation task failed: {str(e)}")
        raise