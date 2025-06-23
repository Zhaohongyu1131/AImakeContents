"""
Image Video Models Module
图像视频模块数据模型 - [image_video][models]
"""

from .image_basic import ImageBasic
from .image_analyse import ImageAnalyse
from .image_template import ImageTemplate
from .video_basic import VideoBasic
from .video_analyse import VideoAnalyse
from .video_template import VideoTemplate

__all__ = [
    "ImageBasic",
    "ImageAnalyse",
    "ImageTemplate",
    "VideoBasic", 
    "VideoAnalyse",
    "VideoTemplate",
]