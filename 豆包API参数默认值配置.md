# 豆包API参数默认值配置

## 概述

为豆包API的所有参数提供科学合理的默认建议值，分为基础设置和高级设置两个层次，确保用户在不同使用场景下都能获得最佳体验。

## 1. 音色克隆参数默认值

### 1.1 基础设置默认值

```json
{
  "voice_clone_basic_defaults": {
    "timbre_name": "",
    "timbre_description": "",
    "language": {
      "default": 0,
      "options": [
        { "value": 0, "label": "中文", "recommended": true },
        { "value": 1, "label": "英文" },
        { "value": 2, "label": "日语" },
        { "value": 3, "label": "西班牙语" },
        { "value": 4, "label": "印尼语" },
        { "value": 5, "label": "葡萄牙语" }
      ]
    },
    "model_type": {
      "default": 1,
      "recommended": 1,
      "options": [
        { 
          "value": 0, 
          "label": "1.0效果", 
          "description": "经典版本，稳定可靠",
          "recommended": false
        },
        { 
          "value": 1, 
          "label": "2.0效果(ICL)", 
          "description": "推荐选择，音质自然，训练速度快",
          "recommended": true
        },
        { 
          "value": 2, 
          "label": "DiT标准版", 
          "description": "还原音色，不保留个人风格",
          "recommended": false
        },
        { 
          "value": 3, 
          "label": "DiT还原版", 
          "description": "还原音色和个人说话风格",
          "recommended": false,
          "advanced": true
        }
      ]
    },
    "source": 2,
    "audio_requirements": {
      "min_duration": 10,
      "max_duration": 60,
      "max_file_size": 10485760,
      "supported_formats": ["wav", "mp3", "ogg", "m4a", "aac", "pcm"],
      "recommended_format": "wav"
    }
  }
}
```

### 1.2 高级设置默认值

```json
{
  "voice_clone_advanced_defaults": {
    "reference_text": {
      "default": "",
      "max_length": 1000,
      "placeholder": "可选：输入音频中说话的内容文本，有助于提高训练质量"
    },
    "audio_format": {
      "default": "wav",
      "recommended": "wav",
      "options": [
        { "value": "wav", "label": "WAV", "description": "无损音质，推荐" },
        { "value": "mp3", "label": "MP3", "description": "压缩格式" },
        { "value": "ogg", "label": "OGG", "description": "开源格式" },
        { "value": "m4a", "label": "M4A", "description": "Apple格式" },
        { "value": "aac", "label": "AAC", "description": "高效压缩" },
        { "value": "pcm", "label": "PCM", "description": "原始格式" }
      ]
    },
    "quality_priority": {
      "default": "balanced",
      "options": [
        { "value": "speed", "label": "速度优先", "description": "快速训练，标准质量" },
        { "value": "balanced", "label": "平衡模式", "description": "速度和质量平衡", "recommended": true },
        { "value": "quality", "label": "质量优先", "description": "最佳音质，训练时间较长" }
      ]
    },
    "noise_reduction": {
      "default": true,
      "description": "智能降噪，提高音频质量"
    },
    "volume_normalization": {
      "default": true,
      "description": "音量标准化，确保音量一致性"
    },
    "training_iterations": {
      "default": 100,
      "min": 50,
      "max": 200,
      "step": 10,
      "marks": {
        "50": "快速",
        "100": "标准",
        "150": "精细", 
        "200": "极致"
      }
    },
    "learning_rate": {
      "default": 0.001,
      "min": 0.0001,
      "max": 0.01,
      "step": 0.0001,
      "marks": {
        "0.0001": "保守",
        "0.001": "标准",
        "0.005": "激进",
        "0.01": "极速"
      }
    },
    "experimental_features": {
      "voice_conversion": {
        "default": false,
        "description": "声音转换增强，实验性功能"
      },
      "emotion_preservation": {
        "default": false,
        "description": "情感保持，实验性功能"
      }
    }
  }
}
```

## 2. 语音合成参数默认值

### 2.1 基础设置默认值

