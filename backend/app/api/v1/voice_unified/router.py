"""
Voice Unified API Router
统一语音API路由 - [api][v1][voice_unified][router]
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import io
import asyncio
from datetime import datetime

from app.services.voice_service_unified import (
    VoiceServiceUnified,
    VoiceCloneRequest, 
    TTSRequest,
    VoiceOperationResult,
    VoiceOperationType,
    voice_service_unified
)
from app.services.voice_platform_manager import (
    VoicePlatformManager,
    VoicePlatformType,
    voice_platform_manager
)
from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db


# ==================== Request/Response Models ====================

class VoicePlatformInfoResponse(BaseModel):
    """平台信息响应"""
    platform_type: str
    platform_name: str
    platform_description: str
    is_enabled: bool
    is_healthy: bool
    supported_features: List[str]
    priority: int
    cost_per_minute: float

class VoiceCloneSubmitRequest(BaseModel):
    """音色克隆提交请求"""
    timbre_name: str = Field(..., description="音色名称")
    timbre_description: Optional[str] = Field(None, description="音色描述")
    language: str = Field("zh-CN", description="语言代码")
    model_type: Optional[str] = Field(None, description="模型类型")
    reference_text: Optional[str] = Field(None, description="参考文本")
    preferred_platform: Optional[str] = Field(None, description="首选平台")
    advanced_params: Optional[Dict[str, Any]] = Field(None, description="高级参数")

class TTSSynthesizeRequest(BaseModel):
    """TTS合成请求"""
    text: str = Field(..., description="待合成文本")
    voice_id: str = Field(..., description="音色ID")
    language: Optional[str] = Field("zh-CN", description="语言代码")
    speed_ratio: float = Field(1.0, description="语速比例")
    volume_ratio: float = Field(1.0, description="音量比例")
    pitch_ratio: float = Field(1.0, description="音调比例")
    audio_format: str = Field("mp3", description="音频格式")
    sample_rate: int = Field(24000, description="采样率")
    use_ssml: bool = Field(False, description="是否使用SSML")
    streaming: bool = Field(False, description="是否流式合成")
    preferred_platform: Optional[str] = Field(None, description="首选平台")
    advanced_params: Optional[Dict[str, Any]] = Field(None, description="高级参数")

class VoiceOperationResponse(BaseModel):
    """语音操作响应"""
    success: bool
    operation_id: str
    operation_type: str
    platform_used: str
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_time_ms: float
    metadata: Optional[Dict[str, Any]] = None

class ApiResponse(BaseModel):
    """统一API响应格式"""
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


def voice_unified_router_get() -> APIRouter:
    """
    获取统一语音API路由
    [api][v1][voice_unified][router][get]
    """
    router = APIRouter()

    # ==================== 平台管理 ====================
    
    @router.get(
        "/platforms/list",
        response_model=ApiResponse,
        summary="获取可用平台列表",
        description="获取所有可用的语音服务平台信息"
    )
    async def voice_unified_platforms_list():
        """
        获取可用平台列表
        [api][v1][voice_unified][platforms_list]
        """
        try:
            available_platforms = await voice_platform_manager.voice_platform_manager_get_available_platforms()
            platform_status = await voice_platform_manager.voice_platform_manager_get_platform_status_summary()
            
            platform_list = []
            for config in available_platforms:
                platform_info = VoicePlatformInfoResponse(
                    platform_type=config.platform_type.value,
                    platform_name=config.platform_name,
                    platform_description=config.platform_description,
                    is_enabled=config.is_enabled,
                    is_healthy=platform_status["platform_details"][config.platform_type.value]["healthy"],
                    supported_features=list(config.feature_support.keys()),
                    priority=config.priority,
                    cost_per_minute=config.cost_per_minute
                )
                platform_list.append(platform_info.dict())
            
            return ApiResponse(
                success=True,
                message="获取平台列表成功",
                data={
                    "platforms": platform_list,
                    "total_count": len(platform_list),
                    "summary": platform_status
                }
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取平台列表失败: {str(e)}"
            )
    
    @router.get(
        "/platforms/{platform_type}",
        response_model=ApiResponse,
        summary="获取指定平台信息",
        description="获取指定平台的详细信息和状态"
    )
    async def voice_unified_platform_info(platform_type: str):
        """
        获取指定平台信息
        [api][v1][voice_unified][platform_info]
        """
        try:
            # 验证平台类型
            try:
                platform_enum = VoicePlatformType(platform_type)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"不支持的平台类型: {platform_type}"
                )
            
            # 获取平台配置
            config = voice_platform_manager.platform_configs.get(platform_enum)
            if not config:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"平台 {platform_type} 未配置"
                )
            
            # 获取平台状态
            status_info = voice_platform_manager.platform_status.get(platform_enum)
            
            platform_info = VoicePlatformInfoResponse(
                platform_type=config.platform_type.value,
                platform_name=config.platform_name,
                platform_description=config.platform_description,
                is_enabled=config.is_enabled,
                is_healthy=status_info.is_healthy if status_info else False,
                supported_features=list(config.feature_support.keys()),
                priority=config.priority,
                cost_per_minute=config.cost_per_minute
            )
            
            return ApiResponse(
                success=True,
                message=f"获取平台 {platform_type} 信息成功",
                data={
                    "platform": platform_info.dict(),
                    "status": {
                        "is_healthy": status_info.is_healthy if status_info else False,
                        "last_health_check": status_info.last_health_check.isoformat() if status_info else None,
                        "response_time_ms": status_info.response_time_ms if status_info else None,
                        "daily_requests_used": status_info.daily_requests_used if status_info else 0,
                        "daily_requests_limit": status_info.daily_requests_limit if status_info else 0
                    }
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取平台信息失败: {str(e)}"
            )

    # ==================== 音色克隆 ====================
    
    @router.post(
        "/timbre/clone",
        response_model=ApiResponse,
        status_code=status.HTTP_201_CREATED,
        summary="音色克隆",
        description="使用音频文件创建自定义音色"
    )
    async def voice_unified_timbre_clone(
        audio_file: UploadFile = File(..., description="音频文件"),
        request_data: str = Form(..., description="克隆参数JSON"),
        current_user = Depends(get_current_user),
        db = Depends(get_db)
    ):
        """
        音色克隆
        [api][v1][voice_unified][timbre_clone]
        """
        try:
            import json
            
            # 解析请求数据
            try:
                clone_params = VoiceCloneSubmitRequest.parse_raw(request_data)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"请求参数格式错误: {str(e)}"
                )
            
            # 验证音频文件
            if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="请上传有效的音频文件"
                )
            
            # 读取音频数据
            audio_data = await audio_file.read()
            if len(audio_data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="音频文件为空"
                )
            
            # 转换首选平台
            preferred_platform = None
            if clone_params.preferred_platform:
                try:
                    preferred_platform = VoicePlatformType(clone_params.preferred_platform)
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"不支持的平台类型: {clone_params.preferred_platform}"
                    )
            
            # 创建克隆请求
            clone_request = VoiceCloneRequest(
                user_id=current_user.user_id,
                timbre_name=clone_params.timbre_name,
                timbre_description=clone_params.timbre_description,
                audio_data=audio_data,
                audio_format=audio_file.content_type.split('/')[-1],
                language=clone_params.language,
                model_type=clone_params.model_type,
                reference_text=clone_params.reference_text,
                advanced_params=clone_params.advanced_params,
                preferred_platform=preferred_platform
            )
            
            # 执行音色克隆
            result = await voice_service_unified.voice_service_unified_clone_voice(clone_request)
            
            # 转换响应
            operation_response = VoiceOperationResponse(
                success=result.success,
                operation_id=result.operation_id,
                operation_type=result.operation_type.value,
                platform_used=result.platform_used.value,
                result_data=result.result_data,
                error_message=result.error_message,
                processing_time_ms=result.processing_time_ms,
                metadata=result.metadata
            )
            
            return ApiResponse(
                success=result.success,
                message="音色克隆任务已创建" if result.success else f"音色克隆失败: {result.error_message}",
                data=operation_response.dict()
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"音色克隆处理失败: {str(e)}"
            )
    
    @router.get(
        "/timbre/list",
        response_model=ApiResponse,
        summary="获取音色列表",
        description="获取用户的自定义音色和平台可用音色"
    )
    async def voice_unified_timbre_list(
        platform: Optional[str] = Query(None, description="指定平台"),
        current_user = Depends(get_current_user)
    ):
        """
        获取音色列表
        [api][v1][voice_unified][timbre_list]
        """
        try:
            # 转换平台参数
            platform_filter = None
            if platform:
                try:
                    platform_filter = VoicePlatformType(platform)
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"不支持的平台类型: {platform}"
                    )
            
            # 获取可用音色
            voices = await voice_service_unified.voice_service_unified_get_available_voices(
                platform_type=platform_filter
            )
            
            return ApiResponse(
                success=True,
                message="获取音色列表成功",
                data={
                    "voices_by_platform": voices,
                    "total_platforms": len(voices),
                    "user_id": current_user.user_id
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取音色列表失败: {str(e)}"
            )

    # ==================== TTS合成 ====================
    
    @router.post(
        "/synthesis/text-to-speech",
        response_model=ApiResponse,
        summary="文本转语音",
        description="将文本转换为语音"
    )
    async def voice_unified_synthesize_speech(
        request: TTSSynthesizeRequest,
        current_user = Depends(get_current_user)
    ):
        """
        文本转语音合成
        [api][v1][voice_unified][synthesize_speech]
        """
        try:
            # 验证文本长度
            if len(request.text.strip()) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="文本内容不能为空"
                )
            
            if len(request.text) > 5000:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="文本长度不能超过5000字符"
                )
            
            # 转换首选平台
            preferred_platform = None
            if request.preferred_platform:
                try:
                    preferred_platform = VoicePlatformType(request.preferred_platform)
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"不支持的平台类型: {request.preferred_platform}"
                    )
            
            # 创建TTS请求
            tts_request = TTSRequest(
                user_id=current_user.user_id,
                text=request.text,
                voice_id=request.voice_id,
                language=request.language,
                speed_ratio=request.speed_ratio,
                volume_ratio=request.volume_ratio,
                pitch_ratio=request.pitch_ratio,
                audio_format=request.audio_format,
                sample_rate=request.sample_rate,
                use_ssml=request.use_ssml,
                streaming=request.streaming,
                advanced_params=request.advanced_params,
                preferred_platform=preferred_platform
            )
            
            # 执行TTS合成
            result = await voice_service_unified.voice_service_unified_synthesize_speech(tts_request)
            
            # 转换响应
            operation_response = VoiceOperationResponse(
                success=result.success,
                operation_id=result.operation_id,
                operation_type=result.operation_type.value,
                platform_used=result.platform_used.value,
                result_data=result.result_data,
                error_message=result.error_message,
                processing_time_ms=result.processing_time_ms,
                metadata=result.metadata
            )
            
            return ApiResponse(
                success=result.success,
                message="语音合成成功" if result.success else f"语音合成失败: {result.error_message}",
                data=operation_response.dict()
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"语音合成处理失败: {str(e)}"
            )
    
    @router.get(
        "/synthesis/stream/{operation_id}",
        summary="获取流式音频数据",
        description="获取流式TTS合成的音频数据"
    )
    async def voice_unified_get_stream_audio(
        operation_id: str,
        current_user = Depends(get_current_user)
    ):
        """
        获取流式音频数据
        [api][v1][voice_unified][get_stream_audio]
        """
        try:
            # 获取操作结果
            operation_result = await voice_service_unified.voice_service_unified_get_operation_status(
                operation_id
            )
            
            if not operation_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"操作 {operation_id} 不存在"
                )
            
            if not operation_result.success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"操作失败: {operation_result.error_message}"
                )
            
            # 获取音频数据
            audio_data = operation_result.result_data.get("audio_data")
            if not audio_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="音频数据不可用"
                )
            
            # 返回音频流
            audio_format = operation_result.result_data.get("format", "mp3")
            media_type = f"audio/{audio_format}"
            
            return StreamingResponse(
                io.BytesIO(audio_data),
                media_type=media_type,
                headers={
                    "Content-Disposition": f"attachment; filename=tts_audio_{operation_id}.{audio_format}"
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取音频数据失败: {str(e)}"
            )

    # ==================== 操作状态和统计 ====================
    
    @router.get(
        "/operations/{operation_id}",
        response_model=ApiResponse,
        summary="获取操作状态",
        description="查询语音操作的状态和结果"
    )
    async def voice_unified_get_operation_status(
        operation_id: str,
        current_user = Depends(get_current_user)
    ):
        """
        获取操作状态
        [api][v1][voice_unified][get_operation_status]
        """
        try:
            operation_result = await voice_service_unified.voice_service_unified_get_operation_status(
                operation_id
            )
            
            if not operation_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"操作 {operation_id} 不存在"
                )
            
            operation_response = VoiceOperationResponse(
                success=operation_result.success,
                operation_id=operation_result.operation_id,
                operation_type=operation_result.operation_type.value,
                platform_used=operation_result.platform_used.value,
                result_data=operation_result.result_data,
                error_message=operation_result.error_message,
                processing_time_ms=operation_result.processing_time_ms,
                metadata=operation_result.metadata
            )
            
            return ApiResponse(
                success=True,
                message="获取操作状态成功",
                data=operation_response.dict()
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取操作状态失败: {str(e)}"
            )
    
    @router.get(
        "/statistics",
        response_model=ApiResponse,
        summary="获取平台使用统计",
        description="获取语音服务的使用统计信息"
    )
    async def voice_unified_get_statistics(
        current_user = Depends(get_current_user)
    ):
        """
        获取平台使用统计
        [api][v1][voice_unified][get_statistics]
        """
        try:
            statistics = await voice_service_unified.voice_service_unified_get_platform_statistics()
            
            return ApiResponse(
                success=True,
                message="获取统计信息成功",
                data=statistics
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取统计信息失败: {str(e)}"
            )
    
    @router.post(
        "/health-check",
        response_model=ApiResponse,
        summary="执行健康检查",
        description="检查所有平台的健康状态"
    )
    async def voice_unified_health_check():
        """
        执行健康检查
        [api][v1][voice_unified][health_check]
        """
        try:
            await voice_platform_manager.voice_platform_manager_health_check_all_platforms()
            status_summary = await voice_platform_manager.voice_platform_manager_get_platform_status_summary()
            
            return ApiResponse(
                success=True,
                message="健康检查完成",
                data=status_summary
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"健康检查失败: {str(e)}"
            )
    
    return router