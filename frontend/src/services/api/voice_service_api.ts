/**
 * Voice Service API Layer
 * 语音服务API层 - [services][api][voice_service_api]
 */

import { axiosInstance } from '../axios/axios_instance';
import type { ApiResponse, PaginatedResponse } from './base_api_types';

// ================================
// 基础类型定义 - Voice Service Types
// ================================

export type VoicePlatformType = 'doubao' | 'azure' | 'openai' | 'elevenlabs';
export type VoiceGender = 'male' | 'female' | 'neutral';
export type VoiceLanguage = 'zh-CN' | 'en-US' | 'ja-JP' | 'ko-KR';
export type VoiceStatus = 'processing' | 'completed' | 'failed' | 'pending';
export type TimbreType = 'default' | 'cloned' | 'custom';

// 语音音频基础信息
export interface VoiceAudioBasic {
  audio_id: number;
  text_id?: number;
  audio_title: string;
  audio_url?: string;
  audio_duration?: number;
  audio_size?: number;
  audio_format: string;
  platform_type: VoicePlatformType;
  voice_timbre_id?: number;
  synthesis_params?: Record<string, any>;
  audio_status: VoiceStatus;
  created_at: string;
  updated_at: string;
}

// 语音音色管理
export interface VoiceTimbreBasic {
  timbre_id: number;
  timbre_name: string;
  timbre_type: TimbreType;
  platform_type: VoicePlatformType;
  platform_voice_id: string;
  voice_gender: VoiceGender;
  voice_language: VoiceLanguage;
  voice_description?: string;
  sample_audio_url?: string;
  clone_source_audio?: string;
  timbre_params?: Record<string, any>;
  is_available: boolean;
  created_at: string;
  updated_at: string;
}

// ================================
// 请求/响应类型 - Voice Service DTOs
// ================================

// 语音合成请求
export interface VoiceSynthesisRequest {
  text: string;
  voice_timbre_id: number;
  platform_type?: VoicePlatformType;
  synthesis_params?: {
    speed?: number;          // 语速 0.5-2.0
    pitch?: number;          // 音调 -20 to 20
    volume?: number;         // 音量 0-100
    emotion?: string;        // 情感 neutral, happy, sad, angry
    style?: string;          // 说话风格
    break_time?: number;     // 停顿时间(ms)
  };
  audio_format?: 'mp3' | 'wav' | 'ogg';
  save_to_library?: boolean;
  audio_title?: string;
}

// 语音合成响应
export interface VoiceSynthesisResponse {
  audio_id: number;
  audio_url: string;
  audio_duration: number;
  audio_size: number;
  synthesis_time: number;
  platform_used: VoicePlatformType;
  cost_info?: {
    tokens_used: number;
    cost_amount: number;
    currency: string;
  };
}

// 音色克隆请求
export interface VoiceTimbreCloneRequest {
  timbre_name: string;
  platform_type: VoicePlatformType;
  source_audio_files: File[];
  voice_description?: string;
  voice_gender: VoiceGender;
  voice_language: VoiceLanguage;
  clone_params?: {
    sample_duration?: number;    // 样本时长要求(秒)
    quality_level?: 'standard' | 'high' | 'premium';
    enhancement?: boolean;       // 是否启用音频增强
  };
}

// 音色克隆响应
export interface VoiceTimbreCloneResponse {
  timbre_id: number;
  clone_task_id: string;
  estimated_time: number;
  status: 'processing' | 'completed' | 'failed';
  platform_task_id?: string;
}

// 音色创建请求
export interface VoiceTimbreCreateRequest {
  timbre_name: string;
  timbre_type: TimbreType;
  platform_type: VoicePlatformType;
  platform_voice_id: string;
  voice_gender: VoiceGender;
  voice_language: VoiceLanguage;
  voice_description?: string;
  timbre_params?: Record<string, any>;
}

// 音色更新请求
export interface VoiceTimbreUpdateRequest {
  timbre_id: number;
  timbre_name?: string;
  voice_description?: string;
  timbre_params?: Record<string, any>;
  is_available?: boolean;
}

// 语音分析请求
export interface VoiceAudioAnalyseRequest {
  audio_id?: number;
  audio_url?: string;
  analysis_types: ('quality' | 'emotion' | 'speaker' | 'content')[];
}