```json
{
  "tts_basic_defaults": {
    "voice_type": {
      "default": "",
      "required": true,
      "placeholder": "请选择音色"
    },
    "speed_ratio": {
      "default": 1.0,
      "min": 0.2,
      "max": 3.0,
      "step": 0.1,
      "marks": {
        "0.2": "很慢",
        "0.5": "慢",
        "1.0": "正常",
        "1.5": "快", 
        "2.0": "很快",
        "3.0": "极快"
      },
      "presets": {
        "news": 0.8,
        "presentation": 1.2,
        "storytelling": 0.9,
        "audiobook": 0.95
      }
    },
    "volume_ratio": {
      "default": 1.0,
      "min": 0.1,
      "max": 2.0,
      "step": 0.1,
      "marks": {
        "0.1": "很小",
        "0.5": "小",
        "1.0": "正常",
        "1.5": "大",
        "2.0": "很大"
      }
    },
    "pitch_ratio": {
      "default": 1.0,
      "min": 0.5,
      "max": 2.0,
      "step": 0.1,
      "marks": {
        "0.5": "很低",
        "0.8": "低",
        "1.0": "正常",
        "1.2": "高",
        "2.0": "很高"
      }
    },
    "encoding": {
      "default": "mp3",
      "recommended": "mp3",
      "options": [
        { 
          "value": "mp3", 
          "label": "MP3", 
          "description": "推荐格式，兼容性好，文件小",
          "recommended": true,
          "file_size": "small"
        },
        { 
          "value": "wav", 
          "label": "WAV", 
          "description": "无损音质，文件较大",
          "file_size": "large",
          "quality": "highest"
        },
        { 
          "value": "ogg_opus", 
          "label": "OGG Opus", 
          "description": "高压缩比，音质优秀",
          "file_size": "small",
          "quality": "high"
        },
        { 
          "value": "pcm", 
          "label": "PCM", 
          "description": "原始格式，专业用途",
          "file_size": "largest",
          "quality": "highest",
          "advanced": true
        }
      ]
    },
    "rate": {
      "default": 24000,
      "recommended": 24000,
      "options": [
        { 
          "value": 8000, 
          "label": "8kHz", 
          "description": "电话质量，文件最小",
          "quality": "low"
        },
        { 
          "value": 16000, 
          "label": "16kHz", 
          "description": "标准质量，平衡选择",
          "quality": "standard"
        },
        { 
          "value": 24000, 
          "label": "24kHz", 
          "description": "高质量，推荐选择",
          "quality": "high",
          "recommended": true
        }
      ]
    },
    "language": {
      "default": "zh-CN",
      "options": [
        { "value": "zh-CN", "label": "中文（简体）", "recommended": true },
        { "value": "zh-TW", "label": "中文（繁体）" },
        { "value": "en-US", "label": "英语（美式）" },
        { "value": "en-GB", "label": "英语（英式）" },
        { "value": "ja-JP", "label": "日语" },
        { "value": "ko-KR", "label": "韩语" }
      ]
    },
    "quick_presets": {
      "news_broadcast": {
        "speed_ratio": 0.8,
        "pitch_ratio": 0.9,
        "volume_ratio": 1.1,
        "description": "新闻播报 - 稳重清晰"
      },
      "energetic_presentation": {
        "speed_ratio": 1.2,
        "pitch_ratio": 1.1,
        "volume_ratio": 1.0,
        "description": "活力讲解 - 生动有趣"
      },
      "gentle_narration": {
        "speed_ratio": 0.9,
        "pitch_ratio": 0.95,
        "volume_ratio": 0.9,
        "description": "温和叙述 - 温馨自然"
      },
      "audiobook": {
        "speed_ratio": 0.95,
        "pitch_ratio": 1.0,
        "volume_ratio": 0.95,
        "description": "有声读物 - 舒缓耐听"
      }
    }
  }
}
```

### 2.2 高级设置默认值

