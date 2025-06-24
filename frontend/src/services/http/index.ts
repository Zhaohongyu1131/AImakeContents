/**
 * HTTP Services Index
 * HTTP服务模块入口 - [services][http][index]
 */

// 导出核心HTTP客户端
export { httpClient } from './http_client';
export type { HttpClientConfig, ResponseInterceptorConfig } from './http_client';

// 导出拦截器
export {
  http_interceptors_setup_default_interceptors,
  http_interceptors_cleanup_interceptors,
  interceptorManager,
  authInterceptor,
  loggingInterceptor,
  responseLoggingInterceptor,
  retryInterceptor,
  cacheInterceptor,
  errorHandlingInterceptor
} from './http_interceptors';

// 导出请求包装器
export {
  httpRequestWrapper,
  get,
  post,
  put,
  del as delete,
  patch,
  paginatedGet,
  batchRequest,
  uploadFile,
  uploadMultipleFiles,
  downloadFile,
  streamRequest,
  pollRequest
} from './http_request_wrapper';

export type {
  PaginationParams,
  PaginatedResponse,
  RequestOptions
} from './http_request_wrapper';

// 初始化HTTP服务
export function http_services_initialize(): void {
  // 设置默认拦截器
  http_interceptors_setup_default_interceptors();
  
  console.log('HTTP services initialized');
}

// 清理HTTP服务
export function http_services_cleanup(): void {
  // 清理拦截器
  http_interceptors_cleanup_interceptors();
  
  console.log('HTTP services cleaned up');
}