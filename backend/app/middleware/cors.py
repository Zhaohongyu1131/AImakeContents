"""
CORS Middleware
跨域资源共享中间件 - [middleware][cors]
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import app_config_get_settings

def cors_middleware_add(app: FastAPI) -> None:
    """
    添加CORS中间件
    [middleware][cors][add]
    """
    settings = app_config_get_settings()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-Request-ID",
            "X-User-Agent",
            "X-API-Key"
        ],
        expose_headers=[
            "X-Request-ID",
            "X-Response-Time",
            "X-Rate-Limit-Remaining",
            "X-Rate-Limit-Reset"
        ]
    )