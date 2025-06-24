/**
 * Image Service Store
 * 图像服务状态管理 - [stores][image_service][image_service_store]
 */

import { create } from 'zustand';
import { devtools, subscribeWithSelector } from 'zustand/middleware';
import { imageServiceApiService } from '../../services/api/image_service_api';
import type {
  ImageContentBasic,
  ImageTemplateBasic,
  ImageGenerationRequest,
  ImageGenerationResponse,
  ImageEditRequest,
  ImageEditResponse,
  ImageTemplateCreateRequest,
  ImageTemplateUpdateRequest,
  ImageAnalyseRequest,
  ImageAnalyseResponse,
  ImageUsageStatsResponse,
  PlatformModelListResponse,
  ImagePlatformType,
  ImageStatus,
  ImageStyle
} from '../../services/api/image_service_api';
import type { PaginatedResponse } from '../../services/api/base_api_types';

// ================================
// State 接口定义
// ================================

interface ImageServiceState {
  // ================================
  // 图像内容状态
  // ================================
  imageList: PaginatedResponse<ImageContentBasic> | null;
  currentImage: ImageContentBasic | null;
  imageListLoading: boolean;
  imageDetailLoading: boolean;
  
  // ================================
  // 图像生成状态
  // ================================
  generationLoading: boolean;
  lastGenerationResult: ImageGenerationResponse | null;
  generationProgress: number;
  batchGenerationStatus: {
    task_id?: string;
    status?: 'processing' | 'completed' | 'failed' | 'partial';
    progress?: number;
    completed_count?: number;
    failed_count?: number;
  } | null;

  // ================================
  // 图像编辑状态
  // ================================
  editLoading: boolean;
  lastEditResult: ImageEditResponse | null;
  variationLoading: boolean;
  upscaleLoading: boolean;

  // ================================
  // 模板管理状态
  // ================================
  templateList: PaginatedResponse<ImageTemplateBasic> | null;
  currentTemplate: ImageTemplateBasic | null;
  templateListLoading: boolean;
  templateDetailLoading: boolean;
  templateCreateLoading: boolean;
  templateUpdateLoading: boolean;

  // ================================
  // 平台管理状态
  // ================================
  platformModels: Record<ImagePlatformType, PlatformModelListResponse | null>;
  platformConnectionStatus: Record<ImagePlatformType, {
    is_connected: boolean;
    response_time?: number;
    last_check?: string;
    error_message?: string;
  }>;
  platformTestLoading: Record<ImagePlatformType, boolean>;

  // ================================
  // 图像分析状态
  // ================================
  analysisLoading: boolean;
  lastAnalysisResult: ImageAnalyseResponse | null;

  // ================================
  // 文件上传状态
  // ================================
  uploadLoading: boolean;
  uploadedFiles: Array<{
    file_id: string;
    file_url: string;
    file_name: string;
    purpose: string;
  }>;

  // ================================
  // 统计数据状态
  // ================================
  usageStats: ImageUsageStatsResponse | null;
  statsLoading: boolean;

  // ================================
  // 通用状态
  // ================================
  error: string | null;
  loading: boolean;

  // ================================
  // Actions - 图像内容管理
  // ================================
  image_service_store_load_image_list: (
    page?: number,
    pageSize?: number,
    filters?: any
  ) => Promise<void>;
  
  image_service_store_load_image_detail: (imageId: number) => Promise<void>;
  
  image_service_store_delete_image: (imageId: number) => Promise<boolean>;

  // ================================
  // Actions - 图像生成
  // ================================
  image_service_store_generate_image: (
    request: ImageGenerationRequest
  ) => Promise<ImageGenerationResponse | null>;

  image_service_store_batch_generate: (
    prompts: Array<{
      prompt: string;
      negative_prompt?: string;
      image_title?: string;
    }>,
    common_params?: Partial<ImageGenerationRequest>
  ) => Promise<boolean>;

  image_service_store_check_batch_status: (taskId: string) => Promise<void>;

