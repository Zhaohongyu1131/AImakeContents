/**
 * HTTP Request Wrapper Module
 * HTTP请求包装器模块 - [services][http][http_request_wrapper]
 */

import { AxiosResponse } from 'axios';
import { httpClient, HttpClientConfig } from './http_client';
import type { ApiResponse } from '../../types/auth';

// 分页参数
export interface PaginationParams {
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

// 分页响应
export interface PaginatedResponse<T> {
  items: T[];
  pagination: {
    page: number;
    page_size: number;
    total: number;
    total_pages: number;
  };
}

// 请求选项
export interface RequestOptions extends HttpClientConfig {
  showLoading?: boolean;
  loadingText?: string;
  successMessage?: string;
  skipErrorHandler?: boolean;
  retryCount?: number;
  cache?: boolean | 'no-cache' | 'force-cache';
}

class HttpRequestWrapper {
  /**
   * 包装GET请求
   * [services][http][http_request_wrapper][get]
   */
  async http_request_wrapper_get<T = any>(
    url: string,
    params?: Record<string, any>,
    options?: RequestOptions
  ): Promise<ApiResponse<T>> {
    try {
      const response: AxiosResponse<ApiResponse<T>> = await httpClient.get(url, {
        params,
        ...options
      });
      return response.data;
    } catch (error) {
      return this.http_request_wrapper_handle_error(error);
    }
  }

  /**
   * 包装POST请求
   * [services][http][http_request_wrapper][post]
   */
  async http_request_wrapper_post<T = any>(
    url: string,
    data?: any,
    options?: RequestOptions
  ): Promise<ApiResponse<T>> {
    try {
      const response: AxiosResponse<ApiResponse<T>> = await httpClient.post(url, data, options);
      return response.data;
    } catch (error) {
      return this.http_request_wrapper_handle_error(error);
    }
  }

  /**
   * 包装PUT请求
   * [services][http][http_request_wrapper][put]
   */
  async http_request_wrapper_put<T = any>(
    url: string,
    data?: any,
    options?: RequestOptions
  ): Promise<ApiResponse<T>> {
    try {
      const response: AxiosResponse<ApiResponse<T>> = await httpClient.put(url, data, options);
      return response.data;
    } catch (error) {
      return this.http_request_wrapper_handle_error(error);
    }
  }

  /**
   * 包装DELETE请求
   * [services][http][http_request_wrapper][delete]
   */
  async http_request_wrapper_delete<T = any>(
    url: string,
    options?: RequestOptions
  ): Promise<ApiResponse<T>> {
    try {
      const response: AxiosResponse<ApiResponse<T>> = await httpClient.delete(url, options);
      return response.data;
    } catch (error) {
      return this.http_request_wrapper_handle_error(error);
    }
  }

  /**
   * 包装PATCH请求
   * [services][http][http_request_wrapper][patch]
   */
  async http_request_wrapper_patch<T = any>(
    url: string,
    data?: any,
    options?: RequestOptions
  ): Promise<ApiResponse<T>> {
    try {
      const response: AxiosResponse<ApiResponse<T>> = await httpClient.patch(url, data, options);
      return response.data;
    } catch (error) {
      return this.http_request_wrapper_handle_error(error);
    }
  }

  /**
   * 分页查询
   * [services][http][http_request_wrapper][paginated_get]
   */
  async http_request_wrapper_paginated_get<T = any>(
    url: string,
    pagination: PaginationParams = {},
    filters?: Record<string, any>,
    options?: RequestOptions
  ): Promise<ApiResponse<PaginatedResponse<T>>> {
    const params = {
      page: pagination.page || 1,
      page_size: pagination.page_size || 20,
      sort_by: pagination.sort_by,
      sort_order: pagination.sort_order,
      ...filters
    };

    return this.http_request_wrapper_get(`${url}`, params, options);
  }

  /**
   * 批量操作
   * [services][http][http_request_wrapper][batch_request]
   */
  async http_request_wrapper_batch_request<T = any>(
    requests: Array<{
      method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
      url: string;
      data?: any;
      params?: any;
    }>,
    options?: RequestOptions
  ): Promise<ApiResponse<T[]>> {
    try {
      const promises = requests.map(request => {
        switch (request.method) {
          case 'GET':
            return httpClient.get(request.url, { params: request.params, ...options });
          case 'POST':
            return httpClient.post(request.url, request.data, options);
          case 'PUT':
            return httpClient.put(request.url, request.data, options);
          case 'DELETE':
            return httpClient.delete(request.url, options);
          case 'PATCH':
            return httpClient.patch(request.url, request.data, options);
          default:
            throw new Error(`Unsupported method: ${request.method}`);
        }
      });

      const responses = await Promise.allSettled(promises);
      const results = responses.map(response => {
        if (response.status === 'fulfilled') {
          return response.value.data;
        } else {
          return { success: false, error: { message: response.reason.message } };
        }
      });

      return {
        success: true,
        data: results
      };
    } catch (error) {
      return this.http_request_wrapper_handle_error(error);
    }
  }

  /**
   * 文件上传
   * [services][http][http_request_wrapper][upload_file]
   */
  async http_request_wrapper_upload_file<T = any>(
    url: string,
    file: File,
    onProgress?: (progress: number) => void,
    additionalData?: Record<string, any>,
    options?: RequestOptions
  ): Promise<ApiResponse<T>> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      // 添加额外数据
      if (additionalData) {
        Object.keys(additionalData).forEach(key => {
          formData.append(key, additionalData[key]);
        });
      }

