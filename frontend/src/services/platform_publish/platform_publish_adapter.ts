/**
 * Platform Publish Adapter
 * 平台发布适配器 - [services][platform_publish][adapter]
 * 
 * 统一的社交媒体发布平台适配器，支持抖音、微信、小红书、B站等平台
 */

import { axiosInstance } from '../axios/axios_instance'

// ================================
// 平台类型和基础接口定义
// ================================

export type PlatformPublishType = 'douyin' | 'wechat' | 'xiaohongshu' | 'bilibili' | 'weibo' | 'kuaishou'

export interface PlatformPublishConfig {
  platform_type: PlatformPublishType
  app_id: string
  app_secret: string
  access_token?: string
  refresh_token?: string
  oauth_callback_url: string
  enabled: boolean
  priority: number
  rate_limit?: number
  daily_quota?: number
}

export interface PublishContentInfo {
  content_id: string
  title: string
  description: string
  tags: string[]
  cover_image_url?: string
  video_url?: string
  audio_url?: string
  images: string[]
  content_type: 'video' | 'image' | 'audio' | 'text' | 'article'
  duration?: number
  file_size?: number
  format?: string
  quality?: string
}

export interface PublishScheduleInfo {
  schedule_type: 'immediate' | 'scheduled' | 'draft'
  publish_time?: string
  timezone?: string
  auto_republish?: boolean
  republish_interval?: number
}

export interface PlatformSpecificParams {
  // 抖音特定参数
  douyin?: {
    poi_id?: string
    allow_comment?: boolean
    allow_duet?: boolean
    allow_stitch?: boolean
    privacy_level?: 'public' | 'friends' | 'private'
    brand_content?: boolean
  }
  
  // 微信公众号特定参数
  wechat?: {
    article_type?: 'normal' | 'video' | 'voice'
    original?: boolean
    comment_enabled?: boolean
    redirect_url?: string
    thumb_media_id?: string
  }
  
  // 小红书特定参数
  xiaohongshu?: {
    poi_name?: string
    topic_ids?: string[]
    collaboration_users?: string[]
    brand_info?: {
      brand_name: string
      brand_id: string
    }
  }
  
  // B站特定参数
  bilibili?: {
    copyright?: 1 | 2  // 1原创 2转载
    source?: string
    tid?: number  // 分区ID
    tag?: string
    no_reprint?: 0 | 1
    subtitle?: {
      open: 0 | 1
      lan?: string
    }
  }
}

export interface PublishParams {
  content: PublishContentInfo
  schedule: PublishScheduleInfo
  platform_params: PlatformSpecificParams
  target_platforms: PlatformPublishType[]
}

export interface PublishResult {
  platform_type: PlatformPublishType
  success: boolean
  post_id?: string
  post_url?: string
  error_message?: string
  error_code?: string
  published_at?: string
  status: 'published' | 'pending' | 'failed' | 'draft'
  engagement?: {
    views?: number
    likes?: number
    comments?: number
    shares?: number
  }
}

export interface PublishTaskStatus {
  task_id: string
  content_id: string
  platform_type: PlatformPublishType
  status: 'pending' | 'processing' | 'published' | 'failed' | 'cancelled'
  progress: number
  created_at: string
  updated_at: string
  published_at?: string
  result?: PublishResult
  error_message?: string
  retry_count: number
  max_retries: number
}

// ================================
// 平台适配器接口
// ================================

export interface IPlatformPublishAdapter {
  platform_type: PlatformPublishType
  
  // 基础功能
  testConnection(): Promise<boolean>
  getAuthUrl(): Promise<string>
  exchangeToken(auth_code: string): Promise<{ access_token: string; refresh_token: string }>
  refreshToken(refresh_token: string): Promise<{ access_token: string; refresh_token: string }>
  
  // 内容发布
  publishContent(params: PublishParams): Promise<PublishResult>
  scheduleContent(params: PublishParams): Promise<{ task_id: string }>
  cancelScheduledContent(task_id: string): Promise<boolean>
  
  // 状态管理
  getPublishStatus(post_id: string): Promise<PublishTaskStatus>
  getContentEngagement(post_id: string): Promise<PublishResult['engagement']>
  
