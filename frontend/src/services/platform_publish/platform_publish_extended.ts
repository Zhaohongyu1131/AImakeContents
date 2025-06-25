/**
 * Platform Publish Extended Adapters
 * 平台发布扩展适配器 - [services][platform_publish][extended]
 * 
 * 扩展平台适配器：小红书、B站、微博、快手等
 */

import { axiosInstance } from '../axios/axios_instance'
import {
  IPlatformPublishAdapter,
  PlatformPublishConfig,
  PlatformPublishType,
  PublishParams,
  PublishResult,
  PublishTaskStatus,
  PublishContentInfo
} from './platform_publish_adapter'

// ================================
// 小红书平台适配器
// ================================

export class XiaohongshuPublishAdapter implements IPlatformPublishAdapter {
  platform_type: PlatformPublishType = 'xiaohongshu'
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
      const response = await axiosInstance.get('/platform/xiaohongshu/health', {
        headers: { 'Authorization': `Bearer ${this.config.access_token}` }
      })
      return response.data.success
    } catch (error) {
      console.error('Xiaohongshu connection test failed:', error)
      return false
    }
  }

  async getAuthUrl(): Promise<string> {
    const params = new URLSearchParams({
      client_id: this.config.app_id,
      response_type: 'code',
      scope: 'feeds_write,user_info',
      redirect_uri: this.config.oauth_callback_url,
      state: 'xiaohongshu_auth'
    })
    
    return `https://open.xiaohongshu.com/oauth2/authorize?${params.toString()}`
  }

  async exchangeToken(auth_code: string): Promise<{ access_token: string; refresh_token: string }> {
    try {
      const response = await axiosInstance.post('/platform/xiaohongshu/oauth/token', {
        client_id: this.config.app_id,
        client_secret: this.config.app_secret,
        code: auth_code,
        grant_type: 'authorization_code',
        redirect_uri: this.config.oauth_callback_url
      })
      
      return {
        access_token: response.data.access_token,
        refresh_token: response.data.refresh_token
      }
    } catch (error) {
      console.error('Xiaohongshu token exchange failed:', error)
      throw error
    }
  }

  async refreshToken(refresh_token: string): Promise<{ access_token: string; refresh_token: string }> {
    try {
      const response = await axiosInstance.post('/platform/xiaohongshu/oauth/refresh_token', {
        client_id: this.config.app_id,
        client_secret: this.config.app_secret,
        refresh_token: refresh_token,
        grant_type: 'refresh_token'
      })
      
      return {
        access_token: response.data.access_token,
        refresh_token: response.data.refresh_token
      }
    } catch (error) {
      console.error('Xiaohongshu token refresh failed:', error)
      throw error
    }
  }

  async publishContent(params: PublishParams): Promise<PublishResult> {
    try {
      let publishData: any

      if (params.content.content_type === 'image') {
        // 图文笔记
        publishData = {
          type: 'image',
          title: params.content.title,
          desc: params.content.description,
          images: params.content.images,
          poi_name: params.platform_params.xiaohongshu?.poi_name,
          topic_ids: params.platform_params.xiaohongshu?.topic_ids || [],
          collaboration_users: params.platform_params.xiaohongshu?.collaboration_users || []
        }
      } else if (params.content.content_type === 'video') {
        // 视频笔记
        publishData = {
          type: 'video',
          title: params.content.title,
          desc: params.content.description,
          video_url: params.content.video_url,
          cover_image: params.content.cover_image_url,
          poi_name: params.platform_params.xiaohongshu?.poi_name,
          topic_ids: params.platform_params.xiaohongshu?.topic_ids || []
        }
      }

      const response = await axiosInstance.post('/platform/xiaohongshu/feeds/create', publishData, {
        headers: { 'Authorization': `Bearer ${this.config.access_token}` }
      })

      return {
        platform_type: this.platform_type,
        success: true,
        post_id: response.data.data.note_id,
        post_url: `https://www.xiaohongshu.com/explore/${response.data.data.note_id}`,
        published_at: new Date().toISOString(),
        status: 'published'
      }
    } catch (error) {
      console.error('Xiaohongshu publish failed:', error)
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
      const response = await axiosInstance.post('/platform/xiaohongshu/schedule', {
        content: params.content,
        schedule_time: params.schedule.publish_time,
        platform_params: params.platform_params.xiaohongshu
      })
      
      return { task_id: response.data.task_id }
    } catch (error) {
      console.error('Xiaohongshu schedule failed:', error)
      throw error
    }
  }

  async cancelScheduledContent(task_id: string): Promise<boolean> {
    try {
      await axiosInstance.delete(`/platform/xiaohongshu/schedule/${task_id}`)
      return true
    } catch (error) {
      console.error('Xiaohongshu cancel schedule failed:', error)
      return false
    }
  }

  async getPublishStatus(post_id: string): Promise<PublishTaskStatus> {
    try {
      const response = await axiosInstance.get(`/platform/xiaohongshu/feeds/status/${post_id}`)
      return response.data.data
    } catch (error) {
      console.error('Failed to get Xiaohongshu publish status:', error)
      throw error
    }
  }

  async getContentEngagement(post_id: string): Promise<PublishResult['engagement']> {
    try {
      const response = await axiosInstance.get(`/platform/xiaohongshu/feeds/data/${post_id}`)
      return {
        views: response.data.data.view_count,
        likes: response.data.data.like_count,
        comments: response.data.data.comment_count,
        shares: response.data.data.share_count
      }
    } catch (error) {
      console.error('Failed to get Xiaohongshu engagement:', error)
      return {}
    }
  }

  async updateContent(post_id: string, updates: Partial<PublishContentInfo>): Promise<boolean> {
    try {
      await axiosInstance.put(`/platform/xiaohongshu/feeds/${post_id}`, updates)
      return true
    } catch (error) {
      console.error('Xiaohongshu content update failed:', error)
      return false
    }
  }

  async deleteContent(post_id: string): Promise<boolean> {
    try {
      await axiosInstance.delete(`/platform/xiaohongshu/feeds/${post_id}`)
      return true
    } catch (error) {
      console.error('Xiaohongshu content deletion failed:', error)
      return false
    }
  }

  async validateContent(content: PublishContentInfo): Promise<{ valid: boolean; errors: string[] }> {
    const errors: string[] = []
    
    if (!content.title || content.title.length < 1) {
      errors.push('笔记标题不能为空')
    }
    
    if (content.title && content.title.length > 100) {
      errors.push('笔记标题不能超过100个字符')
    }
    
    if (!content.description) {
      errors.push('笔记内容不能为空')
    }
    
    if (content.description && content.description.length > 1000) {
      errors.push('笔记内容不能超过1000个字符')
    }
    
    if (content.content_type === 'image' && content.images.length === 0) {
      errors.push('图文笔记至少需要一张图片')
    }
    
    if (content.content_type === 'image' && content.images.length > 9) {
      errors.push('图文笔记最多支持9张图片')
    }
    
    if (content.content_type === 'video' && !content.video_url) {
      errors.push('视频笔记需要上传视频文件')
    }
    
    return {
      valid: errors.length === 0,
      errors
    }
  }
}

