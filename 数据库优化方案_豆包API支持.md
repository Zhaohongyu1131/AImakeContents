# 数据库优化方案 - 豆包API完整支持

## 概述

根据豆包API调用说明文档，需要对现有数据库设计进行优化，确保支持所有豆包API参数，并为界面设计提供基础设置和高级设置的数据支持。

## 1. 音色克隆模块优化

### 1.1 voice_timbre_basic 表字段补充

```sql
-- 添加豆包API特有字段
ALTER TABLE voice_timbre_basic 
ADD COLUMN timbre_speaker_id VARCHAR(100),                    -- 豆包speaker_id (S_开头)
ADD COLUMN timbre_model_type INTEGER DEFAULT 1,               -- 模型类型 0=1.0, 1=2.0, 2=DiT标准, 3=DiT还原
ADD COLUMN timbre_source_duration DECIMAL(10,2),             -- 源音频时长
ADD COLUMN timbre_training_text TEXT,                        -- 训练用参考文本
ADD COLUMN timbre_demo_audio_url VARCHAR(500),               -- 训练完成后的demo音频URL
ADD COLUMN timbre_version VARCHAR(10) DEFAULT 'V1',          -- 训练版本
ADD COLUMN timbre_create_time_volcano BIGINT,                -- 火山引擎创建时间戳
ADD COLUMN timbre_available_training_times INTEGER DEFAULT 10, -- 剩余训练次数
ADD COLUMN timbre_instance_no VARCHAR(100),                  -- 火山引擎实例编号
ADD COLUMN timbre_is_activable BOOLEAN DEFAULT TRUE,         -- 是否可激活
ADD COLUMN timbre_expire_time BIGINT,                        -- 过期时间戳
ADD COLUMN timbre_order_time BIGINT,                         -- 下单时间戳
ADD COLUMN timbre_alias VARCHAR(100);                        -- 别名

-- 创建新索引
CREATE INDEX idx_voice_timbre_basic_speaker_id ON voice_timbre_basic(timbre_speaker_id);
CREATE INDEX idx_voice_timbre_basic_model_type ON voice_timbre_basic(timbre_model_type);
```

### 1.2 voice_timbre_clone 表字段补充

```sql
-- 优化克隆参数存储结构
ALTER TABLE voice_timbre_clone 
ADD COLUMN clone_audio_format VARCHAR(20) DEFAULT 'wav',     -- 音频格式
ADD COLUMN clone_audio_bytes_base64 TEXT,                    -- base64编码的音频数据
ADD COLUMN clone_reference_text TEXT,                        -- 参考文本
ADD COLUMN clone_language INTEGER DEFAULT 0,                -- 语种：0=中文,1=英文,2=日语等
ADD COLUMN clone_model_type INTEGER DEFAULT 1,              -- 模型类型
ADD COLUMN clone_volcano_task_id VARCHAR(100),              -- 火山引擎任务ID
ADD COLUMN clone_demo_audio_url VARCHAR(500),               -- 生成的demo音频URL
ADD COLUMN clone_wer_score DECIMAL(5,2),                    -- 字错率分数
ADD COLUMN clone_snr_score DECIMAL(5,2),                    -- 信噪比分数
ADD COLUMN clone_quality_check_result JSONB;                -- 质量检查结果

-- 更新clone_training_params的标准结构
COMMENT ON COLUMN voice_timbre_clone.clone_training_params IS 
'标准结构: {
  "volcano_params": {
    "speaker_id": "S_xxxxx",
    "audio_format": "wav",
    "text": "参考文本",
    "source": 2,
    "language": 0,
    "model_type": 1
  },
  "quality_requirements": {
    "min_duration": 10,
    "max_wer": 0.3,
    "min_snr": 15
  }
}';
```

## 2. 音频合成模块优化

### 2.1 voice_audio_basic 表字段补充

