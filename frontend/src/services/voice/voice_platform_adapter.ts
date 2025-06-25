/**
 * Voice Platform Adapter
 * 语音平台适配器 - [services][voice][platform_adapter]
 * 
 * 统一的多平台语音服务适配器，支持豆包、阿里、Google等平台
 */

import { axiosInstance } from '../axios/axios_instance'

// ================================
// 平台类型和基础接口定义
// ================================

export type VoicePlatformType = 'doubao' | 'aliyun' | 'google' | 'azure' | 'openai' | 'elevenlabs'

export interface VoicePlatformConfig {
  platform_type: VoicePlatformType
  api_key: string
  secret_key?: string
  endpoint?: string
  region?: string
  enabled: boolean
  priority: number
  rate_limit?: number
  cost_per_character?: number
}

export interface VoiceTimbreInfo {
  timbre_id: string
  timbre_name: string
  platform_type: VoicePlatformType
  platform_voice_id: string
  voice_gender: 'male' | 'female' | 'neutral'
  voice_language: string
  voice_style?: string
  sample_url?: string
  is_custom: boolean
  parameters?: Record<string, any>
}

export interface VoiceSynthesisParams {
  text: string
  timbre_id: string
  speed?: number
  pitch?: number
  volume?: number
  emotion?: string
  style?: string
  format?: 'mp3' | 'wav' | 'ogg'
  sample_rate?: number
  quality?: 'standard' | 'high' | 'premium'
}

export interface VoiceCloneParams {
  name: string
  description?: string
  audio_files: File[]
  gender?: 'male' | 'female' | 'auto'
  language: string
  quality_level?: 'standard' | 'high' | 'premium'
  enhancement?: boolean
}

export interface VoiceSynthesisResult {
  audio_url: string
  audio_data?: ArrayBuffer
  duration: number
  file_size: number
  cost: number
  platform_used: VoicePlatformType
  quality_score?: number
  processing_time: number
}

export interface VoiceCloneResult {
  clone_id: string
  status: 'processing' | 'completed' | 'failed'
  progress: number
  timbre_info?: VoiceTimbreInfo
  estimated_time?: number
  error_message?: string
}

// ================================
// 平台适配器接口
// ================================

export interface IVoicePlatformAdapter {
  platform_type: VoicePlatformType
  
  // 基础功能
  testConnection(): Promise<boolean>
  getAvailableVoices(language?: string): Promise<VoiceTimbreInfo[]>
  
  // 语音合成
  synthesizeText(params: VoiceSynthesisParams): Promise<VoiceSynthesisResult>
  
  // 音色克隆（如果平台支持）
  cloneVoice?(params: VoiceCloneParams): Promise<VoiceCloneResult>
  getCloneStatus?(clone_id: string): Promise<VoiceCloneResult>
  
  // 平台特定配置
  configure(config: VoicePlatformConfig): void
  getConfig(): VoicePlatformConfig
}

// ================================
// 豆包平台适配器
// ================================

export class DoubaoVoiceAdapter implements IVoicePlatformAdapter {
  platform_type: VoicePlatformType = 'doubao'
  private config: VoicePlatformConfig

  constructor(config: VoicePlatformConfig) {
    this.config = config
  }

  configure(config: VoicePlatformConfig): void {
    this.config = { ...this.config, ...config }
  }

  getConfig(): VoicePlatformConfig {
    return this.config
  }

  async testConnection(): Promise<boolean> {
    try {
      const response = await axiosInstance.get('/voice/platform/doubao/health')
      return response.data.success
    } catch (error) {
      console.error('Doubao connection test failed:', error)
      return false
    }
  }

  async getAvailableVoices(language?: string): Promise<VoiceTimbreInfo[]> {
    try {
      const response = await axiosInstance.get('/voice/platform/doubao/voices', {
        params: { language }
      })
      
      return response.data.data.map((voice: any) => ({
        timbre_id: voice.voice_id,
        timbre_name: voice.voice_name,
        platform_type: this.platform_type,
        platform_voice_id: voice.voice_id,
        voice_gender: voice.gender,
        voice_language: voice.language,
        voice_style: voice.style,
        sample_url: voice.sample_url,
        is_custom: voice.is_cloned || false,
        parameters: voice.parameters
      }))
    } catch (error) {
      console.error('Failed to get Doubao voices:', error)
      throw error
    }
  }

