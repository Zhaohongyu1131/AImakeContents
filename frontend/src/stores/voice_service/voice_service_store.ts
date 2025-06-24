/**
 * Voice Service Store
 * 语音服务状态管理 - [stores][voice_service][voice_service_store]
 */

import { create } from 'zustand';
import { devtools, subscribeWithSelector } from 'zustand/middleware';
import { voiceServiceApiService } from '../../services/api/voice_service_api';
import type {
  VoiceAudioBasic,
  VoiceTimbreBasic,
  VoiceSynthesisRequest,
  VoiceSynthesisResponse,
  VoiceTimbreCloneRequest,
  VoiceTimbreCloneResponse,
  VoiceTimbreCreateRequest,
  VoiceTimbreUpdateRequest,
  VoiceAudioAnalyseRequest,
  VoiceAudioAnalyseResponse,
  VoiceUsageStatsResponse,
  PlatformVoiceListResponse,
  VoicePlatformType,
  VoiceStatus
} from '../../services/api/voice_service_api';
import type { PaginatedResponse } from '../../services/api/base_api_types';

// ================================
// State 接口定义
// ================================

interface VoiceServiceState {
  // ================================
  // 语音音频状态
  // ================================
  audioList: PaginatedResponse<VoiceAudioBasic> | null;
  currentAudio: VoiceAudioBasic | null;
  audioListLoading: boolean;
  audioDetailLoading: boolean;
  
  // ================================
  // 语音合成状态
  // ================================
  synthesisLoading: boolean;
  lastSynthesisResult: VoiceSynthesisResponse | null;
  synthesisProgress: number;
  batchSynthesisStatus: {
    task_id?: string;
    status?: 'processing' | 'completed' | 'failed' | 'partial';
    progress?: number;
    completed_count?: number;
    failed_count?: number;
  } | null;

  // ================================
  // 音色管理状态
  // ================================
  timbreList: PaginatedResponse<VoiceTimbreBasic> | null;
  currentTimbre: VoiceTimbreBasic | null;
  timbreListLoading: boolean;
  timbreDetailLoading: boolean;
  timbreCreateLoading: boolean;
  timbreUpdateLoading: boolean;
  
  // ================================
  // 音色克隆状态
  // ================================
  cloneLoading: boolean;
  cloneProgress: number;
  currentCloneTask: VoiceTimbreCloneResponse | null;
  cloneHistory: VoiceTimbreCloneResponse[];

  // ================================
  // 平台管理状态
  // ================================
  platformVoices: Record<VoicePlatformType, PlatformVoiceListResponse | null>;
  platformConnectionStatus: Record<VoicePlatformType, {
    is_connected: boolean;
    response_time?: number;
    last_check?: string;
    error_message?: string;
  }>;
  platformTestLoading: Record<VoicePlatformType, boolean>;

  // ================================
  // 语音分析状态
  // ================================
  analysisLoading: boolean;
  lastAnalysisResult: VoiceAudioAnalyseResponse | null;

  // ================================
  // 统计数据状态
  // ================================
  usageStats: VoiceUsageStatsResponse | null;
  statsLoading: boolean;

  // ================================
  // 通用状态
  // ================================
  error: string | null;
  loading: boolean;

  // ================================
  // Actions - 语音音频管理
  // ================================
  voice_service_store_load_audio_list: (
    page?: number,
    pageSize?: number,
    filters?: any
  ) => Promise<void>;
  
  voice_service_store_load_audio_detail: (audioId: number) => Promise<void>;
  
  voice_service_store_delete_audio: (audioId: number) => Promise<boolean>;

  // ================================
  // Actions - 语音合成
  // ================================
  voice_service_store_synthesize_text: (
    request: VoiceSynthesisRequest
  ) => Promise<VoiceSynthesisResponse | null>;

  voice_service_store_batch_synthesize: (
    requests: Array<{
      text: string;
      voice_timbre_id: number;
      audio_title?: string;
    }>,
    common_params?: Partial<VoiceSynthesisRequest>
  ) => Promise<boolean>;

  voice_service_store_check_batch_status: (taskId: string) => Promise<void>;

  // ================================
  // Actions - 音色管理
  // ================================
  voice_service_store_load_timbre_list: (
    page?: number,
    pageSize?: number,
    filters?: any
  ) => Promise<void>;

  voice_service_store_load_timbre_detail: (timbreId: number) => Promise<void>;

  voice_service_store_create_timbre: (
    request: VoiceTimbreCreateRequest
  ) => Promise<boolean>;

  voice_service_store_update_timbre: (
    request: VoiceTimbreUpdateRequest
  ) => Promise<boolean>;

