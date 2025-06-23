"""
Error Handler Middleware
错误处理中间件 - [middleware][error]
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from typing import Union
from app.schemas.base import ErrorSchema

logger = logging.getLogger(__name__)

def error_handler_add(app: FastAPI) -> None:
    """
    添加错误处理中间件
    [middleware][error][add]
    """
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        HTTP异常处理器
        [middleware][error][http_exception_handler]
        """
        logger.warning(f"HTTP异常: {exc.status_code} - {exc.detail}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorSchema(
                success=False,
                message=str(exc.detail),
                error_code=f"HTTP_{exc.status_code}",
                error_detail={
                    "status_code": exc.status_code,
                    "path": str(request.url.path),
                    "method": request.method
                }
            ).dict()
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
        """
        Starlette HTTP异常处理器
        [middleware][error][starlette_http_exception_handler]
        """
        logger.warning(f"Starlette HTTP异常: {exc.status_code} - {exc.detail}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorSchema(
                success=False,
                message=str(exc.detail),
                error_code=f"HTTP_{exc.status_code}",
                error_detail={
                    "status_code": exc.status_code,
                    "path": str(request.url.path),
                    "method": request.method
                }
            ).dict()
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        请求验证异常处理器
        [middleware][error][validation_exception_handler]
        """
        logger.warning(f"请求验证异常: {exc}")
        
        # 格式化验证错误信息
        error_details = []
        for error in exc.errors():
            error_details.append({
                "field": " -> ".join([str(loc) for loc in error["loc"]]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        return JSONResponse(
            status_code=422,
            content=ErrorSchema(
                success=False,
                message="请求参数验证失败",
                error_code="VALIDATION_ERROR",
                error_detail={
                    "errors": error_details,
                    "path": str(request.url.path),
                    "method": request.method
                }
            ).dict()
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        通用异常处理器
        [middleware][error][general_exception_handler]
        """
        logger.error(f"未处理的异常: {type(exc).__name__}: {str(exc)}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content=ErrorSchema(
                success=False,
                message="服务器内部错误",
                error_code="INTERNAL_SERVER_ERROR",
                error_detail={
                    "exception_type": type(exc).__name__,
                    "path": str(request.url.path),
                    "method": request.method
                }
            ).dict()
        )

class BusinessException(Exception):
    """
    业务异常基类
    [middleware][error][business_exception]
    """
    
    def __init__(self, message: str, error_code: str = "BUSINESS_ERROR", status_code: int = 400):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)

class AuthenticationException(BusinessException):
    """
    认证异常
    [middleware][error][authentication_exception]
    """
    
    def __init__(self, message: str = "认证失败"):
        super().__init__(message, "AUTHENTICATION_ERROR", 401)

class AuthorizationException(BusinessException):
    """
    授权异常
    [middleware][error][authorization_exception]
    """
    
    def __init__(self, message: str = "权限不足"):
        super().__init__(message, "AUTHORIZATION_ERROR", 403)

class ResourceNotFoundException(BusinessException):
    """
    资源未找到异常
    [middleware][error][resource_not_found_exception]
    """
    
    def __init__(self, message: str = "资源未找到"):
        super().__init__(message, "RESOURCE_NOT_FOUND", 404)

class DuplicateResourceException(BusinessException):
    """
    重复资源异常
    [middleware][error][duplicate_resource_exception]
    """
    
    def __init__(self, message: str = "资源已存在"):
        super().__init__(message, "DUPLICATE_RESOURCE", 409)

class RateLimitException(BusinessException):
    """
    限流异常
    [middleware][error][rate_limit_exception]
    """
    
    def __init__(self, message: str = "请求过于频繁"):
        super().__init__(message, "RATE_LIMIT_EXCEEDED", 429)