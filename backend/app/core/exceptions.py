"""
Exception Handlers
异常处理器 - [app][exception][handler]
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Union
import traceback
import logging

logger = logging.getLogger(__name__)

class AppExceptionBase(Exception):
    """
    应用基础异常类
    [app][exception][base]
    """
    def __init__(self, message: str, code: int = 500, details: str = None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.message)

class AppExceptionValidation(AppExceptionBase):
    """
    数据验证异常
    [app][exception][validation]
    """
    def __init__(self, message: str = "数据验证失败", details: str = None):
        super().__init__(message, 422, details)

class AppExceptionNotFound(AppExceptionBase):
    """
    资源不存在异常
    [app][exception][not_found]
    """
    def __init__(self, message: str = "资源不存在", details: str = None):
        super().__init__(message, 404, details)

class AppExceptionUnauthorized(AppExceptionBase):
    """
    未授权异常
    [app][exception][unauthorized]
    """
    def __init__(self, message: str = "未授权访问", details: str = None):
        super().__init__(message, 401, details)

class AppExceptionForbidden(AppExceptionBase):
    """
    权限不足异常
    [app][exception][forbidden]
    """
    def __init__(self, message: str = "权限不足", details: str = None):
        super().__init__(message, 403, details)

class AppExceptionBusinessLogic(AppExceptionBase):
    """
    业务逻辑异常
    [app][exception][business_logic]
    """
    def __init__(self, message: str = "业务逻辑错误", details: str = None):
        super().__init__(message, 400, details)

async def app_exception_handler_base(request: Request, exc: AppExceptionBase):
    """
    基础异常处理器
    [app][exception][handler][base]
    """
    return JSONResponse(
        status_code=exc.code,
        content={
            "success": False,
            "code": exc.code,
            "message": exc.message,
            "error": {
                "type": exc.__class__.__name__,
                "details": exc.details
            },
            "timestamp": str(request.url),
            "request_id": getattr(request.state, "request_id", None)
        }
    )

async def app_exception_handler_http(request: Request, exc: Union[HTTPException, StarletteHTTPException]):
    """
    HTTP异常处理器
    [app][exception][handler][http]
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "code": exc.status_code,
            "message": exc.detail,
            "error": {
                "type": "HTTPException",
                "details": None
            },
            "timestamp": str(request.url),
            "request_id": getattr(request.state, "request_id", None)
        }
    )

async def app_exception_handler_validation(request: Request, exc: RequestValidationError):
    """
    请求验证异常处理器
    [app][exception][handler][validation]
    """
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "code": 422,
            "message": "请求参数验证失败",
            "error": {
                "type": "ValidationError",
                "details": exc.errors()
            },
            "timestamp": str(request.url),
            "request_id": getattr(request.state, "request_id", None)
        }
    )

async def app_exception_handler_general(request: Request, exc: Exception):
    """
    通用异常处理器
    [app][exception][handler][general]
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "code": 500,
            "message": "服务器内部错误",
            "error": {
                "type": "InternalServerError",
                "details": str(exc) if logger.isEnabledFor(logging.DEBUG) else None
            },
            "timestamp": str(request.url),
            "request_id": getattr(request.state, "request_id", None)
        }
    )

def app_exception_handler_register(app: FastAPI):
    """
    注册异常处理器
    [app][exception][handler][register]
    """
    app.add_exception_handler(AppExceptionBase, app_exception_handler_base)
    app.add_exception_handler(HTTPException, app_exception_handler_http)
    app.add_exception_handler(StarletteHTTPException, app_exception_handler_http)
    app.add_exception_handler(RequestValidationError, app_exception_handler_validation)
    app.add_exception_handler(Exception, app_exception_handler_general)