  voice_service_store_delete_timbre: (timbreId: number) => Promise<boolean>;

  voice_service_store_clone_timbre: (
    request: VoiceTimbreCloneRequest
  ) => Promise<boolean>;

  voice_service_store_check_clone_status: (taskId: string) => Promise<void>;

  // ================================
  // Actions - 平台管理
  // ================================
  voice_service_store_load_platform_voices: (
    platformType: VoicePlatformType,
    language?: string
  ) => Promise<void>;

  voice_service_store_test_platform_connection: (
    platformType: VoicePlatformType
  ) => Promise<boolean>;

  // ================================
  // Actions - 语音分析
  // ================================
  voice_service_store_analyse_audio: (
    request: VoiceAudioAnalyseRequest
  ) => Promise<VoiceAudioAnalyseResponse | null>;

  // ================================
  // Actions - 统计数据
  // ================================
  voice_service_store_load_usage_stats: (
    period?: 'day' | 'week' | 'month' | 'year'
  ) => Promise<void>;

  // ================================
  // Actions - 工具方法
  // ================================
  voice_service_store_clear_errors: () => void;
  voice_service_store_reset_synthesis_state: () => void;
  voice_service_store_reset_clone_state: () => void;
}

// ================================
// Store 创建
// ================================

export const useVoiceServiceStore = create<VoiceServiceState>()(
  devtools(
    subscribeWithSelector((set, get) => ({
      // ================================
      // 初始状态
      // ================================
      audioList: null,
      currentAudio: null,
      audioListLoading: false,
      audioDetailLoading: false,
      
      synthesisLoading: false,
      lastSynthesisResult: null,
      synthesisProgress: 0,
      batchSynthesisStatus: null,

      timbreList: null,
      currentTimbre: null,
      timbreListLoading: false,
      timbreDetailLoading: false,
      timbreCreateLoading: false,
      timbreUpdateLoading: false,
      
      cloneLoading: false,
      cloneProgress: 0,
      currentCloneTask: null,
      cloneHistory: [],

      platformVoices: {
        doubao: null,
        azure: null,
        openai: null,
        elevenlabs: null
      },
      platformConnectionStatus: {
        doubao: { is_connected: false },
        azure: { is_connected: false },
        openai: { is_connected: false },
        elevenlabs: { is_connected: false }
      },
      platformTestLoading: {
        doubao: false,
        azure: false,
        openai: false,
        elevenlabs: false
      },

      analysisLoading: false,
      lastAnalysisResult: null,

      usageStats: null,
      statsLoading: false,

      error: null,
      loading: false,

      // ================================
      // Actions 实现
      // ================================

      // 语音音频管理
      voice_service_store_load_audio_list: async (page = 1, pageSize = 20, filters = {}) => {
        set({ audioListLoading: true, error: null });
        try {
          const response = await voiceServiceApiService.voice_service_api_get_audio_list(
            page,
            pageSize,
            filters
          );
          if (response.success && response.data) {
            set({ audioList: response.data });
          } else {
            set({ error: response.message || '获取语音列表失败' });
          }
        } catch (error) {
          set({ error: '网络错误：获取语音列表失败' });
        } finally {
          set({ audioListLoading: false });
        }
      },

      voice_service_store_load_audio_detail: async (audioId: number) => {
        set({ audioDetailLoading: true, error: null });
        try {
          const response = await voiceServiceApiService.voice_service_api_get_audio_detail(audioId);
          if (response.success && response.data) {
            set({ currentAudio: response.data });
          } else {
            set({ error: response.message || '获取语音详情失败' });
          }
        } catch (error) {
          set({ error: '网络错误：获取语音详情失败' });
        } finally {
          set({ audioDetailLoading: false });
        }
      },

      voice_service_store_delete_audio: async (audioId: number) => {
        set({ loading: true, error: null });
        try {
          const response = await voiceServiceApiService.voice_service_api_delete_audio(audioId);
          if (response.success) {
            // 从列表中移除已删除的音频
            const currentList = get().audioList;
            if (currentList) {
              const updatedItems = currentList.items.filter(item => item.audio_id !== audioId);
              set({
                audioList: {
                  ...currentList,
                  items: updatedItems,
                  total: currentList.total - 1
                }
              });
            }
            return true;
          } else {
            set({ error: response.message || '删除语音失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：删除语音失败' });
          return false;
        } finally {
          set({ loading: false });
        }
      },

      // 语音合成
      voice_service_store_synthesize_text: async (request: VoiceSynthesisRequest) => {
        set({ synthesisLoading: true, synthesisProgress: 0, error: null });
        try {
          const response = await voiceServiceApiService.voice_service_api_synthesize_text(request);
          if (response.success && response.data) {
            set({ 
              lastSynthesisResult: response.data,
              synthesisProgress: 100
            });
            // 刷新音频列表
            get().voice_service_store_load_audio_list();
            return response.data;
          } else {
            set({ error: response.message || '语音合成失败' });
            return null;
          }
        } catch (error) {
          set({ error: '网络错误：语音合成失败' });
          return null;
        } finally {
          set({ synthesisLoading: false });
        }
      },

      voice_service_store_batch_synthesize: async (requests, common_params) => {
        set({ synthesisLoading: true, error: null });
        try {
          const response = await voiceServiceApiService.voice_service_api_batch_synthesize(
            requests,
            common_params
          );
          if (response.success && response.data) {
            set({
              batchSynthesisStatus: {
                task_id: response.data.task_id,
                status: 'processing',
                progress: 0,
                completed_count: 0,
                failed_count: 0
              }
            });
            return true;
          } else {
            set({ error: response.message || '批量合成启动失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：批量合成启动失败' });
          return false;
        } finally {
          set({ synthesisLoading: false });
        }
      },

      voice_service_store_check_batch_status: async (taskId: string) => {
        try {
          const response = await voiceServiceApiService.voice_service_api_get_batch_status(taskId);
          if (response.success && response.data) {
            set({ batchSynthesisStatus: response.data });
          }
        } catch (error) {
          console.warn('Failed to check batch status:', error);
        }
      },

      // 音色管理
      voice_service_store_load_timbre_list: async (page = 1, pageSize = 20, filters = {}) => {
        set({ timbreListLoading: true, error: null });
        try {
          const response = await voiceServiceApiService.voice_service_api_get_timbre_list(
            page,
            pageSize,
            filters
          );
          if (response.success && response.data) {
            set({ timbreList: response.data });
          } else {
            set({ error: response.message || '获取音色列表失败' });
          }
        } catch (error) {
          set({ error: '网络错误：获取音色列表失败' });
        } finally {
          set({ timbreListLoading: false });
        }
      },

      voice_service_store_load_timbre_detail: async (timbreId: number) => {
        set({ timbreDetailLoading: true, error: null });
        try {
          const response = await voiceServiceApiService.voice_service_api_get_timbre_detail(timbreId);
          if (response.success && response.data) {
            set({ currentTimbre: response.data });
          } else {
            set({ error: response.message || '获取音色详情失败' });
          }
        } catch (error) {
          set({ error: '网络错误：获取音色详情失败' });
        } finally {
          set({ timbreDetailLoading: false });
        }
      },

      voice_service_store_create_timbre: async (request: VoiceTimbreCreateRequest) => {
        set({ timbreCreateLoading: true, error: null });
        try {
          const response = await voiceServiceApiService.voice_service_api_create_timbre(request);
          if (response.success && response.data) {
            set({ currentTimbre: response.data });
            // 刷新音色列表
            get().voice_service_store_load_timbre_list();
            return true;
          } else {
            set({ error: response.message || '创建音色失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：创建音色失败' });
          return false;
        } finally {
          set({ timbreCreateLoading: false });
        }
      },

      voice_service_store_update_timbre: async (request: VoiceTimbreUpdateRequest) => {
        set({ timbreUpdateLoading: true, error: null });
        try {
          const response = await voiceServiceApiService.voice_service_api_update_timbre(request);
          if (response.success && response.data) {
            set({ currentTimbre: response.data });
            // 刷新音色列表
            get().voice_service_store_load_timbre_list();
            return true;
          } else {
            set({ error: response.message || '更新音色失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：更新音色失败' });
          return false;
        } finally {
          set({ timbreUpdateLoading: false });
        }
      },

      voice_service_store_delete_timbre: async (timbreId: number) => {
        set({ loading: true, error: null });
        try {
          const response = await voiceServiceApiService.voice_service_api_delete_timbre(timbreId);
          if (response.success) {
            // 从列表中移除已删除的音色
            const currentList = get().timbreList;
            if (currentList) {
              const updatedItems = currentList.items.filter(item => item.timbre_id !== timbreId);
              set({
                timbreList: {
                  ...currentList,
                  items: updatedItems,
                  total: currentList.total - 1
                }
              });
            }
            return true;
          } else {
            set({ error: response.message || '删除音色失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：删除音色失败' });
          return false;
        } finally {
          set({ loading: false });
        }
      },

      voice_service_store_clone_timbre: async (request: VoiceTimbreCloneRequest) => {
        set({ cloneLoading: true, cloneProgress: 0, error: null });
        try {
          const response = await voiceServiceApiService.voice_service_api_clone_timbre(request);
          if (response.success && response.data) {
            set({ 
              currentCloneTask: response.data,
              cloneHistory: [response.data, ...get().cloneHistory.slice(0, 9)] // 保留最近10条记录
            });
            return true;
          } else {
            set({ error: response.message || '音色克隆失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：音色克隆失败' });
          return false;
        } finally {
          set({ cloneLoading: false });
        }
      },

      voice_service_store_check_clone_status: async (taskId: string) => {
        try {
          const response = await voiceServiceApiService.voice_service_api_get_clone_status(taskId);
          if (response.success && response.data) {
            set({ currentCloneTask: response.data });
            // 如果完成了，刷新音色列表
            if (response.data.status === 'completed') {
              get().voice_service_store_load_timbre_list();
            }
          }
        } catch (error) {
          console.warn('Failed to check clone status:', error);
        }
      },

      // 平台管理
      voice_service_store_load_platform_voices: async (platformType, language) => {
        set({ loading: true, error: null });
        try {
          const response = await voiceServiceApiService.voice_service_api_get_platform_voices(
            platformType,
            language
          );
          if (response.success && response.data) {
            set(state => ({
              platformVoices: {
                ...state.platformVoices,
                [platformType]: response.data
              }
            }));
          } else {
            set({ error: response.message || '获取平台语音列表失败' });
          }
        } catch (error) {
          set({ error: '网络错误：获取平台语音列表失败' });
        } finally {
          set({ loading: false });
        }
      },

      voice_service_store_test_platform_connection: async (platformType) => {
        set(state => ({
          platformTestLoading: {
            ...state.platformTestLoading,
            [platformType]: true
          },
          error: null
        }));
        
        try {
          const response = await voiceServiceApiService.voice_service_api_test_platform_connection(platformType);
          if (response.success && response.data) {
            set(state => ({
              platformConnectionStatus: {
                ...state.platformConnectionStatus,
                [platformType]: {
                  ...response.data,
                  last_check: new Date().toISOString()
                }
              }
            }));
            return response.data.is_connected;
          } else {
            set(state => ({
              platformConnectionStatus: {
                ...state.platformConnectionStatus,
                [platformType]: {
                  is_connected: false,
                  error_message: response.message || '连接测试失败',
                  last_check: new Date().toISOString()
                }
              }
            }));
            return false;
          }
        } catch (error) {
          set(state => ({
            platformConnectionStatus: {
              ...state.platformConnectionStatus,
              [platformType]: {
                is_connected: false,
                error_message: '网络错误',
                last_check: new Date().toISOString()
              }
            }
          }));
          return false;
        } finally {
          set(state => ({
            platformTestLoading: {
              ...state.platformTestLoading,
              [platformType]: false
            }
          }));
        }
      },

      // 语音分析
      voice_service_store_analyse_audio: async (request: VoiceAudioAnalyseRequest) => {
        set({ analysisLoading: true, error: null });
        try {
          const response = await voiceServiceApiService.voice_service_api_analyse_audio(request);
          if (response.success && response.data) {
            set({ lastAnalysisResult: response.data });
            return response.data;
          } else {
            set({ error: response.message || '语音分析失败' });
            return null;
          }
        } catch (error) {
          set({ error: '网络错误：语音分析失败' });
          return null;
        } finally {
          set({ analysisLoading: false });
        }
      },

      // 统计数据
      voice_service_store_load_usage_stats: async (period = 'month') => {
        set({ statsLoading: true, error: null });
        try {
          const response = await voiceServiceApiService.voice_service_api_get_usage_stats(period);
          if (response.success && response.data) {
            set({ usageStats: response.data });
          } else {
            set({ error: response.message || '获取使用统计失败' });
          }
        } catch (error) {
          set({ error: '网络错误：获取使用统计失败' });
        } finally {
          set({ statsLoading: false });
        }
      },

      // 工具方法
      voice_service_store_clear_errors: () => {
        set({ error: null });
      },

      voice_service_store_reset_synthesis_state: () => {
        set({ 
          synthesisLoading: false,
          lastSynthesisResult: null,
          synthesisProgress: 0,
          batchSynthesisStatus: null
        });
      },

      voice_service_store_reset_clone_state: () => {
        set({
          cloneLoading: false,
          cloneProgress: 0,
          currentCloneTask: null
        });
      }
    })),
    {
      name: 'voice-service-store',
    }
  )
);