```json
{
  "tts_advanced_defaults": {
    "explicit_language": {
      "default": "zh",
      "options": [
        { "value": "", "label": "自动检测", "description": "智能识别语种" },
        { "value": "crosslingual", "label": "多语种混合", "description": "支持中英日等混读" },
        { "value": "zh", "label": "中文为主", "description": "支持中英混读", "recommended": true },
        { "value": "en", "label": "仅英文", "description": "纯英文处理" },
        { "value": "ja", "label": "仅日文", "description": "纯日文处理" },
        { "value": "es-mx", "label": "仅墨西哥语", "description": "纯墨西哥语处理" },
        { "value": "id", "label": "仅印尼语", "description": "纯印尼语处理" },
        { "value": "pt-br", "label": "仅巴西葡语", "description": "纯巴西葡萄牙语处理" }
      ]
    },
    "context_language": {
      "default": "",
      "options": [
        { "value": "", "label": "默认(英语参考)", "recommended": true },
        { "value": "id", "label": "印尼语参考" },
        { "value": "es", "label": "西班牙语参考" },
        { "value": "pt", "label": "葡萄牙语参考" }
      ]
    },
    "text_type": {
      "default": "plain",
      "options": [
        { 
          "value": "plain", 
          "label": "纯文本", 
          "description": "普通文本，自动处理标点和停顿",
          "recommended": true
        },
        { 
          "value": "ssml", 
          "label": "SSML标记语言", 
          "description": "支持精确的语音控制标记",
          "advanced": true
        }
      ]
    },
    "with_timestamp": {
      "default": false,
      "description": "返回文本的时间戳信息，用于字幕同步等高级功能"
    },
    "split_sentence": {
      "default": false,
      "description": "专门针对1.0音色的语速优化，解决语速过快问题",
      "applicable_to": ["model_type_0"]
    },
    "cache_config": {
      "enabled": {
        "default": false,
        "description": "缓存相同文本的合成结果，大幅提高重复内容的响应速度"
      },
      "text_type": {
        "default": 1,
        "when_enabled": true
      },
      "use_cache": {
        "default": true,
        "when_enabled": true
      }
    },
    "cluster": {
      "default": "volcano_icl",
      "options": [
        { 
          "value": "volcano_icl", 
          "label": "标准集群", 
          "description": "平衡性能和质量，适合大多数场景",
          "recommended": true
        },
        { 
          "value": "volcano_icl_concurr", 
          "label": "并发集群", 
          "description": "高并发处理，适合大量请求场景"
        }
      ]
    },
    "operation": {
      "default": "query",
      "http_only": "query",
      "websocket_options": ["query", "submit"]
    },
    "performance_optimization": {
      "audio_only": {
        "default": true,
        "description": "仅返回音频数据，减少响应大小"
      },
      "compression": {
        "default": false,
        "description": "启用响应压缩"
      }
    },
    "experimental_features": {
      "voice_optimization": {
        "default": false,
        "description": "音质增强，实验性功能"
      },
      "adaptive_speed": {
        "default": false,
        "description": "自适应语速，根据内容自动调整"
      },
      "emotion_detection": {
        "default": false,
        "description": "情感检测，根据文本情感调整语调"
      }
    },
    "custom_parameters": {
      "default": "",
      "format": "json",
      "placeholder": "例如: {\"custom_param\": \"value\"}",
      "description": "高级用户可输入JSON格式的额外参数"
    }
  }
}
```

## 3. 场景化默认配置

### 3.1 常见使用场景预设

```json
{
  "scenario_presets": {
    "podcast": {
      "name": "播客节目",
      "description": "适合播客、访谈等长时间收听场景",
      "settings": {
        "speed_ratio": 1.0,
        "pitch_ratio": 1.0,
        "volume_ratio": 0.95,
        "encoding": "mp3",
        "rate": 24000,
        "cache_enabled": true,
        "with_timestamp": false
      }
    },
    "advertisement": {
      "name": "广告配音",
      "description": "适合广告、宣传片等营销内容",
      "settings": {
        "speed_ratio": 1.1,
        "pitch_ratio": 1.05,
        "volume_ratio": 1.1,
        "encoding": "mp3",
        "rate": 24000,
        "cache_enabled": false,
        "with_timestamp": false
      }
    },
    "audiobook": {
      "name": "有声读物",
      "description": "适合长篇内容朗读，舒缓耐听",
      "settings": {
        "speed_ratio": 0.9,
        "pitch_ratio": 0.98,
        "volume_ratio": 0.9,
        "encoding": "mp3",
        "rate": 24000,
        "cache_enabled": true,
        "with_timestamp": true,
        "split_sentence": true
      }
    },
    "education": {
      "name": "教育培训",
      "description": "适合课程讲解、知识传授",
      "settings": {
        "speed_ratio": 0.95,
        "pitch_ratio": 1.0,
        "volume_ratio": 1.0,
        "encoding": "mp3",
        "rate": 24000,
        "cache_enabled": true,
        "with_timestamp": true
      }
    },
    "news": {
      "name": "新闻播报",
      "description": "适合新闻、资讯类内容播报",
      "settings": {
        "speed_ratio": 0.85,
        "pitch_ratio": 0.95,
        "volume_ratio": 1.0,
        "encoding": "mp3",
        "rate": 24000,
        "cache_enabled": false,
        "with_timestamp": false
      }
    },
    "storytelling": {
      "name": "故事讲述",
      "description": "适合儿童故事、小说朗读",
      "settings": {
        "speed_ratio": 0.9,
        "pitch_ratio": 1.02,
        "volume_ratio": 0.95,
        "encoding": "mp3",
        "rate": 24000,
        "cache_enabled": true,
        "with_timestamp": false
      }
    },
    "customer_service": {
      "name": "客服语音",
      "description": "适合客服系统、语音助手",
      "settings": {
        "speed_ratio": 1.0,
        "pitch_ratio": 1.0,
        "volume_ratio": 1.0,
        "encoding": "pcm",
        "rate": 16000,
        "cache_enabled": true,
        "with_timestamp": false,
        "cluster": "volcano_icl_concurr"
      }
    }
  }
}
```

