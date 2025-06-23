"""
Application Settings Configuration
应用配置管理 - [app][config][settings]
"""

from typing import List, Union
from pydantic import validator
from pydantic_settings import BaseSettings
import os
from functools import lru_cache

class AppConfigSettings(BaseSettings):
    """
    应用配置类
    [app][config][settings]
    """
    
    # 应用基础配置
    APP_NAME: str = "DataSay"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Frontend
        "http://localhost:3001",  # Admin UI
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]
    
    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://datasayai:datasayai123@localhost:5433/datasay"
    DATABASE_ECHO: bool = False
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    
    # Celery配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # JWT配置
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # 文件存储配置
    FILE_UPLOAD_MAX_SIZE: int = 100 * 1024 * 1024  # 100MB
    FILE_STORAGE_PATH: str = "/tmp/datasay/storage"
    FILE_ALLOWED_EXTENSIONS: List[str] = [
        ".txt", ".md", ".pdf",  # 文档
        ".wav", ".mp3", ".m4a", ".flac",  # 音频
        ".jpg", ".jpeg", ".png", ".gif", ".webp",  # 图像
        ".mp4", ".avi", ".mov", ".mkv"  # 视频
    ]
    
    # 豆包API配置
    VOLCANO_VOICE_APPID: str = "2393689094"
    VOLCANO_VOICE_ACCESS_TOKEN: str = "fQsIoCui-VRAhDKSG2uGPjkmK8GeZ8sr"
    VOLCANO_VOICE_CLUSTER: str = "volcano_icl"
    VOLCANO_API_BASE_URL: str = "https://openspeech.bytedance.com"
    
    # 安全配置
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "0.0.0.0"]
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @validator('CORS_ORIGINS', pre=True)
    def app_config_settings_validate_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """
        验证CORS来源配置
        [app][config][settings][validate_cors_origins]
        """
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def app_config_get_settings() -> AppConfigSettings:
    """
    获取应用配置单例
    [app][config][get_settings]
    """
    return AppConfigSettings()