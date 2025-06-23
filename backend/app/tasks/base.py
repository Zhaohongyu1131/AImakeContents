"""
Base Task Classes
基础任务类 - [tasks][base]
"""

from celery import Task
from typing import Any, Dict, Optional
import logging
import traceback

from app.config.celery import celery_app_instance

logger = logging.getLogger(__name__)

class TaskBase(Task):
    """
    基础任务类
    [task][base]
    """
    
    def on_success(self, retval: Any, task_id: str, args: tuple, kwargs: dict) -> None:
        """
        任务成功回调
        [task][base][on_success]
        """
        logger.info(f"Task {task_id} succeeded with result: {retval}")
    
    def on_failure(self, exc: Exception, task_id: str, args: tuple, kwargs: dict, einfo) -> None:
        """
        任务失败回调
        [task][base][on_failure]
        """
        logger.error(f"Task {task_id} failed with exception: {exc}")
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    def on_retry(self, exc: Exception, task_id: str, args: tuple, kwargs: dict, einfo) -> None:
        """
        任务重试回调
        [task][base][on_retry]
        """
        logger.warning(f"Task {task_id} retrying due to: {exc}")

def task_progress_update(task_id: str, current: int, total: int, message: str = "") -> dict:
    """
    更新任务进度
    [task][progress][update]
    """
    progress_data = {
        "current": current,
        "total": total,
        "percentage": round((current / total) * 100, 2) if total > 0 else 0,
        "message": message
    }
    
    # 更新任务状态
    celery_app_instance.backend.store_result(
        task_id,
        progress_data,
        state="PROGRESS"
    )
    
    return progress_data

def task_error_handle(task_id: str, error: Exception, context: str = "") -> dict:
    """
    处理任务错误
    [task][error][handle]
    """
    error_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context,
        "traceback": traceback.format_exc()
    }
    
    logger.error(f"Task {task_id} error in {context}: {error}")
    
    return error_data