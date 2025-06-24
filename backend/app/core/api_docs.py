"""
API Documentation Generator
API文档生成器 - [core][api_docs]
"""

import json
from typing import Dict, Any, List, Optional
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse
import logging

from app.config.settings import app_config_get_settings
from app.core.logging_config import get_logger

logger = get_logger("app.core.api_docs")


def api_docs_generate_custom_openapi(app: FastAPI) -> Dict[str, Any]:
    """
    生成自定义OpenAPI文档
    [core][api_docs][generate_custom_openapi]
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    settings = app_config_get_settings()
    
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="""
# DataSay API 文档

DataSay是一个企业级多模态内容创作平台，提供文本、语音、图像等AI内容生成服务。

## 功能特性

### 核心服务
- **文本内容生成**: 基于大语言模型的智能文本创作
- **语音合成**: 多平台语音合成和音色克隆
- **图像生成**: AI图像创作和编辑
- **混合内容**: 多模态内容组合和渲染

### 平台集成
- **多AI平台支持**: Volcano Engine (豆包)、Azure、OpenAI等
- **第三方平台发布**: 抖音、微信等平台内容发布
- **云存储**: 支持多种云存储服务

### 企业功能
- **用户认证**: JWT令牌认证和权限管理
- **任务队列**: 异步任务处理和状态追踪
- **监控统计**: 使用量统计和性能监控

## API版本控制

当前API支持多版本管理，请在请求中指定版本：

- **URL路径**: `/api/v1/endpoint`
- **Header**: `API-Version: v1`
- **查询参数**: `?version=v1`

## 认证方式

API使用JWT Bearer Token认证：

```http
Authorization: Bearer <your-token>
```

## 错误处理

所有API响应遵循统一格式：

```json
{
    "success": true/false,
    "data": {},
    "error": {
        "code": "ERROR_CODE",
        "message": "错误描述",
        "details": {}
    }
}
```

## 限制说明

- API调用频率限制：默认每分钟60次
- 文件上传大小限制：100MB
- 批量操作限制：单次最多处理100项
        """,
        routes=app.routes,
        servers=[
            {
                "url": "http://localhost:8000",
                "description": "开发环境"
            },
            {
                "url": "https://api.datasay.com",
                "description": "生产环境"
            }
        ]
    )
    
    # 添加自定义信息
    openapi_schema["info"]["contact"] = {
        "name": "DataSay API Support",
        "email": "support@datasay.com",
        "url": "https://datasay.com/support"
    }
    
    openapi_schema["info"]["license"] = {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
    
    # 添加标签描述
    openapi_schema["tags"] = [
        {
            "name": "auth",
            "description": "用户认证和授权相关接口"
        },
        {
            "name": "text",
            "description": "文本内容生成和管理"
        },
        {
            "name": "voice",
            "description": "语音合成和音色管理"
        },
        {
            "name": "image",
            "description": "图像生成和处理"
        },
        {
            "name": "files",
            "description": "文件上传和管理"
        },
        {
            "name": "admin",
            "description": "管理员功能接口"
        },
        {
            "name": "system",
            "description": "系统信息和监控"
        }
    ]
    
    # 添加安全方案
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT认证令牌"
        },
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API密钥认证"
        }
    }
    
    # 添加通用响应模式
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    if "schemas" not in openapi_schema["components"]:
        openapi_schema["components"]["schemas"] = {}
    
    openapi_schema["components"]["schemas"].update({
        "SuccessResponse": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "example": True},
                "data": {"type": "object"},
                "message": {"type": "string", "example": "操作成功"}
            },
            "required": ["success"]
        },
        "ErrorResponse": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "example": False},
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "example": "VALIDATION_ERROR"},
                        "message": {"type": "string", "example": "请求参数验证失败"},
                        "details": {"type": "object"}
                    }
                }
            },
            "required": ["success", "error"]
        },
        "PaginationMeta": {
            "type": "object",
            "properties": {
                "page": {"type": "integer", "example": 1},
                "page_size": {"type": "integer", "example": 20},
                "total": {"type": "integer", "example": 100},
                "total_pages": {"type": "integer", "example": 5}
            }
        }
    })
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def api_docs_generate_redoc_html() -> str:
    """
    生成自定义Redoc HTML页面
    [core][api_docs][generate_redoc_html]
    """
    settings = app_config_get_settings()
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{settings.APP_NAME} - API Documentation</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
        <style>
            body {{
                margin: 0;
                padding: 0;
            }}
        </style>
    </head>
    <body>
        <redoc spec-url='{settings.API_V1_PREFIX}/openapi.json'
               options='{{"theme": {{"colors": {{"primary": {{"main": "#1976d2"}}}}}}}}'></redoc>
        <script src="https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js"></script>
    </body>
    </html>
    """
    return html_content