  // 内容管理
  updateContent(post_id: string, updates: Partial<PublishContentInfo>): Promise<boolean>
  deleteContent(post_id: string): Promise<boolean>
  
  // 平台特定配置
  configure(config: PlatformPublishConfig): void
  getConfig(): PlatformPublishConfig
  
  // 内容验证
  validateContent(content: PublishContentInfo): Promise<{ valid: boolean; errors: string[] }>
}

// ================================
// 抖音平台适配器
// ================================

export class DouyinPublishAdapter implements IPlatformPublishAdapter {
  platform_type: PlatformPublishType = 'douyin'
  private config: PlatformPublishConfig

  constructor(config: PlatformPublishConfig) {
    this.config = config
  }

  configure(config: PlatformPublishConfig): void {
    this.config = { ...this.config, ...config }
  }

  getConfig(): PlatformPublishConfig {
    return this.config
  }

  async testConnection(): Promise<boolean> {
    try {
      const response = await axiosInstance.get('/platform/douyin/health', {
        headers: { 'Authorization': `Bearer ${this.config.access_token}` }
      })
      return response.data.success
    } catch (error) {
      console.error('Douyin connection test failed:', error)
      return false
    }
  }

  async getAuthUrl(): Promise<string> {
    const params = new URLSearchParams({
      client_key: this.config.app_id,
      response_type: 'code',
      scope: 'video.create,video.data,user_info',
      redirect_uri: this.config.oauth_callback_url,
      state: 'douyin_auth'
    })
    
    return `https://open.douyin.com/platform/oauth/connect/?${params.toString()}`
  }

  async exchangeToken(auth_code: string): Promise<{ access_token: string; refresh_token: string }> {
    try {
      const response = await axiosInstance.post('/platform/douyin/oauth/token', {
        client_key: this.config.app_id,
        client_secret: this.config.app_secret,
        code: auth_code,
        grant_type: 'authorization_code'
      })
      
      return {
        access_token: response.data.data.access_token,
        refresh_token: response.data.data.refresh_token
      }
    } catch (error) {
      console.error('Douyin token exchange failed:', error)
      throw error
    }
  }

  async refreshToken(refresh_token: string): Promise<{ access_token: string; refresh_token: string }> {
    try {
      const response = await axiosInstance.post('/platform/douyin/oauth/refresh_token', {
        client_key: this.config.app_id,
        refresh_token: refresh_token,
        grant_type: 'refresh_token'
      })
      
      return {
        access_token: response.data.data.access_token,
        refresh_token: response.data.data.refresh_token
      }
    } catch (error) {
      console.error('Douyin token refresh failed:', error)
      throw error
    }
  }

  async publishContent(params: PublishParams): Promise<PublishResult> {
    try {
      const publishData = {
        video_url: params.content.video_url,
        text: params.content.description,
        poi_id: params.platform_params.douyin?.poi_id,
        micro_app_info: null,
        allow_comment: params.platform_params.douyin?.allow_comment ?? true,
        allow_duet: params.platform_params.douyin?.allow_duet ?? true,
        allow_stitch: params.platform_params.douyin?.allow_stitch ?? true,
        privacy_level: params.platform_params.douyin?.privacy_level || 'public'
      }

      const response = await axiosInstance.post('/platform/douyin/video/create', publishData, {
        headers: { 'Authorization': `Bearer ${this.config.access_token}` }
      })

      return {
        platform_type: this.platform_type,
        success: true,
        post_id: response.data.data.item_id,
        post_url: `https://www.douyin.com/video/${response.data.data.item_id}`,
        published_at: new Date().toISOString(),
        status: 'published'
      }
    } catch (error) {
      console.error('Douyin publish failed:', error)
      return {
        platform_type: this.platform_type,
        success: false,
        error_message: error instanceof Error ? error.message : '发布失败',
        status: 'failed'
      }
    }
  }

  async scheduleContent(params: PublishParams): Promise<{ task_id: string }> {
    try {
      const response = await axiosInstance.post('/platform/douyin/video/schedule', {
        content: params.content,
        schedule_time: params.schedule.publish_time,
        platform_params: params.platform_params.douyin
      })
      
      return { task_id: response.data.data.task_id }
    } catch (error) {
      console.error('Douyin schedule failed:', error)
      throw error
    }
  }

