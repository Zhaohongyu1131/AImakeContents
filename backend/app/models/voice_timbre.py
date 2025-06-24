"""
Voice Timbre Models
音色模型 - [models][voice_timbre]
"""

# 为了兼容性，重新导出音色相关模型
from app.models.voice_timbre.voice_timbre_basic import VoiceTimbreBasic
from app.models.voice_timbre.voice_timbre_clone import VoiceTimbreClone

__all__ = ["VoiceTimbreBasic", "VoiceTimbreClone"]