  async synthesizeText(params: VoiceSynthesisParams): Promise<VoiceSynthesisResult> {
    try {
      const response = await axiosInstance.post('/voice/platform/doubao/synthesize', {
        text: params.text,
        voice_id: params.timbre_id,
        speed: params.speed || 1.0,
        pitch: params.pitch || 1.0,
        volume: params.volume || 1.0,
        emotion: params.emotion || 'neutral',
        style: params.style || 'normal',
        format: params.format || 'mp3',
        sample_rate: params.sample_rate || 22050,
        quality: params.quality || 'high'
      })

      return {
        audio_url: response.data.data.audio_url,
        audio_data: response.data.data.audio_data,
        duration: response.data.data.duration,
        file_size: response.data.data.file_size,
        cost: response.data.data.cost,
        platform_used: this.platform_type,
        quality_score: response.data.data.quality_score,
        processing_time: response.data.data.processing_time
      }
    } catch (error) {
      console.error('Doubao synthesis failed:', error)
      throw error
    }
  }

  async cloneVoice(params: VoiceCloneParams): Promise<VoiceCloneResult> {
    try {
      const formData = new FormData()
      formData.append('name', params.name)
      formData.append('description', params.description || '')
      formData.append('gender', params.gender || 'auto')
      formData.append('language', params.language)
      formData.append('quality_level', params.quality_level || 'high')
      formData.append('enhancement', String(params.enhancement || true))
      
      params.audio_files.forEach((file, index) => {
        formData.append(`audio_files`, file)
      })

      const response = await axiosInstance.post('/voice/platform/doubao/clone', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      return {
        clone_id: response.data.data.clone_id,
        status: response.data.data.status,
        progress: response.data.data.progress || 0,
        estimated_time: response.data.data.estimated_time
      }
    } catch (error) {
      console.error('Doubao voice clone failed:', error)
      throw error
    }
  }

  async getCloneStatus(clone_id: string): Promise<VoiceCloneResult> {
    try {
      const response = await axiosInstance.get(`/voice/platform/doubao/clone/status/${clone_id}`)
      
      return {
        clone_id,
        status: response.data.data.status,
        progress: response.data.data.progress,
        timbre_info: response.data.data.timbre_info,
        error_message: response.data.data.error_message
      }
    } catch (error) {
      console.error('Failed to get Doubao clone status:', error)
      throw error
    }
  }
}

// ================================
// 阿里云平台适配器
// ================================

export class AliyunVoiceAdapter implements IVoicePlatformAdapter {
  platform_type: VoicePlatformType = 'aliyun'
  private config: VoicePlatformConfig

  constructor(config: VoicePlatformConfig) {
    this.config = config
  }

  configure(config: VoicePlatformConfig): void {
    this.config = { ...this.config, ...config }
  }

  getConfig(): VoicePlatformConfig {
    return this.config
  }

  async testConnection(): Promise<boolean> {
    try {
      const response = await axiosInstance.get('/voice/platform/aliyun/health')
      return response.data.success
    } catch (error) {
      console.error('Aliyun connection test failed:', error)
      return false
    }
  }

  async getAvailableVoices(language?: string): Promise<VoiceTimbreInfo[]> {
    try {
      const response = await axiosInstance.get('/voice/platform/aliyun/voices', {
        params: { language }
      })
      
      return response.data.data.map((voice: any) => ({
        timbre_id: voice.voice,
        timbre_name: voice.name,
        platform_type: this.platform_type,
        platform_voice_id: voice.voice,
        voice_gender: voice.gender,
        voice_language: voice.language,
        sample_url: voice.sample_url,
        is_custom: false, // 阿里云暂不支持自定义音色
        parameters: voice.parameters
      }))
    } catch (error) {
      console.error('Failed to get Aliyun voices:', error)
      throw error
    }
  }

