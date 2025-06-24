/**
 * File Service Store
 * 文件服务状态管理 - [stores][file_service][file_service_store]
 */

import { create } from 'zustand';
import { devtools, subscribeWithSelector } from 'zustand/middleware';
import { fileServiceApiService } from '../../services/api/file_service_api';
import type {
  FileStorageBasic,
  FileFolderBasic,
  FileUploadRequest,
  FileUploadResponse,
  FileSearchRequest,
  FileBatchOperationRequest,
  FileShareRequest,
  FileShareResponse,
  FolderCreateRequest,
  FolderUpdateRequest,
  FileAnalyseRequest,
  FileAnalyseResponse,
  FileStorageStatsResponse,
  TrashFileBasic,
  FileType,
  FilePermission,
  FileSortField,
  FileSortOrder
} from '../../services/api/file_service_api';
import type { PaginatedResponse } from '../../services/api/base_api_types';

// ================================
// State 接口定义
// ================================

interface FileServiceState {
  // ================================
  // 文件管理状态
  // ================================
  fileList: PaginatedResponse<FileStorageBasic> | null;
  currentFile: FileStorageBasic | null;
  fileListLoading: boolean;
  fileDetailLoading: boolean;
  selectedFiles: number[];
  currentFolder: FileFolderBasic | null;
  currentFolderId: number | null;
  
  // ================================
  // 文件夹管理状态
  // ================================
  folderList: FileFolderBasic[];
  folderTree: Array<FileFolderBasic & { children?: FileFolderBasic[] }>;
  folderListLoading: boolean;
  folderTreeLoading: boolean;
  folderCreateLoading: boolean;
  folderUpdateLoading: boolean;

  // ================================
  // 文件上传状态
  // ================================
  uploadLoading: boolean;
  uploadProgress: number;
  uploadQueue: Array<{
    file: File;
    progress: number;
    status: 'pending' | 'uploading' | 'completed' | 'failed';
    error?: string;
  }>;
  lastUploadResult: FileUploadResponse | null;

  // ================================
  // 文件搜索状态
  // ================================
  searchLoading: boolean;
  searchResults: PaginatedResponse<FileStorageBasic> | null;
  searchKeyword: string;
  searchFilters: Partial<FileSearchRequest>;

  // ================================
  // 文件分享状态
  // ================================
  shareList: PaginatedResponse<FileShareResponse & {
    file_names: string[];
    file_count: number;
  }> | null;
  shareListLoading: boolean;
  shareCreateLoading: boolean;
  currentShare: FileShareResponse | null;

  // ================================
  // 文件分析状态
  // ================================
  analysisLoading: boolean;
  lastAnalysisResult: FileAnalyseResponse | null;
  duplicateFiles: Array<{
    hash: string;
    file_size: number;
    duplicate_files: Array<{
      file_id: number;
      file_name: string;
      file_path: string;
    }>;
  }>;
  duplicateDetectionLoading: boolean;

  // ================================
  // 回收站状态
  // ================================
  trashList: PaginatedResponse<TrashFileBasic> | null;
  trashListLoading: boolean;

  // ================================
  // 统计数据状态
  // ================================
  storageStats: FileStorageStatsResponse | null;
  quotaInfo: {
    total_quota: number;
    used_quota: number;
    available_quota: number;
    file_count: number;
    quota_percentage: number;
  } | null;
  statsLoading: boolean;

  // ================================
  // 视图状态
  // ================================
  viewMode: 'list' | 'grid' | 'detail';
  sortField: FileSortField;
  sortOrder: FileSortOrder;
  showHiddenFiles: boolean;

  // ================================
  // 通用状态
  // ================================
  error: string | null;
  loading: boolean;

  // ================================
  // Actions - 文件管理
  // ================================
  file_service_store_load_file_list: (
    page?: number,
    pageSize?: number,
    folderId?: number,
    filters?: Partial<FileSearchRequest>
  ) => Promise<void>;
  
