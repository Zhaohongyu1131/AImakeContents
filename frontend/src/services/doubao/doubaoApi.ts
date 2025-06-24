/**
 * Doubao API Service
 * 豆包API服务 - [services][doubao][api]
 */

import { httpClient } from '../http/httpClient';
import type {
  VoiceCloneFormData,
  VoiceCloneResponse,
  SpeakerStatusResponse,
  TTSFormData,
  ApiResponse
} from '../../components/doubao/types';

const DOUBAO_API_BASE = '/api/v1/doubao';

/**
 * 豆包API服务类
 * [services][doubao][api][DoubaoApiService]
 */
export class DoubaoApiService {
  
  /**
   * 健康检查
   * [services][doubao][api][health_check]
   */
  static async healthCheck(): Promise<ApiResponse> {
    try {
      const response = await httpClient.get(`${DOUBAO_API_BASE}/health`);
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }

  /**
   * 音色克隆上传
   * [services][doubao][api][voice_clone_upload]
   */
  static async voiceCloneUpload(formData: VoiceCloneFormData): Promise<VoiceCloneResponse> {
    try {
      const uploadFormData = new FormData();
      
      // 添加音频文件
      if (formData.audio_file) {
        uploadFormData.append('audio_file', formData.audio_file);
      }
      
      // 添加其他参数
      const requestData = {
        timbre_name: formData.timbre_name,
        timbre_description: formData.timbre_description,
        language: formData.language,
        model_type: formData.model_type,
        reference_text: ''
      };
      
      uploadFormData.append('request_data', JSON.stringify(requestData));
      
      const response = await httpClient.post(
        `${DOUBAO_API_BASE}/voice/clone/upload`,
        uploadFormData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          timeout: 60000, // 60秒超时
        }
      );
      
      return response.data;
    } catch (error) {
      console.error('Voice clone upload failed:', error);
      throw error;
    }
  }

  /**
   * 查询音色克隆状态
   * [services][doubao][api][voice_clone_status]
   */
  static async voiceCloneStatus(speakerId: string): Promise<SpeakerStatusResponse> {
    try {
      const response = await httpClient.get(`${DOUBAO_API_BASE}/voice/clone/status/${speakerId}`);
      return response.data;
    } catch (error) {
      console.error('Voice clone status check failed:', error);
      throw error;
    }
  }

  /**
   * 获取用户音色列表
   * [services][doubao][api][voice_clone_list]
   */
  static async voiceCloneList(): Promise<ApiResponse> {
    try {
      const response = await httpClient.get(`${DOUBAO_API_BASE}/voice/clone/list`);
      return response.data;
    } catch (error) {
      console.error('Voice clone list fetch failed:', error);
      throw error;
    }
  }

  /**
   * TTS合成
   * [services][doubao][api][tts_synthesize]
   */
  static async ttsSynthesize(formData: TTSFormData): Promise<Blob> {
    try {
      const response = await httpClient.post(
        `${DOUBAO_API_BASE}/voice/tts/synthesize`,
        formData,
        {
          responseType: 'blob',
          timeout: 120000, // 2分钟超时
        }
      );
      
      return response.data;
    } catch (error) {
      console.error('TTS synthesis failed:', error);
      throw error;
    }
  }

  /**
   * TTS预览
   * [services][doubao][api][tts_preview]
   */
  static async ttsPreview(formData: TTSFormData): Promise<Blob> {
    try {
      // 预览时限制文本长度
      const previewData = {
        ...formData,
        text: formData.text.substring(0, 100) // 只预览前100字符
      };
      
      const response = await httpClient.post(
        `${DOUBAO_API_BASE}/voice/tts/synthesize`,
        previewData,
        {
          responseType: 'blob',
          timeout: 30000, // 30秒超时
        }
      );
      
      return response.data;
    } catch (error) {
      console.error('TTS preview failed:', error);
      throw error;
    }
  }

  /**
   * 流式TTS
   * [services][doubao][api][tts_stream]
   */
  static async ttsStream(
    formData: TTSFormData,
    onChunk?: (chunk: Uint8Array) => void,
    onComplete?: (audioData: Uint8Array) => void
  ): Promise<void> {
    try {
      const response = await httpClient.post(
        `${DOUBAO_API_BASE}/voice/tts/stream`,
        formData,
        {
          responseType: 'stream',
          timeout: 0, // 不设置超时，因为是流式
        }
      );

      const chunks: Uint8Array[] = [];

      // 处理流数据
      response.data.on('data', (chunk: Uint8Array) => {
        chunks.push(chunk);
        if (onChunk) {
          onChunk(chunk);
        }
      });

      response.data.on('end', () => {
        const completeAudio = new Uint8Array(
          chunks.reduce((total, chunk) => total + chunk.length, 0)
        );
        
        let offset = 0;
        chunks.forEach(chunk => {
          completeAudio.set(chunk, offset);
          offset += chunk.length;
        });

        if (onComplete) {
          onComplete(completeAudio);
        }
      });

      response.data.on('error', (error: Error) => {
        console.error('Stream error:', error);
        throw error;
      });

    } catch (error) {
      console.error('TTS stream failed:', error);
      throw error;
    }
  }

  /**
   * 文本预处理
   * [services][doubao][api][text_preprocess]
   */
  static async textPreprocess(
    text: string,
    operation: string = 'normalize',
    parameters?: Record<string, any>
  ): Promise<ApiResponse> {
    try {
      const response = await httpClient.post(`${DOUBAO_API_BASE}/text/preprocess`, {
        text,
        operation,
        parameters
      });
      
      return response.data;
    } catch (error) {
      console.error('Text preprocess failed:', error);
      throw error;
    }
  }

  /**
   * 文本分析
   * [services][doubao][api][text_analyze]
   */
  static async textAnalyze(
    text: string,
    operation: string = 'analyze',
    parameters?: Record<string, any>
  ): Promise<ApiResponse> {
    try {
      const response = await httpClient.post(`${DOUBAO_API_BASE}/text/analyze`, {
        text,
        operation,
        parameters
      });
      
      return response.data;
    } catch (error) {
      console.error('Text analyze failed:', error);
      throw error;
    }
  }

  /**
   * 文本验证
   * [services][doubao][api][text_validate]
   */
  static async textValidate(
    text: string,
    operation: string = 'validate',
    parameters?: Record<string, any>
  ): Promise<ApiResponse> {
    try {
      const response = await httpClient.post(`${DOUBAO_API_BASE}/text/validate`, {
        text,
        operation,
        parameters
      });
      
      return response.data;
    } catch (error) {
      console.error('Text validate failed:', error);
      throw error;
    }
  }

  /**
   * 文本分割
   * [services][doubao][api][text_split]
   */
  static async textSplit(
    text: string,
    operation: string = 'split',
    parameters?: Record<string, any>
  ): Promise<ApiResponse> {
    try {
      const response = await httpClient.post(`${DOUBAO_API_BASE}/text/split`, {
        text,
        operation,
        parameters
      });
      
      return response.data;
    } catch (error) {
      console.error('Text split failed:', error);
      throw error;
    }
  }
}

// 导出单例实例
export const doubaoApi = DoubaoApiService;