### 3.2 音色类型推荐配置

```json
{
  "voice_type_recommendations": {
    "male_professional": {
      "description": "专业男声",
      "recommended_settings": {
        "speed_ratio": 0.95,
        "pitch_ratio": 0.95,
        "volume_ratio": 1.0
      },
      "best_scenarios": ["news", "education", "customer_service"]
    },
    "female_gentle": {
      "description": "温柔女声",
      "recommended_settings": {
        "speed_ratio": 0.9,
        "pitch_ratio": 1.05,
        "volume_ratio": 0.95
      },
      "best_scenarios": ["audiobook", "storytelling", "advertisement"]
    },
    "child_voice": {
      "description": "儿童声音",
      "recommended_settings": {
        "speed_ratio": 1.1,
        "pitch_ratio": 1.2,
        "volume_ratio": 1.0
      },
      "best_scenarios": ["storytelling", "education"]
    },
    "elderly_voice": {
      "description": "老年声音",
      "recommended_settings": {
        "speed_ratio": 0.8,
        "pitch_ratio": 0.9,
        "volume_ratio": 1.1
      },
      "best_scenarios": ["audiobook", "storytelling"]
    }
  }
}
```

## 4. 智能推荐规则

### 4.1 基于内容类型的推荐

```json
{
  "content_based_recommendations": {
    "rules": [
      {
        "condition": "text_length > 1000",
        "recommendations": {
          "cache_enabled": true,
          "split_sentence": true,
          "speed_ratio": 0.9,
          "description": "长文本建议启用缓存和分句处理"
        }
      },
      {
        "condition": "contains_numbers || contains_english",
        "recommendations": {
          "explicit_language": "zh",
          "description": "包含数字或英文时建议设置明确语种"
        }
      },
      {
        "condition": "is_dialogue || contains_emotion_words",
        "recommendations": {
          "emotion_detection": true,
          "speed_ratio": 1.0,
          "description": "对话或情感内容建议启用情感检测"
        }
      },
      {
        "condition": "is_technical_content",
        "recommendations": {
          "speed_ratio": 0.85,
          "split_sentence": true,
          "description": "技术内容建议放慢语速并分句处理"
        }
      }
    ]
  }
}
```

### 4.2 性能优化建议

```json
{
  "performance_recommendations": {
    "high_frequency_usage": {
      "cache_enabled": true,
      "cluster": "volcano_icl_concurr",
      "encoding": "mp3",
      "description": "高频使用建议启用缓存和并发集群"
    },
    "batch_processing": {
      "encoding": "pcm",
      "rate": 16000,
      "audio_only": true,
      "description": "批量处理建议使用PCM格式和较低采样率"
    },
    "real_time_interaction": {
      "cluster": "volcano_icl_concurr",
      "cache_enabled": true,
      "encoding": "mp3",
      "rate": 16000,
      "description": "实时交互建议使用并发集群和压缩格式"
    },
    "high_quality_production": {
      "encoding": "wav",
      "rate": 24000,
      "quality_priority": "quality",
      "noise_reduction": true,
      "description": "高质量制作建议使用无损格式和质量优先模式"
    }
  }
}
```

## 5. 验证规则配置

### 5.1 参数验证规则

