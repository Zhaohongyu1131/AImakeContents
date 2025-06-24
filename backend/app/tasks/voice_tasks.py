"""
Voice Generation Tasks
语音生成Celery任务 - [tasks][voice]
"""

from typing import Dict, Any, Optional
import logging
from celery import Task
import asyncio

from app.services.task_queue_service import celery_app
from app.services.voice_service_unified import VoiceServiceUnified
from app.dependencies.db import get_db

logger = logging.getLogger(__name__)


class VoiceTask(Task):
    """
    语音任务基类
    [tasks][voice][base]
    """
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败时的回调"""
        logger.error(f"Voice task {task_id} failed: {exc}")
        
        # 记录失败信息
        metadata = kwargs.get('_task_metadata', {})
        user_id = metadata.get('user_id')
        
        # 这里可以添加失败通知逻辑
        # 例如：发送邮件、更新数据库状态等


@celery_app.task(base=VoiceTask, bind=True, name="app.tasks.voice_tasks.generate_voice")
def generate_voice(self, text: str, voice_config: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    生成语音任务
    [tasks][voice][generate_voice]
    """
    try:
        metadata = kwargs.get('_task_metadata', {})
        task_id = metadata.get('task_id')
        user_id = metadata.get('user_id')
        
        logger.info(f"Starting voice generation task {task_id} for user {user_id}")
        
        # 更新任务状态
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': 100,
                'status': '开始语音生成...'
            }
        )
        
        # 运行异步语音生成
        result = asyncio.run(_async_generate_voice(text, voice_config, self))
        
        if result["success"]:
            logger.info(f"Voice generation task {task_id} completed successfully")
            return {
                "success": True,
                "data": result["data"],
                "task_id": task_id,
                "user_id": user_id
            }
        else:
            logger.error(f"Voice generation task {task_id} failed: {result['error']}")
            raise Exception(result["error"])
            
    except Exception as e:
        logger.error(f"Voice generation task failed: {str(e)}")
        raise


