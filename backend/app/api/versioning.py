"""
API Version Management Module
API版本管理模块 - [api][versioning]
"""

from typing import Dict, List, Optional, Tuple
from fastapi import Request, HTTPException, status
from fastapi.routing import APIRoute
from packaging import version
import logging
from datetime import datetime, date

from app.core.logging_config import get_logger

logger = get_logger("app.api.versioning")


class APIVersion:
    """
    API版本信息类
    [api][versioning][api_version]
    """
    
    def __init__(
        self,
        version: str,
        is_supported: bool = True,
        is_deprecated: bool = False,
        deprecation_date: Optional[date] = None,
        sunset_date: Optional[date] = None,
        changelog: Optional[str] = None
    ):
        self.version = version
        self.is_supported = is_supported
        self.is_deprecated = is_deprecated
        self.deprecation_date = deprecation_date
        self.sunset_date = sunset_date
        self.changelog = changelog
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "version": self.version,
            "is_supported": self.is_supported,
            "is_deprecated": self.is_deprecated,
            "deprecation_date": self.deprecation_date.isoformat() if self.deprecation_date else None,
            "sunset_date": self.sunset_date.isoformat() if self.sunset_date else None,
            "changelog": self.changelog
        }


class APIVersionManager:
    """
    API版本管理器
    [api][versioning][api_version_manager]
    """
    
    def __init__(self):
        self.versions: Dict[str, APIVersion] = {}
        self.default_version = "v1"
        self.supported_versions = {"v1"}
        
        # 初始化版本信息
        self._api_version_manager_initialize_versions()
    
    def _api_version_manager_initialize_versions(self):
        """
        初始化支持的API版本
        [api][versioning][api_version_manager][initialize_versions]
        """
        # v1 - 当前稳定版本
        self.versions["v1"] = APIVersion(
            version="v1",
            is_supported=True,
            is_deprecated=False,
            changelog="Initial stable release with core functionality"
        )
        
        # 可以添加更多版本
        # self.versions["v2"] = APIVersion(
        #     version="v2",
        #     is_supported=False,
        #     is_deprecated=False,
        #     changelog="Enhanced features and performance improvements"
        # )
    
    def api_version_manager_get_version_from_request(self, request: Request) -> str:
        """
        从请求中提取API版本
        [api][versioning][api_version_manager][get_version_from_request]
        """
        # 方法1: 从URL路径中提取 (如 /api/v1/users)
        path_parts = request.url.path.strip("/").split("/")
        if len(path_parts) >= 2 and path_parts[0] == "api":
            version_part = path_parts[1]
            if version_part.startswith("v") and version_part[1:].isdigit():
                return version_part
        
        # 方法2: 从Header中提取
        api_version = request.headers.get("API-Version")
        if api_version:
            return api_version
        
        # 方法3: 从查询参数中提取
        version_param = request.query_params.get("version")
        if version_param:
            return version_param
        
        # 方法4: 从Accept Header中提取 (如 Accept: application/vnd.datasay.v1+json)
        accept_header = request.headers.get("Accept", "")
        if "vnd.datasay." in accept_header:
            try:
                version_part = accept_header.split("vnd.datasay.")[1].split("+")[0]
                return version_part
            except (IndexError, AttributeError):
                pass
        
        # 默认版本
        return self.default_version
    
    def api_version_manager_validate_version(self, version: str) -> Tuple[bool, Optional[str]]:
        """
        验证API版本是否有效
        [api][versioning][api_version_manager][validate_version]
        """
        if version not in self.versions:
            return False, f"API version '{version}' is not recognized"
        
        version_info = self.versions[version]
        
        if not version_info.is_supported:
            return False, f"API version '{version}' is no longer supported"
        
        # 检查是否过期
        if version_info.sunset_date and datetime.now().date() > version_info.sunset_date:
            return False, f"API version '{version}' has been sunset"
        
        return True, None
    
    def api_version_manager_get_version_info(self, version: str) -> Optional[APIVersion]:
        """
        获取版本信息
        [api][versioning][api_version_manager][get_version_info]
        """
        return self.versions.get(version)
    
    def api_version_manager_get_all_versions(self) -> Dict[str, Dict]:
        """
        获取所有版本信息
        [api][versioning][api_version_manager][get_all_versions]
        """
        return {v: info.to_dict() for v, info in self.versions.items()}
    
    def api_version_manager_get_supported_versions(self) -> List[str]:
        """
        获取支持的版本列表
        [api][versioning][api_version_manager][get_supported_versions]
        """
        return [v for v, info in self.versions.items() if info.is_supported]
    
    def api_version_manager_add_version(self, version_info: APIVersion):
        """
        添加新版本
        [api][versioning][api_version_manager][add_version]
        """
        self.versions[version_info.version] = version_info
        if version_info.is_supported:
            self.supported_versions.add(version_info.version)
        
        logger.info(f"Added API version: {version_info.version}")
    
    def api_version_manager_deprecate_version(
        self, 
        version: str, 
        deprecation_date: Optional[date] = None,
        sunset_date: Optional[date] = None
    ):
        """
        废弃版本
        [api][versioning][api_version_manager][deprecate_version]
        """
        if version in self.versions:
            self.versions[version].is_deprecated = True
            if deprecation_date:
                self.versions[version].deprecation_date = deprecation_date
            if sunset_date:
                self.versions[version].sunset_date = sunset_date
            
            logger.info(f"Deprecated API version: {version}")
    
    def api_version_manager_remove_version(self, version: str):
        """
        移除版本支持
        [api][versioning][api_version_manager][remove_version]
        """
        if version in self.versions:
            self.versions[version].is_supported = False
            self.supported_versions.discard(version)
            
            logger.info(f"Removed support for API version: {version}")


