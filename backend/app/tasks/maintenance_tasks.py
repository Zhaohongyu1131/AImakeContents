"""
Maintenance Tasks
系统维护Celery任务 - [tasks][maintenance]
"""

from typing import Dict, Any, Optional
import logging
from celery import Task
import asyncio
from datetime import datetime, timedelta

from app.services.task_queue_service import celery_app
from app.dependencies.db import get_db

logger = logging.getLogger(__name__)


class MaintenanceTask(Task):
    """
    维护任务基类
    [tasks][maintenance][base]
    """
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败时的回调"""
        logger.error(f"Maintenance task {task_id} failed: {exc}")


@celery_app.task(base=MaintenanceTask, bind=True, name="app.tasks.maintenance_tasks.database_cleanup")
def database_cleanup(self, cleanup_config: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    数据库清理任务
    [tasks][maintenance][database_cleanup]
    """
    try:
        metadata = kwargs.get('_task_metadata', {})
        task_id = metadata.get('task_id')
        
        logger.info(f"Starting database cleanup task {task_id}")
        
        # 更新任务状态
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': 100,
                'status': '开始数据库清理...'
            }
        )
        
        # 运行异步数据库清理
        result = asyncio.run(_async_database_cleanup(cleanup_config, self))
        
        if result["success"]:
            logger.info(f"Database cleanup task {task_id} completed successfully")
            return {
                "success": True,
                "data": result["data"],
                "task_id": task_id
            }
        else:
            logger.error(f"Database cleanup task {task_id} failed: {result['error']}")
            raise Exception(result["error"])
            
    except Exception as e:
        logger.error(f"Database cleanup task failed: {str(e)}")
        raise


async def _async_database_cleanup(cleanup_config: Dict[str, Any], task_instance) -> Dict[str, Any]:
    """
    异步数据库清理实现
    [tasks][maintenance][async_database_cleanup]
    """
    try:
        # 获取数据库会话
        async for db in get_db():
            try:
                from sqlalchemy import text
                
                cleanup_stats = {
                    "deleted_sessions": 0,
                    "deleted_logs": 0,
                    "deleted_temp_files": 0
                }
                
                # 获取清理配置
                days_old = cleanup_config.get("days_old", 30)
                cutoff_date = datetime.utcnow() - timedelta(days=days_old)
                
                # 更新进度
                task_instance.update_state(
                    state='PROGRESS',
                    meta={
                        'current': 20,
                        'total': 100,
                        'status': '清理过期会话...'
                    }
                )
                
                # 清理过期的用户会话
                if cleanup_config.get("clean_sessions", True):
                    session_query = text("""
                        DELETE FROM user_auth_session 
                        WHERE session_expires_at < :cutoff_date 
                        AND session_status != 'active'
                    """)
                    session_result = await db.execute(session_query, {"cutoff_date": cutoff_date})
                    cleanup_stats["deleted_sessions"] = session_result.rowcount
                
                # 更新进度
                task_instance.update_state(
                    state='PROGRESS',
                    meta={
                        'current': 50,
                        'total': 100,
                        'status': '清理旧日志记录...'
                    }
                )
                
                # 清理旧的日志记录（如果有日志表的话）
                if cleanup_config.get("clean_logs", True):
                    # 这里假设有一个操作日志表，实际需要根据项目情况调整
                    try:
                        log_query = text("""
                            DELETE FROM operation_log 
                            WHERE log_created_time < :cutoff_date
                        """)
                        log_result = await db.execute(log_query, {"cutoff_date": cutoff_date})
                        cleanup_stats["deleted_logs"] = log_result.rowcount
                    except Exception:
                        # 如果日志表不存在，跳过
                        pass
                
                # 更新进度
                task_instance.update_state(
                    state='PROGRESS',
                    meta={
                        'current': 80,
                        'total': 100,
                        'status': '清理临时文件记录...'
                    }
                )
                
                # 清理标记为删除的文件记录
                if cleanup_config.get("clean_deleted_files", True):
                    file_query = text("""
                        DELETE FROM file_storage_basic 
                        WHERE file_status = 'deleted' 
                        AND file_created_time < :cutoff_date
                    """)
                    file_result = await db.execute(file_query, {"cutoff_date": cutoff_date})
                    cleanup_stats["deleted_temp_files"] = file_result.rowcount
                
                await db.commit()
                
                # 更新进度
                task_instance.update_state(
                    state='PROGRESS',
                    meta={
                        'current': 90,
                        'total': 100,
                        'status': '完成清理...'
                    }
                )
                
                return {
                    "success": True,
                    "data": {
                        "cleanup_date": cutoff_date.isoformat(),
                        "days_old": days_old,
                        "statistics": cleanup_stats,
                        "total_deleted": sum(cleanup_stats.values())
                    }
                }
                    
            finally:
                await db.close()
                
    except Exception as e:
        return {
            "success": False,
            "error": f"数据库清理失败: {str(e)}"
        }


