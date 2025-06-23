/**
 * API Types
 * API类型定义 - [api][types]
 */

// 通用响应格式
export interface ApiResponse<T = any> {
  success: boolean
  code: number
  message: string
  data?: T
  error?: {
    type: string
    details?: any
  }
  timestamp: string
  request_id?: string
}

// 分页参数
export interface PaginationParams {
  page: number
  size: number
}

// 分页响应
export interface PaginationResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// 用户相关类型
export interface UserAuth {
  user_id: number
  user_name: string
  user_email: string
  user_role: 'user' | 'admin' | 'super_admin'
  access_token: string
  refresh_token: string
  expires_in: number
}

export interface UserProfile {
  user_id: number
  user_name: string
  user_email: string
  user_phone?: string
  user_profile_avatar?: string
  user_profile_nickname?: string
  user_created_time: string
  user_last_login_time?: string
}

// 文本内容相关类型
export interface TextContent {
  text_id: number
  text_title: string
  text_content: string
  text_content_type: 'article' | 'script' | 'prompt' | 'dialogue'
  text_language: string
  text_word_count: number
  text_status: 'draft' | 'published' | 'archived'
  text_tags: string[]
  text_created_time: string
  text_updated_time: string
  text_template_id?: number
}

export interface TextAnalyseResult {
  analyse_id: number
  text_id: number
  analyse_type: 'sentiment' | 'keyword' | 'summary' | 'readability'
  analyse_result: Record<string, any>
  analyse_score: number
  analyse_created_time: string
}

// 音色相关类型
export interface VoiceTimbre {
  timbre_id: number
  timbre_name: string
  timbre_description?: string
  timbre_platform_id?: string
  timbre_platform: 'volcano' | 'azure' | 'openai'
  timbre_language: string
  timbre_gender: 'male' | 'female' | 'neutral'
  timbre_style: string
  timbre_quality_score?: number
  timbre_status: 'training' | 'ready' | 'failed'
  timbre_created_time: string
}

// 音频相关类型
export interface VoiceAudio {
  audio_id: number
  audio_title: string
  audio_text_content: string
  audio_file_id: number
  audio_file_url: string
  audio_duration: number
  audio_timbre_id: number
  audio_language: string
  audio_speed: number
  audio_pitch: number
  audio_volume: number
  audio_status: 'generating' | 'completed' | 'failed'
  audio_tags: string[]
  audio_created_time: string
}

// 图像内容相关类型
export interface ImageContent {
  image_id: number
  image_title: string
  image_prompt: string
  image_file_id: number
  image_file_url: string
  image_type: 'image' | 'video'
  image_width?: number
  image_height?: number
  image_duration?: number
  image_format: string
  image_status: 'generating' | 'completed' | 'failed'
  image_tags: string[]
  image_created_time: string
}

// 混合内容相关类型
export interface MixallContent {
  mixall_id: number
  mixall_title: string
  mixall_description?: string
  mixall_type: 'video_with_voice' | 'presentation' | 'story'
  mixall_text_id?: number
  mixall_audio_id?: number
  mixall_image_ids: number[]
  mixall_final_file_id?: number
  mixall_final_file_url?: string
  mixall_status: 'draft' | 'processing' | 'completed' | 'failed'
  mixall_tags: string[]
  mixall_created_time: string
}

// 文件相关类型
export interface FileStorage {
  file_id: number
  file_name: string
  file_original_name: string
  file_path: string
  file_url: string
  file_size: number
  file_type: 'text' | 'audio' | 'image' | 'video'
  file_mime_type: string
  file_created_time: string
}

// 任务相关类型
export interface TaskStatus {
  task_id: number
  task_uuid: string
  task_name: string
  task_type: 'text_generate' | 'voice_synthesize' | 'image_generate' | 'mixall_create'
  task_status: 'pending' | 'running' | 'completed' | 'failed' | 'revoked'
  task_progress: number
  task_result?: Record<string, any>
  task_error_message?: string
  task_created_time: string
  task_completed_time?: string
}