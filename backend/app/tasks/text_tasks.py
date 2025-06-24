"""
Text Generation Tasks
文本生成Celery任务 - [tasks][text]
"""

from typing import Dict, Any, Optional, List
import logging
from celery import Task
import asyncio

from app.services.task_queue_service import celery_app
from app.services.text_generation_service import TextGenerationService
from app.dependencies.db import get_db

logger = logging.getLogger(__name__)


class TextTask(Task):
    """
    文本任务基类
    [tasks][text][base]
    """
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败时的回调"""
        logger.error(f"Text task {task_id} failed: {exc}")


@celery_app.task(base=TextTask, bind=True, name="app.tasks.text_tasks.generate_text")
def generate_text(self, prompt: str, model_config: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    生成文本任务
    [tasks][text][generate_text]
    """
    try:
        metadata = kwargs.get('_task_metadata', {})
        task_id = metadata.get('task_id')
        user_id = metadata.get('user_id')
        
        logger.info(f"Starting text generation task {task_id} for user {user_id}")
        
        # 更新任务状态
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': 100,
                'status': '开始文本生成...'
            }
        )
        
        # 运行异步文本生成
        result = asyncio.run(_async_generate_text(prompt, model_config, self))
        
        if result["success"]:
            logger.info(f"Text generation task {task_id} completed successfully")
            return {
                "success": True,
                "data": result["data"],
                "task_id": task_id,
                "user_id": user_id
            }
        else:
            logger.error(f"Text generation task {task_id} failed: {result['error']}")
            raise Exception(result["error"])
            
    except Exception as e:
        logger.error(f"Text generation task failed: {str(e)}")
        raise


async def _async_generate_text(prompt: str, model_config: Dict[str, Any], task_instance) -> Dict[str, Any]:
    """
    异步文本生成实现
    [tasks][text][async_generate_text]
    """
    try:
        # 获取数据库会话
        async for db in get_db():
            try:
                # 创建文本生成服务
                text_service = TextGenerationService(db)
                
                # 更新进度
                task_instance.update_state(
                    state='PROGRESS',
                    meta={
                        'current': 20,
                        'total': 100,
                        'status': '初始化文本生成服务...'
                    }
                )
                
                # 提取配置参数
                model_provider = model_config.get("model_provider", "doubao")
                model_name = model_config.get("model_name")
                temperature = model_config.get("temperature", 0.7)
                max_tokens = model_config.get("max_tokens", 2000)
                system_prompt = model_config.get("system_prompt")
                
                # 更新进度
                task_instance.update_state(
                    state='PROGRESS',
                    meta={
                        'current': 50,
                        'total': 100,
                        'status': '正在生成文本...'
                    }
                )
                
                # 调用文本生成服务
                result = await text_service.text_generation_service_generate(
                    prompt=prompt,
                    model_provider=model_provider,
                    model_name=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    system_prompt=system_prompt
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
            "error": f"文本生成失败: {str(e)}"
        }


@celery_app.task(base=TextTask, bind=True, name="app.tasks.text_tasks.batch_generate_text")
def batch_generate_text(self, prompts: List[str], model_config: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    批量文本生成任务
    [tasks][text][batch_generate_text]
    """
    try:
        metadata = kwargs.get('_task_metadata', {})
        task_id = metadata.get('task_id')
        user_id = metadata.get('user_id')
        
        logger.info(f"Starting batch text generation task {task_id} for user {user_id}")
        
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
                
                # 生成单个文本
                result = asyncio.run(_async_generate_text(prompt, model_config, self))
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
        
        logger.info(f"Batch text generation task {task_id} completed: {success_count}/{total_prompts} successful")
        
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
        logger.error(f"Batch text generation task failed: {str(e)}")
        raise


@celery_app.task(base=TextTask, bind=True, name="app.tasks.text_tasks.analyze_text")
def analyze_text(self, text: str, analysis_config: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    文本分析任务
    [tasks][text][analyze_text]
    """
    try:
        metadata = kwargs.get('_task_metadata', {})
        task_id = metadata.get('task_id')
        user_id = metadata.get('user_id')
        
        logger.info(f"Starting text analysis task {task_id} for user {user_id}")
        
        # 更新任务状态
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': 100,
                'status': '开始文本分析...'
            }
        )
        
        # 运行异步文本分析
        result = asyncio.run(_async_analyze_text(text, analysis_config, self))
        
        if result["success"]:
            logger.info(f"Text analysis task {task_id} completed successfully")
            return {
                "success": True,
                "data": result["data"],
                "task_id": task_id,
                "user_id": user_id
            }
        else:
            logger.error(f"Text analysis task {task_id} failed: {result['error']}")
            raise Exception(result["error"])
            
    except Exception as e:
        logger.error(f"Text analysis task failed: {str(e)}")
        raise


async def _async_analyze_text(text: str, analysis_config: Dict[str, Any], task_instance) -> Dict[str, Any]:
    """
    异步文本分析实现
    [tasks][text][async_analyze_text]
    """
    try:
        # 获取数据库会话
        async for db in get_db():
            try:
                # 创建文本生成服务
                text_service = TextGenerationService(db)
                
                # 更新进度
                task_instance.update_state(
                    state='PROGRESS',
                    meta={
                        'current': 20,
                        'total': 100,
                        'status': '初始化分析引擎...'
                    }
                )
                
                # 提取分析类型
                analysis_types = analysis_config.get("types", ["sentiment", "keywords", "summary"])
                
                results = {}
                
                for i, analysis_type in enumerate(analysis_types):
                    # 更新进度
                    progress = 20 + int((i / len(analysis_types)) * 70)
                    task_instance.update_state(
                        state='PROGRESS',
                        meta={
                            'current': progress,
                            'total': 100,
                            'status': f'执行{analysis_type}分析...'
                        }
                    )
                    
                    if analysis_type == "sentiment":
                        # 情感分析
                        sentiment_prompt = f"请分析以下文本的情感倾向，只返回正面/负面/中性：\n{text}"
                        sentiment_result = await text_service.text_generation_service_generate(
                            prompt=sentiment_prompt,
                            max_tokens=50
                        )
                        results["sentiment"] = sentiment_result.get("data", {}).get("generated_text", "")
                    
                    elif analysis_type == "keywords":
                        # 关键词提取
                        keywords_prompt = f"请提取以下文本的关键词，用逗号分隔：\n{text}"
                        keywords_result = await text_service.text_generation_service_generate(
                            prompt=keywords_prompt,
                            max_tokens=100
                        )
                        results["keywords"] = keywords_result.get("data", {}).get("generated_text", "")
                    
                    elif analysis_type == "summary":
                        # 文本摘要
                        summary_prompt = f"请为以下文本生成简洁的摘要：\n{text}"
                        summary_result = await text_service.text_generation_service_generate(
                            prompt=summary_prompt,
                            max_tokens=200
                        )
                        results["summary"] = summary_result.get("data", {}).get("generated_text", "")
                
                # 更新进度
                task_instance.update_state(
                    state='PROGRESS',
                    meta={
                        'current': 90,
                        'total': 100,
                        'status': '完成分析...'
                    }
                )
                
                return {
                    "success": True,
                    "data": {
                        "text": text,
                        "analysis_results": results,
                        "analyzed_types": analysis_types
                    }
                }
                    
            finally:
                await db.close()
                
    except Exception as e:
        return {
            "success": False,
            "error": f"文本分析失败: {str(e)}"
        }