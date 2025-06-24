/**
 * Voice Workbench Service Hook
 * 语音工作台服务Hook - [services][voice_workbench][hook]
 */

import { useState, useCallback, useEffect } from 'react';
import { message } from 'antd';
import { httpClient } from '../http/httpClient';
import type {
  VoiceWorkbenchState,
  VoicePlatformInfo,
  PlatformHealthStatus,
  VoiceOperationResult,
  UserVoiceInfo,
  VoiceCloneFormData,
  TTSFormData,
  PlatformStatistics,
  ApiResponse
} from './types';

/**
 * 语音工作台服务Hook
 * [services][voice_workbench][useVoiceWorkbenchService]
 */
export const useVoiceWorkbenchService = () => {
  // 状态管理
  const [state, setState] = useState<VoiceWorkbenchState>({
    // 平台相关
    platforms: [],
    selectedPlatform: null,
    platformHealth: {},
    platformsLoading: false,
    
    // 操作状态
    voiceCloneLoading: false,
    ttsLoading: false,
    ttsPreviewLoading: false,
    
    // 数据
    userVoices: [],
    operationHistory: [],
    
    // 错误处理
    error: null,
    lastError: null
  });

  // 更新状态的辅助函数
  const updateState = useCallback((updates: Partial<VoiceWorkbenchState>) => {
    setState(prev => ({ ...prev, ...updates }));
  }, []);

  // 错误处理
  const handleError = useCallback((error: any, operation: string) => {
    console.error(`${operation} failed:`, error);
    const errorMessage = error.response?.data?.detail || error.message || `${operation}失败`;
    updateState({
      error: errorMessage,
      lastError: error
    });
  }, [updateState]);

  // 清除错误
  const clearError = useCallback(() => {
    updateState({
      error: null,
      lastError: null
    });
  }, [updateState]);

  // ==================== 平台管理 ====================

  /**
   * 刷新平台列表
   * [services][voice_workbench][refreshPlatforms]
   */
  const refreshPlatforms = useCallback(async () => {
    try {
      updateState({ platformsLoading: true });
      
      const response = await httpClient.get<ApiResponse<{
        platforms: VoicePlatformInfo[];
        summary: any;
      }>>('/voice/platforms/list');
      
      if (response.data.success) {
        const platforms = response.data.data?.platforms || [];
        const platformHealth: Record<string, PlatformHealthStatus> = {};
        
        // 提取平台健康状态
        platforms.forEach(platform => {
          platformHealth[platform.platform_type] = {
            is_healthy: platform.is_healthy,
            last_health_check: new Date().toISOString(),
            response_time_ms: 0,
            daily_requests_used: 0,
            daily_requests_limit: 1000
          };
        });
        
        updateState({
          platforms,
          platformHealth,
          // 自动选择第一个可用平台
          selectedPlatform: state.selectedPlatform || platforms.find(p => p.is_enabled && p.is_healthy)?.platform_type || null
        });
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      handleError(error, '刷新平台列表');
    } finally {
      updateState({ platformsLoading: false });
    }
  }, [state.selectedPlatform, updateState, handleError]);

  /**
   * 选择平台
   * [services][voice_workbench][selectPlatform]
   */
  const selectPlatform = useCallback(async (platformType: string) => {
    try {
      const platform = state.platforms.find(p => p.platform_type === platformType);
      if (!platform) {
        throw new Error('平台不存在');
      }
      
      if (!platform.is_enabled || !platform.is_healthy) {
        throw new Error('平台不可用');
      }
      
      updateState({ selectedPlatform: platformType });
      
      // 自动刷新用户音色列表
      await fetchUserVoices(platformType);
      
      message.success(`已切换到 ${platform.platform_name}`);
    } catch (error) {
      handleError(error, '选择平台');
    }
  }, [state.platforms, updateState, handleError]);

  /**
   * 健康检查所有平台
   * [services][voice_workbench][healthCheckPlatforms]
   */
  const healthCheckPlatforms = useCallback(async () => {
    try {
      updateState({ platformsLoading: true });
      
      const response = await httpClient.post<ApiResponse>('/voice/health-check');
      
      if (response.data.success) {
        message.success('平台健康检查完成');
        // 重新加载平台信息
        await refreshPlatforms();
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      handleError(error, '平台健康检查');
    } finally {
      updateState({ platformsLoading: false });
    }
  }, [updateState, handleError, refreshPlatforms]);

  // ==================== 音色管理 ====================

  /**
   * 获取用户音色列表
   * [services][voice_workbench][fetchUserVoices]
   */
  const fetchUserVoices = useCallback(async (platform?: string) => {
    try {
      const targetPlatform = platform || state.selectedPlatform;
      if (!targetPlatform) return;
      
      const response = await httpClient.get<ApiResponse<{
        voices_by_platform: Record<string, UserVoiceInfo[]>;
      }>>('/voice/timbre/list', {
        params: { platform: targetPlatform }
      });
      
      if (response.data.success) {
        const voicesData = response.data.data?.voices_by_platform || {};
        const userVoices = voicesData[targetPlatform] || [];
        updateState({ userVoices });
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      handleError(error, '获取音色列表');
    }
  }, [state.selectedPlatform, updateState, handleError]);

  /**
   * 提交音色克隆
   * [services][voice_workbench][submitVoiceClone]
   */
  const submitVoiceClone = useCallback(async (formData: VoiceCloneFormData) => {
    try {
      updateState({ voiceCloneLoading: true });
      
      // 构建FormData
      const submitData = new FormData();
      submitData.append('audio_file', formData.audio_file);
      
      const requestData = {
        timbre_name: formData.timbre_name,
        timbre_description: formData.timbre_description,
        language: formData.language,
        model_type: formData.model_type,
        reference_text: formData.reference_text,
        preferred_platform: formData.preferred_platform,
        advanced_params: formData.advanced_params
      };
      
      submitData.append('request_data', JSON.stringify(requestData));
      
      const response = await httpClient.post<ApiResponse<VoiceOperationResult>>(
        '/voice/timbre/clone',
        submitData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      
      if (response.data.success) {
        const result = response.data.data!;
        updateState({
          operationHistory: [result, ...state.operationHistory]
        });
        
        message.success('音色克隆任务已创建，请等待训练完成');
        
        // 刷新音色列表
        await fetchUserVoices();
        
        return result;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      handleError(error, '音色克隆');
      throw error;
    } finally {
      updateState({ voiceCloneLoading: false });
    }
  }, [state.operationHistory, updateState, handleError, fetchUserVoices]);

  // ==================== TTS合成 ====================

  /**
   * TTS语音合成
   * [services][voice_workbench][synthesizeTTS]
   */
  const synthesizeTTS = useCallback(async (formData: TTSFormData) => {
    try {
      updateState({ ttsLoading: true });
      
      const response = await httpClient.post<ApiResponse<VoiceOperationResult>>(
        '/voice/synthesis/text-to-speech',
        formData
      );
      
      if (response.data.success) {
        const result = response.data.data!;
        updateState({
          operationHistory: [result, ...state.operationHistory]
        });
        
        message.success('语音合成成功');
        return result;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      handleError(error, 'TTS语音合成');
      throw error;
    } finally {
      updateState({ ttsLoading: false });
    }
  }, [state.operationHistory, updateState, handleError]);

  /**
   * TTS预览
   * [services][voice_workbench][previewTTS]
   */
  const previewTTS = useCallback(async (formData: Partial<TTSFormData>) => {
    try {
      updateState({ ttsPreviewLoading: true });
      
      // 预览用较短的文本
      const previewData = {
        ...formData,
        text: formData.text?.substring(0, 100) + '...' || '这是一个语音预览测试。',
        streaming: false
      };
      
      const response = await httpClient.post<ApiResponse<VoiceOperationResult>>(
        '/voice/synthesis/text-to-speech',
        previewData
      );
      
      if (response.data.success) {
        const result = response.data.data!;
        
        // 播放预览音频
        if (result.result_data?.audio_data) {
          // 这里需要实现音频播放逻辑
          message.success('预览音频已生成');
        }
        
        return result;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      handleError(error, 'TTS预览');
      throw error;
    } finally {
      updateState({ ttsPreviewLoading: false });
    }
  }, [updateState, handleError]);

  // ==================== 操作状态查询 ====================

  /**
   * 获取操作状态
   * [services][voice_workbench][getOperationStatus]
   */
  const getOperationStatus = useCallback(async (operationId: string) => {
    try {
      const response = await httpClient.get<ApiResponse<VoiceOperationResult>>(
        `/voice/operations/${operationId}`
      );
      
      if (response.data.success) {
        const result = response.data.data!;
        
        // 更新操作历史中的对应记录
        updateState({
          operationHistory: state.operationHistory.map(op => 
            op.operation_id === operationId ? result : op
          )
        });
        
        return result;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      handleError(error, '获取操作状态');
      throw error;
    }
  }, [state.operationHistory, updateState, handleError]);

  /**
   * 获取平台统计信息
   * [services][voice_workbench][getPlatformStatistics]
   */
  const getPlatformStatistics = useCallback(async (): Promise<PlatformStatistics | null> => {
    try {
      const response = await httpClient.get<ApiResponse<PlatformStatistics>>('/voice/statistics');
      
      if (response.data.success) {
        return response.data.data!;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      handleError(error, '获取平台统计');
      return null;
    }
  }, [handleError]);

  // ==================== 初始化和清理 ====================

  // 组件初始化时自动加载平台信息
  useEffect(() => {
    refreshPlatforms();
  }, []);

  // 返回Hook接口
  return {
    // 状态
    ...state,
    
    // 平台管理
    refreshPlatforms,
    selectPlatform,
    healthCheckPlatforms,
    
    // 音色管理
    fetchUserVoices,
    submitVoiceClone,
    
    // TTS功能
    synthesizeTTS,
    previewTTS,
    
    // 状态查询
    getOperationStatus,
    getPlatformStatistics,
    
    // 错误处理
    clearError
  };
};