# 全局版本管理器
api_version_manager = APIVersionManager()


def api_versioning_create_version_middleware():
    """
    创建版本检查中间件
    [api][versioning][create_version_middleware]
    """
    async def version_middleware(request: Request, call_next):
        """API版本检查中间件"""
        
        # 跳过非API路径
        if not request.url.path.startswith("/api/"):
            return await call_next(request)
        
        # 获取请求的API版本
        requested_version = api_version_manager.api_version_manager_get_version_from_request(request)
        
        # 验证版本
        is_valid, error_message = api_version_manager.api_version_manager_validate_version(requested_version)
        
        if not is_valid:
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error": {
                        "code": "INVALID_API_VERSION",
                        "message": error_message,
                        "supported_versions": api_version_manager.api_version_manager_get_supported_versions()
                    }
                }
            )
        
        # 获取版本信息并添加到请求状态
        version_info = api_version_manager.api_version_manager_get_version_info(requested_version)
        request.state.api_version = requested_version
        request.state.api_version_info = version_info
        
        # 处理请求
        response = await call_next(request)
        
        # 添加版本相关的响应头
        response.headers["API-Version"] = requested_version
        
        # 如果版本已废弃，添加警告头
        if version_info and version_info.is_deprecated:
            warning_msg = f"API version {requested_version} is deprecated"
            if version_info.sunset_date:
                warning_msg += f" and will be sunset on {version_info.sunset_date}"
            response.headers["Warning"] = f'299 - "{warning_msg}"'
        
        return response
    
    return version_middleware


class VersionedAPIRoute(APIRoute):
    """
    支持版本控制的API路由
    [api][versioning][versioned_api_route]
    """
    
    def __init__(self, *args, min_version: str = "v1", max_version: Optional[str] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.min_version = min_version
        self.max_version = max_version
    
    def matches(self, scope) -> Tuple[bool, str]:
        """检查路由是否匹配当前请求"""
        match, child_scope = super().matches(scope)
        
        if not match:
            return False, child_scope
        
        # 检查版本兼容性
        request_version = scope.get("state", {}).get("api_version", "v1")
        
        # 解析版本号
        try:
            current_version = version.parse(request_version.lstrip("v"))
            min_ver = version.parse(self.min_version.lstrip("v"))
            
            if current_version < min_ver:
                return False, child_scope
            
            if self.max_version:
                max_ver = version.parse(self.max_version.lstrip("v"))
                if current_version > max_ver:
                    return False, child_scope
                    
        except Exception as e:
            logger.warning(f"Error parsing version: {e}")
            return False, child_scope
        
        return True, child_scope


def api_versioning_require_version(min_version: str = "v1", max_version: Optional[str] = None):
    """
    版本要求装饰器
    [api][versioning][require_version]
    """
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            current_version = getattr(request.state, "api_version", "v1")
            
            # 检查最低版本要求
            try:
                current_ver = version.parse(current_version.lstrip("v"))
                min_ver = version.parse(min_version.lstrip("v"))
                
                if current_ver < min_ver:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "success": False,
                            "error": {
                                "code": "VERSION_TOO_LOW",
                                "message": f"This endpoint requires API version {min_version} or higher",
                                "current_version": current_version,
                                "required_version": min_version
                            }
                        }
                    )
                
                # 检查最高版本限制
                if max_version:
                    max_ver = version.parse(max_version.lstrip("v"))
                    if current_ver > max_ver:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail={
                                "success": False,
                                "error": {
                                    "code": "VERSION_TOO_HIGH",
                                    "message": f"This endpoint is not supported in API version {current_version}",
                                    "current_version": current_version,
                                    "max_supported_version": max_version
                                }
                            }
                        )
                        
            except Exception as e:
                logger.error(f"Version validation error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "success": False,
                        "error": {
                            "code": "VERSION_VALIDATION_ERROR",
                            "message": "Failed to validate API version"
                        }
                    }
                )
            
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator