/**
 * Doubao Service Hook
 * 豆包服务React Hook - [services][doubao][use_doubao_service]
 */

import { useState, useCallback, useRef } from 'react';
import { message } from 'antd';
import { doubaoApi } from './doubaoApi';
import { downloadAudio, playAudioPreview } from '../../components/doubao/utils';
import type {
  VoiceCloneFormData,
  TTSFormData,
  VoiceOption
} from '../../components/doubao/types';

interface DoubaoServiceState {
  // 加载状态
  voiceCloneLoading: boolean;
  ttsLoading: boolean;
  ttsPreviewLoading: boolean;
  healthCheckLoading: boolean;
  
  // 数据状态
  userVoices: VoiceOption[];
  healthStatus: 'healthy' | 'unhealthy' | 'unknown';
  lastHealthCheck: string | null;
  
  // 错误状态
  error: string | null;
}

/**
 * 豆包服务Hook
 * [services][doubao][use_doubao_service][useDoubaoService]
 */
export const useDoubaoService = () => {
  const [state, setState] = useState<DoubaoServiceState>({
    voiceCloneLoading: false,
    ttsLoading: false,
    ttsPreviewLoading: false,
    healthCheckLoading: false,
    userVoices: [],
    healthStatus: 'unknown',
    lastHealthCheck: null,
    error: null
  });

  // 用于存储当前播放的音频
  const currentAudioRef = useRef<HTMLAudioElement | null>(null);

  /**
   * 更新状态的辅助函数
   */
  const updateState = useCallback((updates: Partial<DoubaoServiceState>) => {
    setState(prev => ({ ...prev, ...updates }));
  }, []);

  /**
   * 清除错误
   */
  const clearError = useCallback(() => {
    updateState({ error: null });
  }, [updateState]);

  /**
   * 健康检查
   * [services][doubao][use_doubao_service][checkHealth]
   */
  const checkHealth = useCallback(async () => {
    updateState({ healthCheckLoading: true, error: null });
    
    try {
      const response = await doubaoApi.healthCheck();
      
      if (response.success) {
        updateState({
          healthStatus: 'healthy',
          lastHealthCheck: new Date().toLocaleTimeString(),
          healthCheckLoading: false
        });
        message.success('服务状态检查完成');
      } else {
        updateState({
          healthStatus: 'unhealthy',
          lastHealthCheck: new Date().toLocaleTimeString(),
          healthCheckLoading: false,
          error: response.message
        });
        message.error('服务状态异常');
      }
    } catch (error) {
      updateState({
        healthStatus: 'unhealthy',
        lastHealthCheck: new Date().toLocaleTimeString(),
        healthCheckLoading: false,
        error: error instanceof Error ? error.message : '健康检查失败'
      });
      message.error('健康检查失败');
    }
  }, [updateState]);

  /**
   * 获取用户音色列表
   * [services][doubao][use_doubao_service][fetchUserVoices]
   */
  const fetchUserVoices = useCallback(async () => {
    try {
      const response = await doubaoApi.voiceCloneList();
      
      if (response.success && response.data?.voices) {
        const voices: VoiceOption[] = response.data.voices.map((voice: any) => ({
          value: voice.timbre_speaker_id || `custom_${voice.timbre_id}`,
          label: voice.timbre_name,
          language: voice.timbre_language || '中文',
          gender: '自定义',
          style: voice.timbre_description || '用户定制音色',
          description: voice.timbre_description,
          isCustom: true
        }));
        
        updateState({ userVoices: voices });
        return voices;
      } else {
        updateState({ userVoices: [] });
        return [];
      }
    } catch (error) {
      console.error('Failed to fetch user voices:', error);
      updateState({ userVoices: [] });
      return [];
    }
  }, [updateState]);

  /**
   * 音色克隆提交
   * [services][doubao][use_doubao_service][submitVoiceClone]
   */
  const submitVoiceClone = useCallback(async (formData: VoiceCloneFormData) => {
    updateState({ voiceCloneLoading: true, error: null });
    
    try {
      const response = await doubaoApi.voiceCloneUpload(formData);
      
      if (response.success) {
        message.success({
          content: '音色克隆任务已提交，预计需要5-10分钟完成训练',
          duration: 5
        });
        
        // 刷新用户音色列表
        await fetchUserVoices();
        
        updateState({ voiceCloneLoading: false });
        return response;
      } else {
        throw new Error(response.message || '音色克隆提交失败');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '音色克隆提交失败';
      updateState({ 
        voiceCloneLoading: false, 
        error: errorMessage 
      });
      message.error(errorMessage);
      throw error;
    }
  }, [updateState, fetchUserVoices]);

  /**
   * 查询音色克隆状态
   * [services][doubao][use_doubao_service][checkVoiceCloneStatus]
   */
  const checkVoiceCloneStatus = useCallback(async (speakerId: string) => {
    try {
      const response = await doubaoApi.voiceCloneStatus(speakerId);
      return response;
    } catch (error) {
      console.error('Failed to check voice clone status:', error);
      throw error;
    }
  }, []);

  /**
   * TTS合成
   * [services][doubao][use_doubao_service][synthesizeTTS]
   */
  const synthesizeTTS = useCallback(async (formData: TTSFormData) => {
    updateState({ ttsLoading: true, error: null });
    
    try {
      const audioBlob = await doubaoApi.ttsSynthesize(formData);
      
      // 转换为Uint8Array用于下载
      const arrayBuffer = await audioBlob.arrayBuffer();
      const audioData = new Uint8Array(arrayBuffer);
      
      // 生成文件名
      const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
      const filename = `tts_${timestamp}`;
      
      // 下载文件
      downloadAudio(audioData, filename, formData.encoding);
      
      updateState({ ttsLoading: false });
      message.success('音频合成完成');
      
      return audioData;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'TTS合成失败';
      updateState({ 
        ttsLoading: false, 
        error: errorMessage 
      });
      message.error(errorMessage);
      throw error;
    }
  }, [updateState]);

  /**
   * TTS预览
   * [services][doubao][use_doubao_service][previewTTS]
   */
  const previewTTS = useCallback(async (formData: TTSFormData) => {
    updateState({ ttsPreviewLoading: true, error: null });
    
    try {
      // 停止当前播放的音频
      if (currentAudioRef.current) {
        currentAudioRef.current.pause();
        currentAudioRef.current = null;
      }
      
      const audioBlob = await doubaoApi.ttsPreview(formData);
      
      // 转换为Uint8Array用于播放
      const arrayBuffer = await audioBlob.arrayBuffer();
      const audioData = new Uint8Array(arrayBuffer);
      
      // 播放预览
      await playAudioPreview(audioData, formData.encoding);
      
      updateState({ ttsPreviewLoading: false });
      message.success('预览播放完成');
      
      return audioData;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '预览生成失败';
      updateState({ 
        ttsPreviewLoading: false, 
        error: errorMessage 
      });
      message.error(errorMessage);
      throw error;
    }
  }, [updateState]);

  /**
   * 文本预处理
   * [services][doubao][use_doubao_service][preprocessText]
   */
  const preprocessText = useCallback(async (
    text: string,
    operation: string = 'normalize',
    parameters?: Record<string, any>
  ) => {
    try {
      const response = await doubaoApi.textPreprocess(text, operation, parameters);
      
      if (response.success) {
        return response.data;
      } else {
        throw new Error(response.message || '文本预处理失败');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '文本预处理失败';
      message.error(errorMessage);
      throw error;
    }
  }, []);

  /**
   * 停止音频播放
   * [services][doubao][use_doubao_service][stopAudio]
   */
  const stopAudio = useCallback(() => {
    if (currentAudioRef.current) {
      currentAudioRef.current.pause();
      currentAudioRef.current = null;
    }
  }, []);

  /**
   * 重置所有状态
   * [services][doubao][use_doubao_service][reset]
   */
  const reset = useCallback(() => {
    stopAudio();
    setState({
      voiceCloneLoading: false,
      ttsLoading: false,
      ttsPreviewLoading: false,
      healthCheckLoading: false,
      userVoices: [],
      healthStatus: 'unknown',
      lastHealthCheck: null,
      error: null
    });
  }, [stopAudio]);

  return {
    // 状态
    ...state,
    
    // 操作函数
    checkHealth,
    fetchUserVoices,
    submitVoiceClone,
    checkVoiceCloneStatus,
    synthesizeTTS,
    previewTTS,
    preprocessText,
    stopAudio,
    clearError,
    reset
  };
};