// 语音分析响应
export interface VoiceAudioAnalyseResponse {
  analysis_id: string;
  audio_info: {
    duration: number;
    sample_rate: number;
    channels: number;
    format: string;
  };
  analysis_results: {
    quality?: {
      overall_score: number;
      noise_level: number;
      clarity: number;
      volume_level: number;
    };
    emotion?: {
      primary_emotion: string;
      emotion_scores: Record<string, number>;
      confidence: number;
    };
    speaker?: {
      gender: VoiceGender;
      age_range: string;
      accent: string;
      confidence: number;
    };
    content?: {
      transcription: string;
      confidence: number;
      word_timestamps?: Array<{
        word: string;
        start_time: number;
        end_time: number;
      }>;
    };
  };
}

// 平台语音列表响应
export interface PlatformVoiceListResponse {
  platform_type: VoicePlatformType;
  voices: Array<{
    voice_id: string;
    voice_name: string;
    voice_gender: VoiceGender;
    voice_language: VoiceLanguage;
    voice_description?: string;
    sample_rate?: number;
    is_premium?: boolean;
    tags?: string[];
  }>;
}

// 使用统计响应
export interface VoiceUsageStatsResponse {
  period: string;
  total_synthesis_count: number;
  total_duration: number;
  total_tokens_used: number;
  total_cost: number;
  platform_usage: Record<VoicePlatformType, {
    synthesis_count: number;
    duration: number;
    tokens_used: number;
    cost: number;
  }>;
  timbre_usage: Array<{
    timbre_id: number;
    timbre_name: string;
    usage_count: number;
    total_duration: number;
  }>;
}

// ================================
// Voice Service API 类
// ================================

class VoiceServiceApiService {
  
  // ================================
  // 语音合成相关 API
  // ================================
  
  /**
   * 语音合成
   */
  async voice_service_api_synthesize_text(
    request: VoiceSynthesisRequest
  ): Promise<ApiResponse<VoiceSynthesisResponse>> {
    const response = await axiosInstance.post('/voice/synthesize', request);
    return response.data;
  }

  /**
   * 获取语音音频列表
   */
  async voice_service_api_get_audio_list(
    page: number = 1,
    pageSize: number = 20,
    filters?: {
      platform_type?: VoicePlatformType;
      audio_status?: VoiceStatus;
      timbre_id?: number;
      date_range?: [string, string];
    }
  ): Promise<ApiResponse<PaginatedResponse<VoiceAudioBasic>>> {
    const response = await axiosInstance.get('/voice/audio/list', {
      params: {
        page,
        page_size: pageSize,
        ...filters
      }
    });
    return response.data;
  }

  /**
   * 获取语音音频详情
   */
  async voice_service_api_get_audio_detail(
    audioId: number
  ): Promise<ApiResponse<VoiceAudioBasic>> {
    const response = await axiosInstance.get(`/voice/audio/${audioId}`);
    return response.data;
  }

  /**
   * 删除语音音频
   */
  async voice_service_api_delete_audio(
    audioId: number
  ): Promise<ApiResponse<boolean>> {
    const response = await axiosInstance.delete(`/voice/audio/${audioId}`);
    return response.data;
  }

  // ================================
  // 音色管理相关 API
  // ================================

  /**
   * 获取音色列表
   */
  async voice_service_api_get_timbre_list(
    page: number = 1,
    pageSize: number = 20,
    filters?: {
      platform_type?: VoicePlatformType;
      timbre_type?: TimbreType;
      voice_gender?: VoiceGender;
      voice_language?: VoiceLanguage;
      is_available?: boolean;
    }
  ): Promise<ApiResponse<PaginatedResponse<VoiceTimbreBasic>>> {
    const response = await axiosInstance.get('/voice/timbre/list', {
      params: {
        page,
        page_size: pageSize,
        ...filters
      }
    });
    return response.data;
  }

  /**
   * 获取音色详情
   */
  async voice_service_api_get_timbre_detail(
    timbreId: number
  ): Promise<ApiResponse<VoiceTimbreBasic>> {
    const response = await axiosInstance.get(`/voice/timbre/${timbreId}`);
    return response.data;
  }

  /**
   * 创建音色
   */
  async voice_service_api_create_timbre(
    request: VoiceTimbreCreateRequest
  ): Promise<ApiResponse<VoiceTimbreBasic>> {
    const response = await axiosInstance.post('/voice/timbre/create', request);
    return response.data;
  }

