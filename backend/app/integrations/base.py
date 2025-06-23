"""
Base Integration Class
第三方服务集成基类 - [integrations][base]
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import asyncio
import aiohttp
import logging


class IntegrationStatus(Enum):
    """
    集成状态枚举
    [integrations][base][integration_status]
    """
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    MAINTENANCE = "maintenance"


@dataclass
class IntegrationError(Exception):
    """
    集成错误类
    [integrations][base][integration_error]
    """
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    retry_after: Optional[int] = None
    
    def __str__(self) -> str:
        return f"IntegrationError({self.code}): {self.message}"


@dataclass
class IntegrationResponse:
    """
    集成响应类
    [integrations][base][integration_response]
    """
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[IntegrationError] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def success_response(cls, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """创建成功响应"""
        return cls(success=True, data=data, metadata=metadata)
    
    @classmethod
    def error_response(cls, error: IntegrationError, metadata: Optional[Dict[str, Any]] = None):
        """创建错误响应"""
        return cls(success=False, error=error, metadata=metadata)


class IntegrationBase(ABC):
    """
    第三方服务集成基类
    [integrations][base]
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化集成基类
        [integrations][base][init]
        """
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self.status = IntegrationStatus.INACTIVE
        self.session: Optional[aiohttp.ClientSession] = None
        
        # 基础配置
        self.base_url = config.get("base_url", "")
        self.api_key = config.get("api_key", "")
        self.timeout = config.get("timeout", 30)
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay = config.get("retry_delay", 1)
        
        # 速率限制配置
        self.rate_limit_enabled = config.get("rate_limit_enabled", True)
        self.requests_per_minute = config.get("requests_per_minute", 60)
        self.requests_per_second = config.get("requests_per_second", 10)
        
        # 内部状态
        self._request_history = []
        self._last_request_time = 0
    
    async def integration_base_initialize(self) -> bool:
        """
        初始化集成
        [integrations][base][initialize]
        """
        try:
            # 创建HTTP会话
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers=self._get_default_headers()
            )
            
            # 执行健康检查
            if await self.integration_base_health_check():
                self.status = IntegrationStatus.ACTIVE
                self.logger.info(f"{self.__class__.__name__} integration initialized successfully")
                return True
            else:
                self.status = IntegrationStatus.ERROR
                self.logger.error(f"{self.__class__.__name__} health check failed")
                return False
                
        except Exception as e:
            self.status = IntegrationStatus.ERROR
            self.logger.error(f"Failed to initialize {self.__class__.__name__}: {str(e)}")
            return False
    
    async def integration_base_cleanup(self):
        """
        清理资源
        [integrations][base][cleanup]
        """
        if self.session:
            await self.session.close()
            self.session = None
        
        self.status = IntegrationStatus.INACTIVE
        self.logger.info(f"{self.__class__.__name__} integration cleaned up")
    
    async def integration_base_health_check(self) -> bool:
        """
        健康检查
        [integrations][base][health_check]
        """
        try:
            response = await self._make_request("GET", "/health", timeout=5)
            return response.success
        except Exception:
            return False
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        retry_count: int = 0
    ) -> IntegrationResponse:
        """
        发起HTTP请求
        [integrations][base][_make_request]
        """
        if not self.session:
            raise IntegrationError(
                code="SESSION_NOT_INITIALIZED",
                message="HTTP session not initialized"
            )
        
        # 速率限制检查
        await self._check_rate_limit()
        
        # 构建请求URL
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # 合并请求头
        request_headers = self._get_default_headers()
        if headers:
            request_headers.update(headers)
        
        # 设置超时
        request_timeout = timeout or self.timeout
        
        try:
            self.logger.debug(f"Making {method} request to {url}")
            
            async with self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=request_headers,
                timeout=aiohttp.ClientTimeout(total=request_timeout)
            ) as response:
                
                # 记录请求历史
                self._record_request()
                
                # 处理响应
                return await self._handle_response(response)
                
        except asyncio.TimeoutError:
            error = IntegrationError(
                code="REQUEST_TIMEOUT",
                message=f"Request timeout after {request_timeout}s"
            )
            
            # 重试逻辑
            if retry_count < self.max_retries:
                self.logger.warning(f"Request timeout, retrying {retry_count + 1}/{self.max_retries}")
                await asyncio.sleep(self.retry_delay * (retry_count + 1))
                return await self._make_request(
                    method, endpoint, data, params, headers, timeout, retry_count + 1
                )
            
            return IntegrationResponse.error_response(error)
            
        except aiohttp.ClientError as e:
            error = IntegrationError(
                code="CLIENT_ERROR",
                message=f"HTTP client error: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
            
        except Exception as e:
            error = IntegrationError(
                code="UNEXPECTED_ERROR",
                message=f"Unexpected error: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
    async def _handle_response(self, response: aiohttp.ClientResponse) -> IntegrationResponse:
        """
        处理HTTP响应
        [integrations][base][_handle_response]
        """
        try:
            # 读取响应内容
            content_type = response.headers.get('content-type', '')
            
            if 'application/json' in content_type:
                response_data = await response.json()
            else:
                response_text = await response.text()
                response_data = {"content": response_text}
            
            # 检查HTTP状态码
            if 200 <= response.status < 300:
                return IntegrationResponse.success_response(
                    data=response_data,
                    metadata={
                        "status_code": response.status,
                        "headers": dict(response.headers)
                    }
                )
            
            elif response.status == 429:
                # 速率限制
                retry_after = int(response.headers.get('retry-after', 60))
                error = IntegrationError(
                    code="RATE_LIMITED",
                    message="API rate limit exceeded",
                    retry_after=retry_after
                )
                self.status = IntegrationStatus.RATE_LIMITED
                return IntegrationResponse.error_response(error)
            
            elif 400 <= response.status < 500:
                # 客户端错误
                error = IntegrationError(
                    code="CLIENT_ERROR",
                    message=f"Client error: {response.status}",
                    details=response_data
                )
                return IntegrationResponse.error_response(error)
            
            elif 500 <= response.status < 600:
                # 服务器错误
                error = IntegrationError(
                    code="SERVER_ERROR",
                    message=f"Server error: {response.status}",
                    details=response_data
                )
                return IntegrationResponse.error_response(error)
            
            else:
                error = IntegrationError(
                    code="UNKNOWN_STATUS",
                    message=f"Unknown status code: {response.status}",
                    details=response_data
                )
                return IntegrationResponse.error_response(error)
                
        except Exception as e:
            error = IntegrationError(
                code="RESPONSE_PARSE_ERROR",
                message=f"Failed to parse response: {str(e)}"
            )
            return IntegrationResponse.error_response(error)
    
    def _get_default_headers(self) -> Dict[str, str]:
        """
        获取默认请求头
        [integrations][base][_get_default_headers]
        """
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"DataSay/{self.__class__.__name__}",
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        return headers
    
    async def _check_rate_limit(self):
        """
        检查速率限制
        [integrations][base][_check_rate_limit]
        """
        if not self.rate_limit_enabled:
            return
        
        import time
        current_time = time.time()
        
        # 清理过期的请求记录
        cutoff_time = current_time - 60  # 保留最近1分钟的记录
        self._request_history = [
            timestamp for timestamp in self._request_history 
            if timestamp > cutoff_time
        ]
        
        # 检查每分钟请求数限制
        if len(self._request_history) >= self.requests_per_minute:
            sleep_time = 60 - (current_time - self._request_history[0])
            if sleep_time > 0:
                self.logger.warning(f"Rate limit reached, sleeping for {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)
        
        # 检查每秒请求数限制
        recent_requests = [
            timestamp for timestamp in self._request_history 
            if timestamp > current_time - 1
        ]
        
        if len(recent_requests) >= self.requests_per_second:
            sleep_time = 1 - (current_time - recent_requests[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
    
    def _record_request(self):
        """
        记录请求时间
        [integrations][base][_record_request]
        """
        import time
        current_time = time.time()
        self._request_history.append(current_time)
        self._last_request_time = current_time
    
    def integration_base_get_status(self) -> Dict[str, Any]:
        """
        获取集成状态
        [integrations][base][get_status]
        """
        import time
        return {
            "status": self.status.value,
            "last_request_time": self._last_request_time,
            "requests_in_last_minute": len([
                timestamp for timestamp in self._request_history 
                if timestamp > time.time() - 60
            ]),
            "config": {
                "base_url": self.base_url,
                "timeout": self.timeout,
                "max_retries": self.max_retries,
                "rate_limit_enabled": self.rate_limit_enabled
            }
        }
    
    @abstractmethod
    async def test_connection(self) -> IntegrationResponse:
        """
        测试连接
        [integrations][base][test_connection]
        """
        pass
    
    @abstractmethod
    async def get_service_info(self) -> IntegrationResponse:
        """
        获取服务信息
        [integrations][base][get_service_info]
        """
        pass