  file_service_store_load_file_detail: (fileId: number) => Promise<void>;
  
  file_service_store_upload_files: (
    request: FileUploadRequest
  ) => Promise<boolean>;

  file_service_store_search_files: (
    request: FileSearchRequest,
    page?: number,
    pageSize?: number
  ) => Promise<void>;

  file_service_store_rename_file: (
    fileId: number,
    newName: string
  ) => Promise<boolean>;

  file_service_store_move_file: (
    fileId: number,
    targetFolderId: number
  ) => Promise<boolean>;

  file_service_store_copy_file: (
    fileId: number,
    targetFolderId: number,
    newName?: string
  ) => Promise<boolean>;

  file_service_store_delete_file: (
    fileId: number,
    permanent?: boolean
  ) => Promise<boolean>;

  file_service_store_batch_operation: (
    request: FileBatchOperationRequest
  ) => Promise<boolean>;

  // ================================
  // Actions - 文件夹管理
  // ================================
  file_service_store_load_folder_list: (parentFolderId?: number) => Promise<void>;
  
  file_service_store_load_folder_tree: () => Promise<void>;
  
  file_service_store_create_folder: (request: FolderCreateRequest) => Promise<boolean>;
  
  file_service_store_update_folder: (request: FolderUpdateRequest) => Promise<boolean>;
  
  file_service_store_delete_folder: (
    folderId: number,
    deleteFiles?: boolean
  ) => Promise<boolean>;

  file_service_store_navigate_to_folder: (folderId: number | null) => void;

  // ================================
  // Actions - 文件分享
  // ================================
  file_service_store_create_share: (request: FileShareRequest) => Promise<string | null>;
  
  file_service_store_load_share_list: (page?: number, pageSize?: number) => Promise<void>;
  
  file_service_store_cancel_share: (shareId: string) => Promise<boolean>;
  
  file_service_store_get_share_detail: (
    shareId: string,
    accessPassword?: string
  ) => Promise<{
    share_info: FileShareResponse;
    files: FileStorageBasic[];
  } | null>;

  // ================================
  // Actions - 文件分析
  // ================================
  file_service_store_analyse_file: (request: FileAnalyseRequest) => Promise<FileAnalyseResponse | null>;
  
  file_service_store_detect_duplicates: (
    folderId?: number,
    scanSubfolders?: boolean
  ) => Promise<void>;

  // ================================
  // Actions - 回收站
  // ================================
  file_service_store_load_trash_list: (page?: number, pageSize?: number) => Promise<void>;
  
  file_service_store_restore_file: (
    trashId: number,
    targetFolderId?: number
  ) => Promise<boolean>;
  
  file_service_store_permanent_delete: (trashId: number) => Promise<boolean>;
  
  file_service_store_empty_trash: () => Promise<boolean>;

  // ================================
  // Actions - 统计数据
  // ================================
  file_service_store_load_storage_stats: (
    period?: 'day' | 'week' | 'month' | 'year'
  ) => Promise<void>;

  file_service_store_load_quota_info: () => Promise<void>;

  // ================================
  // Actions - 下载
  // ================================
  file_service_store_get_download_url: (
    fileId: number,
    expires?: number
  ) => Promise<string | null>;

  file_service_store_batch_download: (
    fileIds: number[],
    archiveName?: string
  ) => Promise<string | null>;

  // ================================
  // Actions - 文件选择和视图
  // ================================
  file_service_store_select_file: (fileId: number) => void;
  file_service_store_select_files: (fileIds: number[]) => void;
  file_service_store_toggle_file_selection: (fileId: number) => void;
  file_service_store_clear_selection: () => void;
  file_service_store_select_all: () => void;

  file_service_store_set_view_mode: (mode: 'list' | 'grid' | 'detail') => void;
  file_service_store_set_sort: (field: FileSortField, order: FileSortOrder) => void;
  file_service_store_toggle_hidden_files: () => void;

