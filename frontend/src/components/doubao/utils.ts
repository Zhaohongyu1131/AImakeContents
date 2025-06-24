/**
 * Doubao Components Utils
 * 豆包组件工具函数 - [components][doubao][utils]
 */

import { message } from 'antd';
import type { 
  VoiceCloneFormData, 
  TTSFormData, 
  ScenePreset,
  LanguageOption,
  ModelTypeOption,
  AudioFormatOption
} from './types';

/**
 * 验证音频文件
 * [components][doubao][utils][validate_audio_file]
 */
export const validateAudioFile = (file: File): { valid: boolean; message?: string } => {
  // 检查文件类型
  const allowedTypes = ['audio/wav', 'audio/mp3', 'audio/mpeg', 'audio/m4a', 'audio/flac', 'audio/aac'];
  if (!allowedTypes.includes(file.type)) {
    return {
      valid: false,
      message: '不支持的音频格式，请上传 WAV、MP3、M4A、FLAC 或 AAC 格式文件'
    };
  }

  // 检查文件大小 (50MB)
  const maxSize = 50 * 1024 * 1024;
  if (file.size > maxSize) {
    return {
      valid: false,
      message: '文件大小超过 50MB 限制'
    };
  }

  // 检查文件名
  if (file.name.length > 100) {
    return {
      valid: false,
      message: '文件名过长，请使用较短的文件名'
    };
  }

  return { valid: true };
};

/**
 * 获取音频文件时长
 * [components][doubao][utils][get_audio_duration]
 */
export const getAudioDuration = (file: File): Promise<number> => {
  return new Promise((resolve, reject) => {
    const audio = new Audio();
    const url = URL.createObjectURL(file);
    
    audio.onloadedmetadata = () => {
      resolve(audio.duration);
      URL.revokeObjectURL(url);
    };
    
    audio.onerror = () => {
      reject(new Error('无法获取音频时长'));
      URL.revokeObjectURL(url);
    };
    
    audio.src = url;
  });
};

/**
 * 格式化文件大小
 * [components][doubao][utils][format_file_size]
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
};

/**
 * 格式化时长
 * [components][doubao][utils][format_duration]
 */
export const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  } else {
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  }
};

/**
 * 估算合成时长
 * [components][doubao][utils][estimate_synthesis_duration]
 */
export const estimateSynthesisDuration = (
  text: string, 
  speedRatio: number = 1.0,
  language: string = 'zh'
): number => {
  let wordsPerMinute = 200; // 默认中文语速
  
  // 根据语言调整语速
  switch (language) {
    case 'en':
      wordsPerMinute = 150;
      break;
    case 'ja':
      wordsPerMinute = 180;
      break;
    case 'es':
      wordsPerMinute = 160;
      break;
    default:
      wordsPerMinute = 200;
  }
  
  const characterCount = text.length;
  const baseMinutes = characterCount / wordsPerMinute;
  const adjustedMinutes = baseMinutes / speedRatio;
  
  return adjustedMinutes * 60; // 转换为秒
};

/**
 * 场景预设配置
 * [components][doubao][utils][scene_presets]
 */
export const getScenePresets = (): ScenePreset[] => [
  {
    name: '新闻播报',
    values: { speed_ratio: 1.0, volume_ratio: 1.0, pitch_ratio: 1.0 }
  },
  {
    name: '有声书',
    values: { speed_ratio: 0.9, volume_ratio: 0.9, pitch_ratio: 1.0 }
  },
  {
    name: '客服语音',
    values: { speed_ratio: 1.1, volume_ratio: 1.1, pitch_ratio: 1.05 }
  },
  {
    name: '儿童内容',
    values: { speed_ratio: 0.8, volume_ratio: 1.2, pitch_ratio: 1.1 }
  },
  {
    name: '广告配音',
    values: { speed_ratio: 1.2, volume_ratio: 1.2, pitch_ratio: 1.08 }
  },
  {
    name: '电话语音',
    values: { speed_ratio: 1.0, volume_ratio: 1.3, pitch_ratio: 1.0 }
  }
];

/**
 * 语言选项配置
 * [components][doubao][utils][language_options]
 */
export const getLanguageOptions = (): LanguageOption[] => [
  { value: 0, label: '中文', description: '支持普通话和部分方言', recommended: true },
  { value: 1, label: '英文', description: '美式和英式英语' },
  { value: 2, label: '日语', description: '标准日本语' },
  { value: 3, label: '西班牙语', description: '拉丁美洲西班牙语' },
  { value: 4, label: '印尼语', description: '标准印尼语' },
  { value: 5, label: '葡萄牙语', description: '巴西葡萄牙语' }
];

/**
 * 模型类型选项配置
 * [components][doubao][utils][model_type_options]
 */
