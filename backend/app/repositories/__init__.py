"""
Repository Layer Module
数据访问层 - [repositories]
"""

from .base import RepositoryBase
from .user_auth import UserAuthRepository
from .file_storage import FileStorageRepository
# from .text_content import TextContentRepository      # 临时注释，缺少模型
# from .voice_timbre import VoiceTimbreRepository      # 临时注释，缺少模型
# from .voice_audio import VoiceAudioRepository        # 临时注释，缺少模型

__all__ = [
    "RepositoryBase",
    "UserAuthRepository",
    "FileStorageRepository",
    # "TextContentRepository", 
    # "VoiceTimbreRepository",
    # "VoiceAudioRepository",
]