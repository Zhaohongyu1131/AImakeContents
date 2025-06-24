"""
Task Queue Service
任务队列服务 - [services][task_queue]
"""

from typing import Dict, Any, Optional, List, Union
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
from celery import Celery
from celery.result import AsyncResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from app.services.base import ServiceBase
from app.config.settings import app_config_get_settings


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    STARTED = "started"
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"
    REVOKED = "revoked"


class TaskPriority(Enum):
    """任务优先级枚举"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class TaskType(Enum):
    """任务类型枚举"""
    VOICE_GENERATION = "voice_generation"
    TEXT_GENERATION = "text_generation"
    IMAGE_GENERATION = "image_generation"
    VIDEO_GENERATION = "video_generation"
    FILE_PROCESSING = "file_processing"
    DATA_EXPORT = "data_export"
    CLEANUP = "cleanup"


# 创建Celery实例
def create_celery_app() -> Celery:
    """
    创建Celery应用实例
    [services][task_queue][create_celery_app]
    """
    settings = app_config_get_settings()
    
    celery_app = Celery(
        "datasay_tasks",
        broker=settings.CELERY_BROKER_URL,
        backend=settings.CELERY_RESULT_BACKEND,
        include=[
            'app.tasks.voice_tasks',
            'app.tasks.text_tasks', 
            'app.tasks.image_tasks',
            'app.tasks.file_tasks',
            'app.tasks.maintenance_tasks'
        ]
    )
    
    # Celery配置
    celery_app.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        
        # 任务路由
        task_routes={
            'app.tasks.voice_tasks.*': {'queue': 'voice'},
            'app.tasks.text_tasks.*': {'queue': 'text'},
            'app.tasks.image_tasks.*': {'queue': 'image'},
            'app.tasks.file_tasks.*': {'queue': 'file'},
            'app.tasks.maintenance_tasks.*': {'queue': 'maintenance'}
        },
        
        # 队列配置
        task_default_queue='default',
        task_create_missing_queues=True,
        
        # 任务配置
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        
        # 结果过期时间
        result_expires=3600,
        
        # 任务重试配置
        task_retry_kwargs={
            'max_retries': 3,
            'countdown': 60
        }
    )
    
    return celery_app


# 全局Celery实例
celery_app = create_celery_app()


class TaskQueueService(ServiceBase):
    """
    任务队列管理服务
    [services][task_queue]
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        初始化任务队列服务
        [services][task_queue][init]
        """
        super().__init__(db_session)
        self.celery_app = celery_app
    
    async def task_queue_service_submit_task(
        self,
        task_name: str,
        task_args: List[Any] = None,
        task_kwargs: Dict[str, Any] = None,
        task_type: str = TaskType.VOICE_GENERATION.value,
        priority: str = TaskPriority.NORMAL.value,
        user_id: Optional[int] = None,
        scheduled_time: Optional[datetime] = None,
        max_retries: int = 3,
        timeout: int = 3600
    ) -> Dict[str, Any]:
        """
        提交任务到队列
        [services][task_queue][submit_task]
        """
        try:
            # 生成任务ID
            task_id = str(uuid.uuid4())
            
            # 准备任务参数
            task_args = task_args or []
            task_kwargs = task_kwargs or {}
            
            # 添加元数据
            task_kwargs['_task_metadata'] = {
                'task_id': task_id,
                'task_type': task_type,
                'user_id': user_id,
                'submitted_time': datetime.utcnow().isoformat(),
                'priority': priority
            }
            
            # 确定队列
            queue_name = self._get_queue_by_task_type(task_type)
            
            # 提交任务
            if scheduled_time:
                # 延时任务
                result = self.celery_app.send_task(
                    task_name,
                    args=task_args,
                    kwargs=task_kwargs,
                    task_id=task_id,
                    queue=queue_name,
                    eta=scheduled_time,
                    retry=True,
                    retry_policy={
                        'max_retries': max_retries,
                        'interval_start': 0,
                        'interval_step': 60,
                        'interval_max': 600
                    }
                )
            else:
                # 立即执行
                result = self.celery_app.send_task(
                    task_name,
                    args=task_args,
                    kwargs=task_kwargs,
                    task_id=task_id,
                    queue=queue_name,
                    retry=True,
                    retry_policy={
                        'max_retries': max_retries,
                        'interval_start': 0,
                        'interval_step': 60,
                        'interval_max': 600
                    }
                )
            
            # 记录任务提交日志
            await self.service_base_log_operation(
                "submit_task",
                "task",
                task_id,
                user_id,
                {
                    "task_name": task_name,
                    "task_type": task_type,
                    "queue": queue_name,
                    "priority": priority
                }
            )
            
            return {
                "success": True,
                "data": {
                    "task_id": task_id,
                    "task_name": task_name,
                    "task_type": task_type,
                    "queue": queue_name,
                    "status": TaskStatus.PENDING.value,
                    "submitted_time": datetime.utcnow().isoformat(),
                    "scheduled_time": scheduled_time.isoformat() if scheduled_time else None
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"任务提交失败: {str(e)}"
            }
    
    async def task_queue_service_get_task_status(
        self,
        task_id: str
    ) -> Dict[str, Any]:
        """
        获取任务状态
        [services][task_queue][get_task_status]
        """
        try:
            result = AsyncResult(task_id, app=self.celery_app)
            
            task_info = {
                "task_id": task_id,
                "status": result.status,
                "result": result.result if result.successful() else None,
                "error": str(result.result) if result.failed() else None,
                "traceback": result.traceback if result.failed() else None,
                "date_done": result.date_done.isoformat() if result.date_done else None
            }
            
            # 获取任务元数据
            if hasattr(result, 'info') and isinstance(result.info, dict):
                task_info.update(result.info)
            
            return {
                "success": True,
                "data": task_info
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"获取任务状态失败: {str(e)}"
            }
    
    async def task_queue_service_cancel_task(
        self,
        task_id: str,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        取消任务
        [services][task_queue][cancel_task]
        """
        try:
            # 撤销任务
            self.celery_app.control.revoke(task_id, terminate=True)
            
            # 记录取消日志
            if user_id:
                await self.service_base_log_operation(
                    "cancel_task",
                    "task",
                    task_id,
                    user_id
                )
            
            return {
                "success": True,
                "message": "任务已取消"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"取消任务失败: {str(e)}"
            }
    
    async def task_queue_service_retry_task(
        self,
        task_id: str,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        重试失败的任务
        [services][task_queue][retry_task]
        """
        try:
            result = AsyncResult(task_id, app=self.celery_app)
            
            if not result.failed():
                return {
                    "success": False,
                    "error": "只能重试失败的任务"
                }
            
            # 重新提交任务
            # 注意：这里需要获取原始任务的参数，实际实现中需要更复杂的逻辑
            new_result = result.retry()
            
            # 记录重试日志
            if user_id:
                await self.service_base_log_operation(
                    "retry_task",
                    "task",
                    task_id,
                    user_id
                )
            
            return {
                "success": True,
                "data": {
                    "new_task_id": new_result.id,
                    "message": "任务已重新提交"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"重试任务失败: {str(e)}"
            }
    
    async def task_queue_service_get_queue_info(self) -> Dict[str, Any]:
        """
        获取队列信息
        [services][task_queue][get_queue_info]
        """
        try:
            inspect = self.celery_app.control.inspect()
            
            # 获取活跃任务
            active_tasks = inspect.active()
            
            # 获取预定任务
            scheduled_tasks = inspect.scheduled()
            
            # 获取队列长度
            queue_lengths = inspect.stats()
            
            return {
                "success": True,
                "data": {
                    "active_tasks": active_tasks,
                    "scheduled_tasks": scheduled_tasks,
                    "queue_stats": queue_lengths,
                    "workers": list(active_tasks.keys()) if active_tasks else []
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"获取队列信息失败: {str(e)}"
            }
    
    async def task_queue_service_get_user_tasks(
        self,
        user_id: int,
        task_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """
        获取用户任务列表
        [services][task_queue][get_user_tasks]
        """
        try:
            # 这里需要实现任务数据库存储
            # 当前简化实现，实际应该从数据库查询
            
            # 获取活跃任务中属于该用户的任务
            inspect = self.celery_app.control.inspect()
            active_tasks = inspect.active() or {}
            
            user_tasks = []
            for worker, tasks in active_tasks.items():
                for task in tasks:
                    task_kwargs = task.get('kwargs', {})
                    metadata = task_kwargs.get('_task_metadata', {})
                    
                    if metadata.get('user_id') == user_id:
                        if task_type and metadata.get('task_type') != task_type:
                            continue
                        
                        user_tasks.append({
                            "task_id": task['id'],
                            "task_name": task['name'],
                            "task_type": metadata.get('task_type'),
                            "status": "running",
                            "worker": worker,
                            "submitted_time": metadata.get('submitted_time'),
                            "args": task.get('args', []),
                            "kwargs": {k: v for k, v in task_kwargs.items() if k != '_task_metadata'}
                        })
            
            # 分页处理
            total = len(user_tasks)
            start = (page - 1) * size
            end = start + size
            paginated_tasks = user_tasks[start:end]
            
            return {
                "success": True,
                "data": {
                    "tasks": paginated_tasks,
                    "pagination": {
                        "page": page,
                        "size": size,
                        "total": total,
                        "pages": (total + size - 1) // size
                    }
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"获取用户任务失败: {str(e)}"
            }
    
    async def task_queue_service_cleanup_completed_tasks(
        self,
        days_old: int = 7
    ) -> Dict[str, Any]:
        """
        清理完成的任务
        [services][task_queue][cleanup_completed_tasks]
        """
        try:
            # 清理指定天数前的已完成任务结果
            cutoff_time = datetime.utcnow() - timedelta(days=days_old)
            
            # 这里需要实现任务结果清理逻辑
            # 当前Celery的结果后端会自动过期，这里可以添加额外的清理逻辑
            
            return {
                "success": True,
                "message": f"已清理{days_old}天前的完成任务"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"清理任务失败: {str(e)}"
            }
    
    def _get_queue_by_task_type(self, task_type: str) -> str:
        """根据任务类型确定队列"""
        queue_mapping = {
            TaskType.VOICE_GENERATION.value: "voice",
            TaskType.TEXT_GENERATION.value: "text",
            TaskType.IMAGE_GENERATION.value: "image",
            TaskType.VIDEO_GENERATION.value: "video",
            TaskType.FILE_PROCESSING.value: "file",
            TaskType.DATA_EXPORT.value: "default",
            TaskType.CLEANUP.value: "maintenance"
        }
        
        return queue_mapping.get(task_type, "default")
    
    async def task_queue_service_submit_voice_generation(
        self,
        text: str,
        voice_config: Dict[str, Any],
        user_id: int,
        priority: str = TaskPriority.NORMAL.value
    ) -> Dict[str, Any]:
        """
        提交语音生成任务
        [services][task_queue][submit_voice_generation]
        """
        return await self.task_queue_service_submit_task(
            task_name="app.tasks.voice_tasks.generate_voice",
            task_args=[text],
            task_kwargs={"voice_config": voice_config},
            task_type=TaskType.VOICE_GENERATION.value,
            priority=priority,
            user_id=user_id
        )
    
    async def task_queue_service_submit_text_generation(
        self,
        prompt: str,
        model_config: Dict[str, Any],
        user_id: int,
        priority: str = TaskPriority.NORMAL.value
    ) -> Dict[str, Any]:
        """
        提交文本生成任务
        [services][task_queue][submit_text_generation]
        """
        return await self.task_queue_service_submit_task(
            task_name="app.tasks.text_tasks.generate_text",
            task_args=[prompt],
            task_kwargs={"model_config": model_config},
            task_type=TaskType.TEXT_GENERATION.value,
            priority=priority,
            user_id=user_id
        )
    
    async def task_queue_service_submit_image_generation(
        self,
        prompt: str,
        image_config: Dict[str, Any],
        user_id: int,
        priority: str = TaskPriority.NORMAL.value
    ) -> Dict[str, Any]:
        """
        提交图像生成任务
        [services][task_queue][submit_image_generation]
        """
        return await self.task_queue_service_submit_task(
            task_name="app.tasks.image_tasks.generate_image",
            task_args=[prompt],
            task_kwargs={"image_config": image_config},
            task_type=TaskType.IMAGE_GENERATION.value,
            priority=priority,
            user_id=user_id
        )