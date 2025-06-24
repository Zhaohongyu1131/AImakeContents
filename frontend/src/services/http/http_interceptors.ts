/**
 * HTTP Interceptors Module
 * HTTP拦截器模块 - [services][http][http_interceptors]
 */

import { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { message, notification } from 'antd';
import { httpClient } from './http_client';

// 请求拦截器类型
export interface RequestInterceptor {
  onFulfilled?: (config: AxiosRequestConfig) => AxiosRequestConfig | Promise<AxiosRequestConfig>;
  onRejected?: (error: any) => any;
}

// 响应拦截器类型
export interface ResponseInterceptor {
  onFulfilled?: (response: AxiosResponse) => AxiosResponse | Promise<AxiosResponse>;
  onRejected?: (error: AxiosError) => any;
}

class HttpInterceptorManager {
  private requestInterceptors: Map<string, number> = new Map();
  private responseInterceptors: Map<string, number> = new Map();

  /**
   * 添加请求拦截器
   * [services][http][http_interceptors][add_request_interceptor]
   */
  http_interceptors_add_request_interceptor(
    name: string, 
    interceptor: RequestInterceptor
  ): void {
    const id = httpClient.defaults.interceptors?.request?.use(
      interceptor.onFulfilled,
      interceptor.onRejected
    );
    
    if (id !== undefined) {
      this.requestInterceptors.set(name, id);
    }
  }

  /**
   * 添加响应拦截器
   * [services][http][http_interceptors][add_response_interceptor]
   */
  http_interceptors_add_response_interceptor(
    name: string, 
    interceptor: ResponseInterceptor
  ): void {
    const id = httpClient.defaults.interceptors?.response?.use(
      interceptor.onFulfilled,
      interceptor.onRejected
    );
    
    if (id !== undefined) {
      this.responseInterceptors.set(name, id);
    }
  }

  /**
   * 移除请求拦截器
   * [services][http][http_interceptors][remove_request_interceptor]
   */
  http_interceptors_remove_request_interceptor(name: string): void {
    const id = this.requestInterceptors.get(name);
    if (id !== undefined) {
      httpClient.defaults.interceptors?.request?.eject(id);
      this.requestInterceptors.delete(name);
    }
  }

  /**
   * 移除响应拦截器
   * [services][http][http_interceptors][remove_response_interceptor]
   */
  http_interceptors_remove_response_interceptor(name: string): void {
    const id = this.responseInterceptors.get(name);
    if (id !== undefined) {
      httpClient.defaults.interceptors?.response?.eject(id);
      this.responseInterceptors.delete(name);
    }
  }

  /**
   * 清除所有拦截器
   * [services][http][http_interceptors][clear_all_interceptors]
   */
  http_interceptors_clear_all_interceptors(): void {
    // 清除请求拦截器
    this.requestInterceptors.forEach((id) => {
      httpClient.defaults.interceptors?.request?.eject(id);
    });
    this.requestInterceptors.clear();

    // 清除响应拦截器
    this.responseInterceptors.forEach((id) => {
      httpClient.defaults.interceptors?.response?.eject(id);
    });
    this.responseInterceptors.clear();
  }
}

// 创建拦截器管理器实例
const interceptorManager = new HttpInterceptorManager();

/**
 * 认证拦截器
 * [services][http][http_interceptors][auth_interceptor]
 */
export const authInterceptor: RequestInterceptor = {
  onFulfilled: (config) => {
    // 从localStorage获取token
    try {
      const authStorage = localStorage.getItem('auth-storage');
      if (authStorage) {
        const authData = JSON.parse(authStorage);
        const token = authData.state?.token;
        
        if (token && !config.skipAuth) {
          config.headers = config.headers || {};
          config.headers.Authorization = `Bearer ${token}`;
        }
      }
    } catch (error) {
      console.error('Auth interceptor error:', error);
    }
    
    return config;
  },
  onRejected: (error) => {
    return Promise.reject(error);
  }
};

/**
 * 请求日志拦截器
 * [services][http][http_interceptors][logging_interceptor]
 */
export const loggingInterceptor: RequestInterceptor = {
  onFulfilled: (config) => {
    // 添加请求ID
    const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    config.headers = config.headers || {};
    config.headers['X-Request-ID'] = requestId;

    // 记录请求日志
    if (import.meta.env.VITE_LOG_LEVEL === 'debug') {
      console.group(`🚀 HTTP Request [${requestId}]`);
      console.log('URL:', `${config.method?.toUpperCase()} ${config.baseURL}${config.url}`);
      console.log('Headers:', config.headers);
      console.log('Params:', config.params);
      console.log('Data:', config.data);
      console.groupEnd();
    }

    return config;
  },
  onRejected: (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
};

/**
 * 响应日志拦截器
 * [services][http][http_interceptors][response_logging_interceptor]
 */
export const responseLoggingInterceptor: ResponseInterceptor = {
  onFulfilled: (response) => {
    const requestId = response.config.headers?.['X-Request-ID'];
    
    if (import.meta.env.VITE_LOG_LEVEL === 'debug') {
      console.group(`✅ HTTP Response [${requestId}]`);
      console.log('Status:', response.status);
      console.log('Headers:', response.headers);
      console.log('Data:', response.data);
      console.groupEnd();
    }

    return response;
  },
  onRejected: (error) => {
    const requestId = error.config?.headers?.['X-Request-ID'];
    
    console.group(`❌ HTTP Error [${requestId}]`);
    console.log('Status:', error.response?.status);
    console.log('URL:', error.config?.url);
    console.log('Error:', error.response?.data || error.message);
    console.groupEnd();

    return Promise.reject(error);
  }
};

/**
 * 重试拦截器
 * [services][http][http_interceptors][retry_interceptor]
 */
export const retryInterceptor: ResponseInterceptor = {
  onRejected: async (error: AxiosError) => {
    const config = error.config as any;
    
    // 检查是否需要重试
    if (!config || !config.retry) {
      return Promise.reject(error);
    }

    // 设置重试次数
    config.__retryCount = config.__retryCount || 0;
    
    if (config.__retryCount >= config.retry) {
      return Promise.reject(error);
    }

    config.__retryCount += 1;

    // 计算延迟时间
    const delay = config.retryDelay || 1000;
    const backoff = Math.min(delay * Math.pow(2, config.__retryCount - 1), 10000);

    // 等待后重试
    await new Promise(resolve => setTimeout(resolve, backoff));

    return httpClient.defaults.request(config);
  }
};

/**
 * 缓存拦截器
 * [services][http][http_interceptors][cache_interceptor]
 */
export const cacheInterceptor: RequestInterceptor = {
  onFulfilled: (config) => {
    // 只对GET请求添加缓存控制
    if (config.method?.toLowerCase() === 'get' && config.cache !== false) {
      config.headers = config.headers || {};
      
      if (config.cache === 'no-cache') {
        config.headers['Cache-Control'] = 'no-cache';
        config.params = {
          ...config.params,
          _t: Date.now()
        };
      } else if (config.cache === 'force-cache') {
        config.headers['Cache-Control'] = 'max-age=3600';
      }
    }

    return config;
  }
};

/**
 * 错误处理拦截器
 * [services][http][http_interceptors][error_handling_interceptor]
 */
export const errorHandlingInterceptor: ResponseInterceptor = {
  onRejected: (error: AxiosError) => {
    const config = error.config as any;
    
    // 跳过错误处理
    if (config?.skipErrorHandler) {
      return Promise.reject(error);
    }

    const status = error.response?.status;
    const data = error.response?.data as any;

    switch (status) {
      case 400:
        message.error(data?.error?.message || '请求参数错误');
        break;
      
      case 401:
        // 认证失败，清除token并重定向
        localStorage.removeItem('auth-storage');
        message.error('登录已过期，请重新登录');
        if (window.location.pathname !== '/auth/login') {
          window.location.href = '/auth/login';
        }
        break;
      
      case 403:
        message.error('权限不足，无法访问该资源');
        break;
      
      case 404:
        message.error('请求的资源不存在');
        break;
      
      case 422:
        // 验证错误
        if (data?.error?.details?.errors) {
          const errors = data.error.details.errors;
          errors.forEach((err: any) => {
            message.error(`${err.field}: ${err.message}`);
          });
        } else {
          message.error(data?.error?.message || '数据验证失败');
        }
        break;
      
      case 429:
        message.warning('请求过于频繁，请稍后再试');
        break;
      
      case 500:
        notification.error({
          message: '服务器错误',
          description: '服务器内部错误，请稍后重试或联系技术支持',
          duration: 5
        });
        break;
      
      case 502:
      case 503:
      case 504:
        notification.error({
          message: '服务不可用',
          description: '服务暂时不可用，请稍后重试',
          duration: 5
        });
        break;
      
      default:
        if (!error.response) {
          message.error('网络连接失败，请检查网络设置');
        } else {
          message.error(data?.error?.message || data?.message || '请求失败');
        }
    }

    return Promise.reject(error);
  }
};

/**
 * 加载状态拦截器
 * [services][http][http_interceptors][loading_interceptor]
 */
class LoadingInterceptor {
  private loadingCount = 0;
  private loadingInstance: any = null;

  request: RequestInterceptor = {
    onFulfilled: (config) => {
      if (config.showLoading !== false) {
        this.http_interceptors_show_loading(config.loadingText);
      }
      return config;
    }
  };

  response: ResponseInterceptor = {
    onFulfilled: (response) => {
      if (response.config.showLoading !== false) {
        this.http_interceptors_hide_loading();
      }
      return response;
    },
    onRejected: (error) => {
      if (error.config?.showLoading !== false) {
        this.http_interceptors_hide_loading();
      }
      return Promise.reject(error);
    }
  };

  private http_interceptors_show_loading(text = '加载中...'): void {
    this.loadingCount++;
    
    if (this.loadingCount === 1) {
      // 这里可以显示全局loading组件
      // 例如使用antd的message.loading
      this.loadingInstance = message.loading(text, 0);
    }
  }

  private http_interceptors_hide_loading(): void {
    this.loadingCount = Math.max(0, this.loadingCount - 1);
    
    if (this.loadingCount === 0 && this.loadingInstance) {
      this.loadingInstance();
      this.loadingInstance = null;
    }
  }
}

const loadingInterceptor = new LoadingInterceptor();

/**
 * 初始化默认拦截器
 * [services][http][http_interceptors][setup_default_interceptors]
 */
export function http_interceptors_setup_default_interceptors(): void {
  // 请求拦截器
  interceptorManager.http_interceptors_add_request_interceptor('auth', authInterceptor);
  interceptorManager.http_interceptors_add_request_interceptor('logging', loggingInterceptor);
  interceptorManager.http_interceptors_add_request_interceptor('cache', cacheInterceptor);
  interceptorManager.http_interceptors_add_request_interceptor('loading', loadingInterceptor.request);

  // 响应拦截器
  interceptorManager.http_interceptors_add_response_interceptor('logging', responseLoggingInterceptor);
  interceptorManager.http_interceptors_add_response_interceptor('retry', retryInterceptor);
  interceptorManager.http_interceptors_add_response_interceptor('error', errorHandlingInterceptor);
  interceptorManager.http_interceptors_add_response_interceptor('loading', loadingInterceptor.response);
}

/**
 * 清理拦截器
 * [services][http][http_interceptors][cleanup_interceptors]
 */
export function http_interceptors_cleanup_interceptors(): void {
  interceptorManager.http_interceptors_clear_all_interceptors();
}

// 导出拦截器管理器
export { interceptorManager };