  // ================================
  // Actions - 工具方法
  // ================================
  file_service_store_clear_errors: () => void;
  file_service_store_reset_search: () => void;
  file_service_store_clear_upload_queue: () => void;
}

// ================================
// Store 创建
// ================================

export const useFileServiceStore = create<FileServiceState>()(
  devtools(
    subscribeWithSelector((set, get) => ({
      // ================================
      // 初始状态
      // ================================
      fileList: null,
      currentFile: null,
      fileListLoading: false,
      fileDetailLoading: false,
      selectedFiles: [],
      currentFolder: null,
      currentFolderId: null,
      
      folderList: [],
      folderTree: [],
      folderListLoading: false,
      folderTreeLoading: false,
      folderCreateLoading: false,
      folderUpdateLoading: false,

      uploadLoading: false,
      uploadProgress: 0,
      uploadQueue: [],
      lastUploadResult: null,

      searchLoading: false,
      searchResults: null,
      searchKeyword: '',
      searchFilters: {},

      shareList: null,
      shareListLoading: false,
      shareCreateLoading: false,
      currentShare: null,

      analysisLoading: false,
      lastAnalysisResult: null,
      duplicateFiles: [],
      duplicateDetectionLoading: false,

      trashList: null,
      trashListLoading: false,

      storageStats: null,
      quotaInfo: null,
      statsLoading: false,

      viewMode: 'list',
      sortField: 'created_at',
      sortOrder: 'desc',
      showHiddenFiles: false,

      error: null,
      loading: false,

      // ================================
      // Actions 实现
      // ================================

      // 文件管理
      file_service_store_load_file_list: async (page = 1, pageSize = 20, folderId, filters = {}) => {
        set({ fileListLoading: true, error: null });
        try {
          const response = await fileServiceApiService.file_service_api_get_file_list(
            page,
            pageSize,
            folderId,
            filters
          );
          if (response.success && response.data) {
            set({ 
              fileList: response.data,
              currentFolderId: folderId || null
            });
          } else {
            set({ error: response.message || '获取文件列表失败' });
          }
        } catch (error) {
          set({ error: '网络错误：获取文件列表失败' });
        } finally {
          set({ fileListLoading: false });
        }
      },

      file_service_store_load_file_detail: async (fileId: number) => {
        set({ fileDetailLoading: true, error: null });
        try {
          const response = await fileServiceApiService.file_service_api_get_file_detail(fileId);
          if (response.success && response.data) {
            set({ currentFile: response.data });
          } else {
            set({ error: response.message || '获取文件详情失败' });
          }
        } catch (error) {
          set({ error: '网络错误：获取文件详情失败' });
        } finally {
          set({ fileDetailLoading: false });
        }
      },

      file_service_store_upload_files: async (request: FileUploadRequest) => {
        set({ uploadLoading: true, uploadProgress: 0, error: null });
        
        // 初始化上传队列
        const queue = request.files.map(file => ({
          file,
          progress: 0,
          status: 'pending' as const
        }));
        set({ uploadQueue: queue });

        try {
          const response = await fileServiceApiService.file_service_api_upload_files(
            request,
            (progress) => set({ uploadProgress: progress })
          );
          
          if (response.success && response.data) {
            set({ 
              lastUploadResult: response.data,
              uploadProgress: 100
            });
            
            // 刷新文件列表
            const { currentFolderId } = get();
            get().file_service_store_load_file_list(1, 20, currentFolderId || undefined);
            
            return true;
          } else {
            set({ error: response.message || '文件上传失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：文件上传失败' });
          return false;
        } finally {
          set({ uploadLoading: false });
        }
      },

      file_service_store_search_files: async (request: FileSearchRequest, page = 1, pageSize = 20) => {
        set({ searchLoading: true, error: null, searchFilters: request });
        try {
          const response = await fileServiceApiService.file_service_api_search_files(request, page, pageSize);
          if (response.success && response.data) {
            set({ 
              searchResults: response.data,
              searchKeyword: request.keyword || ''
            });
          } else {
            set({ error: response.message || '文件搜索失败' });
          }
        } catch (error) {
          set({ error: '网络错误：文件搜索失败' });
        } finally {
          set({ searchLoading: false });
        }
      },

      file_service_store_rename_file: async (fileId: number, newName: string) => {
        set({ loading: true, error: null });
        try {
          const response = await fileServiceApiService.file_service_api_rename_file(fileId, newName);
          if (response.success) {
            // 更新文件列表中的文件信息
            const { fileList } = get();
            if (fileList) {
              const updatedItems = fileList.items.map(item =>
                item.file_id === fileId ? { ...item, file_name: newName } : item
              );
              set({
                fileList: {
                  ...fileList,
                  items: updatedItems
                }
              });
            }
            return true;
          } else {
            set({ error: response.message || '文件重命名失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：文件重命名失败' });
          return false;
        } finally {
          set({ loading: false });
        }
      },

      file_service_store_move_file: async (fileId: number, targetFolderId: number) => {
        set({ loading: true, error: null });
        try {
          const response = await fileServiceApiService.file_service_api_move_file(fileId, targetFolderId);
          if (response.success) {
            // 从当前列表中移除文件
            const { fileList } = get();
            if (fileList) {
              const updatedItems = fileList.items.filter(item => item.file_id !== fileId);
              set({
                fileList: {
                  ...fileList,
                  items: updatedItems,
                  total: fileList.total - 1
                }
              });
            }
            return true;
          } else {
            set({ error: response.message || '文件移动失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：文件移动失败' });
          return false;
        } finally {
          set({ loading: false });
        }
      },

      file_service_store_copy_file: async (fileId: number, targetFolderId: number, newName?: string) => {
        set({ loading: true, error: null });
        try {
          const response = await fileServiceApiService.file_service_api_copy_file(fileId, targetFolderId, newName);
          if (response.success) {
            return true;
          } else {
            set({ error: response.message || '文件复制失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：文件复制失败' });
          return false;
        } finally {
          set({ loading: false });
        }
      },

      file_service_store_delete_file: async (fileId: number, permanent = false) => {
        set({ loading: true, error: null });
        try {
          const response = await fileServiceApiService.file_service_api_delete_file(fileId, permanent);
          if (response.success) {
            // 从列表中移除文件
            const { fileList } = get();
            if (fileList) {
              const updatedItems = fileList.items.filter(item => item.file_id !== fileId);
              set({
                fileList: {
                  ...fileList,
                  items: updatedItems,
                  total: fileList.total - 1
                }
              });
            }
            return true;
          } else {
            set({ error: response.message || '文件删除失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：文件删除失败' });
          return false;
        } finally {
          set({ loading: false });
        }
      },

      file_service_store_batch_operation: async (request: FileBatchOperationRequest) => {
        set({ loading: true, error: null });
        try {
          const response = await fileServiceApiService.file_service_api_batch_operation(request);
          if (response.success && response.data) {
            if (response.data.failed_count > 0) {
              set({ error: `${response.data.failed_count} 个文件操作失败` });
            }
            
            // 刷新文件列表
            const { currentFolderId } = get();
            get().file_service_store_load_file_list(1, 20, currentFolderId || undefined);
            
            return response.data.success_count > 0;
          } else {
            set({ error: response.message || '批量操作失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：批量操作失败' });
          return false;
        } finally {
          set({ loading: false });
        }
      },

      // 文件夹管理
      file_service_store_load_folder_list: async (parentFolderId?: number) => {
        set({ folderListLoading: true, error: null });
        try {
          const response = await fileServiceApiService.file_service_api_get_folder_list(parentFolderId);
          if (response.success && response.data) {
            set({ folderList: response.data });
          } else {
            set({ error: response.message || '获取文件夹列表失败' });
          }
        } catch (error) {
          set({ error: '网络错误：获取文件夹列表失败' });
        } finally {
          set({ folderListLoading: false });
        }
      },

      file_service_store_load_folder_tree: async () => {
        set({ folderTreeLoading: true, error: null });
        try {
          const response = await fileServiceApiService.file_service_api_get_folder_tree();
          if (response.success && response.data) {
            set({ folderTree: response.data });
          } else {
            set({ error: response.message || '获取文件夹树失败' });
          }
        } catch (error) {
          set({ error: '网络错误：获取文件夹树失败' });
        } finally {
          set({ folderTreeLoading: false });
        }
      },

      file_service_store_create_folder: async (request: FolderCreateRequest) => {
        set({ folderCreateLoading: true, error: null });
        try {
          const response = await fileServiceApiService.file_service_api_create_folder(request);
          if (response.success && response.data) {
            // 刷新文件夹列表
            get().file_service_store_load_folder_list(request.parent_folder_id);
            get().file_service_store_load_folder_tree();
            return true;
          } else {
            set({ error: response.message || '创建文件夹失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：创建文件夹失败' });
          return false;
        } finally {
          set({ folderCreateLoading: false });
        }
      },

      file_service_store_update_folder: async (request: FolderUpdateRequest) => {
        set({ folderUpdateLoading: true, error: null });
        try {
          const response = await fileServiceApiService.file_service_api_update_folder(request);
          if (response.success) {
            // 刷新文件夹列表
            get().file_service_store_load_folder_tree();
            return true;
          } else {
            set({ error: response.message || '更新文件夹失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：更新文件夹失败' });
          return false;
        } finally {
          set({ folderUpdateLoading: false });
        }
      },

      file_service_store_delete_folder: async (folderId: number, deleteFiles = false) => {
        set({ loading: true, error: null });
        try {
          const response = await fileServiceApiService.file_service_api_delete_folder(folderId, deleteFiles);
          if (response.success) {
            // 刷新文件夹列表
            get().file_service_store_load_folder_tree();
            return true;
          } else {
            set({ error: response.message || '删除文件夹失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：删除文件夹失败' });
          return false;
        } finally {
          set({ loading: false });
        }
      },

      file_service_store_navigate_to_folder: (folderId: number | null) => {
        set({ currentFolderId: folderId, selectedFiles: [] });
        get().file_service_store_load_file_list(1, 20, folderId || undefined);
      },

      // 文件分享
      file_service_store_create_share: async (request: FileShareRequest) => {
        set({ shareCreateLoading: true, error: null });
        try {
          const response = await fileServiceApiService.file_service_api_create_share(request);
          if (response.success && response.data) {
            set({ currentShare: response.data });
            // 刷新分享列表
            get().file_service_store_load_share_list();
            return response.data.share_id;
          } else {
            set({ error: response.message || '创建分享失败' });
            return null;
          }
        } catch (error) {
          set({ error: '网络错误：创建分享失败' });
          return null;
        } finally {
          set({ shareCreateLoading: false });
        }
      },

      file_service_store_load_share_list: async (page = 1, pageSize = 20) => {
        set({ shareListLoading: true, error: null });
        try {
          const response = await fileServiceApiService.file_service_api_get_share_list(page, pageSize);
          if (response.success && response.data) {
            set({ shareList: response.data });
          } else {
            set({ error: response.message || '获取分享列表失败' });
          }
        } catch (error) {
          set({ error: '网络错误：获取分享列表失败' });
        } finally {
          set({ shareListLoading: false });
        }
      },

      file_service_store_cancel_share: async (shareId: string) => {
        set({ loading: true, error: null });
        try {
          const response = await fileServiceApiService.file_service_api_cancel_share(shareId);
          if (response.success) {
            // 刷新分享列表
            get().file_service_store_load_share_list();
            return true;
          } else {
            set({ error: response.message || '取消分享失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：取消分享失败' });
          return false;
        } finally {
          set({ loading: false });
        }
      },

      file_service_store_get_share_detail: async (shareId: string, accessPassword?: string) => {
        set({ loading: true, error: null });
        try {
          const response = await fileServiceApiService.file_service_api_get_share_detail(shareId, accessPassword);
          if (response.success && response.data) {
            return response.data;
          } else {
            set({ error: response.message || '获取分享详情失败' });
            return null;
          }
        } catch (error) {
          set({ error: '网络错误：获取分享详情失败' });
          return null;
        } finally {
          set({ loading: false });
        }
      },

      // 文件分析
      file_service_store_analyse_file: async (request: FileAnalyseRequest) => {
        set({ analysisLoading: true, error: null });
        try {
          const response = await fileServiceApiService.file_service_api_analyse_file(request);
          if (response.success && response.data) {
            set({ lastAnalysisResult: response.data });
            return response.data;
          } else {
            set({ error: response.message || '文件分析失败' });
            return null;
          }
        } catch (error) {
          set({ error: '网络错误：文件分析失败' });
          return null;
        } finally {
          set({ analysisLoading: false });
        }
      },

      file_service_store_detect_duplicates: async (folderId?: number, scanSubfolders = true) => {
        set({ duplicateDetectionLoading: true, error: null });
        try {
          const response = await fileServiceApiService.file_service_api_detect_duplicates(folderId, scanSubfolders);
          if (response.success && response.data) {
            set({ duplicateFiles: response.data });
          } else {
            set({ error: response.message || '重复文件检测失败' });
          }
        } catch (error) {
          set({ error: '网络错误：重复文件检测失败' });
        } finally {
          set({ duplicateDetectionLoading: false });
        }
      },

      // 回收站
      file_service_store_load_trash_list: async (page = 1, pageSize = 20) => {
        set({ trashListLoading: true, error: null });
        try {
          const response = await fileServiceApiService.file_service_api_get_trash_list(page, pageSize);
          if (response.success && response.data) {
            set({ trashList: response.data });
          } else {
            set({ error: response.message || '获取回收站列表失败' });
          }
        } catch (error) {
          set({ error: '网络错误：获取回收站列表失败' });
        } finally {
          set({ trashListLoading: false });
        }
      },

      file_service_store_restore_file: async (trashId: number, targetFolderId?: number) => {
        set({ loading: true, error: null });
        try {
          const response = await fileServiceApiService.file_service_api_restore_file(trashId, targetFolderId);
          if (response.success) {
            // 刷新回收站列表
            get().file_service_store_load_trash_list();
            return true;
          } else {
            set({ error: response.message || '文件恢复失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：文件恢复失败' });
          return false;
        } finally {
          set({ loading: false });
        }
      },

      file_service_store_permanent_delete: async (trashId: number) => {
        set({ loading: true, error: null });
        try {
          const response = await fileServiceApiService.file_service_api_permanent_delete(trashId);
          if (response.success) {
            // 从回收站列表中移除
            const { trashList } = get();
            if (trashList) {
              const updatedItems = trashList.items.filter(item => item.trash_id !== trashId);
              set({
                trashList: {
                  ...trashList,
                  items: updatedItems,
                  total: trashList.total - 1
                }
              });
            }
            return true;
          } else {
            set({ error: response.message || '永久删除失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：永久删除失败' });
          return false;
        } finally {
          set({ loading: false });
        }
      },

      file_service_store_empty_trash: async () => {
        set({ loading: true, error: null });
        try {
          const response = await fileServiceApiService.file_service_api_empty_trash();
          if (response.success) {
            set({ trashList: { items: [], total: 0, page: 1, page_size: 20, total_pages: 0 } });
            return true;
          } else {
            set({ error: response.message || '清空回收站失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：清空回收站失败' });
          return false;
        } finally {
          set({ loading: false });
        }
      },

      // 统计数据
      file_service_store_load_storage_stats: async (period = 'month') => {
        set({ statsLoading: true, error: null });
        try {
          const response = await fileServiceApiService.file_service_api_get_storage_stats(period);
          if (response.success && response.data) {
            set({ storageStats: response.data });
          } else {
            set({ error: response.message || '获取存储统计失败' });
          }
        } catch (error) {
          set({ error: '网络错误：获取存储统计失败' });
        } finally {
          set({ statsLoading: false });
        }
      },

      file_service_store_load_quota_info: async () => {
        set({ loading: true, error: null });
        try {
          const response = await fileServiceApiService.file_service_api_get_quota_info();
          if (response.success && response.data) {
            set({ quotaInfo: response.data });
          } else {
            set({ error: response.message || '获取配额信息失败' });
          }
        } catch (error) {
          set({ error: '网络错误：获取配额信息失败' });
        } finally {
          set({ loading: false });
        }
      },

      // 下载
      file_service_store_get_download_url: async (fileId: number, expires?: number) => {
        set({ loading: true, error: null });
        try {
          const response = await fileServiceApiService.file_service_api_get_download_url(fileId, expires);
          if (response.success && response.data) {
            return response.data.download_url;
          } else {
            set({ error: response.message || '获取下载链接失败' });
            return null;
          }
        } catch (error) {
          set({ error: '网络错误：获取下载链接失败' });
          return null;
        } finally {
          set({ loading: false });
        }
      },

      file_service_store_batch_download: async (fileIds: number[], archiveName?: string) => {
        set({ loading: true, error: null });
        try {
          const response = await fileServiceApiService.file_service_api_batch_download(fileIds, archiveName);
          if (response.success && response.data) {
            return response.data.task_id;
          } else {
            set({ error: response.message || '批量下载失败' });
            return null;
          }
        } catch (error) {
          set({ error: '网络错误：批量下载失败' });
          return null;
        } finally {
          set({ loading: false });
        }
      },

      // 文件选择和视图
      file_service_store_select_file: (fileId: number) => {
        set({ selectedFiles: [fileId] });
      },

      file_service_store_select_files: (fileIds: number[]) => {
        set({ selectedFiles: fileIds });
      },

      file_service_store_toggle_file_selection: (fileId: number) => {
        const { selectedFiles } = get();
        const isSelected = selectedFiles.includes(fileId);
        if (isSelected) {
          set({ selectedFiles: selectedFiles.filter(id => id !== fileId) });
        } else {
          set({ selectedFiles: [...selectedFiles, fileId] });
        }
      },

      file_service_store_clear_selection: () => {
        set({ selectedFiles: [] });
      },

      file_service_store_select_all: () => {
        const { fileList } = get();
        if (fileList) {
          const allFileIds = fileList.items.map(file => file.file_id);
          set({ selectedFiles: allFileIds });
        }
      },

      file_service_store_set_view_mode: (mode: 'list' | 'grid' | 'detail') => {
        set({ viewMode: mode });
      },

      file_service_store_set_sort: (field: FileSortField, order: FileSortOrder) => {
        set({ sortField: field, sortOrder: order });
        // 重新加载文件列表
        const { currentFolderId } = get();
        get().file_service_store_load_file_list(1, 20, currentFolderId || undefined, {
          sort_field: field,
          sort_order: order
        });
      },

      file_service_store_toggle_hidden_files: () => {
        set(state => ({ showHiddenFiles: !state.showHiddenFiles }));
      },

      // 工具方法
      file_service_store_clear_errors: () => {
        set({ error: null });
      },

      file_service_store_reset_search: () => {
        set({ 
          searchResults: null,
          searchKeyword: '',
          searchFilters: {}
        });
      },

      file_service_store_clear_upload_queue: () => {
        set({ 
          uploadQueue: [],
          uploadProgress: 0,
          lastUploadResult: null
        });
      }
    })),
    {
      name: 'file-service-store',
    }
  )
);