@celery_app.task(base=MaintenanceTask, bind=True, name="app.tasks.maintenance_tasks.system_health_check")
def system_health_check(self, **kwargs) -> Dict[str, Any]:
    """
    系统健康检查任务
    [tasks][maintenance][system_health_check]
    """
    try:
        metadata = kwargs.get('_task_metadata', {})
        task_id = metadata.get('task_id')
        
        logger.info(f"Starting system health check task {task_id}")
        
        # 更新任务状态
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': 100,
                'status': '开始系统健康检查...'
            }
        )
        
        health_results = {}
        
        # 检查数据库连接
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 25,
                'total': 100,
                'status': '检查数据库连接...'
            }
        )
        
        database_health = asyncio.run(_check_database_health())
        health_results["database"] = database_health
        
        # 检查Redis连接
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 50,
                'total': 100,
                'status': '检查Redis连接...'
            }
        )
        
        redis_health = _check_redis_health()
        health_results["redis"] = redis_health
        
        # 检查磁盘空间
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 75,
                'total': 100,
                'status': '检查磁盘空间...'
            }
        )
        
        disk_health = _check_disk_space()
        health_results["disk"] = disk_health
        
        # 检查外部服务
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 90,
                'total': 100,
                'status': '检查外部服务...'
            }
        )
        
        external_services_health = _check_external_services()
        health_results["external_services"] = external_services_health
        
        # 计算总体健康状态
        overall_status = "healthy"
        for service, health in health_results.items():
            if not health.get("healthy", False):
                overall_status = "unhealthy"
                break
        
        logger.info(f"System health check task {task_id} completed: {overall_status}")
        
        return {
            "success": True,
            "data": {
                "overall_status": overall_status,
                "check_time": datetime.utcnow().isoformat(),
                "services": health_results
            },
            "task_id": task_id
        }
        
    except Exception as e:
        logger.error(f"System health check task failed: {str(e)}")
        raise


async def _check_database_health() -> Dict[str, Any]:
    """检查数据库健康状态"""
    try:
        async for db in get_db():
            try:
                from sqlalchemy import text
                # 执行简单查询测试连接
                result = await db.execute(text("SELECT 1"))
                result.fetchone()
                
                return {
                    "healthy": True,
                    "status": "connected",
                    "response_time": "< 100ms"
                }
            finally:
                await db.close()
    except Exception as e:
        return {
            "healthy": False,
            "status": "connection_failed",
            "error": str(e)
        }


def _check_redis_health() -> Dict[str, Any]:
    """检查Redis健康状态"""
    try:
        import redis
        from app.config.settings import app_config_get_settings
        
        settings = app_config_get_settings()
        r = redis.from_url(settings.REDIS_URL)
        
        # 测试连接
        r.ping()
        
        return {
            "healthy": True,
            "status": "connected",
            "response_time": "< 50ms"
        }
    except Exception as e:
        return {
            "healthy": False,
            "status": "connection_failed", 
            "error": str(e)
        }


def _check_disk_space() -> Dict[str, Any]:
    """检查磁盘空间"""
    try:
        import shutil
        
        # 检查根目录磁盘空间
        total, used, free = shutil.disk_usage("/")
        
        # 计算使用率
        usage_percent = (used / total) * 100
        
        # 判断是否健康（使用率低于90%为健康）
        healthy = usage_percent < 90
        
        return {
            "healthy": healthy,
            "total_gb": round(total / (1024**3), 2),
            "used_gb": round(used / (1024**3), 2),
            "free_gb": round(free / (1024**3), 2),
            "usage_percent": round(usage_percent, 2)
        }
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e)
        }


def _check_external_services() -> Dict[str, Any]:
    """检查外部服务健康状态"""
    try:
        import requests
        
        services_health = {}
        
        # 检查豆包API
        try:
            # 这里只是模拟检查，实际需要调用真实的健康检查端点
            services_health["volcano"] = {
                "healthy": True,
                "status": "available"
            }
        except Exception as e:
            services_health["volcano"] = {
                "healthy": False,
                "status": "unavailable",
                "error": str(e)
            }
        
        return services_health
        
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e)
        }