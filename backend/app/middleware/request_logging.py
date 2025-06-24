"""
Request Logging Middleware
请求日志记录中间件 - [middleware][request_logging]
"""

import time
import uuid
import json
import contextvars
from typing import Callable, Optional, Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
import logging

from app.core.logging_config import get_logger

# 请求ID上下文变量
request_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('request_id', default=None)

logger = get_logger("app.middleware.request_logging")
access_logger = get_logger("app.api")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志记录中间件
    [middleware][request_logging][middleware]
    """
    
    def __init__(
        self,
        app,
        skip_paths: Optional[list] = None,
        log_request_body: bool = False,
        log_response_body: bool = False,
        max_body_size: int = 1024
    ):
        super().__init__(app)
        self.skip_paths = skip_paths or ["/health", "/metrics", "/docs", "/redoc", "/openapi.json"]
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.max_body_size = max_body_size
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求并记录日志
        [middleware][request_logging][dispatch]
        """
        # 生成请求ID
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)
        
        # 检查是否跳过日志记录
        if any(request.url.path.startswith(path) for path in self.skip_paths):
            return await call_next(request)
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取客户端信息
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        # 准备请求日志数据
        request_log_data = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": client_ip,
            "user_agent": user_agent,
            "headers": dict(request.headers),
            "start_time": start_time
        }
        
        # 记录请求体（如果启用）
        if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
            request_body = await self._get_request_body(request)
            if request_body:
                request_log_data["request_body"] = request_body
        
        # 记录请求开始
        access_logger.info("Request started", extra=request_log_data)
        
        # 处理响应
        response = None
        error = None
        
        try:
            response = await call_next(request)
        except Exception as e:
            error = e
            # 创建错误响应
            from fastapi.responses import JSONResponse
            response = JSONResponse(
                status_code=500,
                content={"success": False, "error": "Internal Server Error"}
            )
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 准备响应日志数据
        response_log_data = {
            "request_id": request_id,
            "status_code": response.status_code,
            "process_time": round(process_time * 1000, 2),  # 毫秒
            "response_size": self._get_response_size(response)
        }
        
        # 记录响应体（如果启用且不是流式响应）
        if self.log_response_body and not isinstance(response, StreamingResponse):
            response_body = await self._get_response_body(response)
            if response_body:
                response_log_data["response_body"] = response_body
        
        # 添加错误信息
        if error:
            response_log_data["error"] = str(error)
            response_log_data["error_type"] = type(error).__name__
        
        # 记录响应完成
        log_level = "ERROR" if response.status_code >= 500 else "WARNING" if response.status_code >= 400 else "INFO"
        getattr(access_logger, log_level.lower())("Request completed", extra=response_log_data)
        
        # 添加响应头
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """
        获取客户端真实IP
        [middleware][request_logging][get_client_ip]
        """
        # 检查代理头
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # 使用客户端IP
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return "unknown"
    
    async def _get_request_body(self, request: Request) -> Optional[str]:
        """
        获取请求体内容
        [middleware][request_logging][get_request_body]
        """
        try:
            body = await request.body()
            if len(body) > self.max_body_size:
                return f"[Body too large: {len(body)} bytes]"
            
            # 尝试解析为JSON
            try:
                content_type = request.headers.get("content-type", "")
                if "application/json" in content_type:
                    return json.loads(body.decode("utf-8"))
                else:
                    return body.decode("utf-8")[:self.max_body_size]
            except (json.JSONDecodeError, UnicodeDecodeError):
                return f"[Binary content: {len(body)} bytes]"
        except Exception:
            return None
    
    def _get_response_size(self, response: Response) -> Optional[int]:
        """
        获取响应大小
        [middleware][request_logging][get_response_size]
        """
        try:
            content_length = response.headers.get("content-length")
            if content_length:
                return int(content_length)
        except (ValueError, TypeError):
            pass
        return None
    
    async def _get_response_body(self, response: Response) -> Optional[Any]:
        """
        获取响应体内容
        [middleware][request_logging][get_response_body]
        """
        try:
            if hasattr(response, 'body'):
                body = response.body
                if isinstance(body, bytes):
                    if len(body) > self.max_body_size:
                        return f"[Response too large: {len(body)} bytes]"
                    
                    try:
                        return json.loads(body.decode("utf-8"))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        return body.decode("utf-8")[:self.max_body_size]
        except Exception:
            pass
        return None


def add_request_logging_middleware(app, **kwargs):
    """
    添加请求日志记录中间件
    [middleware][request_logging][add_middleware]
    """
    app.add_middleware(RequestLoggingMiddleware, **kwargs)
    logger.info("Request logging middleware added")