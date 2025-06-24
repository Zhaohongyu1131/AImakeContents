"""
Logging Configuration Module
日志配置模块 - [core][logging_config]
"""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime
from pythonjsonlogger import jsonlogger

from app.config.settings import app_config_get_settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    自定义JSON日志格式化器
    [core][logging_config][custom_json_formatter]
    """
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # 添加时间戳
        if not log_record.get('timestamp'):
            now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record['timestamp'] = now
        
        # 添加日志级别
        log_record['level'] = record.levelname
        
        # 添加日志来源
        log_record['logger'] = record.name
        
        # 添加文件信息
        log_record['file'] = f"{record.filename}:{record.lineno}"
        
        # 添加函数名
        if record.funcName:
            log_record['function'] = record.funcName


def get_logging_config() -> Dict[str, Any]:
    """
    获取日志配置
    [core][logging_config][get_logging_config]
    """
    settings = app_config_get_settings()
    
    # 确保日志目录存在
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "json": {
                "()": CustomJsonFormatter,
                "format": "%(timestamp)s %(level)s %(name)s %(message)s"
            }
        },
        "filters": {
            "request_id": {
                "()": "app.core.logging_config.RequestIdFilter"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "default",
                "stream": sys.stdout,
                "filters": ["request_id"]
            },
            "file_app": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "json",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8",
                "filters": ["request_id"]
            },
            "file_error": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "json",
                "filename": "logs/error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8",
                "filters": ["request_id"]
            },
            "file_access": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "json",
                "filename": "logs/access.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8"
            }
        },
        "loggers": {
            "app": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file_app"],
                "propagate": False
            },
            "app.api": {
                "level": "INFO",
                "handlers": ["console", "file_app", "file_access"],
                "propagate": False
            },
            "app.errors": {
                "level": "ERROR",
                "handlers": ["console", "file_error"],
                "propagate": False
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["console", "file_error"],
                "propagate": False
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["file_access"],
                "propagate": False
            },
            "sqlalchemy": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False
            },
            "sqlalchemy.engine": {
                "level": "WARNING" if not settings.DATABASE_ECHO else "INFO",
                "handlers": ["console"],
                "propagate": False
            }
        },
        "root": {
            "level": settings.LOG_LEVEL,
            "handlers": ["console", "file_app"]
        }
    }


class RequestIdFilter(logging.Filter):
    """
    请求ID过滤器
    [core][logging_config][request_id_filter]
    """
    def filter(self, record):
        # 从上下文中获取请求ID
        import contextvars
        request_id_var = contextvars.ContextVar('request_id', default=None)
        request_id = request_id_var.get()
        
        if request_id:
            record.request_id = request_id
        
        return True


def setup_logging():
    """
    设置日志配置
    [core][logging_config][setup_logging]
    """
    config = get_logging_config()
    logging.config.dictConfig(config)
    
    logger = logging.getLogger(__name__)
    logger.info("Logging configuration initialized")


class LoggerMixin:
    """
    日志混入类
    [core][logging_config][logger_mixin]
    """
    @property
    def logger(self):
        """获取类专用的日志记录器"""
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        return self._logger


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器
    [core][logging_config][get_logger]
    """
    return logging.getLogger(name)