def api_docs_generate_swagger_html() -> str:
    """
    生成自定义Swagger UI HTML页面
    [core][api_docs][generate_swagger_html]
    """
    settings = app_config_get_settings()
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4.15.5/swagger-ui.css">
        <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
        <title>{settings.APP_NAME} - API Documentation</title>
    </head>
    <body>
        <div id="swagger-ui">
        </div>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4.15.5/swagger-ui-bundle.js"></script>
        <script>
        const ui = SwaggerUIBundle({{
            url: '{settings.API_V1_PREFIX}/openapi.json',
            dom_id: '#swagger-ui',
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIBundle.presets.standalone
            ],
            layout: "BaseLayout",
            deepLinking: true,
            showExtensions: true,
            showCommonExtensions: true,
            docExpansion: "none",
            defaultModelsExpandDepth: 1,
            defaultModelExpandDepth: 1,
            tryItOutEnabled: true,
            filter: true,
            requestInterceptor: function(request) {{
                // 添加自定义请求头
                request.headers['Accept'] = 'application/json';
                return request;
            }},
            responseInterceptor: function(response) {{
                // 处理响应
                return response;
            }}
        }});
        </script>
    </body>
    </html>
    """
    return html_content


class APIDocumentationGenerator:
    """
    API文档生成器类
    [core][api_docs][api_documentation_generator]
    """
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.settings = app_config_get_settings()
    
    def api_docs_generator_setup_custom_docs(self):
        """
        设置自定义文档页面
        [core][api_docs][api_documentation_generator][setup_custom_docs]
        """
        # 设置自定义OpenAPI生成器
        self.app.openapi = lambda: api_docs_generate_custom_openapi(self.app)
        
        # 添加自定义文档路由
        @self.app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
        async def custom_swagger_ui_html():
            return HTMLResponse(api_docs_generate_swagger_html())
        
        @self.app.get("/redoc", response_class=HTMLResponse, include_in_schema=False)
        async def custom_redoc_html():
            return HTMLResponse(api_docs_generate_redoc_html())
        
        logger.info("Custom API documentation setup completed")
    
    def api_docs_generator_export_openapi_schema(self, file_path: str):
        """
        导出OpenAPI schema到文件
        [core][api_docs][api_documentation_generator][export_openapi_schema]
        """
        try:
            schema = api_docs_generate_custom_openapi(self.app)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(schema, f, indent=2, ensure_ascii=False)
            
            logger.info(f"OpenAPI schema exported to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to export OpenAPI schema: {str(e)}")
            raise
    
    def api_docs_generator_generate_postman_collection(self) -> Dict[str, Any]:
        """
        生成Postman集合
        [core][api_docs][api_documentation_generator][generate_postman_collection]
        """
        schema = api_docs_generate_custom_openapi(self.app)
        
        collection = {
            "info": {
                "name": schema["info"]["title"],
                "description": schema["info"]["description"],
                "version": schema["info"]["version"],
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "auth": {
                "type": "bearer",
                "bearer": [
                    {
                        "key": "token",
                        "value": "{{auth_token}}",
                        "type": "string"
                    }
                ]
            },
            "variable": [
                {
                    "key": "base_url",
                    "value": "http://localhost:8000",
                    "type": "string"
                },
                {
                    "key": "auth_token",
                    "value": "",
                    "type": "string"
                }
            ],
            "item": []
        }
        
        # 转换API路径为Postman请求
        for path, methods in schema.get("paths", {}).items():
            for method, details in methods.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    item = {
                        "name": details.get("summary", f"{method.upper()} {path}"),
                        "request": {
                            "method": method.upper(),
                            "header": [
                                {
                                    "key": "Content-Type",
                                    "value": "application/json"
                                }
                            ],
                            "url": {
                                "raw": "{{base_url}}" + path,
                                "host": ["{{base_url}}"],
                                "path": path.strip("/").split("/")
                            }
                        },
                        "response": []
                    }
                    
                    # 添加请求体示例
                    if "requestBody" in details:
                        content = details["requestBody"].get("content", {})
                        if "application/json" in content:
                            schema_ref = content["application/json"].get("schema", {})
                            if "example" in schema_ref:
                                item["request"]["body"] = {
                                    "mode": "raw",
                                    "raw": json.dumps(schema_ref["example"], indent=2)
                                }
                    
                    collection["item"].append(item)
        
        return collection


def api_docs_setup_documentation(app: FastAPI):
    """
    设置API文档
    [core][api_docs][setup_documentation]
    """
    doc_generator = APIDocumentationGenerator(app)
    doc_generator.api_docs_generator_setup_custom_docs()
    
    logger.info("API documentation setup completed")
    
    return doc_generator