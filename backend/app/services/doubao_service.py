"""
Doubao Integrated Service
豆包集成服务 - [services][doubao_service]
"""

from typing import Dict, Any, Optional, List, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime
import logging

from app.services.volcano_enhanced_service import VolcanoEnhancedService
from app.services.base import ServiceBase
from app.models.voice_timbre import VoiceTimbreBasic, VoiceTimbreClone
from app.models.voice_audio import VoiceAudioBasic
from app.models.user import UserBasic
from app.integrations.base import IntegrationResponse


class DoubaoService(ServiceBase):
    """
    豆包综合服务
    [services][doubao_service]
    """
    
    def __init__(self, db: AsyncSession):
        """
        初始化豆包服务
        [services][doubao_service][init]
        """
        super().__init__(db)
        self.volcano_service = VolcanoEnhancedService()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def doubao_service_voice_clone_create(
        self,
        user_id: int,
        timbre_name: str,
        audio_data: bytes,
        timbre_description: Optional[str] = None,
        language: int = 0,
        model_type: int = 1,
        reference_text: Optional[str] = None,
        audio_format: str = "wav"
    ) -> Dict[str, Any]:
        """
        创建音色克隆
        [services][doubao_service][voice_clone_create]
        """
        try:
            # 验证用户权限
            user_check = await self.db.execute(
                select(UserBasic).where(UserBasic.user_id == user_id)
            )
            user = user_check.scalar_one_or_none()
            if not user:
                return {
                    "success": False,
                    "message": "用户不存在",
                    "error_code": "USER_NOT_FOUND"
                }
            
            # 生成唯一的speaker_id
            speaker_id = f"custom_{user_id}_{int(datetime.now().timestamp())}"
            
            # 上传到火山引擎
            volcano_response = await self.volcano_service.volcano_upload_voice_clone(
                speaker_id=speaker_id,
                audio_data=audio_data,
                audio_format=audio_format,
                language=language,
                model_type=model_type,
                reference_text=reference_text
            )
            
            if not volcano_response.success:
                return {
                    "success": False,
                    "message": f"音色上传失败: {volcano_response.error.message if volcano_response.error else 'Unknown error'}",
                    "error_code": "VOLCANO_UPLOAD_FAILED"
                }
            
            # 创建基础音色记录
            timbre_basic = VoiceTimbreBasic(
                timbre_name=timbre_name,
                timbre_description=timbre_description,
                timbre_platform="volcano",
                timbre_language=self._language_code_to_string(language),
                timbre_created_user_id=user_id,
                timbre_status="training"
            )
            
            self.db.add(timbre_basic)
            await self.db.flush()  # 获取timbre_id
            
            # 创建克隆记录
            clone_record = VoiceTimbreClone(
                timbre_id=timbre_basic.timbre_id,
                clone_source_duration=None,  # TODO: 从音频文件计算
                clone_training_params={
                    "language": language,
                    "model_type": model_type,
                    "reference_text": reference_text,
                    "audio_format": audio_format
                },
                clone_created_user_id=user_id,
                clone_status="training",
                clone_audio_format=audio_format,
                clone_reference_text=reference_text,
                clone_language=language,
                clone_model_type=model_type,
                clone_volcano_task_id=speaker_id
            )
            
            self.db.add(clone_record)
            await self.db.commit()
            
            return {
                "success": True,
                "message": "音色克隆已提交",
                "data": {
                    "timbre_id": timbre_basic.timbre_id,
                    "clone_id": clone_record.clone_id,
                    "speaker_id": speaker_id,
                    "status": "training"
                }
            }
            
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"音色克隆创建失败: {str(e)}")
            return {
                "success": False,
                "message": f"音色克隆创建失败: {str(e)}",
                "error_code": "CLONE_CREATE_FAILED"
            }
    
    async def doubao_service_voice_clone_status_check(
        self,
        user_id: int,
        speaker_id: str
    ) -> Dict[str, Any]:
        """
        检查音色克隆状态
        [services][doubao_service][voice_clone_status_check]
        """
        try:
            # 检查用户权限
            clone_check = await self.db.execute(
                select(VoiceTimbreClone).join(VoiceTimbreBasic).where(
                    and_(
                        VoiceTimbreClone.clone_volcano_task_id == speaker_id,
                        VoiceTimbreBasic.timbre_created_user_id == user_id
                    )
                )
            )
            clone_record = clone_check.scalar_one_or_none()
            if not clone_record:
                return {
                    "success": False,
                    "message": "音色记录不存在或无权限访问",
                    "error_code": "CLONE_NOT_FOUND"
                }
            
            # 从火山引擎获取状态
            volcano_response = await self.volcano_service.volcano_check_speaker_status(speaker_id)
            
            if volcano_response.success:
                status_data = volcano_response.data
                
                # 更新本地状态
                volcano_status = status_data.get("status")
                if volcano_status == 2:  # Success
                    clone_record.clone_status = "completed"
                    clone_record.clone_completed_time = datetime.now()
                    clone_record.clone_progress = 100
                elif volcano_status == 3:  # Failed
                    clone_record.clone_status = "failed"
                    clone_record.clone_error_message = "训练失败"
                elif volcano_status == 1:  # Training
                    clone_record.clone_status = "training"
                    # 更新进度（这里可以根据实际API返回值调整）
                    
                await self.db.commit()
                
                return {
                    "success": True,
                    "message": "状态查询成功",
                    "data": {
                        "speaker_id": speaker_id,
                        "status": clone_record.clone_status,
                        "progress": clone_record.clone_progress,
                        "volcano_status": volcano_status,
                        "demo_audio": status_data.get("demo_audio"),
                        "is_ready": status_data.get("is_ready", False)
                    }
                }
            else:
                return {
                    "success": False,
                    "message": f"状态查询失败: {volcano_response.error.message if volcano_response.error else 'Unknown error'}",
                    "error_code": "STATUS_CHECK_FAILED"
                }
                
        except Exception as e:
            self.logger.error(f"音色状态检查失败: {str(e)}")
            return {
                "success": False,
                "message": f"音色状态检查失败: {str(e)}",
                "error_code": "STATUS_CHECK_ERROR"
            }
    
    async def doubao_service_tts_synthesize(
        self,
        user_id: int,
        text: str,
        voice_type: str,
        encoding: str = "mp3",
        speed_ratio: float = 1.0,
        volume_ratio: float = 1.0,
        pitch_ratio: float = 1.0,
        sample_rate: int = 24000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        TTS合成
        [services][doubao_service][tts_synthesize]
        """
        try:
            # 验证用户权限
            user_check = await self.db.execute(
                select(UserBasic).where(UserBasic.user_id == user_id)
            )
            user = user_check.scalar_one_or_none()
            if not user:
                return {
                    "success": False,
                    "message": "用户不存在",
                    "error_code": "USER_NOT_FOUND"
                }
            
            # 执行TTS合成
            volcano_response = await self.volcano_service.volcano_text_to_speech_http(
                text=text,
                voice_type=voice_type,
                encoding=encoding,
                speed_ratio=speed_ratio,
                volume_ratio=volume_ratio,
                pitch_ratio=pitch_ratio,
                sample_rate=sample_rate,
                user_id=str(user_id),
                **kwargs
            )
            
            if volcano_response.success:
                # TODO: 保存合成记录到数据库
                # 这里可以创建VoiceAudioBasic记录
                
                return {
                    "success": True,
                    "message": "TTS合成成功",
                    "data": volcano_response.data
                }
            else:
                return {
                    "success": False,
                    "message": f"TTS合成失败: {volcano_response.error.message if volcano_response.error else 'Unknown error'}",
                    "error_code": "TTS_SYNTHESIS_FAILED"
                }
                
        except Exception as e:
            self.logger.error(f"TTS合成失败: {str(e)}")
            return {
                "success": False,
                "message": f"TTS合成失败: {str(e)}",
                "error_code": "TTS_SYNTHESIS_ERROR"
            }
    
    async def doubao_service_tts_stream(
        self,
        user_id: int,
        text: str,
        voice_type: str,
        encoding: str = "mp3",
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式TTS合成
        [services][doubao_service][tts_stream]
        """
        try:
            # 验证用户权限
            user_check = await self.db.execute(
                select(UserBasic).where(UserBasic.user_id == user_id)
            )
            user = user_check.scalar_one_or_none()
            if not user:
                yield {
                    "success": False,
                    "message": "用户不存在",
                    "error_code": "USER_NOT_FOUND"
                }
                return
            
            # 执行流式TTS
            async for response in self.volcano_service.volcano_text_to_speech_websocket(
                text=text,
                voice_type=voice_type,
                encoding=encoding,
                user_id=str(user_id),
                **kwargs
            ):
                if response.success:
                    yield {
                        "success": True,
                        "data": response.data,
                        "message": "流式数据"
                    }
                else:
                    yield {
                        "success": False,
                        "message": f"流式TTS错误: {response.error.message if response.error else 'Unknown error'}",
                        "error_code": "STREAM_TTS_ERROR"
                    }
                    break
                    
        except Exception as e:
            self.logger.error(f"流式TTS失败: {str(e)}")
            yield {
                "success": False,
                "message": f"流式TTS失败: {str(e)}",
                "error_code": "STREAM_TTS_EXCEPTION"
            }
    
    async def doubao_service_user_voices_list(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户音色列表
        [services][doubao_service][user_voices_list]
        """
        try:
            # 获取用户的音色记录
            result = await self.db.execute(
                select(VoiceTimbreBasic).where(
                    VoiceTimbreBasic.timbre_created_user_id == user_id
                ).order_by(VoiceTimbreBasic.timbre_created_time.desc())
            )
            voices = result.scalars().all()
            
            voice_list = []
            for voice in voices:
                voice_list.append({
                    "timbre_id": voice.timbre_id,
                    "timbre_name": voice.timbre_name,
                    "timbre_description": voice.timbre_description,
                    "timbre_status": voice.timbre_status,
                    "timbre_language": voice.timbre_language,
                    "timbre_platform": voice.timbre_platform,
                    "timbre_created_time": voice.timbre_created_time.isoformat() if voice.timbre_created_time else None,
                    "quality_score": float(voice.timbre_quality_score) if voice.timbre_quality_score else None
                })
            
            return {
                "success": True,
                "message": "音色列表获取成功",
                "data": {
                    "voices": voice_list,
                    "total_count": len(voice_list)
                }
            }
            
        except Exception as e:
            self.logger.error(f"获取用户音色列表失败: {str(e)}")
            return {
                "success": False,
                "message": f"获取音色列表失败: {str(e)}",
                "error_code": "VOICES_LIST_ERROR"
            }
    
    async def doubao_service_health_check(self) -> Dict[str, Any]:
        """
        豆包服务健康检查
        [services][doubao_service][health_check]
        """
        try:
            # 检查火山引擎连接
            volcano_health = await self.volcano_service.volcano_health_check()
            
            return {
                "success": True,
                "message": "豆包服务健康检查完成",
                "data": {
                    "service_status": "healthy",
                    "volcano_engine": {
                        "status": "healthy" if volcano_health.success else "unhealthy",
                        "details": volcano_health.data if volcano_health.success else volcano_health.error.message
                    },
                    "database": "connected",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"豆包服务健康检查失败: {str(e)}")
            return {
                "success": False,
                "message": f"健康检查失败: {str(e)}",
                "error_code": "HEALTH_CHECK_FAILED"
            }
    
    def _language_code_to_string(self, language_code: int) -> str:
        """
        将语言代码转换为字符串
        [services][doubao_service][_language_code_to_string]
        """
        language_map = {
            0: "zh-CN",
            1: "en-US", 
            2: "ja-JP",
            3: "es-ES",
            4: "id-ID",
            5: "pt-PT"
        }
        return language_map.get(language_code, "zh-CN")
    
    async def doubao_service_text_preprocess(
        self,
        text: str,
        operation: str = "normalize",
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        文本预处理
        [services][doubao_service][text_preprocess]
        """
        try:
            processed_text = text.strip()
            
            if parameters:
                # 数字规范化
                if parameters.get("normalize_numbers"):
                    # TODO: 实现数字规范化
                    pass
                
                # 标点符号优化
                if parameters.get("optimize_punctuation"):
                    if not processed_text.endswith(('.', '!', '?', '。', '！', '？')):
                        processed_text += "。"
                
                # 缩写展开
                if parameters.get("expand_abbreviations"):
                    # TODO: 实现缩写展开
                    pass
            
            return {
                "success": True,
                "message": "文本预处理完成",
                "data": {
                    "original_text": text,
                    "processed_text": processed_text,
                    "operation": operation,
                    "parameters": parameters or {},
                    "changes": {
                        "length_change": len(processed_text) - len(text),
                        "character_count": len(processed_text),
                        "word_count": len(processed_text.split())
                    }
                }
            }
            
        except Exception as e:
            self.logger.error(f"文本预处理失败: {str(e)}")
            return {
                "success": False,
                "message": f"文本预处理失败: {str(e)}",
                "error_code": "TEXT_PREPROCESS_ERROR"
            }