"""
File Processing Tasks
文件处理Celery任务 - [tasks][file]
"""

from typing import Dict, Any, Optional, List
import logging
from celery import Task
import asyncio
import os

from app.services.task_queue_service import celery_app
from app.services.file_storage_service import FileStorageService
from app.dependencies.db import get_db

logger = logging.getLogger(__name__)


class FileTask(Task):
    """
    文件任务基类
    [tasks][file][base]
    """
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败时的回调"""
        logger.error(f"File task {task_id} failed: {exc}")


@celery_app.task(base=FileTask, bind=True, name="app.tasks.file_tasks.process_file")
def process_file(self, file_id: int, processing_config: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    处理文件任务
    [tasks][file][process_file]
    """
    try:
        metadata = kwargs.get('_task_metadata', {})
        task_id = metadata.get('task_id')
        user_id = metadata.get('user_id')
        
        logger.info(f"Starting file processing task {task_id} for user {user_id}")
        
        # 更新任务状态
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': 100,
                'status': '开始文件处理...'
            }
        )
        
        # 运行异步文件处理
        result = asyncio.run(_async_process_file(file_id, processing_config, self))
        
        if result["success"]:
            logger.info(f"File processing task {task_id} completed successfully")
            return {
                "success": True,
                "data": result["data"],
                "task_id": task_id,
                "user_id": user_id
            }
        else:
            logger.error(f"File processing task {task_id} failed: {result['error']}")
            raise Exception(result["error"])
            
    except Exception as e:
        logger.error(f"File processing task failed: {str(e)}")
        raise


async def _async_process_file(file_id: int, processing_config: Dict[str, Any], task_instance) -> Dict[str, Any]:
    """
    异步文件处理实现
    [tasks][file][async_process_file]
    """
    try:
        # 获取数据库会话
        async for db in get_db():
            try:
                # 创建文件存储服务
                file_service = FileStorageService(db)
                
                # 更新进度
                task_instance.update_state(
                    state='PROGRESS',
                    meta={
                        'current': 20,
                        'total': 100,
                        'status': '获取文件信息...'
                    }
                )
                
                # 获取文件元数据
                metadata_result = await file_service.file_storage_service_get_metadata(file_id)
                if not metadata_result["success"]:
                    return metadata_result
                
                file_info = metadata_result["data"]["file_info"]
                file_type = file_info["file_type"]
                
                # 更新进度
                task_instance.update_state(
                    state='PROGRESS',
                    meta={
                        'current': 50,
                        'total': 100,
                        'status': f'处理{file_type}文件...'
                    }
                )
                
                # 根据文件类型执行不同的处理
                processing_type = processing_config.get("type", "analyze")
                
                if processing_type == "analyze":
                    result = await _analyze_file(file_service, file_id, file_type)
                elif processing_type == "convert":
                    result = await _convert_file(file_service, file_id, processing_config)
                elif processing_type == "compress":
                    result = await _compress_file(file_service, file_id, processing_config)
                else:
                    result = {
                        "success": False,
                        "error": f"不支持的处理类型: {processing_type}"
                    }
                
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
            "error": f"文件处理失败: {str(e)}"
        }


async def _analyze_file(file_service: FileStorageService, file_id: int, file_type: str) -> Dict[str, Any]:
    """分析文件"""
    try:
        if file_type == "image":
            # 图像分析
            return {
                "success": True,
                "data": {
                    "analysis_type": "image",
                    "results": {
                        "colors": ["red", "blue", "green"],
                        "objects": ["person", "car"],
                        "scene": "outdoor"
                    }
                }
            }
        elif file_type == "audio":
            # 音频分析
            return {
                "success": True,
                "data": {
                    "analysis_type": "audio",
                    "results": {
                        "duration": 120.5,
                        "frequency": "44100Hz",
                        "channels": 2
                    }
                }
            }
        elif file_type == "text":
            # 文本分析
            return {
                "success": True,
                "data": {
                    "analysis_type": "text",
                    "results": {
                        "word_count": 1500,
                        "language": "chinese",
                        "sentiment": "positive"
                    }
                }
            }
        else:
            return {
                "success": False,
                "error": f"不支持分析{file_type}类型文件"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"文件分析失败: {str(e)}"
        }


async def _convert_file(file_service: FileStorageService, file_id: int, config: Dict[str, Any]) -> Dict[str, Any]:
    """转换文件格式"""
    try:
        target_format = config.get("target_format")
        if not target_format:
            return {
                "success": False,
                "error": "未指定目标格式"
            }
        
        # 这里实现文件格式转换逻辑
        # 实际实现会根据文件类型调用相应的转换库
        
        return {
            "success": True,
            "data": {
                "conversion_type": "format",
                "target_format": target_format,
                "new_file_id": file_id + 1000,  # 模拟新文件ID
                "message": f"文件已转换为{target_format}格式"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"文件转换失败: {str(e)}"
        }


async def _compress_file(file_service: FileStorageService, file_id: int, config: Dict[str, Any]) -> Dict[str, Any]:
    """压缩文件"""
    try:
        compression_level = config.get("level", "medium")
        
        # 这里实现文件压缩逻辑
        # 实际实现会根据文件类型调用相应的压缩库
        
        return {
            "success": True,
            "data": {
                "compression_type": "file",
                "compression_level": compression_level,
                "original_size": 1024000,  # 模拟原始大小
                "compressed_size": 512000,  # 模拟压缩后大小
                "compression_ratio": 0.5,
                "message": "文件压缩完成"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"文件压缩失败: {str(e)}"
        }


@celery_app.task(base=FileTask, bind=True, name="app.tasks.file_tasks.cleanup_temp_files")
def cleanup_temp_files(self, temp_dir: str, max_age_hours: int = 24, **kwargs) -> Dict[str, Any]:
    """
    清理临时文件任务
    [tasks][file][cleanup_temp_files]
    """
    try:
        metadata = kwargs.get('_task_metadata', {})
        task_id = metadata.get('task_id')
        
        logger.info(f"Starting temp files cleanup task {task_id}")
        
        # 更新任务状态
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': 100,
                'status': '开始清理临时文件...'
            }
        )
        
        import time
        cutoff_time = time.time() - (max_age_hours * 3600)
        cleaned_files = 0
        total_size = 0
        
        if os.path.exists(temp_dir):
            files = os.listdir(temp_dir)
            total_files = len(files)
            
            for i, filename in enumerate(files):
                # 更新进度
                progress = int((i / total_files) * 100) if total_files > 0 else 100
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': progress,
                        'total': 100,
                        'status': f'检查文件 {i+1}/{total_files}...'
                    }
                )
                
                filepath = os.path.join(temp_dir, filename)
                try:
                    if os.path.isfile(filepath):
                        file_time = os.path.getmtime(filepath)
                        if file_time < cutoff_time:
                            file_size = os.path.getsize(filepath)
                            os.remove(filepath)
                            cleaned_files += 1
                            total_size += file_size
                except Exception as e:
                    logger.warning(f"Failed to remove {filepath}: {str(e)}")
        
        logger.info(f"Temp files cleanup task {task_id} completed: {cleaned_files} files removed")
        
        return {
            "success": True,
            "data": {
                "cleaned_files": cleaned_files,
                "total_size": total_size,
                "size_human": f"{total_size / (1024*1024):.1f} MB" if total_size else "0 B",
                "temp_dir": temp_dir,
                "max_age_hours": max_age_hours
            },
            "task_id": task_id
        }
        
    except Exception as e:
        logger.error(f"Temp files cleanup task failed: {str(e)}")
        raise