  async cancelScheduledContent(task_id: string): Promise<boolean> {
    try {
      await axiosInstance.delete(`/platform/douyin/video/schedule/${task_id}`)
      return true
    } catch (error) {
      console.error('Douyin cancel schedule failed:', error)
      return false
    }
  }

  async getPublishStatus(post_id: string): Promise<PublishTaskStatus> {
    try {
      const response = await axiosInstance.get(`/platform/douyin/video/status/${post_id}`)
      return response.data.data
    } catch (error) {
      console.error('Failed to get Douyin publish status:', error)
      throw error
    }
  }

  async getContentEngagement(post_id: string): Promise<PublishResult['engagement']> {
    try {
      const response = await axiosInstance.get(`/platform/douyin/video/data/${post_id}`)
      return {
        views: response.data.data.play_count,
        likes: response.data.data.digg_count,
        comments: response.data.data.comment_count,
        shares: response.data.data.share_count
      }
    } catch (error) {
      console.error('Failed to get Douyin engagement:', error)
      return {}
    }
  }

  async updateContent(post_id: string, updates: Partial<PublishContentInfo>): Promise<boolean> {
    try {
      await axiosInstance.put(`/platform/douyin/video/${post_id}`, updates)
      return true
    } catch (error) {
      console.error('Douyin content update failed:', error)
      return false
    }
  }

  async deleteContent(post_id: string): Promise<boolean> {
    try {
      await axiosInstance.delete(`/platform/douyin/video/${post_id}`)
      return true
    } catch (error) {
      console.error('Douyin content deletion failed:', error)
      return false
    }
  }

  async validateContent(content: PublishContentInfo): Promise<{ valid: boolean; errors: string[] }> {
    const errors: string[] = []
    
    if (!content.video_url) {
      errors.push('视频文件是必需的')
    }
    
    if (!content.description || content.description.length < 1) {
      errors.push('视频描述不能为空')
    }
    
    if (content.description && content.description.length > 2200) {
      errors.push('视频描述不能超过2200个字符')
    }
    
    if (content.duration && (content.duration < 1 || content.duration > 900)) {
      errors.push('视频时长必须在1秒到15分钟之间')
    }
    
    return {
      valid: errors.length === 0,
      errors
    }
  }
}

// ================================
// 微信公众号平台适配器
// ================================

export class WechatPublishAdapter implements IPlatformPublishAdapter {
  platform_type: PlatformPublishType = 'wechat'
  private config: PlatformPublishConfig

  constructor(config: PlatformPublishConfig) {
    this.config = config
  }

  configure(config: PlatformPublishConfig): void {
    this.config = { ...this.config, ...config }
  }

  getConfig(): PlatformPublishConfig {
    return this.config
  }

  async testConnection(): Promise<boolean> {
    try {
      const response = await axiosInstance.get('/platform/wechat/health')
      return response.data.success
    } catch (error) {
      console.error('Wechat connection test failed:', error)
      return false
    }
  }

  async getAuthUrl(): Promise<string> {
    const params = new URLSearchParams({
      appid: this.config.app_id,
      redirect_uri: this.config.oauth_callback_url,
      response_type: 'code',
      scope: 'snsapi_base',
      state: 'wechat_auth'
    })
    
    return `https://open.weixin.qq.com/connect/oauth2/authorize?${params.toString()}#wechat_redirect`
  }

  async exchangeToken(auth_code: string): Promise<{ access_token: string; refresh_token: string }> {
    try {
      const response = await axiosInstance.post('/platform/wechat/oauth/token', {
        appid: this.config.app_id,
        secret: this.config.app_secret,
        code: auth_code,
        grant_type: 'authorization_code'
      })
      
      return {
        access_token: response.data.access_token,
        refresh_token: response.data.refresh_token || ''
      }
    } catch (error) {
      console.error('Wechat token exchange failed:', error)
      throw error
    }
  }

