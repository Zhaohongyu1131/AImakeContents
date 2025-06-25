/**
 * Voice Service Hook
 * 语音服务钩子 - [hooks][voice][useVoiceService]
 * 
 * 统一的语音服务钩子，整合所有语音相关功能
 */

import { useState, useCallback, useRef } from 'react'
import { message } from 'antd'
import { 
  voicePlatformManager,
  type VoicePlatformType,
  type VoiceTimbreInfo,
  type VoiceSynthesisParams,
  type VoiceSynthesisResult,
  type VoiceCloneParams,
  type VoiceCloneResult
} from '../../services/voice/voice_platform_adapter'

// ================================
// Hook State Types
// ================================

interface VoiceServiceState {
  // 平台状态
  currentPlatform: VoicePlatformType | null
  availablePlatforms: VoicePlatformType[]
  platformConnected: boolean
  
  // 音色状态
  availableVoices: VoiceTimbreInfo[]
  selectedVoice: VoiceTimbreInfo | null
  
  // 合成状态
  synthesizing: boolean
  lastSynthesisResult: VoiceSynthesisResult | null
  
  // 克隆状态
  cloning: boolean
  cloneProgress: number
  cloneResults: Map<string, VoiceCloneResult>
  
  // 播放状态
  playing: boolean
  currentAudio: HTMLAudioElement | null
}

interface VoiceServiceActions {
  // 平台管理
  switchPlatform: (platform: VoicePlatformType) => Promise<boolean>
  testPlatformConnection: (platform?: VoicePlatformType) => Promise<boolean>
  selectBestPlatform: (criteria?: any) => Promise<void>
  
  // 音色管理
  loadAvailableVoices: (language?: string) => Promise<void>
  selectVoice: (voice: VoiceTimbreInfo) => void
  
  // 语音合成
  synthesizeText: (text: string, params?: Partial<VoiceSynthesisParams>) => Promise<VoiceSynthesisResult>
  synthesizeWithFallback: (text: string, params?: Partial<VoiceSynthesisParams>) => Promise<VoiceSynthesisResult>
  
  // 音色克隆
  startVoiceClone: (params: VoiceCloneParams) => Promise<string>
  getCloneStatus: (cloneId: string) => Promise<VoiceCloneResult>
  
  // 音频播放
  playAudio: (audioUrl: string) => Promise<void>
  stopAudio: () => void
  
  // 批量操作
  batchSynthesize: (texts: string[], params?: Partial<VoiceSynthesisParams>) => Promise<VoiceSynthesisResult[]>
}

// ================================
// Main Hook
// ================================

