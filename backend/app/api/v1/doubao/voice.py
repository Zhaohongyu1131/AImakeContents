"""
Doubao Voice API Router
豆包语音API路由 - [api][v1][doubao][voice]
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import io
import asyncio
from datetime import datetime

from app.services.doubao_service import DoubaoService
from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db


class VoiceCloneRequest(BaseModel):
    """
    音色克隆请求模型
    [api][v1][doubao][voice][clone_request]
    """
    timbre_name: str = Field(..., description="音色名称")
    timbre_description: Optional[str] = Field(None, description="音色描述")
    language: int = Field(0, description="语言类型: 0=中文, 1=英文, 2=日语, 3=西班牙语, 4=印尼语, 5=葡萄牙语")
    model_type: int = Field(1, description="模型类型: 0=1.0效果, 1=2.0效果(ICL), 2=DiT标准版, 3=DiT还原版")
    reference_text: Optional[str] = Field(None, description="参考文本")
    audio_format: str = Field("wav", description="音频格式")


class VoiceCloneResponse(BaseModel):
    """
    音色克隆响应模型
    [api][v1][doubao][voice][clone_response]
    """
    success: bool
    speaker_id: str
    status: str
    message: str


class TTSRequest(BaseModel):
    """
    文本转语音请求模型
    [api][v1][doubao][voice][tts_request]
    """
    text: str = Field(..., description="要合成的文本")
    voice_type: str = Field(..., description="音色类型")
    encoding: str = Field("mp3", description="音频编码格式")
    speed_ratio: float = Field(1.0, description="语速比例")
    volume_ratio: float = Field(1.0, description="音量比例")
    pitch_ratio: float = Field(1.0, description="音调比例")
    sample_rate: int = Field(24000, description="采样率")
    
    # 高级参数
    explicit_language: Optional[str] = Field(None, description="语种控制")
    context_language: Optional[str] = Field(None, description="参考语种")
    text_type: str = Field("plain", description="文本类型")
    with_timestamp: bool = Field(False, description="是否返回时间戳")
    split_sentence: bool = Field(False, description="是否分句处理")
    cache_enabled: bool = Field(False, description="是否启用缓存")
    cluster: str = Field("volcano_icl", description="集群选择")


class TTSResponse(BaseModel):
    """
    文本转语音响应模型
    [api][v1][doubao][voice][tts_response]
    """
    success: bool
    reqid: str
    audio_data: Optional[bytes] = None
    encoding: str
    sample_rate: int
    duration: Optional[float] = None
    message: str


class SpeakerStatusResponse(BaseModel):
    """
    音色状态响应模型
    [api][v1][doubao][voice][speaker_status_response]
    """
    speaker_id: str
    status: int
    status_text: str
    create_time: Optional[str] = None
    version: str = "V1"
    demo_audio: Optional[str] = None
    is_ready: bool


def doubao_voice_router_get() -> APIRouter:
    """
    获取豆包语音API路由
    [api][v1][doubao][voice][router_get]
    """
    router = APIRouter()
    
    @router.post(
        "/clone/upload",
        response_model=VoiceCloneResponse,
        summary="上传音频进行音色克隆",
        description="上传音频文件，创建自定义音色"
    )
    async def doubao_voice_clone_upload(
        audio_file: UploadFile = File(..., description="音频文件"),
        request_data: str = Form(..., description="克隆请求参数JSON"),
        current_user = Depends(get_current_user),
        db = Depends(get_db)
    ):
        """
        上传音频进行音色克隆
        [api][v1][doubao][voice][clone_upload]
        """
        try:
            import json
            clone_request = VoiceCloneRequest.parse_raw(request_data)
            
            # 读取音频文件数据
            audio_data = await audio_file.read()
            
            # 验证音频文件
            if len(audio_data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="音频文件为空"
                )
            
            # 使用豆包服务创建音色克隆
            doubao_service = DoubaoService(db)
            
            result = await doubao_service.doubao_service_voice_clone_create(
                user_id=current_user.user_id,
                timbre_name=clone_request.timbre_name,
                audio_data=audio_data,
                timbre_description=clone_request.timbre_description,
                language=clone_request.language,
                model_type=clone_request.model_type,
                reference_text=clone_request.reference_text,
                audio_format=clone_request.audio_format
            )
            
            if result["success"]:
                return VoiceCloneResponse(
                    success=True,
                    speaker_id=result["data"]["speaker_id"],
                    status=result["data"]["status"],
                    message=result["message"]
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result["message"]
                )
                
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请求参数JSON格式错误"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"音色克隆上传失败: {str(e)}"
            )
    
    @router.get(
        "/clone/status/{speaker_id}",
        response_model=SpeakerStatusResponse,
        summary="查询音色克隆状态",
        description="查询指定speaker_id的音色训练状态"
    )
    async def doubao_voice_clone_status(
        speaker_id: str,
        current_user = Depends(get_current_user),
        db = Depends(get_db)
    ):
        """
        查询音色克隆状态
        [api][v1][doubao][voice][clone_status]
        """
        try:
            # 使用豆包服务查询状态
            doubao_service = DoubaoService(db)
            
            result = await doubao_service.doubao_service_voice_clone_status_check(
                user_id=current_user.user_id,
                speaker_id=speaker_id
            )
            
            if result["success"]:
                data = result["data"]
                status_map = {
                    0: "NotFound",
                    1: "Training", 
                    2: "Success",
                    3: "Failed",
                    4: "Active"
                }
                
                return SpeakerStatusResponse(
                    speaker_id=data.get("speaker_id"),
                    status=data.get("volcano_status", 0),
                    status_text=data.get("status", "Unknown"),
                    create_time=None,  # TODO: 从数据库获取
                    version="V1",
                    demo_audio=data.get("demo_audio"),
                    is_ready=data.get("is_ready", False)
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result["message"]
                )
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"音色状态查询失败: {str(e)}"
            )
    
    @router.get(
        "/clone/list",
        summary="获取音色列表",
        description="获取当前用户的所有音色列表"
    )
    async def doubao_voice_clone_list(
        current_user = Depends(get_current_user),
        db = Depends(get_db)
    ):
        """
        获取音色列表
        [api][v1][doubao][voice][clone_list]
        """
        try:
            # 使用豆包服务获取用户音色列表
            doubao_service = DoubaoService(db)
            
            result = await doubao_service.doubao_service_user_voices_list(current_user.user_id)
            
            if result["success"]:
                return {
                    "success": True,
                    "data": result["data"],
                    "message": result["message"]
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result["message"]
                )
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"音色列表获取失败: {str(e)}"
            )
    
    @router.post(
        "/tts/synthesize",
        summary="HTTP文本转语音",
        description="使用HTTP方式进行文本转语音合成"
    )
    async def doubao_voice_tts_synthesize(
        request: TTSRequest,
        current_user = Depends(get_current_user),
        db = Depends(get_db)
    ):
        """
        HTTP文本转语音合成
        [api][v1][doubao][voice][tts_synthesize]
        """
        try:
            # 使用豆包服务进行TTS合成
            doubao_service = DoubaoService(db)
            
            result = await doubao_service.doubao_service_tts_synthesize(
                user_id=current_user.user_id,
                text=request.text,
                voice_type=request.voice_type,
                encoding=request.encoding,
                speed_ratio=request.speed_ratio,
                volume_ratio=request.volume_ratio,
                pitch_ratio=request.pitch_ratio,
                sample_rate=request.sample_rate,
                explicit_language=request.explicit_language,
                context_language=request.context_language,
                text_type=request.text_type,
                with_timestamp=request.with_timestamp,
                split_sentence=request.split_sentence,
                cache_enabled=request.cache_enabled,
                cluster=request.cluster
            )
            
            if result["success"]:
                data = result["data"]
                
                # 如果有音频数据，返回音频流
                if data.get("audio_data"):
                    media_type = {
                        "mp3": "audio/mpeg",
                        "wav": "audio/wav", 
                        "ogg_opus": "audio/ogg",
                        "pcm": "audio/pcm"
                    }.get(request.encoding, "audio/mpeg")
                    
                    return StreamingResponse(
                        io.BytesIO(data["audio_data"]),
                        media_type=media_type,
                        headers={
                            "Content-Disposition": f"attachment; filename=tts_output.{request.encoding}",
                            "X-Request-ID": data.get("reqid"),
                            "X-Duration": str(data.get("duration", 0)),
                            "X-Sample-Rate": str(request.sample_rate)
                        }
                    )
                else:
                    return {
                        "success": True,
                        "reqid": data.get("reqid"),
                        "message": "TTS合成完成，但无音频数据返回"
                    }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result["message"]
                )
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"TTS合成失败: {str(e)}"
            )
    
    @router.post(
        "/tts/stream",
        summary="WebSocket流式文本转语音",
        description="使用WebSocket进行流式文本转语音合成"
    )
    async def doubao_voice_tts_stream(
        request: TTSRequest,
        current_user = Depends(get_current_user),
        db = Depends(get_db)
    ):
        """
        WebSocket流式文本转语音合成
        [api][v1][doubao][voice][tts_stream]
        """
        try:
            # 使用豆包服务进行流式TTS
            doubao_service = DoubaoService(db)
            
            async def audio_stream_generator():
                """音频流生成器"""
                async for result in doubao_service.doubao_service_tts_stream(
                    user_id=current_user.user_id,
                    text=request.text,
                    voice_type=request.voice_type,
                    encoding=request.encoding,
                    speed_ratio=request.speed_ratio,
                    volume_ratio=request.volume_ratio,
                    pitch_ratio=request.pitch_ratio,
                    sample_rate=request.sample_rate,
                    explicit_language=request.explicit_language,
                    cluster=request.cluster
                ):
                    if result["success"] and result.get("data"):
                        data = result["data"]
                        if data.get("type") == "audio_chunk" and data.get("audio_data"):
                            yield data["audio_data"]
                        elif data.get("type") == "complete":
                            break
                    else:
                        # 错误处理
                        break
            
            media_type = {
                "mp3": "audio/mpeg",
                "wav": "audio/wav",
                "ogg_opus": "audio/ogg", 
                "pcm": "audio/pcm"
            }.get(request.encoding, "audio/mpeg")
            
            return StreamingResponse(
                audio_stream_generator(),
                media_type=media_type,
                headers={
                    "Content-Disposition": f"attachment; filename=tts_stream.{request.encoding}",
                    "X-Stream-Type": "websocket",
                    "X-Sample-Rate": str(request.sample_rate)
                }
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"流式TTS合成失败: {str(e)}"
            )
    
    return router