/**
 * Text Content Store
 * 文本内容状态管理 - [stores][text_content][text_content_store]
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { textContentApiService } from '../../services/api/text_content_api';
import type {
  TextContentBasic,
  TextContentCreateRequest,
  TextContentUpdateRequest,
  TextGenerationRequest,
  TextGenerationResponse,
  TextAnalyseRequest,
  TextAnalyseResponse,
  TextTemplateBasic,
  TextTemplateCreateRequest,
  TextTemplateRenderRequest
} from '../../services/api/text_content_api';
import type { PaginatedResponse, PaginationParams } from '../../types/auth';

interface TextContentState {
  // 内容列表状态
  contentList: PaginatedResponse<TextContentBasic> | null;
  currentContent: TextContentBasic | null;
  contentLoading: boolean;
  contentError: string | null;

  // 生成状态
  generationLoading: boolean;
  generationError: string | null;
  lastGenerationResult: TextGenerationResponse | null;

  // 分析状态
  analysisLoading: boolean;
  analysisError: string | null;
  lastAnalysisResult: TextAnalyseResponse | null;

  // 模板状态
  templateList: PaginatedResponse<TextTemplateBasic> | null;
  currentTemplate: TextTemplateBasic | null;
  templateLoading: boolean;
  templateError: string | null;

  // 筛选和分页状态
  filters: {
    content_type?: TextContentBasic['content_type'];
    content_status?: TextContentBasic['content_status'];
    search?: string;
    tags?: string[];
    date_from?: string;
    date_to?: string;
  };
  pagination: PaginationParams;

  // 操作方法 - 内容管理
  text_content_store_load_content_list: (params?: PaginationParams, filters?: any) => Promise<void>;
  text_content_store_load_content_detail: (contentId: number) => Promise<void>;
  text_content_store_create_content: (data: TextContentCreateRequest) => Promise<boolean>;
  text_content_store_update_content: (data: TextContentUpdateRequest) => Promise<boolean>;
  text_content_store_delete_content: (contentId: number) => Promise<boolean>;
  text_content_store_batch_delete_content: (contentIds: number[]) => Promise<boolean>;

  // 操作方法 - AI生成
  text_content_store_generate_text: (data: TextGenerationRequest) => Promise<TextGenerationResponse | null>;
  text_content_store_batch_generate_text: (requests: TextGenerationRequest[]) => Promise<TextGenerationResponse[] | null>;

  // 操作方法 - 文本分析
  text_content_store_analyse_text: (data: TextAnalyseRequest) => Promise<TextAnalyseResponse | null>;

  // 操作方法 - 模板管理
  text_content_store_load_template_list: (params?: PaginationParams, filters?: any) => Promise<void>;
  text_content_store_load_template_detail: (templateId: number) => Promise<void>;
  text_content_store_create_template: (data: TextTemplateCreateRequest) => Promise<boolean>;
  text_content_store_render_template: (data: TextTemplateRenderRequest) => Promise<TextGenerationResponse | null>;

  // 操作方法 - 状态管理
  text_content_store_set_filters: (filters: any) => void;
  text_content_store_set_pagination: (pagination: PaginationParams) => void;
  text_content_store_clear_errors: () => void;
  text_content_store_reset_state: () => void;
}

export const useTextContentStore = create<TextContentState>()(
  persist(
    (set, get) => ({
      // 初始状态
      contentList: null,
      currentContent: null,
      contentLoading: false,
      contentError: null,

      generationLoading: false,
      generationError: null,
      lastGenerationResult: null,

      analysisLoading: false,
      analysisError: null,
      lastAnalysisResult: null,

      templateList: null,
      currentTemplate: null,
      templateLoading: false,
      templateError: null,

      filters: {},
      pagination: { page: 1, page_size: 20 },

      // 内容管理方法
      text_content_store_load_content_list: async (params, filters) => {
        set({ contentLoading: true, contentError: null });
        
        try {
          const response = await textContentApiService.text_content_api_get_content_list(
            params || get().pagination,
            filters || get().filters
          );

          if (response.success && response.data) {
            set({
              contentList: response.data,
              contentLoading: false,
              pagination: params || get().pagination
            });
          } else {
            set({
              contentError: response.error?.message || '获取内容列表失败',
              contentLoading: false
            });
          }
        } catch (error) {
          set({
            contentError: error instanceof Error ? error.message : '获取内容列表失败',
            contentLoading: false
          });
        }
      },

      text_content_store_load_content_detail: async (contentId) => {
        set({ contentLoading: true, contentError: null });
        
        try {
          const response = await textContentApiService.text_content_api_get_content_detail(contentId);

          if (response.success && response.data) {
            set({
              currentContent: response.data,
              contentLoading: false
            });
          } else {
            set({
              contentError: response.error?.message || '获取内容详情失败',
              contentLoading: false
            });
          }
        } catch (error) {
          set({
            contentError: error instanceof Error ? error.message : '获取内容详情失败',
            contentLoading: false
          });
        }
      },

      text_content_store_create_content: async (data) => {
        set({ contentLoading: true, contentError: null });
        
        try {
          const response = await textContentApiService.text_content_api_create_content(data);

          if (response.success && response.data) {
            set({
              currentContent: response.data,
              contentLoading: false
            });
            
            // 刷新列表
            await get().text_content_store_load_content_list();
            return true;
          } else {
            set({
              contentError: response.error?.message || '创建内容失败',
              contentLoading: false
            });
            return false;
          }
        } catch (error) {
          set({
            contentError: error instanceof Error ? error.message : '创建内容失败',
            contentLoading: false
          });
          return false;
        }
      },

      text_content_store_update_content: async (data) => {
        set({ contentLoading: true, contentError: null });
        
        try {
          const response = await textContentApiService.text_content_api_update_content(data);

          if (response.success && response.data) {
            set({
              currentContent: response.data,
              contentLoading: false
            });
            
            // 刷新列表
            await get().text_content_store_load_content_list();
            return true;
          } else {
            set({
              contentError: response.error?.message || '更新内容失败',
              contentLoading: false
            });
            return false;
          }
        } catch (error) {
          set({
            contentError: error instanceof Error ? error.message : '更新内容失败',
            contentLoading: false
          });
          return false;
        }
      },

      text_content_store_delete_content: async (contentId) => {
        set({ contentLoading: true, contentError: null });
        
        try {
          const response = await textContentApiService.text_content_api_delete_content(contentId);

          if (response.success) {
            set({ contentLoading: false });
            
            // 刷新列表
            await get().text_content_store_load_content_list();
            return true;
          } else {
            set({
              contentError: response.error?.message || '删除内容失败',
              contentLoading: false
            });
            return false;
          }
        } catch (error) {
          set({
            contentError: error instanceof Error ? error.message : '删除内容失败',
            contentLoading: false
          });
          return false;
        }
      },

      text_content_store_batch_delete_content: async (contentIds) => {
        set({ contentLoading: true, contentError: null });
        
        try {
          const response = await textContentApiService.text_content_api_batch_delete_content(contentIds);

          if (response.success) {
            set({ contentLoading: false });
            
            // 刷新列表
            await get().text_content_store_load_content_list();
            return true;
          } else {
            set({
              contentError: response.error?.message || '批量删除失败',
              contentLoading: false
            });
            return false;
          }
        } catch (error) {
          set({
            contentError: error instanceof Error ? error.message : '批量删除失败',
            contentLoading: false
          });
          return false;
        }
      },

      // AI生成方法
      text_content_store_generate_text: async (data) => {
        set({ generationLoading: true, generationError: null });
        
        try {
          const response = await textContentApiService.text_content_api_generate_text(data);

          if (response.success && response.data) {
            set({
              lastGenerationResult: response.data,
              generationLoading: false
            });
            
            // 如果保存到内容库，刷新列表
            if (data.save_to_content) {
              await get().text_content_store_load_content_list();
            }
            
            return response.data;
          } else {
            set({
              generationError: response.error?.message || '文本生成失败',
              generationLoading: false
            });
            return null;
          }
        } catch (error) {
          set({
            generationError: error instanceof Error ? error.message : '文本生成失败',
            generationLoading: false
          });
          return null;
        }
      },

      text_content_store_batch_generate_text: async (requests) => {
        set({ generationLoading: true, generationError: null });
        
        try {
          const response = await textContentApiService.text_content_api_batch_generate_text(requests);

          if (response.success && response.data) {
            set({ generationLoading: false });
            
            // 如果任何请求保存到内容库，刷新列表
            if (requests.some(req => req.save_to_content)) {
              await get().text_content_store_load_content_list();
            }
            
            return response.data;
          } else {
            set({
              generationError: response.error?.message || '批量生成失败',
              generationLoading: false
            });
            return null;
          }
        } catch (error) {
          set({
            generationError: error instanceof Error ? error.message : '批量生成失败',
            generationLoading: false
          });
          return null;
        }
      },

      // 文本分析方法
      text_content_store_analyse_text: async (data) => {
        set({ analysisLoading: true, analysisError: null });
        
        try {
          const response = await textContentApiService.text_content_api_analyse_text(data);

          if (response.success && response.data) {
            set({
              lastAnalysisResult: response.data,
              analysisLoading: false
            });
            return response.data;
          } else {
            set({
              analysisError: response.error?.message || '文本分析失败',
              analysisLoading: false
            });
            return null;
          }
        } catch (error) {
          set({
            analysisError: error instanceof Error ? error.message : '文本分析失败',
            analysisLoading: false
          });
          return null;
        }
      },

      // 模板管理方法
      text_content_store_load_template_list: async (params, filters) => {
        set({ templateLoading: true, templateError: null });
        
        try {
          const response = await textContentApiService.text_content_api_get_template_list(
            params || get().pagination,
            filters
          );

          if (response.success && response.data) {
            set({
              templateList: response.data,
              templateLoading: false
            });
          } else {
            set({
              templateError: response.error?.message || '获取模板列表失败',
              templateLoading: false
            });
          }
        } catch (error) {
          set({
            templateError: error instanceof Error ? error.message : '获取模板列表失败',
            templateLoading: false
          });
        }
      },

      text_content_store_load_template_detail: async (templateId) => {
        set({ templateLoading: true, templateError: null });
        
        try {
          const response = await textContentApiService.text_content_api_get_template_detail(templateId);

          if (response.success && response.data) {
            set({
              currentTemplate: response.data,
              templateLoading: false
            });
          } else {
            set({
              templateError: response.error?.message || '获取模板详情失败',
              templateLoading: false
            });
          }
        } catch (error) {
          set({
            templateError: error instanceof Error ? error.message : '获取模板详情失败',
            templateLoading: false
          });
        }
      },

      text_content_store_create_template: async (data) => {
        set({ templateLoading: true, templateError: null });
        
        try {
          const response = await textContentApiService.text_content_api_create_template(data);

          if (response.success && response.data) {
            set({
              currentTemplate: response.data,
              templateLoading: false
            });
            
            // 刷新模板列表
            await get().text_content_store_load_template_list();
            return true;
          } else {
            set({
              templateError: response.error?.message || '创建模板失败',
              templateLoading: false
            });
            return false;
          }
        } catch (error) {
          set({
            templateError: error instanceof Error ? error.message : '创建模板失败',
            templateLoading: false
          });
          return false;
        }
      },

      text_content_store_render_template: async (data) => {
        set({ generationLoading: true, generationError: null });
        
        try {
          const response = await textContentApiService.text_content_api_render_template(data);

          if (response.success && response.data) {
            set({
              lastGenerationResult: response.data,
              generationLoading: false
            });
            
            // 如果保存到内容库，刷新列表
            if (data.save_to_content) {
              await get().text_content_store_load_content_list();
            }
            
            return response.data;
          } else {
            set({
              generationError: response.error?.message || '模板渲染失败',
              generationLoading: false
            });
            return null;
          }
        } catch (error) {
          set({
            generationError: error instanceof Error ? error.message : '模板渲染失败',
            generationLoading: false
          });
          return null;
        }
      },

      // 状态管理方法
      text_content_store_set_filters: (filters) => {
        set({ filters: { ...get().filters, ...filters } });
      },

      text_content_store_set_pagination: (pagination) => {
        set({ pagination: { ...get().pagination, ...pagination } });
      },

      text_content_store_clear_errors: () => {
        set({
          contentError: null,
          generationError: null,
          analysisError: null,
          templateError: null
        });
      },

      text_content_store_reset_state: () => {
        set({
          contentList: null,
          currentContent: null,
          contentLoading: false,
          contentError: null,
          generationLoading: false,
          generationError: null,
          lastGenerationResult: null,
          analysisLoading: false,
          analysisError: null,
          lastAnalysisResult: null,
          templateList: null,
          currentTemplate: null,
          templateLoading: false,
          templateError: null,
          filters: {},
          pagination: { page: 1, page_size: 20 }
        });
      }
    }),
    {
      name: 'text-content-storage',
      storage: createJSONStorage(() => localStorage),
      // 只持久化必要的数据
      partialize: (state) => ({
        filters: state.filters,
        pagination: state.pagination,
        lastGenerationResult: state.lastGenerationResult,
        lastAnalysisResult: state.lastAnalysisResult
      }),
    }
  )
);