  /**
   * 更新音色
   */
  async voice_service_api_update_timbre(
    request: VoiceTimbreUpdateRequest
  ): Promise<ApiResponse<VoiceTimbreBasic>> {
    const response = await axiosInstance.put('/voice/timbre/update', request);
    return response.data;
  }

  /**
   * 删除音色
   */
  async voice_service_api_delete_timbre(
    timbreId: number
  ): Promise<ApiResponse<boolean>> {
    const response = await axiosInstance.delete(`/voice/timbre/${timbreId}`);
    return response.data;
  }

  /**
   * 音色克隆
   */
  async voice_service_api_clone_timbre(
    request: VoiceTimbreCloneRequest
  ): Promise<ApiResponse<VoiceTimbreCloneResponse>> {
    const formData = new FormData();
    formData.append('timbre_name', request.timbre_name);
    formData.append('platform_type', request.platform_type);
    formData.append('voice_gender', request.voice_gender);
    formData.append('voice_language', request.voice_language);
    
    if (request.voice_description) {
      formData.append('voice_description', request.voice_description);
    }
    
    if (request.clone_params) {
      formData.append('clone_params', JSON.stringify(request.clone_params));
    }

    // 添加音频文件
    request.source_audio_files.forEach((file, index) => {
      formData.append(`source_audio_files`, file);
    });

    const response = await axiosInstance.post('/voice/timbre/clone', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  /**
   * 获取克隆任务状态
   */
  async voice_service_api_get_clone_status(
    taskId: string
  ): Promise<ApiResponse<VoiceTimbreCloneResponse>> {
    const response = await axiosInstance.get(`/voice/timbre/clone/status/${taskId}`);
    return response.data;
  }

  // ================================
  // 平台管理相关 API
  // ================================

  /**
   * 获取平台语音列表
   */
  async voice_service_api_get_platform_voices(
    platformType: VoicePlatformType,
    language?: VoiceLanguage
  ): Promise<ApiResponse<PlatformVoiceListResponse>> {
    const response = await axiosInstance.get(`/voice/platform/${platformType}/voices`, {
      params: { language }
    });
    return response.data;
  }

  /**
   * 测试平台连接
   */
  async voice_service_api_test_platform_connection(
    platformType: VoicePlatformType
  ): Promise<ApiResponse<{
    is_connected: boolean;
    response_time: number;
    error_message?: string;
    platform_info?: Record<string, any>;
  }>> {
    const response = await axiosInstance.post(`/voice/platform/${platformType}/test`);
    return response.data;
  }

  // ================================
  // 语音分析相关 API
  // ================================

  /**
   * 语音分析
   */
  async voice_service_api_analyse_audio(
    request: VoiceAudioAnalyseRequest
  ): Promise<ApiResponse<VoiceAudioAnalyseResponse>> {
    const response = await axiosInstance.post('/voice/analyse', request);
    return response.data;
  }

  // ================================
  // 统计分析相关 API
  // ================================

  /**
   * 获取使用统计
   */
  async voice_service_api_get_usage_stats(
    period: 'day' | 'week' | 'month' | 'year' = 'month'
  ): Promise<ApiResponse<VoiceUsageStatsResponse>> {
    const response = await axiosInstance.get('/voice/stats/usage', {
      params: { period }
    });
    return response.data;
  }

  // ================================
  // 批量操作 API
  // ================================

  /**
   * 批量合成语音
   */
  async voice_service_api_batch_synthesize(
    requests: Array<{
      text: string;
      voice_timbre_id: number;
      audio_title?: string;
    }>,
    common_params?: Partial<VoiceSynthesisRequest>
  ): Promise<ApiResponse<{
    task_id: string;
    total_count: number;
    estimated_time: number;
  }>> {
    const response = await axiosInstance.post('/voice/batch/synthesize', {
      requests,
      common_params
    });
    return response.data;
  }

  /**
   * 获取批量任务状态
   */
  async voice_service_api_get_batch_status(
    taskId: string
  ): Promise<ApiResponse<{
    task_id: string;
    status: 'processing' | 'completed' | 'failed' | 'partial';
    progress: number;
    completed_count: number;
    failed_count: number;
    results?: VoiceSynthesisResponse[];
  }>> {
    const response = await axiosInstance.get(`/voice/batch/status/${taskId}`);
    return response.data;
  }
}

// 导出服务实例
export const voiceServiceApiService = new VoiceServiceApiService();
export default voiceServiceApiService;