/**
 * HTTP Client Service
 * HTTP客户端服务 - [http][client]
 */

import axios, { 
  AxiosInstance, 
  AxiosRequestConfig, 
  AxiosResponse, 
  AxiosError 
} from 'axios'
import { message } from 'antd'
import type { ApiResponse } from '@/types/api'

class HttpClient {
  private instance: AxiosInstance
  private baseURL: string

  constructor() {
    this.baseURL = import.meta.env.VITE_API_BASE_URL || '/api/v1'
    this.instance = this.createInstance()
    this.setupInterceptors()
  }

  /**
   * 创建axios实例
   * [http][client][create_instance]
   */
  private createInstance(): AxiosInstance {
    return axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  }

  /**
   * 设置拦截器
   * [http][client][setup_interceptors]
   */
  private setupInterceptors(): void {
    // 请求拦截器
    this.instance.interceptors.request.use(
      (config) => {
        // 添加认证token
        const token = this.getAuthToken()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }

        // 添加请求ID用于追踪
        config.headers['X-Request-ID'] = this.generateRequestId()

        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // 响应拦截器
    this.instance.interceptors.response.use(
      (response: AxiosResponse<ApiResponse>) => {
        const { data } = response

        // 检查业务状态码
        if (!data.success) {
          this.handleBusinessError(data)
          return Promise.reject(new Error(data.message))
        }

        return response
      },
      (error: AxiosError<ApiResponse>) => {
        this.handleHttpError(error)
        return Promise.reject(error)
      }
    )
  }

  /**
   * 获取认证token
   * [http][client][get_auth_token]
   */
  private getAuthToken(): string | null {
    // TODO: 从状态管理中获取token
    return localStorage.getItem('access_token')
  }

  /**
   * 生成请求ID
   * [http][client][generate_request_id]
   */
  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  /**
   * 处理业务错误
   * [http][client][handle_business_error]
   */
  private handleBusinessError(data: ApiResponse): void {
    switch (data.code) {
      case 401:
        message.error('登录已过期，请重新登录')
        // TODO: 跳转到登录页面
        break
      case 403:
        message.error('权限不足')
        break
      case 404:
        message.error('请求的资源不存在')
        break
      case 422:
        message.error('请求参数验证失败')
        break
      case 429:
        message.error('请求过于频繁，请稍后重试')
        break
      default:
        message.error(data.message || '操作失败')
    }
  }

  /**
   * 处理HTTP错误
   * [http][client][handle_http_error]
   */
  private handleHttpError(error: AxiosError<ApiResponse>): void {
    if (error.response) {
      // 服务器响应错误
      const { status, data } = error.response
      switch (status) {
        case 500:
          message.error('服务器内部错误')
          break
        case 502:
        case 503:
        case 504:
          message.error('服务暂时不可用，请稍后重试')
          break
        default:
          message.error(data?.message || `请求失败 (${status})`)
      }
    } else if (error.request) {
      // 网络错误
      message.error('网络连接失败，请检查网络')
    } else {
      // 其他错误
      message.error('请求配置错误')
    }
  }

  /**
   * GET请求
   * [http][client][get]
   */
  async get<T = any>(
    url: string, 
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    const response = await this.instance.get<ApiResponse<T>>(url, config)
    return response.data
  }

  /**
   * POST请求
   * [http][client][post]
   */
  async post<T = any>(
    url: string, 
    data?: any, 
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    const response = await this.instance.post<ApiResponse<T>>(url, data, config)
    return response.data
  }

  /**
   * PUT请求
   * [http][client][put]
   */
  async put<T = any>(
    url: string, 
    data?: any, 
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    const response = await this.instance.put<ApiResponse<T>>(url, data, config)
    return response.data
  }

  /**
   * DELETE请求
   * [http][client][delete]
   */
  async delete<T = any>(
    url: string, 
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    const response = await this.instance.delete<ApiResponse<T>>(url, config)
    return response.data
  }

  /**
   * 文件上传
   * [http][client][upload]
   */
  async upload<T = any>(
    url: string,
    formData: FormData,
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<T>> {
    const response = await this.instance.post<ApiResponse<T>>(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          )
          onProgress(progress)
        }
      },
    })
    return response.data
  }

  /**
   * 文件下载
   * [http][client][download]
   */
  async download(url: string, filename?: string): Promise<void> {
    const response = await this.instance.get(url, {
      responseType: 'blob',
    })

    const blob = new Blob([response.data])
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = filename || 'download'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)
  }
}

// 创建单例实例
export const httpClient = new HttpClient()
export default httpClient