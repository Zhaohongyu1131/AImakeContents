"""
Models Module
数据模型模块 - [models]
"""

from .base import ModelBase

# 导入所有业务模型
from .user_auth import *
from .file_storage import *
from .text_content import *
from .voice_timbre import *
from .voice_audio import *
from .image_video import *
from .mixed_content import *

__all__ = [
    "ModelBase",
    # 用户认证模块
    "UserAuthBasic",
    "UserAuthProfile",
    "UserAuthSession",
    # 文件存储模块
    "FileStorageBasic",
    "FileStorageAnalyse",
    # 文本内容模块
    "TextContentBasic",
    "TextContentAnalyse",
    "TextTemplateBasic",
    # 音色管理模块
    "VoiceTimbreBasic",
    "VoiceTimbreClone",
    "VoiceTimbreTemplate",
    # 音频管理模块
    "VoiceAudioBasic",
    "VoiceAudioAnalyse",
    "VoiceAudioTemplate",
    # 图像视频模块
    "ImageBasic",
    "ImageAnalyse",
    "ImageTemplate",
    "VideoBasic",
    "VideoAnalyse",
    "VideoTemplate",
    # 混合内容模块
    "MixedContentBasic",
    "MixedContentAnalyse",
    "MixedContentTemplate",
]