// ================================
// B站平台适配器
// ================================

export class BilibiliPublishAdapter implements IPlatformPublishAdapter {
  platform_type: PlatformPublishType = 'bilibili'
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
      const response = await axiosInstance.get('/platform/bilibili/health', {
        headers: { 'Authorization': `Bearer ${this.config.access_token}` }
      })
      return response.data.success
    } catch (error) {
      console.error('Bilibili connection test failed:', error)
      return false
    }
  }

  async getAuthUrl(): Promise<string> {
    const params = new URLSearchParams({
      client_id: this.config.app_id,
      response_type: 'code',
      scope: 'video:upload,user:info',
      redirect_uri: this.config.oauth_callback_url,
      state: 'bilibili_auth'
    })
    
    return `https://passport.bilibili.com/oauth2/authorize?${params.toString()}`
  }

  async exchangeToken(auth_code: string): Promise<{ access_token: string; refresh_token: string }> {
    try {
      const response = await axiosInstance.post('/platform/bilibili/oauth/token', {
        client_id: this.config.app_id,
        client_secret: this.config.app_secret,
        code: auth_code,
        grant_type: 'authorization_code',
        redirect_uri: this.config.oauth_callback_url
      })
      
      return {
        access_token: response.data.access_token,
        refresh_token: response.data.refresh_token
      }
    } catch (error) {
      console.error('Bilibili token exchange failed:', error)
      throw error
    }
  }

  async refreshToken(refresh_token: string): Promise<{ access_token: string; refresh_token: string }> {
    try {
      const response = await axiosInstance.post('/platform/bilibili/oauth/refresh_token', {
        client_id: this.config.app_id,
        client_secret: this.config.app_secret,
        refresh_token: refresh_token,
        grant_type: 'refresh_token'
      })
      
      return {
        access_token: response.data.access_token,
        refresh_token: response.data.refresh_token
      }
    } catch (error) {
      console.error('Bilibili token refresh failed:', error)
      throw error
    }
  }

  async publishContent(params: PublishParams): Promise<PublishResult> {
    try {
      // B站视频投稿需要先上传视频，再提交投稿信息
      const uploadResponse = await this.uploadVideo(params.content.video_url!)
      
      const submitData = {
        cover: params.content.cover_image_url,
        title: params.content.title,
        copyright: params.platform_params.bilibili?.copyright || 1,
        tid: params.platform_params.bilibili?.tid || 21, // 默认日常分区
        tag: params.content.tags.join(','),
        desc: params.content.description,
        source: params.platform_params.bilibili?.source || '',
        no_reprint: params.platform_params.bilibili?.no_reprint || 0,
        videos: [{
          filename: uploadResponse.filename,
          title: params.content.title,
          desc: params.content.description
        }]
      }

      const response = await axiosInstance.post('/platform/bilibili/video/submit', submitData, {
        headers: { 'Authorization': `Bearer ${this.config.access_token}` }
      })

      return {
        platform_type: this.platform_type,
        success: true,
        post_id: response.data.data.aid.toString(),
        post_url: `https://www.bilibili.com/video/av${response.data.data.aid}`,
        published_at: new Date().toISOString(),
        status: 'published'
      }
    } catch (error) {
      console.error('Bilibili publish failed:', error)
      return {
        platform_type: this.platform_type,
        success: false,
        error_message: error instanceof Error ? error.message : '发布失败',
        status: 'failed'
      }
    }
  }

  private async uploadVideo(videoUrl: string): Promise<{ filename: string }> {
    try {
      const response = await axiosInstance.post('/platform/bilibili/video/upload', {
        video_url: videoUrl
      })
      
      return { filename: response.data.data.filename }
    } catch (error) {
      console.error('Bilibili video upload failed:', error)
      throw error
    }
  }

  async scheduleContent(params: PublishParams): Promise<{ task_id: string }> {
    try {
      const response = await axiosInstance.post('/platform/bilibili/schedule', {
        content: params.content,
        schedule_time: params.schedule.publish_time,
        platform_params: params.platform_params.bilibili
      })
      
      return { task_id: response.data.task_id }
    } catch (error) {
      console.error('Bilibili schedule failed:', error)
      throw error
    }
  }

  async cancelScheduledContent(task_id: string): Promise<boolean> {
    try {
      await axiosInstance.delete(`/platform/bilibili/schedule/${task_id}`)
      return true
    } catch (error) {
      console.error('Bilibili cancel schedule failed:', error)
      return false
    }
  }

  async getPublishStatus(post_id: string): Promise<PublishTaskStatus> {
    try {
      const response = await axiosInstance.get(`/platform/bilibili/video/status/${post_id}`)
      return response.data.data
    } catch (error) {
      console.error('Failed to get Bilibili publish status:', error)
      throw error
    }
  }

  async getContentEngagement(post_id: string): Promise<PublishResult['engagement']> {
    try {
      const response = await axiosInstance.get(`/platform/bilibili/video/stat/${post_id}`)
      return {
        views: response.data.data.view,
        likes: response.data.data.like,
        comments: response.data.data.reply,
        shares: response.data.data.share
      }
    } catch (error) {
      console.error('Failed to get Bilibili engagement:', error)
      return {}
    }
  }

  async updateContent(post_id: string, updates: Partial<PublishContentInfo>): Promise<boolean> {
    try {
      await axiosInstance.put(`/platform/bilibili/video/${post_id}`, updates)
      return true
    } catch (error) {
      console.error('Bilibili content update failed:', error)
      return false
    }
  }

  async deleteContent(post_id: string): Promise<boolean> {
    try {
      await axiosInstance.delete(`/platform/bilibili/video/${post_id}`)
      return true
    } catch (error) {
      console.error('Bilibili content deletion failed:', error)
      return false
    }
  }

  async validateContent(content: PublishContentInfo): Promise<{ valid: boolean; errors: string[] }> {
    const errors: string[] = []
    
    if (!content.title || content.title.length < 1) {
      errors.push('视频标题不能为空')
    }
    
    if (content.title && content.title.length > 80) {
      errors.push('视频标题不能超过80个字符')
    }
    
    if (!content.video_url) {
      errors.push('视频文件是必需的')
    }
    
    if (!content.cover_image_url) {
      errors.push('视频封面是必需的')
    }
    
    if (!content.description) {
      errors.push('视频简介不能为空')
    }
    
    if (content.description && content.description.length > 2000) {
      errors.push('视频简介不能超过2000个字符')
    }
    
    if (content.tags.length === 0) {
      errors.push('至少需要添加一个标签')
    }
    
    if (content.tags.length > 10) {
      errors.push('标签数量不能超过10个')
    }
    
    if (content.duration && content.duration > 7200) {
      errors.push('视频时长不能超过2小时')
    }
    
    return {
      valid: errors.length === 0,
      errors
    }
  }
}

