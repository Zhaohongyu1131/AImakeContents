/**
 * Doubao Services Types
 * 豆包服务类型定义 - [services][doubao][types]
 */

// API响应类型
export interface DoubaoApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
  timestamp?: string;
}

// 健康检查响应
export interface HealthCheckResponse {
  success: boolean;
  message: string;
  service: string;
  details?: {
    service_status: string;
    volcano_engine: {
      status: string;
      details: any;
    };
    database: string;
    timestamp: string;
  };
}

// 音色克隆相关类型
export interface VoiceCloneUploadRequest {
  timbre_name: string;
  timbre_description?: string;
  language: number;
  model_type: number;
  reference_text?: string;
  audio_file: File;
}

export interface VoiceCloneUploadResponse {
  success: boolean;
  speaker_id: string;
  status: string;
  message: string;
}

export interface SpeakerStatus {
  speaker_id: string;
  status: number;
  status_text: string;
  create_time?: string;
  version: string;
  demo_audio?: string;
  is_ready: boolean;
}

export interface UserVoice {
  timbre_id: number;
  timbre_name: string;
  timbre_description?: string;
  timbre_status: string;
  timbre_language: string;
  timbre_platform: string;
  timbre_created_time?: string;
  quality_score?: number;
  timbre_speaker_id?: string;
}

export interface VoiceListResponse {
  success: boolean;
  data: {
    voices: UserVoice[];
    total_count: number;
  };
  message: string;
}

// TTS相关类型
export interface TTSRequest {
  text: string;
  voice_type: string;
  encoding?: string;
  speed_ratio?: number;
  volume_ratio?: number;
  pitch_ratio?: number;
  sample_rate?: number;
  // 高级参数
  explicit_language?: string;
  context_language?: string;
  text_type?: string;
  with_timestamp?: boolean;
  split_sentence?: boolean;
  cache_enabled?: boolean;
  cluster?: string;
}

export interface TTSResponse {
  success: boolean;
  reqid: string;
  audio_data?: ArrayBuffer;
  encoding: string;
  sample_rate: number;
  duration?: number;
  message: string;
}

// 文本处理相关类型
export interface TextProcessRequest {
  text: string;
  operation: string;
  parameters?: Record<string, any>;
}

export interface TextProcessResponse {
  success: boolean;
  processed_text: string;
  operation: string;
  metadata?: any;
  message: string;
}

export interface TextAnalysisResult {
  length: number;
  word_count: number;
  analysis_type: string;
  [key: string]: any;
}

export interface TextValidationResult {
  is_valid: boolean;
  warnings: string[];
  errors: string[];
  suggestions: string[];
  text_stats: {
    length: number;
    word_count: number;
    line_count: number;
  };
}

export interface TextSplitResult {
  segments: string[];
  segment_count: number;
  total_length: number;
  max_segment_length: number;
  min_segment_length: number;
}

// WebSocket相关类型
export interface WebSocketMessage {
  type: 'tts_request' | 'audio_chunk' | 'complete' | 'error';
  data?: any;
  error?: string;
}

export interface StreamChunk {
  sequence: number;
  is_final: boolean;
  audio_data: Uint8Array;
}

// 错误类型
export interface DoubaoError {
  code: string;
  message: string;
  details?: any;
}

// 配置类型
export interface DoubaoServiceConfig {
  apiBaseUrl: string;
  wsBaseUrl: string;
  timeout: number;
  maxRetries: number;
  retryDelay: number;
}

// Hook状态类型
export interface DoubaoServiceHookState {
  // 加载状态
  voiceCloneLoading: boolean;
  ttsLoading: boolean;
  ttsPreviewLoading: boolean;
  healthCheckLoading: boolean;
  textProcessLoading: boolean;
  
  // 数据状态
  userVoices: any[];
  healthStatus: 'healthy' | 'unhealthy' | 'unknown';
  lastHealthCheck: string | null;
  currentTasks: string[];
  
  // 错误状态
  error: string | null;
  lastError: DoubaoError | null;
}

// 回调函数类型
export interface StreamCallbacks {
  onChunk?: (chunk: Uint8Array) => void;
  onComplete?: (audioData: Uint8Array) => void;
  onError?: (error: Error) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onProgress?: (progress: number) => void;
}

// 音频相关类型
export interface AudioMetadata {
  duration: number;
  sampleRate: number;
  channels: number;
  bitRate: number;
  format: string;
}

export interface AudioProcessingOptions {
  normalize: boolean;
  removeNoise: boolean;
  enhanceQuality: boolean;
}

// 场景预设类型
export interface VoiceScenePreset {
  id: string;
  name: string;
  description: string;
  settings: {
    speed_ratio: number;
    volume_ratio: number;
    pitch_ratio: number;
  };
  category: 'news' | 'audiobook' | 'customer_service' | 'children' | 'advertisement' | 'phone';
}

// 统计信息类型
export interface UsageStats {
  voice_clone_count: number;
  tts_count: number;
  total_audio_duration: number;
  monthly_usage: number;
  quota_remaining: number;
}

// 导出所有类型
export type {
  // 从组件types导入的类型
  VoiceOption,
  LanguageOption,
  ModelTypeOption,
  AudioFormatOption,
  VoiceCloneFormData,
  VoiceCloneAdvancedData,
  TTSFormData,
  TTSAdvancedData,
  ScenePreset,
  ApiResponse
} from '../../components/doubao/types';