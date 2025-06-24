/**
 * Text Content API Service
 * 文本内容API服务 - [services][api][text_content_api]
 */

import { httpRequestWrapper } from '../http';
import type { ApiResponse, PaginatedResponse, PaginationParams } from '../../types/auth';

// 文本内容相关类型定义
export interface TextContentBasic {
  content_id: number;
  user_id: number;
  content_title: string;
  content_body: string;
  content_type: 'article' | 'prompt' | 'script' | 'description';
  content_length: number;
  content_tags: string[];
  content_status: 'draft' | 'published' | 'archived';
  generation_provider?: string;
  generation_model?: string;
  generation_params?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface TextContentCreateRequest {
  content_title: string;
  content_body: string;
  content_type: TextContentBasic['content_type'];
  content_tags?: string[];
  content_status?: TextContentBasic['content_status'];
}

export interface TextContentUpdateRequest extends Partial<TextContentCreateRequest> {
  content_id: number;
}

export interface TextGenerationRequest {
  prompt: string;
  model_provider?: 'doubao' | 'openai' | 'azure';
  model_name?: string;
  temperature?: number;
  max_tokens?: number;
  content_type?: TextContentBasic['content_type'];
  save_to_content?: boolean;
  content_title?: string;
  content_tags?: string[];
}

export interface TextGenerationResponse {
  generated_text: string;
  model_provider: string;
  model_name: string;
  generation_params: Record<string, any>;
  usage_stats: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  content_id?: number; // 如果保存到内容库
}

export interface TextAnalyseRequest {
  text: string;
  analysis_types: ('sentiment' | 'keywords' | 'summary' | 'readability')[];
}

export interface TextAnalyseResponse {
  text_id: string;
  analysis_results: {
    sentiment?: {
      score: number;
      label: 'positive' | 'neutral' | 'negative';
      confidence: number;
    };
    keywords?: Array<{
      keyword: string;
      score: number;
      frequency: number;
    }>;
    summary?: {
      summary_text: string;
      compression_ratio: number;
    };
    readability?: {
      flesch_score: number;
      reading_level: string;
      avg_sentence_length: number;
      avg_syllables_per_word: number;
    };
  };
}

export interface TextTemplateBasic {
  template_id: number;
  template_name: string;
  template_type: 'article' | 'marketing' | 'social' | 'email' | 'blog';
  template_content: string;
  template_variables: Array<{
    name: string;
    type: 'text' | 'number' | 'select';
    required: boolean;
    default_value?: any;
    options?: string[];
  }>;
  template_category: string;
  template_tags: string[];
  usage_count: number;
  is_public: boolean;
  created_by: number;
  created_at: string;
  updated_at: string;
}

export interface TextTemplateCreateRequest {
  template_name: string;
  template_type: TextTemplateBasic['template_type'];
  template_content: string;
  template_variables: TextTemplateBasic['template_variables'];
  template_category: string;
  template_tags?: string[];
  is_public?: boolean;
}

export interface TextTemplateRenderRequest {
  template_id: number;
  variables: Record<string, any>;
  save_to_content?: boolean;
  content_title?: string;
}

class TextContentApiService {
  private baseUrl = '/text';

  /**
   * 获取文本内容列表
   * [services][api][text_content_api][get_content_list]
   */
  async text_content_api_get_content_list(
    pagination: PaginationParams = {},
    filters?: {
      content_type?: TextContentBasic['content_type'];
      content_status?: TextContentBasic['content_status'];
      search?: string;
      tags?: string[];
      date_from?: string;
      date_to?: string;
    }
  ): Promise<ApiResponse<PaginatedResponse<TextContentBasic>>> {
    return httpRequestWrapper.http_request_wrapper_paginated_get(
      `${this.baseUrl}/content`,
      pagination,
      filters
    );
  }

  /**
   * 获取单个文本内容
   * [services][api][text_content_api][get_content_detail]
   */
  async text_content_api_get_content_detail(
    contentId: number
  ): Promise<ApiResponse<TextContentBasic>> {
    return httpRequestWrapper.http_request_wrapper_get(
      `${this.baseUrl}/content/${contentId}`
    );
  }

  /**
   * 创建文本内容
   * [services][api][text_content_api][create_content]
   */
  async text_content_api_create_content(
    data: TextContentCreateRequest
  ): Promise<ApiResponse<TextContentBasic>> {
    return httpRequestWrapper.http_request_wrapper_post(
      `${this.baseUrl}/content`,
      data,
      {
        successMessage: '文本内容创建成功',
        showLoading: true,
        loadingText: '正在创建内容...'
      }
    );
  }

  /**
   * 更新文本内容
   * [services][api][text_content_api][update_content]
   */
  async text_content_api_update_content(
    data: TextContentUpdateRequest
  ): Promise<ApiResponse<TextContentBasic>> {
    return httpRequestWrapper.http_request_wrapper_put(
      `${this.baseUrl}/content/${data.content_id}`,
      data,
      {
        successMessage: '文本内容更新成功',
        showLoading: true,
        loadingText: '正在更新内容...'
      }
    );
  }

  /**
   * 删除文本内容
   * [services][api][text_content_api][delete_content]
   */
  async text_content_api_delete_content(
    contentId: number
  ): Promise<ApiResponse<void>> {
    return httpRequestWrapper.http_request_wrapper_delete(
      `${this.baseUrl}/content/${contentId}`,
      {
        successMessage: '文本内容删除成功'
      }
    );
  }