      const response: AxiosResponse<ApiResponse<T>> = await httpClient.post(url, formData, {
        ...options,
        headers: {
          'Content-Type': 'multipart/form-data',
          ...options?.headers
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            onProgress(progress);
          }
        }
      });

      return response.data;
    } catch (error) {
      return this.http_request_wrapper_handle_error(error);
    }
  }

  /**
   * 多文件上传
   * [services][http][http_request_wrapper][upload_multiple_files]
   */
  async http_request_wrapper_upload_multiple_files<T = any>(
    url: string,
    files: File[],
    onProgress?: (progress: number) => void,
    additionalData?: Record<string, any>,
    options?: RequestOptions
  ): Promise<ApiResponse<T>> {
    try {
      const formData = new FormData();
      
      files.forEach((file, index) => {
        formData.append(`files`, file);
      });
      
      // 添加额外数据
      if (additionalData) {
        Object.keys(additionalData).forEach(key => {
          formData.append(key, additionalData[key]);
        });
      }

      const response: AxiosResponse<ApiResponse<T>> = await httpClient.post(url, formData, {
        ...options,
        headers: {
          'Content-Type': 'multipart/form-data',
          ...options?.headers
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            onProgress(progress);
          }
        }
      });

      return response.data;
    } catch (error) {
      return this.http_request_wrapper_handle_error(error);
    }
  }

  /**
   * 文件下载
   * [services][http][http_request_wrapper][download_file]
   */
  async http_request_wrapper_download_file(
    url: string,
    filename?: string,
    options?: RequestOptions
  ): Promise<void> {
    try {
      await httpClient.http_client_download_file(url, filename, options);
    } catch (error) {
      console.error('File download failed:', error);
      throw error;
    }
  }

  /**
   * 流式请求（Server-Sent Events）
   * [services][http][http_request_wrapper][stream_request]
   */
  http_request_wrapper_stream_request(
    url: string,
    onMessage: (data: any) => void,
    onError?: (error: Event) => void,
    onClose?: () => void,
    options?: RequestOptions
  ): EventSource {
    const params = new URLSearchParams();
    
    // 添加认证token
    const token = this.http_request_wrapper_get_auth_token();
    if (token) {
      params.append('token', token);
    }

    const eventSource = new EventSource(`${url}?${params.toString()}`);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('Failed to parse SSE data:', error);
      }
    };

    eventSource.onerror = (error) => {
      console.error('SSE error:', error);
      if (onError) {
        onError(error);
      }
    };

    eventSource.addEventListener('close', () => {
      eventSource.close();
      if (onClose) {
        onClose();
      }
    });

    return eventSource;
  }

  /**
   * 轮询请求
   * [services][http][http_request_wrapper][poll_request]
   */
  http_request_wrapper_poll_request<T = any>(
    url: string,
    params?: Record<string, any>,
    interval: number = 5000,
    maxAttempts?: number,
    options?: RequestOptions
  ): {
    start: () => void;
    stop: () => void;
    onData: (callback: (data: T) => void) => void;
    onError: (callback: (error: any) => void) => void;
  } {
    let intervalId: NodeJS.Timeout | null = null;
    let attemptCount = 0;
    let dataCallback: ((data: T) => void) | null = null;
    let errorCallback: ((error: any) => void) | null = null;

    const poll = async () => {
      try {
        attemptCount++;
        const response = await this.http_request_wrapper_get<T>(url, params, {
          ...options,
          skipErrorHandler: true
        });

        if (response.success && response.data && dataCallback) {
          dataCallback(response.data);
        }

        // 检查最大尝试次数
        if (maxAttempts && attemptCount >= maxAttempts) {
          this.stop();
        }
      } catch (error) {
        if (errorCallback) {
          errorCallback(error);
        }
        
        // 错误时也检查最大尝试次数
        if (maxAttempts && attemptCount >= maxAttempts) {
          this.stop();
        }
      }
    };

    const start = () => {
      if (!intervalId) {
        poll(); // 立即执行一次
        intervalId = setInterval(poll, interval);
      }
    };

    const stop = () => {
      if (intervalId) {
        clearInterval(intervalId);
        intervalId = null;
        attemptCount = 0;
      }
    };

    return {
      start,
      stop,
      onData: (callback: (data: T) => void) => {
        dataCallback = callback;
      },
      onError: (callback: (error: any) => void) => {
        errorCallback = callback;
      }
    };
  }

  /**
   * 获取认证token
   * [services][http][http_request_wrapper][get_auth_token]
   */
  private http_request_wrapper_get_auth_token(): string | null {
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
   * 处理错误
   * [services][http][http_request_wrapper][handle_error]
   */
  private http_request_wrapper_handle_error(error: any): ApiResponse<any> {
    console.error('Request wrapper error:', error);
    
    if (error.response?.data) {
      return error.response.data;
    }
    
    return {
      success: false,
      error: {
        code: 'NETWORK_ERROR',
        message: error.message || '网络请求失败'
      }
    };
  }
}

// 导出单例实例
export const httpRequestWrapper = new HttpRequestWrapper();

// 导出便捷方法
export const {
  http_request_wrapper_get: get,
  http_request_wrapper_post: post,
  http_request_wrapper_put: put,
  http_request_wrapper_delete: del,
  http_request_wrapper_patch: patch,
  http_request_wrapper_paginated_get: paginatedGet,
  http_request_wrapper_batch_request: batchRequest,
  http_request_wrapper_upload_file: uploadFile,
  http_request_wrapper_upload_multiple_files: uploadMultipleFiles,
  http_request_wrapper_download_file: downloadFile,
  http_request_wrapper_stream_request: streamRequest,
  http_request_wrapper_poll_request: pollRequest
} = httpRequestWrapper;