  async synthesizeText(params: VoiceSynthesisParams): Promise<VoiceSynthesisResult> {
    try {
      const response = await axiosInstance.post('/voice/platform/aliyun/synthesize', {
        text: params.text,
        voice: params.timbre_id,
        speech_rate: Math.round((params.speed || 1.0) * 100), // 阿里云使用0-500的范围
        pitch_rate: Math.round((params.pitch || 1.0) * 100),
        volume: Math.round((params.volume || 1.0) * 100),
        format: params.format || 'mp3',
        sample_rate: params.sample_rate || 16000
      })

      return {
        audio_url: response.data.data.audio_url,
        duration: response.data.data.duration,
        file_size: response.data.data.file_size,
        cost: response.data.data.cost,
        platform_used: this.platform_type,
        processing_time: response.data.data.processing_time
      }
    } catch (error) {
      console.error('Aliyun synthesis failed:', error)
      throw error
    }
  }
}

// ================================
// Google Cloud TTS适配器
// ================================

export class GoogleVoiceAdapter implements IVoicePlatformAdapter {
  platform_type: VoicePlatformType = 'google'
  private config: VoicePlatformConfig

  constructor(config: VoicePlatformConfig) {
    this.config = config
  }

  configure(config: VoicePlatformConfig): void {
    this.config = { ...this.config, ...config }
  }

  getConfig(): VoicePlatformConfig {
    return this.config
  }

  async testConnection(): Promise<boolean> {
    try {
      const response = await axiosInstance.get('/voice/platform/google/health')
      return response.data.success
    } catch (error) {
      console.error('Google connection test failed:', error)
      return false
    }
  }

  async getAvailableVoices(language?: string): Promise<VoiceTimbreInfo[]> {
    try {
      const response = await axiosInstance.get('/voice/platform/google/voices', {
        params: { language_code: language }
      })
      
      return response.data.data.map((voice: any) => ({
        timbre_id: voice.name,
        timbre_name: voice.display_name,
        platform_type: this.platform_type,
        platform_voice_id: voice.name,
        voice_gender: voice.ssml_gender.toLowerCase(),
        voice_language: voice.language_codes[0],
        voice_style: voice.voice_type,
        is_custom: false,
        parameters: {
          natural_sample_rate: voice.natural_sample_rate_hertz
        }
      }))
    } catch (error) {
      console.error('Failed to get Google voices:', error)
      throw error
    }
  }

  async synthesizeText(params: VoiceSynthesisParams): Promise<VoiceSynthesisResult> {
    try {
      const response = await axiosInstance.post('/voice/platform/google/synthesize', {
        input: { text: params.text },
        voice: {
          language_code: params.timbre_id.split('-')[0] + '-' + params.timbre_id.split('-')[1],
          name: params.timbre_id
        },
        audio_config: {
          audio_encoding: params.format?.toUpperCase() || 'MP3',
          speaking_rate: params.speed || 1.0,
          pitch: (params.pitch || 1.0 - 1.0) * 20, // Google使用-20到20的范围
          volume_gain_db: ((params.volume || 1.0) - 1.0) * 16,
          sample_rate_hertz: params.sample_rate || 22050
        }
      })

      return {
        audio_url: response.data.data.audio_url,
        duration: response.data.data.duration,
        file_size: response.data.data.file_size,
        cost: response.data.data.cost,
        platform_used: this.platform_type,
        processing_time: response.data.data.processing_time
      }
    } catch (error) {
      console.error('Google synthesis failed:', error)
      throw error
    }
  }
}

// ================================
// 统一语音平台管理器
// ================================

export class VoicePlatformManager {
  private adapters: Map<VoicePlatformType, IVoicePlatformAdapter> = new Map()
  private activeAdapter: IVoicePlatformAdapter | null = null
  private fallbackChain: VoicePlatformType[] = []