```sql
-- 添加豆包TTS API参数支持
ALTER TABLE voice_audio_basic 
ADD COLUMN audio_encoding VARCHAR(20) DEFAULT 'mp3',         -- 音频编码：wav,pcm,ogg_opus,mp3
ADD COLUMN audio_sample_rate INTEGER DEFAULT 24000,          -- 采样率：8000,16000,24000
ADD COLUMN audio_explicit_language VARCHAR(20),              -- 明确语种：crosslingual,zh,en,ja等
ADD COLUMN audio_context_language VARCHAR(20),               -- 参考语种：id,es,pt等
ADD COLUMN audio_text_type VARCHAR(20) DEFAULT 'plain',      -- 文本类型：plain,ssml
ADD COLUMN audio_with_timestamp INTEGER DEFAULT 0,           -- 时间戳：0/1
ADD COLUMN audio_split_sentence INTEGER DEFAULT 0,           -- 分句处理：0/1
ADD COLUMN audio_cluster VARCHAR(50) DEFAULT 'volcano_icl',  -- 业务集群
ADD COLUMN audio_reqid VARCHAR(100),                         -- 请求ID
ADD COLUMN audio_volcano_sequence INTEGER,                   -- 火山引擎序列号
ADD COLUMN audio_cache_enabled BOOLEAN DEFAULT FALSE,        -- 是否启用缓存
ADD COLUMN audio_synthesis_params JSONB,                     -- 完整合成参数
ADD COLUMN audio_response_data JSONB,                        -- API响应数据
ADD COLUMN audio_processing_time_ms INTEGER,                 -- 处理耗时(毫秒)
ADD COLUMN audio_error_code INTEGER,                         -- 错误码
ADD COLUMN audio_error_message TEXT;                         -- 错误信息

-- 更新audio_synthesis_params的标准结构
COMMENT ON COLUMN voice_audio_basic.audio_synthesis_params IS 
'标准结构: {
  "app": {
    "appid": "xxx",
    "token": "access_token", 
    "cluster": "volcano_icl"
  },
  "user": {
    "uid": "user_id"
  },
  "audio": {
    "voice_type": "S_xxxxx",
    "encoding": "mp3",
    "rate": 24000,
    "speed_ratio": 1.0,
    "volume_ratio": 1.0,
    "pitch_ratio": 1.0,
    "explicit_language": "zh",
    "context_language": null
  },
  "request": {
    "reqid": "uuid",
    "text": "合成文本",
    "text_type": "plain",
    "operation": "query",
    "with_timestamp": 0,
    "split_sentence": 0,
    "extra_param": "{\"cache_config\":{\"text_type\":1,\"use_cache\":true}}"
  }
}';

-- 创建新索引
CREATE INDEX idx_voice_audio_basic_encoding ON voice_audio_basic(audio_encoding);
CREATE INDEX idx_voice_audio_basic_language ON voice_audio_basic(audio_explicit_language);
CREATE INDEX idx_voice_audio_basic_reqid ON voice_audio_basic(audio_reqid);
```

### 2.2 voice_audio_template 表优化

```sql
-- 优化模板参数存储
ALTER TABLE voice_audio_template 
ADD COLUMN template_basic_settings JSONB,                    -- 基础设置参数
ADD COLUMN template_advanced_settings JSONB;                -- 高级设置参数

-- 基础设置参数结构
COMMENT ON COLUMN voice_audio_template.template_basic_settings IS 
'基础设置参数: {
  "voice_type": "S_xxxxx",          # 音色选择
  "speed_ratio": 1.0,               # 语速倍率 [0.2-3.0]
  "volume_ratio": 1.0,              # 音量倍率 [0.1-2.0] 
  "pitch_ratio": 1.0,               # 音调倍率 [0.5-2.0]
  "encoding": "mp3",                # 音频格式
  "sample_rate": 24000,             # 采样率
  "language": "zh-CN"               # 主要语言
}';

-- 高级设置参数结构  
COMMENT ON COLUMN voice_audio_template.template_advanced_settings IS 
'高级设置参数: {
  "explicit_language": "zh",        # 明确语种控制
  "context_language": null,         # 参考语种
  "text_type": "plain",             # 文本类型：plain/ssml
  "with_timestamp": 0,              # 启用时间戳：0/1
  "split_sentence": 0,              # 分句处理：0/1 (针对1.0音色)
  "cache_enabled": false,           # 启用缓存
  "cluster": "volcano_icl",         # 集群选择
  "model_optimization": {           # 模型优化选项
    "quality_priority": "speed",    # 优先级：speed/quality/balanced
    "noise_reduction": true,        # 降噪处理
    "voice_enhancement": false     # 音质增强
  }
}';
```

## 3. 参数配置表设计

### 3.1 创建豆包API配置表

