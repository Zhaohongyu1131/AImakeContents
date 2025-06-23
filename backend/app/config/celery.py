"""
Celery Configuration
Celery配置管理 - [celery][config]
"""

from celery import Celery
from app.config.settings import app_config_get_settings

settings = app_config_get_settings()

def celery_app_create() -> Celery:
    """
    创建Celery应用
    [celery][app][create]
    """
    celery_app = Celery(
        "datasay",
        broker=settings.CELERY_BROKER_URL,
        backend=settings.CELERY_RESULT_BACKEND,
        include=[
            'app.tasks.text_tasks',
            'app.tasks.voice_tasks', 
            'app.tasks.image_tasks',
            'app.tasks.mixall_tasks',
        ]
    )
    
    # Celery配置
    celery_app.conf.update(
        # 任务序列化
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='Asia/Shanghai',
        enable_utc=True,
        
        # 结果后端配置
        result_expires=3600,  # 结果保存1小时
        result_backend_transport_options={'retry_on_timeout': True},
        
        # 工作者配置
        worker_prefetch_multiplier=1,
        task_acks_late=True,
        worker_max_tasks_per_child=1000,
        
        # 任务路由
        task_routes={
            'app.tasks.text_tasks.*': {'queue': 'text_queue'},
            'app.tasks.voice_tasks.*': {'queue': 'voice_queue'},
            'app.tasks.image_tasks.*': {'queue': 'image_queue'},
            'app.tasks.mixall_tasks.*': {'queue': 'mixall_queue'},
        },
        
        # 重试配置
        task_default_retry_delay=60,  # 60秒后重试
        task_max_retries=3,
        
        # 监控配置
        worker_send_task_events=True,
        task_send_sent_event=True,
        
        # Beat调度器配置（用于定时任务）
        beat_schedule={
            'cleanup-expired-files': {
                'task': 'app.tasks.maintenance_tasks.cleanup_expired_files',
                'schedule': 3600.0,  # 每小时执行一次
            },
            'update-system-stats': {
                'task': 'app.tasks.maintenance_tasks.update_system_stats',
                'schedule': 300.0,  # 每5分钟执行一次
            },
        },
    )
    
    return celery_app

# 创建Celery应用实例
celery_app_instance = celery_app_create()

# 任务状态枚举
class CeleryTaskStatus:
    """
    Celery任务状态枚举
    [celery][task][status]
    """
    PENDING = 'PENDING'      # 等待中
    STARTED = 'STARTED'      # 已开始
    SUCCESS = 'SUCCESS'      # 成功
    FAILURE = 'FAILURE'      # 失败
    RETRY = 'RETRY'          # 重试中
    REVOKED = 'REVOKED'      # 已撤销

def celery_task_status_get(task_id: str) -> dict:
    """
    获取任务状态
    [celery][task][status_get]
    """
    result = celery_app_instance.AsyncResult(task_id)
    
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
        "info": result.info,
        "traceback": result.traceback,
        "ready": result.ready(),
        "successful": result.successful(),
        "failed": result.failed(),
    }

def celery_task_revoke(task_id: str, terminate: bool = False) -> bool:
    """
    撤销任务
    [celery][task][revoke]
    """
    try:
        celery_app_instance.control.revoke(task_id, terminate=terminate)
        return True
    except Exception:
        return False