  async refreshToken(refresh_token: string): Promise<{ access_token: string; refresh_token: string }> {
    try {
      const response = await axiosInstance.post('/platform/wechat/oauth/refresh_token', {
        appid: this.config.app_id,
        refresh_token: refresh_token,
        grant_type: 'refresh_token'
      })
      
      return {
        access_token: response.data.access_token,
        refresh_token: response.data.refresh_token
      }
    } catch (error) {
      console.error('Wechat token refresh failed:', error)
      throw error
    }
  }

  async publishContent(params: PublishParams): Promise<PublishResult> {
    try {
      const articleData = {
        title: params.content.title,
        author: '智能内容创作平台',
        digest: params.content.description,
        content: this.formatWechatContent(params.content),
        content_source_url: params.platform_params.wechat?.redirect_url || '',
        thumb_media_id: params.platform_params.wechat?.thumb_media_id,
        show_cover_pic: 1,
        need_open_comment: params.platform_params.wechat?.comment_enabled ? 1 : 0,
        only_fans_can_comment: 0
      }

      const response = await axiosInstance.post('/platform/wechat/draft/add', {
        articles: [articleData]
      })

      // 如果是立即发布，则发布草稿
      if (params.schedule.schedule_type === 'immediate') {
        const publishResponse = await axiosInstance.post('/platform/wechat/freepublish/submit', {
          media_id: response.data.media_id
        })
        
        return {
          platform_type: this.platform_type,
          success: true,
          post_id: publishResponse.data.publish_id,
          post_url: publishResponse.data.url,
          published_at: new Date().toISOString(),
          status: 'published'
        }
      } else {
        return {
          platform_type: this.platform_type,
          success: true,
          post_id: response.data.media_id,
          status: 'draft'
        }
      }
    } catch (error) {
      console.error('Wechat publish failed:', error)
      return {
        platform_type: this.platform_type,
        success: false,
        error_message: error instanceof Error ? error.message : '发布失败',
        status: 'failed'
      }
    }
  }

  private formatWechatContent(content: PublishContentInfo): string {
    let formattedContent = `<p>${content.description}</p>`
    
    if (content.images.length > 0) {
      content.images.forEach(imageUrl => {
        formattedContent += `<p><img src="${imageUrl}" alt="内容图片" /></p>`
      })
    }
    
    if (content.video_url) {
      formattedContent += `<p><video src="${content.video_url}" controls></video></p>`
    }
    
    return formattedContent
  }

  async scheduleContent(params: PublishParams): Promise<{ task_id: string }> {
    try {
      const response = await axiosInstance.post('/platform/wechat/schedule', {
        content: params.content,
        schedule_time: params.schedule.publish_time,
        platform_params: params.platform_params.wechat
      })
      
      return { task_id: response.data.task_id }
    } catch (error) {
      console.error('Wechat schedule failed:', error)
      throw error
    }
  }

  async cancelScheduledContent(task_id: string): Promise<boolean> {
    try {
      await axiosInstance.delete(`/platform/wechat/schedule/${task_id}`)
      return true
    } catch (error) {
      console.error('Wechat cancel schedule failed:', error)
      return false
    }
  }

  async getPublishStatus(post_id: string): Promise<PublishTaskStatus> {
    try {
      const response = await axiosInstance.get(`/platform/wechat/publish/status/${post_id}`)
      return response.data.data
    } catch (error) {
      console.error('Failed to get Wechat publish status:', error)
      throw error
    }
  }

  async getContentEngagement(post_id: string): Promise<PublishResult['engagement']> {
    try {
      const response = await axiosInstance.get(`/platform/wechat/article/data/${post_id}`)
      return {
        views: response.data.data.read_num,
        likes: response.data.data.like_num,
        comments: response.data.data.comment_num,
        shares: response.data.data.share_num
      }
    } catch (error) {
      console.error('Failed to get Wechat engagement:', error)
      return {}
    }
  }

  async updateContent(post_id: string, updates: Partial<PublishContentInfo>): Promise<boolean> {
    try {
      await axiosInstance.put(`/platform/wechat/article/${post_id}`, updates)
      return true
    } catch (error) {
      console.error('Wechat content update failed:', error)
      return false
    }
  }