```sql
-- 豆包API配置表
CREATE TABLE volcano_api_config (
    config_id SERIAL PRIMARY KEY,
    config_name VARCHAR(100) NOT NULL,
    config_type VARCHAR(50) NOT NULL,                        -- voice_clone, tts_basic, tts_advanced
    config_category VARCHAR(50) NOT NULL,                    -- basic, advanced
    config_key VARCHAR(100) NOT NULL,
    config_label VARCHAR(100) NOT NULL,                      -- 界面显示标签
    config_description TEXT,                                 -- 参数说明
    config_data_type VARCHAR(20) NOT NULL,                   -- string, integer, float, boolean, select
    config_default_value TEXT,                               -- 默认值
    config_options JSONB,                                    -- 选项列表(用于select类型)
    config_validation_rules JSONB,                           -- 验证规则
    config_display_order INTEGER DEFAULT 0,                  -- 显示顺序
    config_is_required BOOLEAN DEFAULT FALSE,                -- 是否必填
    config_is_visible BOOLEAN DEFAULT TRUE,                  -- 是否显示
    config_group_name VARCHAR(50),                           -- 分组名称
    config_created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    config_updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_volcano_api_config_type ON volcano_api_config(config_type);
CREATE INDEX idx_volcano_api_config_category ON volcano_api_config(config_category);
CREATE INDEX idx_volcano_api_config_group ON volcano_api_config(config_group_name);
```

### 3.2 参数配置数据初始化