  // ================================
  // Actions - 图像编辑
  // ================================
  image_service_store_edit_image: (
    request: ImageEditRequest
  ) => Promise<ImageEditResponse | null>;

  image_service_store_create_variation: (
    imageId: number,
    params?: any
  ) => Promise<ImageGenerationResponse | null>;

  image_service_store_upscale_image: (
    imageId: number,
    params?: any
  ) => Promise<ImageEditResponse | null>;

  // ================================
  // Actions - 模板管理
  // ================================
  image_service_store_load_template_list: (
    page?: number,
    pageSize?: number,
    filters?: any
  ) => Promise<void>;

  image_service_store_load_template_detail: (templateId: number) => Promise<void>;

  image_service_store_create_template: (
    request: ImageTemplateCreateRequest
  ) => Promise<boolean>;

  image_service_store_update_template: (
    request: ImageTemplateUpdateRequest
  ) => Promise<boolean>;

  image_service_store_delete_template: (templateId: number) => Promise<boolean>;

  image_service_store_generate_from_template: (
    templateId: number,
    overrideParams?: Partial<ImageGenerationRequest>
  ) => Promise<ImageGenerationResponse | null>;

  // ================================
  // Actions - 平台管理
  // ================================
  image_service_store_load_platform_models: (
    platformType: ImagePlatformType
  ) => Promise<void>;

  image_service_store_test_platform_connection: (
    platformType: ImagePlatformType
  ) => Promise<boolean>;

  // ================================
  // Actions - 图像分析
  // ================================
  image_service_store_analyse_image: (
    request: ImageAnalyseRequest
  ) => Promise<ImageAnalyseResponse | null>;

  // ================================
  // Actions - 文件上传
  // ================================
  image_service_store_upload_reference: (
    file: File,
    purpose?: 'reference' | 'mask' | 'source'
  ) => Promise<string | null>;

  // ================================
  // Actions - 统计数据
  // ================================
  image_service_store_load_usage_stats: (
    period?: 'day' | 'week' | 'month' | 'year'
  ) => Promise<void>;

  // ================================
  // Actions - 工具方法
  // ================================
  image_service_store_clear_errors: () => void;
  image_service_store_reset_generation_state: () => void;
  image_service_store_clear_uploaded_files: () => void;
}

// ================================
// Store 创建
// ================================

