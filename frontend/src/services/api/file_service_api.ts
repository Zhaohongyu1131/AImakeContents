/**
 * File Service API Layer
 * 文件服务API层 - [services][api][file_service_api]
 */

import { axiosInstance } from '../axios/axios_instance';
import type { ApiResponse, PaginatedResponse } from './base_api_types';

// ================================
// 基础类型定义 - File Service Types
// ================================

export type FileStorageProvider = 'local' | 'oss' | 'aws_s3' | 'qcloud_cos' | 'azure_blob';
export type FileType = 'image' | 'audio' | 'video' | 'document' | 'archive' | 'other';
export type FileStatus = 'uploading' | 'processing' | 'completed' | 'failed' | 'deleted';
export type FilePermission = 'private' | 'public' | 'shared' | 'team';
export type FileSortField = 'name' | 'size' | 'created_at' | 'updated_at' | 'download_count';
export type FileSortOrder = 'asc' | 'desc';

// 文件基础信息
export interface FileStorageBasic {
  file_id: number;
  file_name: string;
  file_path: string;
  file_url: string;
  file_size: number;
  file_type: FileType;
  file_extension: string;
  mime_type: string;
  storage_provider: FileStorageProvider;
  file_status: FileStatus;
  file_permission: FilePermission;
  download_count: number;
  thumbnail_url?: string;
  preview_url?: string;
  md5_hash: string;
  created_at: string;
  updated_at: string;
  user_id: number;
}

// 文件夹信息
export interface FileFolderBasic {
  folder_id: number;
  folder_name: string;
  folder_path: string;
  parent_folder_id?: number;
  folder_permission: FilePermission;
  file_count: number;
  total_size: number;
  created_at: string;
  updated_at: string;
  user_id: number;
}

// 文件元数据
export interface FileMetadata {
  meta_id: number;
  file_id: number;
  meta_key: string;
  meta_value: string;
  meta_json?: Record<string, any>;
}

// ================================
// 请求/响应类型 - File Service DTOs
// ================================

// 文件上传请求
export interface FileUploadRequest {
  files: File[];
  folder_id?: number;
  file_permission?: FilePermission;
  auto_rename?: boolean;
  generate_thumbnail?: boolean;
  extract_metadata?: boolean;
  upload_options?: {
    chunk_size?: number;
    concurrent_chunks?: number;
    retry_times?: number;
  };
}

// 文件上传响应
export interface FileUploadResponse {
  upload_id: string;
  uploaded_files: Array<{
    file_id: number;
    file_name: string;
    file_url: string;
    file_size: number;
    thumbnail_url?: string;
    upload_time: number;
  }>;
  failed_files: Array<{
    file_name: string;
    error_message: string;
  }>;
  total_size: number;
  upload_time: number;
}

// 文件搜索请求
export interface FileSearchRequest {
  keyword?: string;
  file_types?: FileType[];
  folder_id?: number;
  date_range?: {
    start_date: string;
    end_date: string;
  };
  size_range?: {
    min_size: number;
    max_size: number;
  };
  file_permission?: FilePermission;
  user_id?: number;
  sort_field?: FileSortField;
  sort_order?: FileSortOrder;
  include_subfolders?: boolean;
}

// 文件批量操作请求
export interface FileBatchOperationRequest {
  file_ids: number[];
  operation: 'move' | 'copy' | 'delete' | 'archive' | 'permission';
  target_folder_id?: number;
  new_permission?: FilePermission;
  operation_options?: Record<string, any>;
}

// 文件分享请求
export interface FileShareRequest {
  file_ids: number[];
  share_type: 'link' | 'email' | 'qr_code';
  share_permission: 'view' | 'download' | 'edit';
  expire_time?: string;
  access_password?: string;
  share_note?: string;
  notify_users?: string[];
}

// 文件分享响应
export interface FileShareResponse {
  share_id: string;
  share_url: string;
  share_code: string;
  qr_code_url?: string;
  expire_time?: string;
  access_count: number;
  download_count: number;
  created_at: string;
}

// 文件夹创建请求
export interface FolderCreateRequest {
  folder_name: string;
  parent_folder_id?: number;
  folder_permission?: FilePermission;
  folder_description?: string;
}

// 文件夹更新请求
export interface FolderUpdateRequest {
  folder_id: number;
  folder_name?: string;
  folder_permission?: FilePermission;
  folder_description?: string;
}

