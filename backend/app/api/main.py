"""
API Main Router
API主路由 - [api][main]
"""

from fastapi import APIRouter
from app.api.routes import auth, admin, files

# 创建主API路由器
api_router = APIRouter(prefix="/api/v1")

# 注册路由
api_router.include_router(auth.router)
api_router.include_router(admin.router)
api_router.include_router(files.router)