async def _async_generate_voice(text: str, voice_config: Dict[str, Any], task_instance) -> Dict[str, Any]:
    """
    异步语音生成实现
    [tasks][voice][async_generate_voice]
    """
    try:
        # 获取数据库会话
        async for db in get_db():
            try:
                # 创建语音服务
                voice_service = VoiceServiceUnified(db)
                
                # 更新进度
                task_instance.update_state(
                    state='PROGRESS',
                    meta={
                        'current': 20,
                        'total': 100,
                        'status': '初始化语音服务...'
                    }
                )
                
                # 提取配置参数
                platform = voice_config.get("platform", "volcano")
                voice_id = voice_config.get("voice_id")
                style = voice_config.get("style", "normal")
                speed = voice_config.get("speed", 1.0)
                volume = voice_config.get("volume", 1.0)
                
                # 更新进度
                task_instance.update_state(
                    state='PROGRESS',
                    meta={
                        'current': 50,
                        'total': 100,
                        'status': '正在生成语音...'
                    }
                )
                
                # 调用语音生成服务
                result = await voice_service.voice_service_unified_synthesize(
                    text=text,
                    platform=platform,
                    voice_id=voice_id,
                    style=style,
                    speed=speed,
                    volume=volume
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
                
                if result["success"]:
                    # 处理生成结果，保存文件等
                    audio_data = result["data"]
                    
                    # 这里可以添加文件保存逻辑
                    # 例如：保存到文件存储服务
                    
                    return {
                        "success": True,
                        "data": {
                            "audio_url": audio_data.get("audio_url"),
                            "duration": audio_data.get("duration"),
                            "file_size": audio_data.get("file_size"),
                            "platform": platform,
                            "voice_id": voice_id,
                            "generated_time": audio_data.get("generated_time")
                        }
                    }
                else:
                    return result
                    
            finally:
                await db.close()
                
    except Exception as e:
        return {
            "success": False,
            "error": f"语音生成失败: {str(e)}"
        }


@celery_app.task(base=VoiceTask, bind=True, name="app.tasks.voice_tasks.clone_voice")
def clone_voice(self, audio_file_path: str, clone_config: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    语音克隆任务
    [tasks][voice][clone_voice]
    """
    try:
        metadata = kwargs.get('_task_metadata', {})
        task_id = metadata.get('task_id')
        user_id = metadata.get('user_id')
        
        logger.info(f"Starting voice cloning task {task_id} for user {user_id}")
        
        # 更新任务状态
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': 100,
                'status': '开始语音克隆...'
            }
        )
        
        # 运行异步语音克隆
        result = asyncio.run(_async_clone_voice(audio_file_path, clone_config, self))
        
        if result["success"]:
            logger.info(f"Voice cloning task {task_id} completed successfully")
            return {
                "success": True,
                "data": result["data"],
                "task_id": task_id,
                "user_id": user_id
            }
        else:
            logger.error(f"Voice cloning task {task_id} failed: {result['error']}")
            raise Exception(result["error"])
            
    except Exception as e:
        logger.error(f"Voice cloning task failed: {str(e)}")
        raise


async def _async_clone_voice(audio_file_path: str, clone_config: Dict[str, Any], task_instance) -> Dict[str, Any]:
    """
    异步语音克隆实现
    [tasks][voice][async_clone_voice]
    """
    try:
        # 获取数据库会话
        async for db in get_db():
            try:
                # 创建语音服务
                voice_service = VoiceServiceUnified(db)
                
                # 更新进度
                task_instance.update_state(
                    state='PROGRESS',
                    meta={
                        'current': 20,
                        'total': 100,
                        'status': '分析音频文件...'
                    }
                )
                
                # 提取配置参数
                platform = clone_config.get("platform", "volcano")
                voice_name = clone_config.get("voice_name", "Custom Voice")
                description = clone_config.get("description", "")
                
                # 更新进度
                task_instance.update_state(
                    state='PROGRESS',
                    meta={
                        'current': 50,
                        'total': 100,
                        'status': '正在训练语音模型...'
                    }
                )
                
                # 调用语音克隆服务
                result = await voice_service.voice_service_unified_clone(
                    audio_file_path=audio_file_path,
                    platform=platform,
                    voice_name=voice_name,
                    description=description
                )
                
                # 更新进度
                task_instance.update_state(
                    state='PROGRESS',
                    meta={
                        'current': 90,
                        'total': 100,
                        'status': '完成处理...'
                    }
                )
                
                return result
                    
            finally:
                await db.close()
                
    except Exception as e:
        return {
            "success": False,
            "error": f"语音克隆失败: {str(e)}"
        }


@celery_app.task(base=VoiceTask, bind=True, name="app.tasks.voice_tasks.batch_generate_voice")
def batch_generate_voice(self, text_list: list, voice_config: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    批量语音生成任务
    [tasks][voice][batch_generate_voice]
    """
    try:
        metadata = kwargs.get('_task_metadata', {})
        task_id = metadata.get('task_id')
        user_id = metadata.get('user_id')
        
        logger.info(f"Starting batch voice generation task {task_id} for user {user_id}")
        
        results = []
        total_texts = len(text_list)
        
        for i, text in enumerate(text_list):
            try:
                # 更新进度
                progress = int((i / total_texts) * 100)
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': progress,
                        'total': 100,
                        'status': f'处理第 {i+1}/{total_texts} 个文本...'
                    }
                )
                
                # 生成单个语音
                result = asyncio.run(_async_generate_voice(text, voice_config, self))
                results.append({
                    "text": text,
                    "result": result,
                    "index": i
                })
                
            except Exception as e:
                results.append({
                    "text": text,
                    "result": {"success": False, "error": str(e)},
                    "index": i
                })
        
        # 统计结果
        success_count = sum(1 for r in results if r["result"]["success"])
        
        logger.info(f"Batch voice generation task {task_id} completed: {success_count}/{total_texts} successful")
        
        return {
            "success": True,
            "data": {
                "results": results,
                "summary": {
                    "total": total_texts,
                    "success": success_count,
                    "failed": total_texts - success_count
                }
            },
            "task_id": task_id,
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Batch voice generation task failed: {str(e)}")
        raise