export function useVoiceService(): VoiceServiceState & VoiceServiceActions {
  // State
  const [state, setState] = useState<VoiceServiceState>({
    currentPlatform: null,
    availablePlatforms: [],
    platformConnected: false,
    availableVoices: [],
    selectedVoice: null,
    synthesizing: false,
    lastSynthesisResult: null,
    cloning: false,
    cloneProgress: 0,
    cloneResults: new Map(),
    playing: false,
    currentAudio: null
  })

  const audioRef = useRef<HTMLAudioElement | null>(null)

  // ================================
  // Platform Management
  // ================================

  const switchPlatform = useCallback(async (platform: VoicePlatformType): Promise<boolean> => {
    try {
      const success = voicePlatformManager.switchToPlatform(platform)
      if (success) {
        setState(prev => ({
          ...prev,
          currentPlatform: platform,
          availableVoices: [], // 清空音色列表，需要重新加载
          selectedVoice: null
        }))
        
        // 测试新平台连接
        const connected = await testPlatformConnection(platform)
        setState(prev => ({ ...prev, platformConnected: connected }))
        
        message.success(`已切换到 ${platform} 平台`)
        return true
      }
      return false
    } catch (error) {
      console.error('Failed to switch platform:', error)
      message.error('平台切换失败')
      return false
    }
  }, [])

  const testPlatformConnection = useCallback(async (platform?: VoicePlatformType): Promise<boolean> => {
    try {
      const adapter = platform 
        ? voicePlatformManager.getAdapter(platform)
        : voicePlatformManager.getActiveAdapter()
      
      if (!adapter) {
        message.error('平台适配器不可用')
        return false
      }

      const connected = await adapter.testConnection()
      setState(prev => ({ ...prev, platformConnected: connected }))
      
      if (connected) {
        message.success('平台连接正常')
      } else {
        message.error('平台连接失败')
      }
      
      return connected
    } catch (error) {
      console.error('Platform connection test failed:', error)
      message.error('连接测试失败')
      return false
    }
  }, [])

  const selectBestPlatform = useCallback(async (criteria: any = {}) => {
    try {
      const bestPlatform = await voicePlatformManager.selectBestPlatform(criteria)
      if (bestPlatform) {
        await switchPlatform(bestPlatform)
      }
    } catch (error) {
      console.error('Failed to select best platform:', error)
      message.error('智能平台选择失败')
    }
  }, [switchPlatform])

  // ================================
  // Voice Management
  // ================================

  const loadAvailableVoices = useCallback(async (language?: string) => {
    try {
      const adapter = voicePlatformManager.getActiveAdapter()
      if (!adapter) {
        message.error('没有可用的语音平台')
        return
      }

      const voices = await adapter.getAvailableVoices(language)
      setState(prev => ({
        ...prev,
        availableVoices: voices,
        selectedVoice: voices.length > 0 ? voices[0] : null
      }))
    } catch (error) {
      console.error('Failed to load voices:', error)
      message.error('加载音色列表失败')
    }
  }, [])

  const selectVoice = useCallback((voice: VoiceTimbreInfo) => {
    setState(prev => ({ ...prev, selectedVoice: voice }))
  }, [])

  // ================================
  // Speech Synthesis
  // ================================

  const synthesizeText = useCallback(async (
    text: string, 
    params: Partial<VoiceSynthesisParams> = {}
  ): Promise<VoiceSynthesisResult> => {
    setState(prev => ({ ...prev, synthesizing: true }))
    
    try {
      const adapter = voicePlatformManager.getActiveAdapter()
      if (!adapter) {
        throw new Error('没有可用的语音平台')
      }

      if (!state.selectedVoice) {
        throw new Error('请先选择音色')
      }

      const synthesisParams: VoiceSynthesisParams = {
        text,
        timbre_id: state.selectedVoice.timbre_id,
        speed: 1.0,
        pitch: 1.0,
        volume: 1.0,
        emotion: 'neutral',
        style: 'normal',
        format: 'mp3',
        quality: 'high',
        ...params
      }

      const result = await adapter.synthesizeText(synthesisParams)
      
      setState(prev => ({ 
        ...prev, 
        synthesizing: false,
        lastSynthesisResult: result
      }))
      
      message.success('语音合成成功')
      return result
    } catch (error) {
      setState(prev => ({ ...prev, synthesizing: false }))
      console.error('Speech synthesis failed:', error)
      message.error('语音合成失败')
      throw error
    }
  }, [state.selectedVoice])

  const synthesizeWithFallback = useCallback(async (
    text: string, 
    params: Partial<VoiceSynthesisParams> = {}
  ): Promise<VoiceSynthesisResult> => {
    setState(prev => ({ ...prev, synthesizing: true }))
    
    try {
      if (!state.selectedVoice) {
        throw new Error('请先选择音色')
      }

      const synthesisParams: VoiceSynthesisParams = {
        text,
        timbre_id: state.selectedVoice.timbre_id,
        speed: 1.0,
        pitch: 1.0,
        volume: 1.0,
        emotion: 'neutral',
        style: 'normal',
        format: 'mp3',
        quality: 'high',
        ...params
      }

      const result = await voicePlatformManager.synthesizeWithFallback(synthesisParams)
      
      setState(prev => ({ 
        ...prev, 
        synthesizing: false,
        lastSynthesisResult: result
      }))
      
      message.success(`语音合成成功 (使用 ${result.platform_used} 平台)`)
      return result
    } catch (error) {
      setState(prev => ({ ...prev, synthesizing: false }))
      console.error('Speech synthesis with fallback failed:', error)
      message.error('语音合成失败：所有平台都不可用')
      throw error
    }
  }, [state.selectedVoice])

  // ================================
  // Voice Cloning
  // ================================

  const startVoiceClone = useCallback(async (params: VoiceCloneParams): Promise<string> => {
    setState(prev => ({ 
      ...prev, 
      cloning: true,
      cloneProgress: 0
    }))
    
    try {
      const result = await voicePlatformManager.cloneVoiceWithFallback(params)
      
      setState(prev => ({
        ...prev,
        cloneResults: new Map(prev.cloneResults.set(result.clone_id, result))
      }))
      
      message.success('音色克隆任务已启动')
      
      // 开始轮询状态
      pollCloneStatus(result.clone_id)
      
      return result.clone_id
    } catch (error) {
      setState(prev => ({ ...prev, cloning: false }))
      console.error('Voice clone failed:', error)
      message.error('音色克隆失败')
      throw error
    }
  }, [])

  const getCloneStatus = useCallback(async (cloneId: string): Promise<VoiceCloneResult> => {
    try {
      const adapter = voicePlatformManager.getActiveAdapter()
      if (!adapter?.getCloneStatus) {
        throw new Error('当前平台不支持音色克隆状态查询')
      }

      const result = await adapter.getCloneStatus(cloneId)
      
      setState(prev => ({
        ...prev,
        cloneResults: new Map(prev.cloneResults.set(cloneId, result)),
        cloneProgress: result.progress
      }))
      
      return result
    } catch (error) {
      console.error('Failed to get clone status:', error)
      throw error
    }
  }, [])

  const pollCloneStatus = useCallback(async (cloneId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const result = await getCloneStatus(cloneId)
        
        if (result.status === 'completed') {
          clearInterval(pollInterval)
          setState(prev => ({ ...prev, cloning: false }))
          message.success('音色克隆完成')
          
          // 重新加载音色列表
          await loadAvailableVoices()
        } else if (result.status === 'failed') {
          clearInterval(pollInterval)
          setState(prev => ({ ...prev, cloning: false }))
          message.error(`音色克隆失败: ${result.error_message}`)
        }
      } catch (error) {
        clearInterval(pollInterval)
        setState(prev => ({ ...prev, cloning: false }))
        console.error('Clone status polling failed:', error)
      }
    }, 2000)
  }, [getCloneStatus, loadAvailableVoices])

  // ================================
  // Audio Playback
  // ================================

  const playAudio = useCallback(async (audioUrl: string) => {
    try {
      // 停止当前播放
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current = null
      }

      const audio = new Audio(audioUrl)
      audioRef.current = audio

      audio.addEventListener('loadstart', () => {
        setState(prev => ({ ...prev, playing: true, currentAudio: audio }))
      })

      audio.addEventListener('ended', () => {
        setState(prev => ({ ...prev, playing: false, currentAudio: null }))
      })

      audio.addEventListener('error', (error) => {
        console.error('Audio playback error:', error)
        message.error('音频播放失败')
        setState(prev => ({ ...prev, playing: false, currentAudio: null }))
      })

      await audio.play()
    } catch (error) {
      console.error('Failed to play audio:', error)
      message.error('音频播放失败')
      setState(prev => ({ ...prev, playing: false }))
    }
  }, [])

  const stopAudio = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
    }
    setState(prev => ({ ...prev, playing: false, currentAudio: null }))
  }, [])

  // ================================
  // Batch Operations
  // ================================

  const batchSynthesize = useCallback(async (
    texts: string[],
    params: Partial<VoiceSynthesisParams> = {}
  ): Promise<VoiceSynthesisResult[]> => {
    setState(prev => ({ ...prev, synthesizing: true }))
    
    try {
      const results: VoiceSynthesisResult[] = []
      
      for (let i = 0; i < texts.length; i++) {
        const result = await synthesizeWithFallback(texts[i], params)
        results.push(result)
        
        // 更新进度（这里可以通过回调传递进度信息）
        const progress = ((i + 1) / texts.length) * 100
        console.log(`Batch synthesis progress: ${progress}%`)
      }
      
      setState(prev => ({ ...prev, synthesizing: false }))
      message.success(`批量合成完成: ${results.length} 个音频文件`)
      return results
    } catch (error) {
      setState(prev => ({ ...prev, synthesizing: false }))
      console.error('Batch synthesis failed:', error)
      message.error('批量合成失败')
      throw error
    }
  }, [synthesizeWithFallback])

  // ================================
  // Initialize
  // ================================

  // 初始化可用平台列表
  const initializePlatforms = useCallback(async () => {
    const platforms = voicePlatformManager.getAvailablePlatforms()
    const currentPlatform = voicePlatformManager.getActiveAdapter()?.platform_type || null
    
    setState(prev => ({
      ...prev,
      availablePlatforms: platforms,
      currentPlatform
    }))

    if (currentPlatform) {
      await testPlatformConnection(currentPlatform)
      await loadAvailableVoices()
    }
  }, [testPlatformConnection, loadAvailableVoices])

  // 组件挂载时初始化
  React.useEffect(() => {
    initializePlatforms()
  }, [initializePlatforms])

  return {
    // State
    ...state,
    
    // Actions
    switchPlatform,
    testPlatformConnection,
    selectBestPlatform,
    loadAvailableVoices,
    selectVoice,
    synthesizeText,
    synthesizeWithFallback,
    startVoiceClone,
    getCloneStatus,
    playAudio,
    stopAudio,
    batchSynthesize
  }
}

export default useVoiceService