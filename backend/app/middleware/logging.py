"""
Logging Middleware
日志记录中间件 - [middleware][logging]
"""

from fastapi import FastAPI, Request, Response
import time
import uuid
import logging
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志中间件
    [middleware][logging][middleware]
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求日志
        [middleware][logging][dispatch]
        """
        # 生成请求ID
        request_id = str(uuid.uuid4())
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取客户端信息
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # 记录请求信息
        logger.info(
            f"请求开始 - ID: {request_id}, "
            f"方法: {request.method}, "
            f"路径: {request.url.path}, "
            f"客户端IP: {client_ip}, "
            f"User-Agent: {user_agent}"
        )
        
        # 设置请求ID到请求状态
        request.state.request_id = request_id
        
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 添加响应头
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{process_time:.4f}s"
        
        # 记录响应信息
        logger.info(
            f"请求完成 - ID: {request_id}, "
            f"状态码: {response.status_code}, "
            f"处理时间: {process_time:.4f}s"
        )
        
        return response

def logging_middleware_add(app: FastAPI) -> None:
    """
    添加日志中间件
    [middleware][logging][add]
    """
    app.add_middleware(LoggingMiddleware)