"""
Text Content API Module
文本内容API模块 - [api][v1][text_content]
"""

from .router_impl import text_content_router_impl_get as text_content_router_get

__all__ = [
    "text_content_router_get",
]