// 文件分析请求
export interface FileAnalyseRequest {
  file_id: number;
  analysis_types: ('metadata' | 'content' | 'security' | 'duplicate')[];
}

// 文件分析响应
export interface FileAnalyseResponse {
  analysis_id: string;
  file_info: {
    file_name: string;
    file_size: number;
    file_type: FileType;
    mime_type: string;
    created_at: string;
  };
  analysis_results: {
    metadata?: {
      exif_data?: Record<string, any>;
      document_properties?: Record<string, any>;
      media_info?: {
        duration?: number;
        resolution?: string;
        codec?: string;
        bitrate?: number;
      };
    };
    content?: {
      text_content?: string;
      extracted_text?: string;
      ocr_results?: Array<{
        text: string;
        confidence: number;
        position: { x: number; y: number; width: number; height: number };
      }>;
    };
    security?: {
      virus_scan_result: 'clean' | 'infected' | 'suspicious';
      scan_engine: string;
      threat_details?: string[];
      risk_level: 'low' | 'medium' | 'high';
    };
    duplicate?: {
      is_duplicate: boolean;
      duplicate_files: Array<{
        file_id: number;
        file_name: string;
        similarity: number;
      }>;
    };
  };
}

// 存储使用统计响应
export interface FileStorageStatsResponse {
  period: string;
  total_files: number;
  total_size: number;
  total_downloads: number;
  total_uploads: number;
  type_distribution: Record<FileType, {
    file_count: number;
    total_size: number;
    percentage: number;
  }>;
  storage_distribution: Record<FileStorageProvider, {
    file_count: number;
    total_size: number;
    cost: number;
  }>;
  daily_usage: Array<{
    date: string;
    upload_count: number;
    upload_size: number;
    download_count: number;
  }>;
  top_files: Array<{
    file_id: number;
    file_name: string;
    download_count: number;
    file_size: number;
  }>;
}

// 回收站文件信息
export interface TrashFileBasic {
  trash_id: number;
  file_id: number;
  file_name: string;
  file_size: number;
  file_type: FileType;
  original_path: string;
  deleted_at: string;
  auto_delete_at: string;
  user_id: number;
}

// ================================
// File Service API 类
// ================================

class FileServiceApiService {
  
  // ================================
  // 文件管理相关 API
  // ================================
  
  /**
   * 获取文件列表
   */
  async file_service_api_get_file_list(
    page: number = 1,
    pageSize: number = 20,
    folderId?: number,
    filters?: Partial<FileSearchRequest>
  ): Promise<ApiResponse<PaginatedResponse<FileStorageBasic>>> {
    const response = await axiosInstance.get('/file/list', {
      params: {
        page,
        page_size: pageSize,
        folder_id: folderId,
        ...filters
      }
    });
    return response.data;
  }

  /**
   * 获取文件详情
   */
  async file_service_api_get_file_detail(
    fileId: number
  ): Promise<ApiResponse<FileStorageBasic & { metadata?: FileMetadata[] }>> {
    const response = await axiosInstance.get(`/file/${fileId}`);
    return response.data;
  }

