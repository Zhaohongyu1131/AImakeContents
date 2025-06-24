"""
Error Handlers Module
错误处理模块 - [core][error_handlers]
"""

from typing import Dict, Any, Optional, Union
from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError
import logging
import traceback
from datetime import datetime

logger = logging.getLogger(__name__)


class AppError(Exception):
    """
    应用自定义错误基类
    [core][error_handlers][app_error]
    """
    def __init__(
        self, 
        message: str, 
        error_code: str = "APP_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class BusinessError(AppError):
    """
    业务逻辑错误
    [core][error_handlers][business_error]
    """
    def __init__(self, message: str, error_code: str = "BUSINESS_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, status.HTTP_400_BAD_REQUEST, details)


class ValidationError(AppError):
    """
    数据验证错误
    [core][error_handlers][validation_error]
    """
    def __init__(self, message: str, error_code: str = "VALIDATION_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, status.HTTP_422_UNPROCESSABLE_ENTITY, details)


class AuthenticationError(AppError):
    """
    认证错误
    [core][error_handlers][authentication_error]
    """
    def __init__(self, message: str = "认证失败", error_code: str = "AUTHENTICATION_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, status.HTTP_401_UNAUTHORIZED, details)


class AuthorizationError(AppError):
    """
    授权错误
    [core][error_handlers][authorization_error]
    """
    def __init__(self, message: str = "权限不足", error_code: str = "AUTHORIZATION_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, status.HTTP_403_FORBIDDEN, details)


class NotFoundError(AppError):
    """
    资源未找到错误
    [core][error_handlers][not_found_error]
    """
    def __init__(self, message: str = "资源未找到", error_code: str = "NOT_FOUND", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, status.HTTP_404_NOT_FOUND, details)


class ExternalAPIError(AppError):
    """
    外部API调用错误
    [core][error_handlers][external_api_error]
    """
    def __init__(self, message: str, api_name: str, error_code: str = "EXTERNAL_API_ERROR", details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details["api_name"] = api_name
        super().__init__(message, error_code, status.HTTP_502_BAD_GATEWAY, details)


def create_error_response(
    request: Request,
    status_code: int,
    error_code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    创建统一的错误响应
    [core][error_handlers][create_error_response]
    """
    error_id = f"ERR-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{id(request)}"
    
    response_body = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
            "details": details or {},
            "error_id": error_id,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path),
            "method": request.method
        }
    }
    
    # 记录错误日志
    logger.error(
        f"Error {error_id}: {error_code} - {message}",
        extra={
            "error_id": error_id,
            "status_code": status_code,
            "error_code": error_code,
            "path": str(request.url.path),
            "method": request.method,
            "details": details
        }
    )
    
    return JSONResponse(
        status_code=status_code,
        content=response_body
    )


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """
    处理应用自定义错误
    [core][error_handlers][app_error_handler]
    """
    return create_error_response(
        request=request,
        status_code=exc.status_code,
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details
    )


async def http_exception_handler(request: Request, exc: Union[HTTPException, StarletteHTTPException]) -> JSONResponse:
    """
    处理HTTP异常
    [core][error_handlers][http_exception_handler]
    """
    error_code = f"HTTP_{exc.status_code}"
    message = exc.detail if hasattr(exc, 'detail') else str(exc)
    
    return create_error_response(
        request=request,
        status_code=exc.status_code,
        error_code=error_code,
        message=message
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    处理请求验证错误
    [core][error_handlers][validation_exception_handler]
    """
    errors = []
    for error in exc.errors():
        error_detail = {
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        }
        errors.append(error_detail)
    
    return create_error_response(
        request=request,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_code="VALIDATION_ERROR",
        message="请求数据验证失败",
        details={"errors": errors}
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    处理SQLAlchemy数据库错误
    [core][error_handlers][sqlalchemy_exception_handler]
    """
    if isinstance(exc, IntegrityError):
        error_code = "DATABASE_INTEGRITY_ERROR"
        message = "数据完整性错误"
        status_code = status.HTTP_409_CONFLICT
    else:
        error_code = "DATABASE_ERROR"
        message = "数据库操作失败"
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    # 开发环境显示详细错误，生产环境隐藏
    details = {"error": str(exc)} if logger.level == logging.DEBUG else {}
    
    return create_error_response(
        request=request,
        status_code=status_code,
        error_code=error_code,
        message=message,
        details=details
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    处理未预期的异常
    [core][error_handlers][general_exception_handler]
    """
    # 记录完整的错误堆栈
    logger.error(
        f"Unexpected error: {str(exc)}",
        exc_info=True,
        extra={
            "path": str(request.url.path),
            "method": request.method,
            "traceback": traceback.format_exc()
        }
    )
    
    # 开发环境显示详细错误，生产环境隐藏
    details = {
        "error": str(exc),
        "type": type(exc).__name__
    } if logger.level == logging.DEBUG else {}
    
    return create_error_response(
        request=request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="INTERNAL_SERVER_ERROR",
        message="服务器内部错误",
        details=details
    )


def register_error_handlers(app):
    """
    注册所有错误处理器
    [core][error_handlers][register_error_handlers]
    """
    # 应用自定义错误
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(BusinessError, app_error_handler)
    app.add_exception_handler(ValidationError, app_error_handler)
    app.add_exception_handler(AuthenticationError, app_error_handler)
    app.add_exception_handler(AuthorizationError, app_error_handler)
    app.add_exception_handler(NotFoundError, app_error_handler)
    app.add_exception_handler(ExternalAPIError, app_error_handler)
    
    # HTTP异常
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    
    # 验证错误
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # 数据库错误
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    
    # 通用异常
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Error handlers registered successfully")