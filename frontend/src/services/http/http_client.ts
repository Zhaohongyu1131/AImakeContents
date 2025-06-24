/**
 * HTTP Client Module
 * HTTP客户端模块 - [services][http][http_client]
 */

import axios, { 
  AxiosInstance, 
  AxiosRequestConfig, 
  AxiosResponse, 
  AxiosError,
  InternalAxiosRequestConfig
} from 'axios';
import { message, notification } from 'antd';
import type { ApiResponse } from '../../types/auth';

// 请求配置接口
interface HttpClientConfig extends AxiosRequestConfig {
  skipAuth?: boolean;
  skipErrorHandler?: boolean;
  showLoading?: boolean;
  loadingText?: string;
  successMessage?: string;
  retryCount?: number;
}

// 响应拦截器配置
interface ResponseInterceptorConfig {
  showSuccessMessage?: boolean;
  showErrorMessage?: boolean;
  redirectOnUnauth?: boolean;
}

class HttpClient {
  private instance: AxiosInstance;
  private loadingCount = 0;
  private retryQueue: Map<string, number> = new Map();

  constructor() {
    this.instance = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      }
    });

    this.http_client_setup_interceptors();
  }

  /**
   * 设置请求和响应拦截器
   * [services][http][http_client][setup_interceptors]
   */
  private http_client_setup_interceptors(): void {
    // 请求拦截器
    this.instance.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        return this.http_client_request_interceptor(config);
      },
      (error: AxiosError) => {
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        return this.http_client_response_success_interceptor(response);
      },
      (error: AxiosError) => {
        return this.http_client_response_error_interceptor(error);
      }
    );
  }

  /**
   * 请求拦截器
   * [services][http][http_client][request_interceptor]
   */
  private http_client_request_interceptor(config: InternalAxiosRequestConfig): InternalAxiosRequestConfig {
    // 添加请求ID
    const requestId = this.http_client_generate_request_id();
    config.headers['X-Request-ID'] = requestId;

    // 添加API版本
    config.headers['API-Version'] = 'v1';

    // 添加时间戳（防缓存）
    if (config.method?.toLowerCase() === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now()
      };
    }

    // 添加认证token
    const token = this.http_client_get_auth_token();
    if (token && !config.skipAuth) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // 显示加载状态
    if (config.showLoading) {
      this.http_client_show_loading(config.loadingText);
    }

    // 记录请求日志
    console.log(`[HTTP] ${config.method?.toUpperCase()} ${config.url}`, {
      requestId,
      params: config.params,
      data: config.data
    });

    return config;
  }

  /**
   * 响应成功拦截器
   * [services][http][http_client][response_success_interceptor]
   */
  private http_client_response_success_interceptor(response: AxiosResponse): AxiosResponse {
    const config = response.config as HttpClientConfig;

    // 隐藏加载状态
    if (config.showLoading) {
      this.http_client_hide_loading();
    }

    // 显示成功消息
    if (config.successMessage) {
      message.success(config.successMessage);
    }

    // 记录响应日志
    const requestId = response.config.headers['X-Request-ID'];
    console.log(`[HTTP] Response ${response.status}`, {
      requestId,
      data: response.data
    });

    return response;
  }

  /**
   * 响应错误拦截器
   * [services][http][http_client][response_error_interceptor]
   */
  private async http_client_response_error_interceptor(error: AxiosError): Promise<any> {
    const config = error.config as HttpClientConfig;

    // 隐藏加载状态
    if (config?.showLoading) {
      this.http_client_hide_loading();
    }

    // 处理网络错误
    if (!error.response) {
      if (!config?.skipErrorHandler) {
        message.error('网络连接失败，请检查网络设置');
      }
      return Promise.reject(error);
    }

    const { status, data } = error.response;
    const requestId = config?.headers?.['X-Request-ID'];

    // 记录错误日志
    console.error(`[HTTP] Error ${status}`, {
      requestId,
      url: config?.url,
      error: data
    });

    // 处理不同状态码
    switch (status) {
      case 401:
        return this.http_client_handle_unauthorized_error(error);
      
      case 403:
        if (!config?.skipErrorHandler) {
          message.error('权限不足，无法访问该资源');
        }
        break;
      
      case 404:
        if (!config?.skipErrorHandler) {
          message.error('请求的资源不存在');
        }
        break;
      
      case 422:
        this.http_client_handle_validation_error(error);
        break;
      
      case 429:
        if (!config?.skipErrorHandler) {
          message.warning('请求过于频繁，请稍后再试');
        }
        break;
      
      case 500:
        if (!config?.skipErrorHandler) {
          message.error('服务器内部错误，请稍后重试');
        }
        break;
      
      default:
        if (!config?.skipErrorHandler) {
          const errorMessage = data?.error?.message || data?.message || '请求失败';
          message.error(errorMessage);
        }
    }

    // 重试机制
    if (this.http_client_should_retry(error)) {
      return this.http_client_retry_request(error);
    }

    return Promise.reject(error);
  }

  /**
   * 处理401未授权错误
   * [services][http][http_client][handle_unauthorized_error]
   */
  private async http_client_handle_unauthorized_error(error: AxiosError): Promise<any> {
    const config = error.config as HttpClientConfig;

    try {
      // 尝试刷新token
      const refreshed = await this.http_client_refresh_token();
      
      if (refreshed && config) {
        // 重新发送原请求
        return this.instance.request(config);
      }
    } catch (refreshError) {
      console.error('Token refresh failed:', refreshError);
    }

    // 刷新失败，清除认证信息并重定向
    this.http_client_clear_auth();
    
    if (!config?.skipErrorHandler) {
      message.error('登录已过期，请重新登录');
      // 重定向到登录页
      window.location.href = '/auth/login';
    }

    return Promise.reject(error);
  }

  /**
   * 处理422验证错误
   * [services][http][http_client][handle_validation_error]
   */
  private http_client_handle_validation_error(error: AxiosError): void {
    const config = error.config as HttpClientConfig;
    
    if (config?.skipErrorHandler) {
      return;
    }

    const data = error.response?.data as ApiResponse;
    
    if (data?.error?.details?.errors) {
      // 显示详细的验证错误
      const errors = data.error.details.errors;
      errors.forEach((err: any) => {
        message.error(`${err.field}: ${err.message}`);
      });
    } else {
      message.error(data?.error?.message || '数据验证失败');
    }
  }

  /**
   * 判断是否应该重试
   * [services][http][http_client][should_retry]
   */
  private http_client_should_retry(error: AxiosError): boolean {
    const config = error.config as HttpClientConfig;
    const maxRetries = config?.retryCount || 0;
    
    if (maxRetries <= 0) {
      return false;
    }

    // 只对特定状态码和网络错误重试
    const retryableStatuses = [408, 429, 500, 502, 503, 504];
    const status = error.response?.status;
    
    return !status || retryableStatuses.includes(status);
  }

  /**
   * 重试请求
   * [services][http][http_client][retry_request]
   */
  private async http_client_retry_request(error: AxiosError): Promise<any> {
    const config = error.config as HttpClientConfig;
    const requestKey = `${config?.method}_${config?.url}`;
    
    const currentRetryCount = this.retryQueue.get(requestKey) || 0;
    const maxRetries = config?.retryCount || 0;
    
    if (currentRetryCount >= maxRetries) {
      this.retryQueue.delete(requestKey);
      return Promise.reject(error);
    }

    // 增加重试次数
    this.retryQueue.set(requestKey, currentRetryCount + 1);

    // 计算延迟时间（指数退避）
    const delay = Math.min(1000 * Math.pow(2, currentRetryCount), 10000);
    
    await new Promise(resolve => setTimeout(resolve, delay));

    try {
      const response = await this.instance.request(config!);
      this.retryQueue.delete(requestKey);
      return response;
    } catch (retryError) {
      return this.http_client_retry_request(retryError as AxiosError);
    }
  }

  /**
   * 生成请求ID
   * [services][http][http_client][generate_request_id]
   */
  private http_client_generate_request_id(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * 获取认证token
   * [services][http][http_client][get_auth_token]
   */
  private http_client_get_auth_token(): string | null {
    try {
      const authStorage = localStorage.getItem('auth-storage');
      if (authStorage) {
        const authData = JSON.parse(authStorage);
        return authData.state?.token || null;
      }
    } catch (error) {
      console.error('Failed to get auth token:', error);
    }
    return null;
  }

  /**
   * 刷新认证token
   * [services][http][http_client][refresh_token]
   */
  private async http_client_refresh_token(): Promise<boolean> {
    try {
      const authStorage = localStorage.getItem('auth-storage');
      if (!authStorage) {
        return false;
      }

      const authData = JSON.parse(authStorage);
      const refreshToken = authData.state?.refreshToken;
      
      if (!refreshToken) {
        return false;
      }

      const response = await this.instance.post('/auth/refresh', {
        refresh_token: refreshToken
      }, {
        skipAuth: true,
        skipErrorHandler: true
      } as HttpClientConfig);

      if (response.data?.success && response.data?.data) {
        const { access_token, refresh_token } = response.data.data;
        
        // 更新本地存储的token
        authData.state.token = access_token;
        authData.state.refreshToken = refresh_token;
        localStorage.setItem('auth-storage', JSON.stringify(authData));
        
        return true;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
    }
    
    return false;
  }

  /**
   * 清除认证信息
   * [services][http][http_client][clear_auth]
   */
  private http_client_clear_auth(): void {
    localStorage.removeItem('auth-storage');
    delete this.instance.defaults.headers.common['Authorization'];
  }

  /**
   * 显示加载状态
   * [services][http][http_client][show_loading]
   */
  private http_client_show_loading(text = '加载中...'): void {
    this.loadingCount++;
    if (this.loadingCount === 1) {
      // 这里可以显示全局loading
      console.log(`Loading: ${text}`);
    }
  }

  /**
   * 隐藏加载状态
   * [services][http][http_client][hide_loading]
   */
  private http_client_hide_loading(): void {
    this.loadingCount = Math.max(0, this.loadingCount - 1);
    if (this.loadingCount === 0) {
      // 这里可以隐藏全局loading
      console.log('Loading complete');
    }
  }

  /**
   * GET请求
   * [services][http][http_client][get]
   */
  async get<T = any>(url: string, config?: HttpClientConfig): Promise<AxiosResponse<T>> {
    return this.instance.get(url, config);
  }

  /**
   * POST请求
   * [services][http][http_client][post]
   */
  async post<T = any>(url: string, data?: any, config?: HttpClientConfig): Promise<AxiosResponse<T>> {
    return this.instance.post(url, data, config);
  }

  /**
   * PUT请求
   * [services][http][http_client][put]
   */
  async put<T = any>(url: string, data?: any, config?: HttpClientConfig): Promise<AxiosResponse<T>> {
    return this.instance.put(url, data, config);
  }

  /**
   * DELETE请求
   * [services][http][http_client][delete]
   */
  async delete<T = any>(url: string, config?: HttpClientConfig): Promise<AxiosResponse<T>> {
    return this.instance.delete(url, config);
  }

  /**
   * PATCH请求
   * [services][http][http_client][patch]
   */
  async patch<T = any>(url: string, data?: any, config?: HttpClientConfig): Promise<AxiosResponse<T>> {
    return this.instance.patch(url, data, config);
  }

  /**
   * 上传文件
   * [services][http][http_client][upload]
   */
  async http_client_upload_file(
    url: string, 
    file: File, 
    onProgress?: (progress: number) => void,
    config?: HttpClientConfig
  ): Promise<AxiosResponse> {
    const formData = new FormData();
    formData.append('file', file);

    return this.instance.post(url, formData, {
      ...config,
      headers: {
        'Content-Type': 'multipart/form-data',
        ...config?.headers
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      }
    });
  }

  /**
   * 下载文件
   * [services][http][http_client][download]
   */
  async http_client_download_file(
    url: string, 
    filename?: string,
    config?: HttpClientConfig
  ): Promise<void> {
    const response = await this.instance.get(url, {
      ...config,
      responseType: 'blob'
    });

    const blob = new Blob([response.data]);
    const downloadUrl = window.URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename || 'download';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    window.URL.revokeObjectURL(downloadUrl);
  }

  /**
   * 设置基础URL
   * [services][http][http_client][set_base_url]
   */
  http_client_set_base_url(baseURL: string): void {
    this.instance.defaults.baseURL = baseURL;
  }

  /**
   * 设置默认headers
   * [services][http][http_client][set_default_headers]
   */
  http_client_set_default_headers(headers: Record<string, string>): void {
    Object.assign(this.instance.defaults.headers.common, headers);
  }

  /**
   * 获取实例
   * [services][http][http_client][get_instance]
   */
  get defaults() {
    return this.instance.defaults;
  }
}

// 导出单例实例
export const httpClient = new HttpClient();

// 导出类型
export type { HttpClientConfig, ResponseInterceptorConfig };