export const getModelTypeOptions = (): ModelTypeOption[] => [
  { 
    value: 1, 
    label: '2.0效果(ICL) - 推荐', 
    description: '最新模型，音质最佳，训练速度快',
    recommended: true
  },
  { 
    value: 0, 
    label: '1.0效果', 
    description: '经典模型，稳定可靠'
  },
  { 
    value: 2, 
    label: 'DiT标准版(音色)', 
    description: '专注音色还原'
  },
  { 
    value: 3, 
    label: 'DiT还原版(音色+风格)', 
    description: '音色和说话风格双重还原'
  }
];

/**
 * 音频格式选项配置
 * [components][doubao][utils][audio_format_options]
 */
export const getAudioFormatOptions = (): AudioFormatOption[] => [
  { 
    value: 'mp3', 
    label: 'MP3 - 推荐', 
    description: '通用格式，文件小，兼容性好',
    recommended: true
  },
  { 
    value: 'wav', 
    label: 'WAV - 高质量', 
    description: '无损格式，音质最佳，文件较大'
  },
  { 
    value: 'ogg_opus', 
    label: 'OGG Opus - 压缩', 
    description: '高压缩比，音质好，文件小'
  },
  { 
    value: 'pcm', 
    label: 'PCM - 原始', 
    description: '原始音频数据，用于特殊需求'
  }
];

/**
 * 验证表单数据
 * [components][doubao][utils][validate_form_data]
 */
export const validateVoiceCloneForm = (data: Partial<VoiceCloneFormData>): string[] => {
  const errors: string[] = [];
  
  if (!data.timbre_name?.trim()) {
    errors.push('音色名称不能为空');
  } else if (data.timbre_name.length > 50) {
    errors.push('音色名称长度不能超过50个字符');
  }
  
  if (data.timbre_description && data.timbre_description.length > 200) {
    errors.push('音色描述长度不能超过200个字符');
  }
  
  if (data.language === undefined || data.language < 0 || data.language > 5) {
    errors.push('请选择有效的语言类型');
  }
  
  if (data.model_type === undefined || ![0, 1, 2, 3].includes(data.model_type)) {
    errors.push('请选择有效的模型类型');
  }
  
  if (!data.audio_file) {
    errors.push('请上传音频文件');
  }
  
  return errors;
};

/**
 * 验证TTS表单数据
 * [components][doubao][utils][validate_tts_form]
 */
export const validateTTSForm = (data: Partial<TTSFormData>): string[] => {
  const errors: string[] = [];
  
  if (!data.text?.trim()) {
    errors.push('请输入要合成的文本');
  } else if (data.text.length > 5000) {
    errors.push('文本长度不能超过5000个字符');
  }
  
  if (!data.voice_type?.trim()) {
    errors.push('请选择音色');
  }
  
  if (data.speed_ratio !== undefined && (data.speed_ratio < 0.2 || data.speed_ratio > 3.0)) {
    errors.push('语速比例应在0.2-3.0之间');
  }
  
  if (data.volume_ratio !== undefined && (data.volume_ratio < 0.1 || data.volume_ratio > 2.0)) {
    errors.push('音量比例应在0.1-2.0之间');
  }
  
  if (data.pitch_ratio !== undefined && (data.pitch_ratio < 0.5 || data.pitch_ratio > 2.0)) {
    errors.push('音调比例应在0.5-2.0之间');
  }
  
  return errors;
};

/**
 * 生成唯一ID
 * [components][doubao][utils][generate_unique_id]
 */
export const generateUniqueId = (prefix: string = 'id'): string => {
  const timestamp = Date.now().toString(36);
  const randomStr = Math.random().toString(36).substring(2, 8);
  return `${prefix}_${timestamp}_${randomStr}`;
};

/**
 * 下载音频文件
 * [components][doubao][utils][download_audio]
 */
export const downloadAudio = (audioData: Uint8Array, filename: string, format: string = 'mp3'): void => {
  try {
    const blob = new Blob([audioData], { 
      type: format === 'mp3' ? 'audio/mpeg' : `audio/${format}` 
    });
    
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    
    link.href = url;
    link.download = filename.endsWith(`.${format}`) ? filename : `${filename}.${format}`;
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
    message.success('音频文件下载完成');
  } catch (error) {
    message.error('音频文件下载失败');
    console.error('Download error:', error);
  }
};

/**
 * 播放音频预览
 * [components][doubao][utils][play_audio_preview]
 */
export const playAudioPreview = (audioData: Uint8Array, format: string = 'mp3'): Promise<void> => {
  return new Promise((resolve, reject) => {
    try {
      const blob = new Blob([audioData], { 
        type: format === 'mp3' ? 'audio/mpeg' : `audio/${format}` 
      });
      
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      
      audio.onended = () => {
        URL.revokeObjectURL(url);
        resolve();
      };
      
      audio.onerror = () => {
        URL.revokeObjectURL(url);
        reject(new Error('音频播放失败'));
      };
      
      audio.play();
    } catch (error) {
      reject(error);
    }
  });
};