export const useImageServiceStore = create<ImageServiceState>()(
  devtools(
    subscribeWithSelector((set, get) => ({
      // ================================
      // 初始状态
      // ================================
      imageList: null,
      currentImage: null,
      imageListLoading: false,
      imageDetailLoading: false,
      
      generationLoading: false,
      lastGenerationResult: null,
      generationProgress: 0,
      batchGenerationStatus: null,

      editLoading: false,
      lastEditResult: null,
      variationLoading: false,
      upscaleLoading: false,

      templateList: null,
      currentTemplate: null,
      templateListLoading: false,
      templateDetailLoading: false,
      templateCreateLoading: false,
      templateUpdateLoading: false,

      platformModels: {
        doubao: null,
        dalle: null,
        midjourney: null,
        stable_diffusion: null,
        azure: null
      },
      platformConnectionStatus: {
        doubao: { is_connected: false },
        dalle: { is_connected: false },
        midjourney: { is_connected: false },
        stable_diffusion: { is_connected: false },
        azure: { is_connected: false }
      },
      platformTestLoading: {
        doubao: false,
        dalle: false,
        midjourney: false,
        stable_diffusion: false,
        azure: false
      },

      analysisLoading: false,
      lastAnalysisResult: null,

      uploadLoading: false,
      uploadedFiles: [],

      usageStats: null,
      statsLoading: false,

      error: null,
      loading: false,

      // ================================
      // Actions 实现
      // ================================

      // 图像内容管理
      image_service_store_load_image_list: async (page = 1, pageSize = 20, filters = {}) => {
        set({ imageListLoading: true, error: null });
        try {
          const response = await imageServiceApiService.image_service_api_get_image_list(
            page,
            pageSize,
            filters
          );
          if (response.success && response.data) {
            set({ imageList: response.data });
          } else {
            set({ error: response.message || '获取图像列表失败' });
          }
        } catch (error) {
          set({ error: '网络错误：获取图像列表失败' });
        } finally {
          set({ imageListLoading: false });
        }
      },

      image_service_store_load_image_detail: async (imageId: number) => {
        set({ imageDetailLoading: true, error: null });
        try {
          const response = await imageServiceApiService.image_service_api_get_image_detail(imageId);
          if (response.success && response.data) {
            set({ currentImage: response.data });
          } else {
            set({ error: response.message || '获取图像详情失败' });
          }
        } catch (error) {
          set({ error: '网络错误：获取图像详情失败' });
        } finally {
          set({ imageDetailLoading: false });
        }
      },

      image_service_store_delete_image: async (imageId: number) => {
        set({ loading: true, error: null });
        try {
          const response = await imageServiceApiService.image_service_api_delete_image(imageId);
          if (response.success) {
            // 从列表中移除已删除的图像
            const currentList = get().imageList;
            if (currentList) {
              const updatedItems = currentList.items.filter(item => item.image_id !== imageId);
              set({
                imageList: {
                  ...currentList,
                  items: updatedItems,
                  total: currentList.total - 1
                }
              });
            }
            return true;
          } else {
            set({ error: response.message || '删除图像失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：删除图像失败' });
          return false;
        } finally {
          set({ loading: false });
        }
      },

      // 图像生成
      image_service_store_generate_image: async (request: ImageGenerationRequest) => {
        set({ generationLoading: true, generationProgress: 0, error: null });
        try {
          const response = await imageServiceApiService.image_service_api_generate_image(request);
          if (response.success && response.data) {
            set({ 
              lastGenerationResult: response.data,
              generationProgress: 100
            });
            // 刷新图像列表
            get().image_service_store_load_image_list();
            return response.data;
          } else {
            set({ error: response.message || '图像生成失败' });
            return null;
          }
        } catch (error) {
          set({ error: '网络错误：图像生成失败' });
          return null;
        } finally {
          set({ generationLoading: false });
        }
      },

      image_service_store_batch_generate: async (prompts, common_params) => {
        set({ generationLoading: true, error: null });
        try {
          const response = await imageServiceApiService.image_service_api_batch_generate({
            prompts,
            common_params
          });
          if (response.success && response.data) {
            set({
              batchGenerationStatus: {
                task_id: response.data.task_id,
                status: 'processing',
                progress: 0,
                completed_count: 0,
                failed_count: 0
              }
            });
            return true;
          } else {
            set({ error: response.message || '批量生成启动失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：批量生成启动失败' });
          return false;
        } finally {
          set({ generationLoading: false });
        }
      },

      image_service_store_check_batch_status: async (taskId: string) => {
        try {
          const response = await imageServiceApiService.image_service_api_get_batch_status(taskId);
          if (response.success && response.data) {
            set({ batchGenerationStatus: response.data });
          }
        } catch (error) {
          console.warn('Failed to check batch status:', error);
        }
      },

      // 图像编辑
      image_service_store_edit_image: async (request: ImageEditRequest) => {
        set({ editLoading: true, error: null });
        try {
          const response = await imageServiceApiService.image_service_api_edit_image(request);
          if (response.success && response.data) {
            set({ lastEditResult: response.data });
            return response.data;
          } else {
            set({ error: response.message || '图像编辑失败' });
            return null;
          }
        } catch (error) {
          set({ error: '网络错误：图像编辑失败' });
          return null;
        } finally {
          set({ editLoading: false });
        }
      },

      image_service_store_create_variation: async (imageId: number, params = {}) => {
        set({ variationLoading: true, error: null });
        try {
          const response = await imageServiceApiService.image_service_api_create_variation(imageId, params);
          if (response.success && response.data) {
            set({ lastGenerationResult: response.data });
            // 刷新图像列表
            get().image_service_store_load_image_list();
            return response.data;
          } else {
            set({ error: response.message || '变体生成失败' });
            return null;
          }
        } catch (error) {
          set({ error: '网络错误：变体生成失败' });
          return null;
        } finally {
          set({ variationLoading: false });
        }
      },

      image_service_store_upscale_image: async (imageId: number, params = {}) => {
        set({ upscaleLoading: true, error: null });
        try {
          const response = await imageServiceApiService.image_service_api_upscale_image(imageId, params);
          if (response.success && response.data) {
            set({ lastEditResult: response.data });
            return response.data;
          } else {
            set({ error: response.message || '图像放大失败' });
            return null;
          }
        } catch (error) {
          set({ error: '网络错误：图像放大失败' });
          return null;
        } finally {
          set({ upscaleLoading: false });
        }
      },

      // 模板管理
      image_service_store_load_template_list: async (page = 1, pageSize = 20, filters = {}) => {
        set({ templateListLoading: true, error: null });
        try {
          const response = await imageServiceApiService.image_service_api_get_template_list(
            page,
            pageSize,
            filters
          );
          if (response.success && response.data) {
            set({ templateList: response.data });
          } else {
            set({ error: response.message || '获取模板列表失败' });
          }
        } catch (error) {
          set({ error: '网络错误：获取模板列表失败' });
        } finally {
          set({ templateListLoading: false });
        }
      },

      image_service_store_load_template_detail: async (templateId: number) => {
        set({ templateDetailLoading: true, error: null });
        try {
          const response = await imageServiceApiService.image_service_api_get_template_detail(templateId);
          if (response.success && response.data) {
            set({ currentTemplate: response.data });
          } else {
            set({ error: response.message || '获取模板详情失败' });
          }
        } catch (error) {
          set({ error: '网络错误：获取模板详情失败' });
        } finally {
          set({ templateDetailLoading: false });
        }
      },

      image_service_store_create_template: async (request: ImageTemplateCreateRequest) => {
        set({ templateCreateLoading: true, error: null });
        try {
          const response = await imageServiceApiService.image_service_api_create_template(request);
          if (response.success && response.data) {
            set({ currentTemplate: response.data });
            // 刷新模板列表
            get().image_service_store_load_template_list();
            return true;
          } else {
            set({ error: response.message || '创建模板失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：创建模板失败' });
          return false;
        } finally {
          set({ templateCreateLoading: false });
        }
      },

      image_service_store_update_template: async (request: ImageTemplateUpdateRequest) => {
        set({ templateUpdateLoading: true, error: null });
        try {
          const response = await imageServiceApiService.image_service_api_update_template(request);
          if (response.success && response.data) {
            set({ currentTemplate: response.data });
            // 刷新模板列表
            get().image_service_store_load_template_list();
            return true;
          } else {
            set({ error: response.message || '更新模板失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：更新模板失败' });
          return false;
        } finally {
          set({ templateUpdateLoading: false });
        }
      },

      image_service_store_delete_template: async (templateId: number) => {
        set({ loading: true, error: null });
        try {
          const response = await imageServiceApiService.image_service_api_delete_template(templateId);
          if (response.success) {
            // 从列表中移除已删除的模板
            const currentList = get().templateList;
            if (currentList) {
              const updatedItems = currentList.items.filter(item => item.template_id !== templateId);
              set({
                templateList: {
                  ...currentList,
                  items: updatedItems,
                  total: currentList.total - 1
                }
              });
            }
            return true;
          } else {
            set({ error: response.message || '删除模板失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：删除模板失败' });
          return false;
        } finally {
          set({ loading: false });
        }
      },

      image_service_store_generate_from_template: async (templateId: number, overrideParams = {}) => {
        set({ generationLoading: true, error: null });
        try {
          const response = await imageServiceApiService.image_service_api_generate_from_template(
            templateId,
            overrideParams
          );
          if (response.success && response.data) {
            set({ lastGenerationResult: response.data });
            // 刷新图像列表
            get().image_service_store_load_image_list();
            return response.data;
          } else {
            set({ error: response.message || '模板生成失败' });
            return null;
          }
        } catch (error) {
          set({ error: '网络错误：模板生成失败' });
          return null;
        } finally {
          set({ generationLoading: false });
        }
      },

      // 平台管理
      image_service_store_load_platform_models: async (platformType) => {
        set({ loading: true, error: null });
        try {
          const response = await imageServiceApiService.image_service_api_get_platform_models(platformType);
          if (response.success && response.data) {
            set(state => ({
              platformModels: {
                ...state.platformModels,
                [platformType]: response.data
              }
            }));
          } else {
            set({ error: response.message || '获取平台模型列表失败' });
          }
        } catch (error) {
          set({ error: '网络错误：获取平台模型列表失败' });
        } finally {
          set({ loading: false });
        }
      },

      image_service_store_test_platform_connection: async (platformType) => {
        set(state => ({
          platformTestLoading: {
            ...state.platformTestLoading,
            [platformType]: true
          },
          error: null
        }));
        
        try {
          const response = await imageServiceApiService.image_service_api_test_platform_connection(platformType);
          if (response.success && response.data) {
            set(state => ({
              platformConnectionStatus: {
                ...state.platformConnectionStatus,
                [platformType]: {
                  ...response.data,
                  last_check: new Date().toISOString()
                }
              }
            }));
            return response.data.is_connected;
          } else {
            set(state => ({
              platformConnectionStatus: {
                ...state.platformConnectionStatus,
                [platformType]: {
                  is_connected: false,
                  error_message: response.message || '连接测试失败',
                  last_check: new Date().toISOString()
                }
              }
            }));
            return false;
          }
        } catch (error) {
          set(state => ({
            platformConnectionStatus: {
              ...state.platformConnectionStatus,
              [platformType]: {
                is_connected: false,
                error_message: '网络错误',
                last_check: new Date().toISOString()
              }
            }
          }));
          return false;
        } finally {
          set(state => ({
            platformTestLoading: {
              ...state.platformTestLoading,
              [platformType]: false
            }
          }));
        }
      },

      // 图像分析
      image_service_store_analyse_image: async (request: ImageAnalyseRequest) => {
        set({ analysisLoading: true, error: null });
        try {
          const response = await imageServiceApiService.image_service_api_analyse_image(request);
          if (response.success && response.data) {
            set({ lastAnalysisResult: response.data });
            return response.data;
          } else {
            set({ error: response.message || '图像分析失败' });
            return null;
          }
        } catch (error) {
          set({ error: '网络错误：图像分析失败' });
          return null;
        } finally {
          set({ analysisLoading: false });
        }
      },

      // 文件上传
      image_service_store_upload_reference: async (file: File, purpose = 'reference') => {
        set({ uploadLoading: true, error: null });
        try {
          const response = await imageServiceApiService.image_service_api_upload_reference(file, purpose);
          if (response.success && response.data) {
            set(state => ({
              uploadedFiles: [
                ...state.uploadedFiles,
                {
                  ...response.data,
                  purpose
                }
              ]
            }));
            return response.data.file_url;
          } else {
            set({ error: response.message || '文件上传失败' });
            return null;
          }
        } catch (error) {
          set({ error: '网络错误：文件上传失败' });
          return null;
        } finally {
          set({ uploadLoading: false });
        }
      },

      // 统计数据
      image_service_store_load_usage_stats: async (period = 'month') => {
        set({ statsLoading: true, error: null });
        try {
          const response = await imageServiceApiService.image_service_api_get_usage_stats(period);
          if (response.success && response.data) {
            set({ usageStats: response.data });
          } else {
            set({ error: response.message || '获取使用统计失败' });
          }
        } catch (error) {
          set({ error: '网络错误：获取使用统计失败' });
        } finally {
          set({ statsLoading: false });
        }
      },

      // 工具方法
      image_service_store_clear_errors: () => {
        set({ error: null });
      },

      image_service_store_reset_generation_state: () => {
        set({ 
          generationLoading: false,
          lastGenerationResult: null,
          generationProgress: 0,
          batchGenerationStatus: null
        });
      },

      image_service_store_clear_uploaded_files: () => {
        set({ uploadedFiles: [] });
      }
    })),
    {
      name: 'image-service-store',
    }
  )
);