// ================================
// 微博平台适配器
// ================================

export class WeiboPublishAdapter implements IPlatformPublishAdapter {
  platform_type: PlatformPublishType = 'weibo'
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
      const response = await axiosInstance.get('/platform/weibo/health', {
        headers: { 'Authorization': `Bearer ${this.config.access_token}` }
      })
      return response.data.success
    } catch (error) {
      console.error('Weibo connection test failed:', error)
      return false
    }
  }

  async getAuthUrl(): Promise<string> {
    const params = new URLSearchParams({
      client_id: this.config.app_id,
      response_type: 'code',
      scope: 'email,direct_messages_read,direct_messages_write,friendships_groups_read,friendships_groups_write,statuses_to_me_read,follow_app_official_microblog,invitation_write',
      redirect_uri: this.config.oauth_callback_url,
      state: 'weibo_auth'
    })
    
    return `https://api.weibo.com/oauth2/authorize?${params.toString()}`
  }

  async exchangeToken(auth_code: string): Promise<{ access_token: string; refresh_token: string }> {
    try {
      const response = await axiosInstance.post('/platform/weibo/oauth/token', {
        client_id: this.config.app_id,
        client_secret: this.config.app_secret,
        code: auth_code,
        grant_type: 'authorization_code',
        redirect_uri: this.config.oauth_callback_url
      })
      
      return {
        access_token: response.data.access_token,
        refresh_token: response.data.refresh_token || ''
      }
    } catch (error) {
      console.error('Weibo token exchange failed:', error)
      throw error
    }
  }

  async refreshToken(refresh_token: string): Promise<{ access_token: string; refresh_token: string }> {
    // 微博的access_token有效期很长，通常不需要刷新
    throw new Error('Weibo does not support token refresh')
  }

  async publishContent(params: PublishParams): Promise<PublishResult> {
    try {
      let publishData: any = {
        status: `${params.content.title}\n${params.content.description}`,
        visible: 0 // 0-所有人可见
      }

      // 如果有图片，先上传图片
      if (params.content.images.length > 0) {
        const picIds: string[] = []
        for (const imageUrl of params.content.images.slice(0, 9)) { // 微博最多9张图
          const uploadResponse = await this.uploadImage(imageUrl)
          picIds.push(uploadResponse.pic_id)
        }
        publishData.pic_id = picIds.join(',')
      }

      const response = await axiosInstance.post('/platform/weibo/statuses/update', publishData, {
        headers: { 'Authorization': `Bearer ${this.config.access_token}` }
      })

      return {
        platform_type: this.platform_type,
        success: true,
        post_id: response.data.data.id.toString(),
        post_url: `https://weibo.com/${response.data.data.user.id}/${response.data.data.bid}`,
        published_at: new Date().toISOString(),
        status: 'published'
      }
    } catch (error) {
      console.error('Weibo publish failed:', error)
      return {
        platform_type: this.platform_type,
        success: false,
        error_message: error instanceof Error ? error.message : '发布失败',
        status: 'failed'
      }
    }
  }

  private async uploadImage(imageUrl: string): Promise<{ pic_id: string }> {
    try {
      const response = await axiosInstance.post('/platform/weibo/upload/pic', {
        image_url: imageUrl
      })
      
      return { pic_id: response.data.data.pic_id }
    } catch (error) {
      console.error('Weibo image upload failed:', error)
      throw error
    }
  }

  async scheduleContent(params: PublishParams): Promise<{ task_id: string }> {
    try {
      const response = await axiosInstance.post('/platform/weibo/schedule', {
        content: params.content,
        schedule_time: params.schedule.publish_time
      })
      
      return { task_id: response.data.task_id }
    } catch (error) {
      console.error('Weibo schedule failed:', error)
      throw error
    }
  }

  async cancelScheduledContent(task_id: string): Promise<boolean> {
    try {
      await axiosInstance.delete(`/platform/weibo/schedule/${task_id}`)
      return true
    } catch (error) {
      console.error('Weibo cancel schedule failed:', error)
      return false
    }
  }

  async getPublishStatus(post_id: string): Promise<PublishTaskStatus> {
    try {
      const response = await axiosInstance.get(`/platform/weibo/statuses/show/${post_id}`)
      return response.data.data
    } catch (error) {
      console.error('Failed to get Weibo publish status:', error)
      throw error
    }
  }

  async getContentEngagement(post_id: string): Promise<PublishResult['engagement']> {
    try {
      const response = await axiosInstance.get(`/platform/weibo/statuses/show/${post_id}`)
      return {
        likes: response.data.data.attitudes_count,
        comments: response.data.data.comments_count,
        shares: response.data.data.reposts_count
      }
    } catch (error) {
      console.error('Failed to get Weibo engagement:', error)
      return {}
    }
  }

  async updateContent(post_id: string, updates: Partial<PublishContentInfo>): Promise<boolean> {
    // 微博不支持编辑已发布内容
    return false
  }

  async deleteContent(post_id: string): Promise<boolean> {
    try {
      await axiosInstance.post('/platform/weibo/statuses/destroy', {
        id: post_id
      })
      return true
    } catch (error) {
      console.error('Weibo content deletion failed:', error)
      return false
    }
  }

  async validateContent(content: PublishContentInfo): Promise<{ valid: boolean; errors: string[] }> {
    const errors: string[] = []
    
    const fullText = `${content.title}\n${content.description}`
    
    if (!fullText.trim()) {
      errors.push('微博内容不能为空')
    }
    
    if (fullText.length > 2000) {
      errors.push('微博内容不能超过2000个字符')
    }
    
    if (content.images.length > 9) {
      errors.push('微博最多支持9张图片')
    }
    
    return {
      valid: errors.length === 0,
      errors
    }
  }
}

// 导出所有扩展适配器
export {
  XiaohongshuPublishAdapter,
  BilibiliPublishAdapter,
  WeiboPublishAdapter
}