```sql
-- 插入基础设置参数配置
INSERT INTO volcano_api_config (config_name, config_type, config_category, config_key, config_label, config_description, config_data_type, config_default_value, config_options, config_validation_rules, config_display_order, config_is_required, config_group_name) VALUES

-- 音色克隆基础设置
('音色名称', 'voice_clone', 'basic', 'timbre_name', '音色名称', '为您的音色起一个易识别的名称', 'string', '', null, '{"min_length": 1, "max_length": 50}', 1, true, '基本信息'),
('音色描述', 'voice_clone', 'basic', 'timbre_description', '音色描述', '描述音色的特点和用途', 'string', '', null, '{"max_length": 200}', 2, false, '基本信息'),
('语言类型', 'voice_clone', 'basic', 'language', '语言类型', '选择音色主要支持的语言', 'select', '0', '{"options": [{"value": "0", "label": "中文"}, {"value": "1", "label": "英文"}, {"value": "2", "label": "日语"}, {"value": "3", "label": "西班牙语"}, {"value": "4", "label": "印尼语"}, {"value": "5", "label": "葡萄牙语"}]}', null, 3, true, '基本信息'),
('模型类型', 'voice_clone', 'basic', 'model_type', '模型类型', '选择音色训练使用的模型版本', 'select', '1', '{"options": [{"value": "1", "label": "2.0效果(ICL) - 推荐"}, {"value": "0", "label": "1.0效果"}, {"value": "2", "label": "DiT标准版(音色)"}, {"value": "3", "label": "DiT还原版(音色+风格)"}]}', null, 4, true, '训练设置'),

-- 音色克隆高级设置  
('参考文本', 'voice_clone', 'advanced', 'reference_text', '参考文本', '提供参考文本可提高训练质量，音频内容应与此文本一致', 'string', '', null, '{"max_length": 1000}', 1, false, '质量优化'),
('音频格式', 'voice_clone', 'advanced', 'audio_format', '音频格式', '源音频文件格式', 'select', 'wav', '{"options": [{"value": "wav", "label": "WAV"}, {"value": "mp3", "label": "MP3"}, {"value": "ogg", "label": "OGG"}, {"value": "m4a", "label": "M4A"}, {"value": "aac", "label": "AAC"}, {"value": "pcm", "label": "PCM"}]}', null, 2, false, '音频设置'),

-- TTS合成基础设置
('语速', 'tts_basic', 'basic', 'speed_ratio', '语速', '调整语音播放速度', 'float', '1.0', null, '{"min": 0.2, "max": 3.0, "step": 0.1}', 1, false, '语音控制'),
('音量', 'tts_basic', 'basic', 'volume_ratio', '音量', '调整语音音量大小', 'float', '1.0', null, '{"min": 0.1, "max": 2.0, "step": 0.1}', 2, false, '语音控制'),
('音调', 'tts_basic', 'basic', 'pitch_ratio', '音调', '调整语音音调高低', 'float', '1.0', null, '{"min": 0.5, "max": 2.0, "step": 0.1}', 3, false, '语音控制'),
('音频格式', 'tts_basic', 'basic', 'encoding', '音频格式', '选择输出音频格式', 'select', 'mp3', '{"options": [{"value": "mp3", "label": "MP3 - 推荐"}, {"value": "wav", "label": "WAV - 高质量"}, {"value": "ogg_opus", "label": "OGG Opus - 压缩"}, {"value": "pcm", "label": "PCM - 原始"}]}', null, 4, false, '输出设置'),
('采样率', 'tts_basic', 'basic', 'sample_rate', '采样率', '音频采样率，影响音质', 'select', '24000', '{"options": [{"value": "8000", "label": "8kHz - 电话质量"}, {"value": "16000", "label": "16kHz - 标准质量"}, {"value": "24000", "label": "24kHz - 高质量"}]}', null, 5, false, '输出设置'),

-- TTS合成高级设置
('语种控制', 'tts_basic', 'advanced', 'explicit_language', '语种控制', '精确控制文本语种识别', 'select', 'zh', '{"options": [{"value": "", "label": "自动检测"}, {"value": "crosslingual", "label": "多语种混合"}, {"value": "zh", "label": "中文为主"}, {"value": "en", "label": "仅英文"}, {"value": "ja", "label": "仅日文"}, {"value": "es-mx", "label": "仅墨西哥语"}, {"value": "id", "label": "仅印尼语"}, {"value": "pt-br", "label": "仅巴西葡萄牙语"}]}', null, 1, false, '语言设置'),
('参考语种', 'tts_basic', 'advanced', 'context_language', '参考语种', '为西欧语种提供参考语言', 'select', '', '{"options": [{"value": "", "label": "默认(英语)"}, {"value": "id", "label": "印尼语参考"}, {"value": "es", "label": "西班牙语参考"}, {"value": "pt", "label": "葡萄牙语参考"}]}', null, 2, false, '语言设置'),
('文本类型', 'tts_basic', 'advanced', 'text_type', '文本类型', '文本标记语言类型', 'select', 'plain', '{"options": [{"value": "plain", "label": "纯文本"}, {"value": "ssml", "label": "SSML标记语言"}]}', null, 3, false, '文本处理'),
('时间戳', 'tts_basic', 'advanced', 'with_timestamp', '时间戳', '返回原文本的时间戳信息', 'boolean', 'false', null, null, 4, false, '输出选项'),
('分句处理', 'tts_basic', 'advanced', 'split_sentence', '分句处理', '针对1.0音色的语速优化(解决语速过快问题)', 'boolean', 'false', null, null, 5, false, '1.0音色优化'),
('启用缓存', 'tts_basic', 'advanced', 'cache_enabled', '启用缓存', '缓存相同文本的合成结果，提高响应速度', 'boolean', 'false', null, null, 6, false, '性能优化'),
('集群选择', 'tts_basic', 'advanced', 'cluster', '集群选择', '选择处理集群类型', 'select', 'volcano_icl', '{"options": [{"value": "volcano_icl", "label": "标准集群"}, {"value": "volcano_icl_concurr", "label": "并发集群"}]}', null, 7, false, '系统设置');
```

## 4. 用户配置表设计

### 4.1 用户偏好配置表

```sql
-- 用户配置偏好表
CREATE TABLE user_volcano_preferences (
    pref_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES user_auth_basic(user_id),
    pref_type VARCHAR(50) NOT NULL,                          -- voice_clone, tts_basic, tts_advanced
    pref_config_key VARCHAR(100) NOT NULL,
    pref_value TEXT NOT NULL,
    pref_created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    pref_updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, pref_type, pref_config_key)
);

CREATE INDEX idx_user_volcano_preferences_user ON user_volcano_preferences(user_id);
CREATE INDEX idx_user_volcano_preferences_type ON user_volcano_preferences(pref_type);
```

## 5. 界面配置建议

### 5.1 基础设置 (默认显示)

