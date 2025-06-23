"""
Schemas Module
API响应模型模块 - [schemas]
"""

from .base import ResponseBaseSchema, PaginationSchema
from .user_auth import *
from .file_storage import *
from .text_content import *
from .voice_timbre import *
from .voice_audio import *
from .image_video import *
from .mixed_content import *

__all__ = [
    "ResponseBaseSchema",
    "PaginationSchema",
    # 用户认证模块
    "UserAuthBasicSchema",
    "UserAuthBasicCreateSchema",
    "UserAuthBasicUpdateSchema",
    "UserAuthProfileSchema",
    "UserAuthProfileCreateSchema",
    "UserAuthProfileUpdateSchema",
    "UserAuthSessionSchema",
    "UserAuthLoginSchema",
    "UserAuthTokenSchema",
    # 文件存储模块
    "FileStorageBasicSchema",
    "FileStorageBasicCreateSchema",
    "FileStorageAnalyseSchema",
    # 文本内容模块
    "TextContentBasicSchema",
    "TextContentBasicCreateSchema",
    "TextContentBasicUpdateSchema",
    "TextContentAnalyseSchema",
    "TextTemplateBasicSchema",
    "TextTemplateBasicCreateSchema",
    "TextTemplateBasicUpdateSchema",
    # 音色管理模块
    "VoiceTimbreBasicSchema",
    "VoiceTimbreBasicCreateSchema",
    "VoiceTimbreBasicUpdateSchema",
    "VoiceTimbreCloneSchema",
    "VoiceTimbreCloneCreateSchema",
    "VoiceTimbreTemplateSchema",
    "VoiceTimbreTemplateCreateSchema",
    # 音频管理模块
    "VoiceAudioBasicSchema",
    "VoiceAudioBasicCreateSchema",
    "VoiceAudioAnalyseSchema",
    "VoiceAudioTemplateSchema",
    "VoiceAudioTemplateCreateSchema",
    # 图像视频模块
    "ImageBasicSchema",
    "ImageBasicCreateSchema",
    "ImageAnalyseSchema",
    "ImageTemplateSchema",
    "VideoBasicSchema",
    "VideoBasicCreateSchema", 
    "VideoAnalyseSchema",
    "VideoTemplateSchema",
    # 混合内容模块
    "MixedContentBasicSchema",
    "MixedContentBasicCreateSchema",
    "MixedContentAnalyseSchema",
    "MixedContentTemplateSchema",
]