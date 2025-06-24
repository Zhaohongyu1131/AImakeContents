/**
 * Doubao Components Types
 * 豆包组件类型定义 - [components][doubao][types]
 */

// 基础类型
export interface VoiceOption {
  value: string;
  label: string;
  language: string;
  gender: string;
  style: string;
  description?: string;
  isCustom?: boolean;
}

export interface LanguageOption {
  value: number | string;
  label: string;
  description: string;
  recommended?: boolean;
}

export interface ModelTypeOption {
  value: number;
  label: string;
  description: string;
  recommended?: boolean;
}

export interface AudioFormatOption {
  value: string;
  label: string;
  description: string;
  recommended?: boolean;
}

// 表单数据类型
export interface VoiceCloneFormData {
  timbre_name: string;
  timbre_description?: string;
  language: number;
  model_type: number;
  audio_file?: File;
}

export interface VoiceCloneAdvancedData {
  reference_text?: string;
  audio_format: string;
  quality_enhancement: boolean;
  noise_reduction: boolean;
  voice_enhancement: boolean;
  training_iterations?: number;
  learning_rate?: number;
  batch_size?: number;
  experimental_features: boolean;
}

export interface TTSFormData {
  text: string;
  voice_type: string;
  speed_ratio: number;
  volume_ratio: number;
  pitch_ratio: number;
  encoding: string;
  sample_rate: number;
}

export interface TTSAdvancedData {
  explicit_language?: string;
  context_language?: string;
  text_type: string;
  with_timestamp: boolean;
  split_sentence: boolean;
  cache_enabled: boolean;
  cluster: string;
  streaming_mode: boolean;
  chunk_size?: number;
  emotion_control?: string;
  prosody_rate?: string;
  prosody_pitch?: string;
  prosody_volume?: string;
}

// 组件Props类型
export interface VoiceCloneBasicSettingsProps {
  onSubmit?: (values: VoiceCloneFormData) => void;
  loading?: boolean;
  onAdvancedToggle?: () => void;
  showAdvanced?: boolean;
}

export interface VoiceCloneAdvancedSettingsProps {
  visible?: boolean;
  onChange?: (values: VoiceCloneAdvancedData) => void;
  initialValues?: Partial<VoiceCloneAdvancedData>;
}

export interface TTSBasicSettingsProps {
  onSynthesize?: (values: TTSFormData) => void;
  onPreview?: (values: TTSFormData) => void;
  loading?: boolean;
  previewLoading?: boolean;
  onAdvancedToggle?: () => void;
  showAdvanced?: boolean;
  voiceList?: VoiceOption[];
}

export interface TTSAdvancedSettingsProps {
  visible?: boolean;
  onChange?: (values: TTSAdvancedData) => void;
  initialValues?: Partial<TTSAdvancedData>;
}

export interface DoubaoMainContainerProps {
  className?: string;
}

// 服务相关类型
export interface HealthStatus {
  status: 'healthy' | 'unhealthy' | 'unknown';
  message: string;
  lastCheck?: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
}

export interface VoiceCloneResponse {
  success: boolean;
  speaker_id: string;
  status: string;
  message: string;
}

export interface SpeakerStatusResponse {
  speaker_id: string;
  status: number;
  status_text: string;
  create_time?: string;
  version: string;
  demo_audio?: string;
  is_ready: boolean;
}

export interface TTSResponse {
  success: boolean;
  reqid: string;
  audio_data?: Uint8Array;
  encoding: string;
  sample_rate: number;
  duration?: number;
  message: string;
}

// 场景预设类型
export interface ScenePreset {
  name: string;
  values: {
    speed_ratio: number;
    volume_ratio: number;
    pitch_ratio: number;
  };
}

// 配置选项类型
export interface DoubaoConfig {
  voice_clone: {
    basic: VoiceCloneFormData;
    advanced: VoiceCloneAdvancedData;
  };
  tts: {
    basic: TTSFormData;
    advanced: TTSAdvancedData;
  };
}