```json
{
  "voice_clone_basic": {
    "title": "音色克隆 - 基础设置",
    "collapsible": false,
    "fields": [
      {
        "key": "timbre_name",
        "label": "音色名称",
        "type": "input",
        "required": true,
        "placeholder": "请输入音色名称",
        "defaultValue": ""
      },
      {
        "key": "language", 
        "label": "语言类型",
        "type": "select",
        "required": true,
        "defaultValue": "0",
        "options": [
          {"value": "0", "label": "中文"},
          {"value": "1", "label": "英文"},
          {"value": "2", "label": "日语"}
        ]
      },
      {
        "key": "model_type",
        "label": "模型类型", 
        "type": "select",
        "required": true,
        "defaultValue": "1",
        "options": [
          {"value": "1", "label": "2.0效果(ICL) - 推荐"},
          {"value": "0", "label": "1.0效果"},
          {"value": "2", "label": "DiT标准版"},
          {"value": "3", "label": "DiT还原版"}
        ]
      }
    ]
  },
  
  "tts_basic": {
    "title": "语音合成 - 基础设置", 
    "collapsible": false,
    "fields": [
      {
        "key": "speed_ratio",
        "label": "语速",
        "type": "slider",
        "defaultValue": 1.0,
        "min": 0.2,
        "max": 3.0,
        "step": 0.1,
        "marks": {
          "0.5": "慢",
          "1.0": "正常", 
          "2.0": "快"
        }
      },
      {
        "key": "encoding",
        "label": "音频格式",
        "type": "radio",
        "defaultValue": "mp3",
        "options": [
          {"value": "mp3", "label": "MP3", "description": "推荐，体积小"},
          {"value": "wav", "label": "WAV", "description": "高质量，体积大"}
        ]
      }
    ]
  }
}
```

### 5.2 高级设置 (默认折叠)

```json
{
  "voice_clone_advanced": {
    "title": "音色克隆 - 高级设置",
    "collapsible": true,
    "collapsed": true,
    "description": "高级用户选项，通常使用默认值即可",
    "fields": [
      {
        "key": "reference_text",
        "label": "参考文本", 
        "type": "textarea",
        "placeholder": "可选：提供与音频内容匹配的文本以提高训练质量",
        "defaultValue": ""
      },
      {
        "key": "audio_format",
        "label": "音频格式",
        "type": "select", 
        "defaultValue": "wav",
        "options": [
          {"value": "wav", "label": "WAV"},
          {"value": "mp3", "label": "MP3"}
        ]
      }
    ]
  },
  
  "tts_advanced": {
    "title": "语音合成 - 高级设置",
    "collapsible": true, 
    "collapsed": true,
    "description": "专业用户选项，可精确控制合成效果",
    "fields": [
      {
        "key": "explicit_language",
        "label": "语种控制",
        "type": "select",
        "defaultValue": "zh", 
        "helpText": "控制文本语种识别方式",
        "options": [
          {"value": "", "label": "自动检测"},
          {"value": "zh", "label": "中文为主"},
          {"value": "en", "label": "仅英文"}
        ]
      },
      {
        "key": "cache_enabled",
        "label": "启用缓存",
        "type": "switch",
        "defaultValue": false,
        "helpText": "缓存相同文本的合成结果，提高响应速度"
      },
      {
        "key": "with_timestamp", 
        "label": "时间戳",
        "type": "switch",
        "defaultValue": false,
        "helpText": "返回文本的时间戳信息"
      }
    ]
  }
}
```

## 6. 数据迁移SQL

```sql
-- 为现有数据添加默认值
UPDATE voice_timbre_basic SET 
  timbre_model_type = 1,
  timbre_language = 'zh-CN',
  timbre_available_training_times = 10
WHERE timbre_model_type IS NULL;

UPDATE voice_audio_basic SET
  audio_encoding = 'mp3',
  audio_sample_rate = 24000,
  audio_text_type = 'plain',
  audio_cluster = 'volcano_icl',
  audio_with_timestamp = 0,
  audio_split_sentence = 0,
  audio_cache_enabled = FALSE
WHERE audio_encoding IS NULL;
```

## 总结

通过以上优化方案：

1. **数据库完整性** - 支持豆包API的所有参数
2. **界面友好性** - 基础设置简单易用，高级设置专业可控  
3. **扩展性** - 配置驱动的界面，易于添加新参数
4. **用户体验** - 智能默认值，分层设置，渐进式配置

这样的设计既满足了普通用户的简单使用需求，也为专业用户提供了精细控制的能力。