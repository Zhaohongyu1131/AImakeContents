"""
Doubao Text API Router
豆包文本API路由 - [api][v1][doubao][text]
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.services.doubao_service import DoubaoService
from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db


class TextProcessRequest(BaseModel):
    """
    文本处理请求模型
    [api][v1][doubao][text][process_request]
    """
    text: str = Field(..., description="要处理的文本")
    operation: str = Field(..., description="处理操作类型")
    parameters: Optional[Dict[str, Any]] = Field(None, description="处理参数")


class TextProcessResponse(BaseModel):
    """
    文本处理响应模型
    [api][v1][doubao][text][process_response]
    """
    success: bool
    processed_text: str
    operation: str
    metadata: Optional[Dict[str, Any]] = None
    message: str


def doubao_text_router_get() -> APIRouter:
    """
    获取豆包文本API路由
    [api][v1][doubao][text][router_get]
    """
    router = APIRouter()
    
    @router.get(
        "/health",
        summary="文本服务健康检查",
        description="检查豆包文本服务状态"
    )
    async def doubao_text_health_check():
        """
        文本服务健康检查
        [api][v1][doubao][text][health_check]
        """
        return {
            "success": True,
            "message": "Doubao Text API is healthy",
            "service": "text_processing"
        }
    
    @router.post(
        "/analyze",
        response_model=TextProcessResponse,
        summary="文本分析",
        description="对文本进行分析处理"
    )
    async def doubao_text_analyze(
        request: TextProcessRequest,
        current_user = Depends(get_current_user)
    ):
        """
        文本分析
        [api][v1][doubao][text][analyze]
        """
        try:
            # TODO: 实现文本分析功能
            # 这里可以集成各种文本分析服务
            
            return TextProcessResponse(
                success=True,
                processed_text=request.text,
                operation=request.operation,
                metadata={
                    "length": len(request.text),
                    "word_count": len(request.text.split()),
                    "analysis_type": request.operation
                },
                message="文本分析完成"
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"文本分析失败: {str(e)}"
            )
    
    @router.post(
        "/preprocess",
        response_model=TextProcessResponse,
        summary="文本预处理",
        description="对文本进行预处理，为TTS做准备"
    )
    async def doubao_text_preprocess(
        request: TextProcessRequest,
        current_user = Depends(get_current_user),
        db = Depends(get_db)
    ):
        """
        文本预处理
        [api][v1][doubao][text][preprocess]
        """
        try:
            # 使用豆包服务进行文本预处理
            doubao_service = DoubaoService(db)
            
            result = await doubao_service.doubao_service_text_preprocess(
                text=request.text,
                operation=request.operation,
                parameters=request.parameters
            )
            
            if result["success"]:
                data = result["data"]
                return TextProcessResponse(
                    success=True,
                    processed_text=data["processed_text"],
                    operation=data["operation"],
                    metadata=data.get("changes"),
                    message=result["message"]
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result["message"]
                )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"文本预处理失败: {str(e)}"
            )
    
    @router.post(
        "/validate",
        summary="文本验证",
        description="验证文本是否适合进行TTS合成"
    )
    async def doubao_text_validate(
        request: TextProcessRequest,
        current_user = Depends(get_current_user)
    ):
        """
        文本验证
        [api][v1][doubao][text][validate]
        """
        try:
            validation_results = {
                "is_valid": True,
                "warnings": [],
                "errors": [],
                "suggestions": []
            }
            
            # 长度检查
            if len(request.text) == 0:
                validation_results["is_valid"] = False
                validation_results["errors"].append("文本不能为空")
            elif len(request.text) > 5000:
                validation_results["warnings"].append("文本过长，可能影响合成质量")
            
            # 字符检查
            if any(char in request.text for char in ['@', '#', '$', '%', '^', '&', '*']):
                validation_results["warnings"].append("文本包含特殊字符，可能影响合成效果")
            
            # 语言一致性检查
            # TODO: 实现更复杂的语言检测
            
            return {
                "success": True,
                "validation": validation_results,
                "text_stats": {
                    "length": len(request.text),
                    "word_count": len(request.text.split()),
                    "line_count": len(request.text.split('\n'))
                },
                "message": "文本验证完成"
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"文本验证失败: {str(e)}"
            )
    
    @router.post(
        "/split",
        summary="文本分割",
        description="将长文本分割为适合TTS处理的片段"
    )
    async def doubao_text_split(
        request: TextProcessRequest,
        current_user = Depends(get_current_user)
    ):
        """
        文本分割
        [api][v1][doubao][text][split]
        """
        try:
            max_length = request.parameters.get("max_length", 500) if request.parameters else 500
            
            # 简单的文本分割实现
            sentences = []
            current_sentence = ""
            
            for char in request.text:
                current_sentence += char
                
                # 遇到句号、感叹号、问号等分句
                if char in ['.', '!', '?', '。', '！', '？', '\n']:
                    if len(current_sentence.strip()) > 0:
                        sentences.append(current_sentence.strip())
                        current_sentence = ""
                
                # 超过最大长度强制分割
                elif len(current_sentence) >= max_length:
                    if len(current_sentence.strip()) > 0:
                        sentences.append(current_sentence.strip())
                        current_sentence = ""
            
            # 添加剩余文本
            if len(current_sentence.strip()) > 0:
                sentences.append(current_sentence.strip())
            
            return {
                "success": True,
                "segments": sentences,
                "segment_count": len(sentences),
                "total_length": len(request.text),
                "max_segment_length": max(len(s) for s in sentences) if sentences else 0,
                "min_segment_length": min(len(s) for s in sentences) if sentences else 0,
                "message": "文本分割完成"
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"文本分割失败: {str(e)}"
            )
    
    return router