  async deleteContent(post_id: string): Promise<boolean> {
    try {
      await axiosInstance.delete(`/platform/wechat/article/${post_id}`)
      return true
    } catch (error) {
      console.error('Wechat content deletion failed:', error)
      return false
    }
  }

  async validateContent(content: PublishContentInfo): Promise<{ valid: boolean; errors: string[] }> {
    const errors: string[] = []
    
    if (!content.title || content.title.length < 1) {
      errors.push('文章标题不能为空')
    }
    
    if (content.title && content.title.length > 64) {
      errors.push('文章标题不能超过64个字符')
    }
    
    if (!content.description) {
      errors.push('文章内容不能为空')
    }
    
    if (!content.cover_image_url) {
      errors.push('文章封面图片是必需的')
    }
    
    return {
      valid: errors.length === 0,
      errors
    }
  }
}

// ================================
// 统一平台发布管理器
// ================================

export class PlatformPublishManager {
  private adapters: Map<PlatformPublishType, IPlatformPublishAdapter> = new Map()
  private activeAdapters: Set<PlatformPublishType> = new Set()

  constructor() {
    this.initializeAdapters()
  }

  private async initializeAdapters() {
    try {
      // 获取平台配置
      const response = await axiosInstance.get('/platform/publish/configs')
      const configs = response.data.data

      configs.forEach((config: PlatformPublishConfig) => {
        if (config.enabled) {
          let adapter: IPlatformPublishAdapter

          switch (config.platform_type) {
            case 'douyin':
              adapter = new DouyinPublishAdapter(config)
              break
            case 'wechat':
              adapter = new WechatPublishAdapter(config)
              break
            // 其他平台适配器可以在这里添加
            default:
              console.warn(`Unsupported platform: ${config.platform_type}`)
              return
          }

          this.adapters.set(config.platform_type, adapter)
          this.activeAdapters.add(config.platform_type)
        }
      })
    } catch (error) {
      console.error('Failed to initialize publish adapters:', error)
    }
  }

  // 获取指定平台的适配器
  getAdapter(platform: PlatformPublishType): IPlatformPublishAdapter | null {
    return this.adapters.get(platform) || null
  }

  // 获取所有可用平台
  getAvailablePlatforms(): PlatformPublishType[] {
    return Array.from(this.activeAdapters)
  }

  // 多平台同时发布
  async publishToMultiplePlatforms(params: PublishParams): Promise<PublishResult[]> {
    const results: PublishResult[] = []
    
    for (const platform of params.target_platforms) {
      const adapter = this.getAdapter(platform)
      if (adapter) {
        try {
          const result = await adapter.publishContent(params)
          results.push(result)
        } catch (error) {
          console.error(`Failed to publish to ${platform}:`, error)
          results.push({
            platform_type: platform,
            success: false,
            error_message: error instanceof Error ? error.message : '发布失败',
            status: 'failed'
          })
        }
      }
    }
    
    return results
  }

  // 验证内容是否适合所有目标平台
  async validateContentForPlatforms(
    content: PublishContentInfo, 
    platforms: PlatformPublishType[]
  ): Promise<Record<PlatformPublishType, { valid: boolean; errors: string[] }>> {
    const validationResults: Record<string, { valid: boolean; errors: string[] }> = {}
    
    for (const platform of platforms) {
      const adapter = this.getAdapter(platform)
      if (adapter) {
        validationResults[platform] = await adapter.validateContent(content)
      }
    }
    
    return validationResults
  }

  // 批量获取发布状态
  async getBatchPublishStatus(tasks: Array<{ platform: PlatformPublishType; post_id: string }>): Promise<PublishTaskStatus[]> {
    const statusPromises = tasks.map(async task => {
      const adapter = this.getAdapter(task.platform)
      if (adapter) {
        try {
          return await adapter.getPublishStatus(task.post_id)
        } catch (error) {
          console.error(`Failed to get status for ${task.platform}:${task.post_id}`, error)
          return null
        }
      }
      return null
    })
    
    const results = await Promise.all(statusPromises)
    return results.filter(result => result !== null) as PublishTaskStatus[]
  }
}

// 导出单例
export const platformPublishManager = new PlatformPublishManager()
export default platformPublishManager