  /**
   * 文件上传
   */
  async file_service_api_upload_files(
    request: FileUploadRequest,
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<FileUploadResponse>> {
    const formData = new FormData();
    
    request.files.forEach((file, index) => {
      formData.append('files', file);
    });

    if (request.folder_id) {
      formData.append('folder_id', request.folder_id.toString());
    }
    
    if (request.file_permission) {
      formData.append('file_permission', request.file_permission);
    }

    if (request.auto_rename) {
      formData.append('auto_rename', request.auto_rename.toString());
    }

    if (request.generate_thumbnail) {
      formData.append('generate_thumbnail', request.generate_thumbnail.toString());
    }

    if (request.extract_metadata) {
      formData.append('extract_metadata', request.extract_metadata.toString());
    }

    if (request.upload_options) {
      formData.append('upload_options', JSON.stringify(request.upload_options));
    }

    const response = await axiosInstance.post('/file/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });
    return response.data;
  }

  /**
   * 文件搜索
   */
  async file_service_api_search_files(
    request: FileSearchRequest,
    page: number = 1,
    pageSize: number = 20
  ): Promise<ApiResponse<PaginatedResponse<FileStorageBasic>>> {
    const response = await axiosInstance.post('/file/search', {
      ...request,
      page,
      page_size: pageSize
    });
    return response.data;
  }

  /**
   * 文件重命名
   */
  async file_service_api_rename_file(
    fileId: number,
    newName: string
  ): Promise<ApiResponse<FileStorageBasic>> {
    const response = await axiosInstance.put(`/file/${fileId}/rename`, {
      new_name: newName
    });
    return response.data;
  }

  /**
   * 文件移动
   */
  async file_service_api_move_file(
    fileId: number,
    targetFolderId: number
  ): Promise<ApiResponse<boolean>> {
    const response = await axiosInstance.put(`/file/${fileId}/move`, {
      target_folder_id: targetFolderId
    });
    return response.data;
  }

  /**
   * 文件复制
   */
  async file_service_api_copy_file(
    fileId: number,
    targetFolderId: number,
    newName?: string
  ): Promise<ApiResponse<FileStorageBasic>> {
    const response = await axiosInstance.post(`/file/${fileId}/copy`, {
      target_folder_id: targetFolderId,
      new_name: newName
    });
    return response.data;
  }

  /**
   * 文件删除
   */
  async file_service_api_delete_file(
    fileId: number,
    permanent: boolean = false
  ): Promise<ApiResponse<boolean>> {
    const response = await axiosInstance.delete(`/file/${fileId}`, {
      params: { permanent }
    });
    return response.data;
  }

  /**
   * 批量操作
   */
  async file_service_api_batch_operation(
    request: FileBatchOperationRequest
  ): Promise<ApiResponse<{
    success_count: number;
    failed_count: number;
    failed_files: Array<{
      file_id: number;
      error_message: string;
    }>;
  }>> {
    const response = await axiosInstance.post('/file/batch', request);
    return response.data;
  }

  // ================================
  // 文件夹管理相关 API
  // ================================

  /**
   * 获取文件夹列表
   */
  async file_service_api_get_folder_list(
    parentFolderId?: number
  ): Promise<ApiResponse<FileFolderBasic[]>> {
    const response = await axiosInstance.get('/file/folder/list', {
      params: { parent_folder_id: parentFolderId }
    });
    return response.data;
  }

  /**
   * 获取文件夹树形结构
   */
  async file_service_api_get_folder_tree(): Promise<ApiResponse<Array<FileFolderBasic & {
    children?: FileFolderBasic[];
  }>>> {
    const response = await axiosInstance.get('/file/folder/tree');
    return response.data;
  }

  /**
   * 创建文件夹
   */
  async file_service_api_create_folder(
    request: FolderCreateRequest
  ): Promise<ApiResponse<FileFolderBasic>> {
    const response = await axiosInstance.post('/file/folder/create', request);
    return response.data;
  }

  /**
   * 更新文件夹
   */
  async file_service_api_update_folder(
    request: FolderUpdateRequest
  ): Promise<ApiResponse<FileFolderBasic>> {
    const response = await axiosInstance.put('/file/folder/update', request);
    return response.data;
  }

  /**
   * 删除文件夹
   */
  async file_service_api_delete_folder(
    folderId: number,
    deleteFiles: boolean = false
  ): Promise<ApiResponse<boolean>> {
    const response = await axiosInstance.delete(`/file/folder/${folderId}`, {
      params: { delete_files: deleteFiles }
    });
    return response.data;
  }

  // ================================
  // 文件分享相关 API
  // ================================

  /**
   * 创建文件分享
   */
  async file_service_api_create_share(
    request: FileShareRequest
  ): Promise<ApiResponse<FileShareResponse>> {
    const response = await axiosInstance.post('/file/share/create', request);
    return response.data;
  }

  /**
   * 获取分享列表
   */
  async file_service_api_get_share_list(
    page: number = 1,
    pageSize: number = 20
  ): Promise<ApiResponse<PaginatedResponse<FileShareResponse & {
    file_names: string[];
    file_count: number;
  }>>> {
    const response = await axiosInstance.get('/file/share/list', {
      params: { page, page_size: pageSize }
    });
    return response.data;
  }

  /**
   * 取消分享
   */
  async file_service_api_cancel_share(
    shareId: string
  ): Promise<ApiResponse<boolean>> {
    const response = await axiosInstance.delete(`/file/share/${shareId}`);
    return response.data;
  }

  /**
   * 获取分享详情
   */
  async file_service_api_get_share_detail(
    shareId: string,
    accessPassword?: string
  ): Promise<ApiResponse<{
    share_info: FileShareResponse;
    files: FileStorageBasic[];
  }>> {
    const response = await axiosInstance.get(`/file/share/${shareId}`, {
      params: { access_password: accessPassword }
    });
    return response.data;
  }

  // ================================
  // 文件分析相关 API
  // ================================

  /**
   * 文件分析
   */
  async file_service_api_analyse_file(
    request: FileAnalyseRequest
  ): Promise<ApiResponse<FileAnalyseResponse>> {
    const response = await axiosInstance.post('/file/analyse', request);
    return response.data;
  }

  /**
   * 重复文件检测
   */
  async file_service_api_detect_duplicates(
    folderId?: number,
    scanSubfolders: boolean = true
  ): Promise<ApiResponse<Array<{
    hash: string;
    file_size: number;
    duplicate_files: Array<{
      file_id: number;
      file_name: string;
      file_path: string;
    }>;
  }>>> {
    const response = await axiosInstance.post('/file/duplicate/detect', {
      folder_id: folderId,
      scan_subfolders: scanSubfolders
    });
    return response.data;
  }

  // ================================
  // 回收站相关 API
  // ================================

  /**
   * 获取回收站文件列表
   */
  async file_service_api_get_trash_list(
    page: number = 1,
    pageSize: number = 20
  ): Promise<ApiResponse<PaginatedResponse<TrashFileBasic>>> {
    const response = await axiosInstance.get('/file/trash/list', {
      params: { page, page_size: pageSize }
    });
    return response.data;
  }

  /**
   * 恢复文件
   */
  async file_service_api_restore_file(
    trashId: number,
    targetFolderId?: number
  ): Promise<ApiResponse<boolean>> {
    const response = await axiosInstance.post(`/file/trash/${trashId}/restore`, {
      target_folder_id: targetFolderId
    });
    return response.data;
  }

  /**
   * 永久删除文件
   */
  async file_service_api_permanent_delete(
    trashId: number
  ): Promise<ApiResponse<boolean>> {
    const response = await axiosInstance.delete(`/file/trash/${trashId}`);
    return response.data;
  }

  /**
   * 清空回收站
   */
  async file_service_api_empty_trash(): Promise<ApiResponse<{
    deleted_count: number;
    freed_size: number;
  }>> {
    const response = await axiosInstance.delete('/file/trash/empty');
    return response.data;
  }

  // ================================
  // 统计分析相关 API
  // ================================

  /**
   * 获取存储统计
   */
  async file_service_api_get_storage_stats(
    period: 'day' | 'week' | 'month' | 'year' = 'month'
  ): Promise<ApiResponse<FileStorageStatsResponse>> {
    const response = await axiosInstance.get('/file/stats/storage', {
      params: { period }
    });
    return response.data;
  }

  /**
   * 获取存储配额信息
   */
  async file_service_api_get_quota_info(): Promise<ApiResponse<{
    total_quota: number;
    used_quota: number;
    available_quota: number;
    file_count: number;
    quota_percentage: number;
  }>> {
    const response = await axiosInstance.get('/file/quota');
    return response.data;
  }

  // ================================
  // 下载相关 API
  // ================================

  /**
   * 获取文件下载链接
   */
  async file_service_api_get_download_url(
    fileId: number,
    expires?: number
  ): Promise<ApiResponse<{
    download_url: string;
    expires_at: string;
  }>> {
    const response = await axiosInstance.get(`/file/${fileId}/download`, {
      params: { expires }
    });
    return response.data;
  }

  /**
   * 批量下载（生成压缩包）
   */
  async file_service_api_batch_download(
    fileIds: number[],
    archiveName?: string
  ): Promise<ApiResponse<{
    task_id: string;
    estimated_time: number;
  }>> {
    const response = await axiosInstance.post('/file/download/batch', {
      file_ids: fileIds,
      archive_name: archiveName
    });
    return response.data;
  }

  /**
   * 获取批量下载状态
   */
  async file_service_api_get_download_status(
    taskId: string
  ): Promise<ApiResponse<{
    status: 'processing' | 'completed' | 'failed';
    progress: number;
    download_url?: string;
    error_message?: string;
  }>> {
    const response = await axiosInstance.get(`/file/download/status/${taskId}`);
    return response.data;
  }
}

// 导出服务实例
export const fileServiceApiService = new FileServiceApiService();
export default fileServiceApiService;