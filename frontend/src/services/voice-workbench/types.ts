/**
 * Voice Workbench Service Types
 * 语音工作台服务类型定义 - [services][voice_workbench][types]
 */

// 平台信息类型
export interface VoicePlatformInfo {
  platform_type: string;
  platform_name: string;
  platform_description: string;
  is_enabled: boolean;
  is_healthy: boolean;
  supported_features: string[];
  priority: number;
  cost_per_minute: number;
}

// 平台健康状态
export interface PlatformHealthStatus {
  is_healthy: boolean;
  last_health_check?: string;
  response_time_ms?: number;
  daily_requests_used?: number;
  daily_requests_limit?: number;
}

// 语音操作结果
export interface VoiceOperationResult {
  success: boolean;
  operation_id: string;
  operation_type: string;
  platform_used: string;
  result_data?: any;
  error_message?: string;
  processing_time_ms: number;
  metadata?: any;
}

// 用户音色信息
export interface UserVoiceInfo {
  voice_id: string;
  voice_name: string;
  voice_description?: string;
  platform: string;
  language: string;
  gender?: string;
  quality_score?: number;
  created_time: string;
  is_custom: boolean;
}

// 音色克隆请求
export interface VoiceCloneFormData {
  timbre_name: string;
  timbre_description?: string;
  language: string;
  model_type: string;
  reference_text?: string;
  preferred_platform: string;
  audio_file: File;
  advanced_params?: {
    noise_reduction?: boolean;
    quality_enhancement?: boolean;
    voice_enhancement?: boolean;
    training_iterations?: number;
    learning_rate?: number;
    batch_size?: number;
    experimental_features?: boolean;
  };
}

// TTS合成请求
export interface TTSFormData {
  text: string;
  voice_id: string;
  language?: string;
  speed_ratio?: number;
  volume_ratio?: number;
  pitch_ratio?: number;
  audio_format?: string;
  sample_rate?: number;
  use_ssml?: boolean;
  streaming?: boolean;
  preferred_platform?: string;
  advanced_params?: any;
}

// 平台统计信息
export interface PlatformStatistics {
  total_operations: number;
  successful_operations: number;
  success_rate: number;
  platform_usage: Record<string, {
    total: number;
    successful: number;
    failed: number;
  }>;
  operation_type_counts: Record<string, number>;
  platform_status: any;
}

// API响应格式
export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  timestamp: string;
}

// Hook状态类型
export interface VoiceWorkbenchState {
  // 平台相关
  platforms: VoicePlatformInfo[];
  selectedPlatform: string | null;
  platformHealth: Record<string, PlatformHealthStatus>;
  platformsLoading: boolean;
  
  // 操作状态
  voiceCloneLoading: boolean;
  ttsLoading: boolean;
  ttsPreviewLoading: boolean;
  
  // 数据
  userVoices: UserVoiceInfo[];
  operationHistory: VoiceOperationResult[];
  
  // 错误处理
  error: string | null;
  lastError: any;
}

// 场景预设类型
export interface VoiceScenePreset {
  id: string;
  name: string;
  description: string;
  platform: string;
  settings: {
    speed_ratio: number;
    volume_ratio: number;
    pitch_ratio: number;
  };
  category: 'news' | 'audiobook' | 'customer_service' | 'children' | 'advertisement' | 'phone';
}

// 平台配置类型
export interface PlatformConfigData {
  platform_type: string;
  is_enabled: boolean;
  api_config: Record<string, any>;
  feature_support: Record<string, boolean>;
  priority: number;
  cost_per_minute: number;
  max_daily_requests: number;
}