  constructor() {
    // 初始化适配器（配置从环境变量或配置文件获取）
    this.initializeAdapters()
  }

  private async initializeAdapters() {
    try {
      // 获取平台配置
      const response = await axiosInstance.get('/voice/platform/configs')
      const configs = response.data.data

      configs.forEach((config: VoicePlatformConfig) => {
        if (config.enabled) {
          let adapter: IVoicePlatformAdapter

          switch (config.platform_type) {
            case 'doubao':
              adapter = new DoubaoVoiceAdapter(config)
              break
            case 'aliyun':
              adapter = new AliyunVoiceAdapter(config)
              break
            case 'google':
              adapter = new GoogleVoiceAdapter(config)
              break
            default:
              console.warn(`Unsupported platform: ${config.platform_type}`)
              return
          }

          this.adapters.set(config.platform_type, adapter)
        }
      })

      // 设置默认适配器和降级链
      this.setupFallbackChain()
    } catch (error) {
      console.error('Failed to initialize voice adapters:', error)
    }
  }

  private setupFallbackChain() {
    // 按优先级排序
    const sortedAdapters = Array.from(this.adapters.entries())
      .sort(([, a], [, b]) => a.getConfig().priority - b.getConfig().priority)

    this.fallbackChain = sortedAdapters.map(([platform]) => platform)
    
    if (this.fallbackChain.length > 0) {
      this.activeAdapter = this.adapters.get(this.fallbackChain[0])!
    }
  }

  // 获取当前活跃的适配器
  getActiveAdapter(): IVoicePlatformAdapter | null {
    return this.activeAdapter
  }

  // 获取指定平台的适配器
  getAdapter(platform: VoicePlatformType): IVoicePlatformAdapter | null {
    return this.adapters.get(platform) || null
  }

  // 切换到指定平台
  switchToPlatform(platform: VoicePlatformType): boolean {
    const adapter = this.adapters.get(platform)
    if (adapter) {
      this.activeAdapter = adapter
      return true
    }
    return false
  }

  // 获取所有可用平台
  getAvailablePlatforms(): VoicePlatformType[] {
    return Array.from(this.adapters.keys())
  }

  // 智能选择最佳平台（基于成本、响应时间等因素）
  async selectBestPlatform(criteria: {
    cost_priority?: number
    speed_priority?: number
    quality_priority?: number
  } = {}): Promise<VoicePlatformType | null> {
    try {
      const response = await axiosInstance.post('/voice/platform/recommend', criteria)
      const recommendedPlatform = response.data.data.platform_type
      
      if (this.adapters.has(recommendedPlatform)) {
        this.switchToPlatform(recommendedPlatform)
        return recommendedPlatform
      }
    } catch (error) {
      console.error('Failed to get platform recommendation:', error)
    }

    return this.fallbackChain[0] || null
  }

  // 带降级的语音合成
  async synthesizeWithFallback(params: VoiceSynthesisParams): Promise<VoiceSynthesisResult> {
    let lastError: Error | null = null

    for (const platform of this.fallbackChain) {
      const adapter = this.adapters.get(platform)
      if (!adapter) continue

      try {
        return await adapter.synthesizeText(params)
      } catch (error) {
        console.warn(`Platform ${platform} failed, trying next...`, error)
        lastError = error as Error
        continue
      }
    }

    throw lastError || new Error('All platforms failed')
  }

  // 带降级的音色克隆
  async cloneVoiceWithFallback(params: VoiceCloneParams): Promise<VoiceCloneResult> {
    let lastError: Error | null = null

    for (const platform of this.fallbackChain) {
      const adapter = this.adapters.get(platform)
      if (!adapter?.cloneVoice) continue

      try {
        return await adapter.cloneVoice(params)
      } catch (error) {
        console.warn(`Platform ${platform} clone failed, trying next...`, error)
        lastError = error as Error
        continue
      }
    }

    throw lastError || new Error('All platforms failed or do not support voice cloning')
  }
}

// 导出单例
export const voicePlatformManager = new VoicePlatformManager()
export default voicePlatformManager