  /**
   * 批量删除文本内容
   * [services][api][text_content_api][batch_delete_content]
   */
  async text_content_api_batch_delete_content(
    contentIds: number[]
  ): Promise<ApiResponse<void>> {
    return httpRequestWrapper.http_request_wrapper_post(
      `${this.baseUrl}/content/batch-delete`,
      { content_ids: contentIds },
      {
        successMessage: `成功删除 ${contentIds.length} 个文本内容`,
        showLoading: true,
        loadingText: '正在批量删除...'
      }
    );
  }

  /**
   * AI文本生成
   * [services][api][text_content_api][generate_text]
   */
  async text_content_api_generate_text(
    data: TextGenerationRequest
  ): Promise<ApiResponse<TextGenerationResponse>> {
    return httpRequestWrapper.http_request_wrapper_post(
      `${this.baseUrl}/generate`,
      data,
      {
        showLoading: true,
        loadingText: '正在生成文本...',
        retryCount: 2
      }
    );
  }

  /**
   * 批量AI文本生成
   * [services][api][text_content_api][batch_generate_text]
   */
  async text_content_api_batch_generate_text(
    requests: TextGenerationRequest[]
  ): Promise<ApiResponse<TextGenerationResponse[]>> {
    return httpRequestWrapper.http_request_wrapper_post(
      `${this.baseUrl}/generate/batch`,
      { requests },
      {
        showLoading: true,
        loadingText: `正在批量生成 ${requests.length} 个文本...`,
        retryCount: 2
      }
    );
  }

  /**
   * 文本分析
   * [services][api][text_content_api][analyse_text]
   */
  async text_content_api_analyse_text(
    data: TextAnalyseRequest
  ): Promise<ApiResponse<TextAnalyseResponse>> {
    return httpRequestWrapper.http_request_wrapper_post(
      `${this.baseUrl}/analyse`,
      data,
      {
        showLoading: true,
        loadingText: '正在分析文本...'
      }
    );
  }

  /**
   * 获取模板列表
   * [services][api][text_content_api][get_template_list]
   */
  async text_content_api_get_template_list(
    pagination: PaginationParams = {},
    filters?: {
      template_type?: TextTemplateBasic['template_type'];
      template_category?: string;
      search?: string;
      is_public?: boolean;
    }
  ): Promise<ApiResponse<PaginatedResponse<TextTemplateBasic>>> {
    return httpRequestWrapper.http_request_wrapper_paginated_get(
      `${this.baseUrl}/template`,
      pagination,
      filters
    );
  }

  /**
   * 获取模板详情
   * [services][api][text_content_api][get_template_detail]
   */
  async text_content_api_get_template_detail(
    templateId: number
  ): Promise<ApiResponse<TextTemplateBasic>> {
    return httpRequestWrapper.http_request_wrapper_get(
      `${this.baseUrl}/template/${templateId}`
    );
  }

  /**
   * 创建模板
   * [services][api][text_content_api][create_template]
   */
  async text_content_api_create_template(
    data: TextTemplateCreateRequest
  ): Promise<ApiResponse<TextTemplateBasic>> {
    return httpRequestWrapper.http_request_wrapper_post(
      `${this.baseUrl}/template`,
      data,
      {
        successMessage: '模板创建成功',
        showLoading: true,
        loadingText: '正在创建模板...'
      }
    );
  }

  /**
   * 渲染模板
   * [services][api][text_content_api][render_template]
   */
  async text_content_api_render_template(
    data: TextTemplateRenderRequest
  ): Promise<ApiResponse<TextGenerationResponse>> {
    return httpRequestWrapper.http_request_wrapper_post(
      `${this.baseUrl}/template/${data.template_id}/render`,
      data,
      {
        showLoading: true,
        loadingText: '正在渲染模板...'
      }
    );
  }

  /**
   * 获取支持的AI模型列表
   * [services][api][text_content_api][get_available_models]
   */
  async text_content_api_get_available_models(): Promise<ApiResponse<Array<{
    provider: string;
    models: Array<{
      name: string;
      display_name: string;
      description: string;
      max_tokens: number;
      supports_streaming: boolean;
      pricing: {
        input_price_per_1k: number;
        output_price_per_1k: number;
      };
    }>;
  }>>> {
    return httpRequestWrapper.http_request_wrapper_get(
      `${this.baseUrl}/models`,
      undefined,
      { cache: 'force-cache' }
    );
  }

  /**
   * 获取使用统计
   * [services][api][text_content_api][get_usage_stats]
   */
  async text_content_api_get_usage_stats(
    period: 'day' | 'week' | 'month' = 'month'
  ): Promise<ApiResponse<{
    total_content_count: number;
    total_generation_count: number;
    total_tokens_used: number;
    generation_by_provider: Record<string, number>;
    content_by_type: Record<string, number>;
    daily_usage: Array<{
      date: string;
      content_count: number;
      generation_count: number;
      tokens_used: number;
    }>;
  }>> {
    return httpRequestWrapper.http_request_wrapper_get(
      `${this.baseUrl}/stats`,
      { period }
    );
  }
}

// 导出单例实例
export const textContentApiService = new TextContentApiService();