```json
{
  "validation_rules": {
    "voice_clone": {
      "timbre_name": {
        "required": true,
        "min_length": 1,
        "max_length": 50,
        "pattern": "^[\\u4e00-\\u9fa5a-zA-Z0-9\\s_-]+$",
        "error_messages": {
          "required": "音色名称不能为空",
          "min_length": "音色名称至少需要1个字符",
          "max_length": "音色名称不能超过50个字符",
          "pattern": "音色名称只能包含中文、英文、数字、空格、下划线和横线"
        }
      },
      "audio_file": {
        "required": true,
        "max_size": 10485760,
        "allowed_formats": ["wav", "mp3", "ogg", "m4a", "aac"],
        "min_duration": 5,
        "max_duration": 120,
        "error_messages": {
          "required": "请上传音频文件",
          "max_size": "文件大小不能超过10MB",
          "allowed_formats": "仅支持WAV、MP3、OGG、M4A、AAC格式",
          "min_duration": "音频时长不能少于5秒",
          "max_duration": "音频时长不能超过2分钟"
        }
      }
    },
    "tts": {
      "text": {
        "required": true,
        "max_length": 1024,
        "encoding": "utf-8",
        "error_messages": {
          "required": "合成文本不能为空",
          "max_length": "文本长度不能超过1024字节（UTF-8编码）"
        }
      },
      "speed_ratio": {
        "min": 0.2,
        "max": 3.0,
        "step": 0.1,
        "error_messages": {
          "min": "语速不能低于0.2倍",
          "max": "语速不能超过3.0倍"
        }
      },
      "volume_ratio": {
        "min": 0.1,
        "max": 2.0,
        "step": 0.1,
        "error_messages": {
          "min": "音量不能低于0.1倍",
          "max": "音量不能超过2.0倍"
        }
      },
      "pitch_ratio": {
        "min": 0.5,
        "max": 2.0,
        "step": 0.1,
        "error_messages": {
          "min": "音调不能低于0.5倍",
          "max": "音调不能超过2.0倍"
        }
      }
    }
  }
}
```

## 6. 用户偏好学习配置

### 6.1 个性化推荐机制

```json
{
  "user_preference_learning": {
    "tracking_parameters": [
      "speed_ratio",
      "pitch_ratio", 
      "volume_ratio",
      "encoding",
      "rate",
      "voice_type_category",
      "scenario_type"
    ],
    "learning_rules": {
      "min_usage_count": 5,
      "confidence_threshold": 0.7,
      "update_frequency": "weekly"
    },
    "preference_categories": {
      "speed_preference": {
        "slow": { "range": [0.2, 0.8], "label": "偏好慢语速" },
        "normal": { "range": [0.8, 1.2], "label": "偏好正常语速" },
        "fast": { "range": [1.2, 3.0], "label": "偏好快语速" }
      },
      "quality_preference": {
        "size_priority": { "encoding": "mp3", "rate": 16000, "label": "偏好小文件" },
        "balanced": { "encoding": "mp3", "rate": 24000, "label": "偏好平衡" },
        "quality_priority": { "encoding": "wav", "rate": 24000, "label": "偏好高音质" }
      }
    }
  }
}
```

## 7. 环境适配配置

### 7.1 设备和网络适配

```json
{
  "environment_adaptation": {
    "device_types": {
      "mobile": {
        "encoding": "mp3",
        "rate": 16000,
        "cache_enabled": true,
        "description": "移动设备优化：小文件、低带宽"
      },
      "desktop": {
        "encoding": "mp3",
        "rate": 24000,
        "cache_enabled": false,
        "description": "桌面设备：标准配置"
      },
      "server": {
        "encoding": "pcm", 
        "rate": 24000,
        "cluster": "volcano_icl_concurr",
        "description": "服务器环境：高性能配置"
      }
    },
    "network_conditions": {
      "slow_network": {
        "encoding": "mp3",
        "rate": 8000,
        "cache_enabled": true,
        "description": "慢网络优化"
      },
      "fast_network": {
        "encoding": "wav",
        "rate": 24000,
        "cache_enabled": false,
        "description": "快网络高质量"
      }
    }
  }
}
```

## 总结

这套参数默认值配置提供了：

1. **科学的默认值** - 基于最佳实践和用户体验优化
2. **场景化预设** - 针对不同使用场景的专门配置
3. **智能推荐** - 基于内容和使用习惯的动态推荐
4. **验证规则** - 确保参数的有效性和安全性
5. **个性化学习** - 基于用户行为的偏好学习机制
6. **环境适配** - 根据设备和网络条件自动优化

通过这样的配置体系，可以确保用户在任何情况下都能获得最适合的参数设置，提升整体使用体验。