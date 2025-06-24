/**
 * Image Service API Layer
 * 图像服务API层 - [services][api][image_service_api]
 */

import { axiosInstance } from '../axios/axios_instance';
import type { ApiResponse, PaginatedResponse } from './base_api_types';

// ================================
// 基础类型定义 - Image Service Types
// ================================

export type ImagePlatformType = 'doubao' | 'dalle' | 'midjourney' | 'stable_diffusion' | 'azure';
export type ImageStyle = 'realistic' | 'anime' | 'cartoon' | 'oil_painting' | 'watercolor' | 'sketch' | 'digital_art';
export type ImageRatio = '1:1' | '16:9' | '9:16' | '4:3' | '3:4' | '2:1' | '1:2';
export type ImageQuality = 'draft' | 'standard' | 'high' | 'ultra';
export type ImageStatus = 'processing' | 'completed' | 'failed' | 'pending';
export type ContentFilterLevel = 'strict' | 'moderate' | 'permissive';

// 图像内容基础信息
export interface ImageContentBasic {
  image_id: number;
  text_id?: number;
  image_title: string;
  image_url?: string;
  thumbnail_url?: string;
  image_width: number;
  image_height: number;
  image_size: number;
  image_format: string;
  platform_type: ImagePlatformType;
  generation_params?: Record<string, any>;
  image_status: ImageStatus;
  created_at: string;
  updated_at: string;
}

// 图像模板基础信息
export interface ImageTemplateBasic {
  template_id: number;
  template_name: string;
  template_type: 'style' | 'prompt' | 'composition';
  template_description?: string;
  template_prompt: string;
  template_params?: Record<string, any>;
  preview_image_url?: string;
  platform_type: ImagePlatformType;
  is_public: boolean;
  usage_count: number;
  created_at: string;
  updated_at: string;
}

// ================================
// 请求/响应类型 - Image Service DTOs
// ================================

// 图像生成请求
export interface ImageGenerationRequest {
  prompt: string;
  negative_prompt?: string;
  platform_type?: ImagePlatformType;
  generation_params?: {
    style?: ImageStyle;
    aspect_ratio?: ImageRatio;
    quality?: ImageQuality;
    steps?: number;           // 生成步数 10-100
    guidance_scale?: number;  // 引导强度 1-20
    seed?: number;           // 随机种子
    num_images?: number;     // 生成数量 1-4
    content_filter?: ContentFilterLevel;
  };
  reference_images?: string[];  // 参考图像URL
  save_to_library?: boolean;
  image_title?: string;
}

// 图像生成响应
export interface ImageGenerationResponse {
  image_id: number;
  image_urls: string[];
  thumbnail_urls: string[];
  generation_time: number;
  platform_used: ImagePlatformType;
  prompt_used: string;
  seed_used?: number;
  cost_info?: {
    credits_used: number;
    cost_amount: number;
    currency: string;
  };
  safety_results?: {
    is_safe: boolean;
    flagged_categories: string[];
    confidence_scores: Record<string, number>;
  };
}

// 图像编辑请求
export interface ImageEditRequest {
  source_image_url: string;
  edit_type: 'inpaint' | 'outpaint' | 'variation' | 'upscale' | 'style_transfer';
  prompt?: string;
  mask_image_url?: string;  // 遮罩图像(用于inpaint)
  edit_params?: {
    strength?: number;      // 编辑强度 0-1
    preserve_original?: boolean;
    target_size?: {
      width: number;
      height: number;
    };
    style_reference?: string;
  };
  platform_type?: ImagePlatformType;
}

// 图像编辑响应
export interface ImageEditResponse {
  image_id: number;
  original_image_url: string;
  edited_image_url: string;
  edit_type: string;
  processing_time: number;
  platform_used: ImagePlatformType;
}

// 图像分析请求
export interface ImageAnalyseRequest {
  image_id?: number;
  image_url?: string;
  analysis_types: ('objects' | 'faces' | 'text' | 'colors' | 'style' | 'quality' | 'safety')[];
}

// 图像分析响应
export interface ImageAnalyseResponse {
  analysis_id: string;
  image_info: {
    width: number;
    height: number;
    format: string;
    file_size: number;
  };
  analysis_results: {
    objects?: {
      detected_objects: Array<{
        label: string;
        confidence: number;
        bounding_box: {
          x: number;
          y: number;
          width: number;
          height: number;
        };
      }>;
    };
    faces?: {
      detected_faces: Array<{
        confidence: number;
        age_range?: string;
        gender?: string;
        emotions?: Record<string, number>;
        bounding_box: {
          x: number;
          y: number;
          width: number;
          height: number;
        };
      }>;
    };
    text?: {
      extracted_text: string;
      text_regions: Array<{
        text: string;
        confidence: number;
        bounding_box: {
          x: number;
          y: number;
          width: number;
          height: number;
        };
      }>;
    };
    colors?: {
      dominant_colors: Array<{
        color: string;
        percentage: number;
        hex: string;
      }>;
      color_palette: string[];
    };
    style?: {
      detected_style: ImageStyle;
      confidence: number;
      style_scores: Record<string, number>;
    };
    quality?: {
      overall_score: number;
      sharpness: number;
      brightness: number;
      contrast: number;
      noise_level: number;
    };
    safety?: {
      is_safe: boolean;
      adult_content: number;
      violence: number;
      medical: number;
      racy: number;
    };
  };
}

// 模板创建请求
export interface ImageTemplateCreateRequest {
  template_name: string;
  template_type: 'style' | 'prompt' | 'composition';
  template_description?: string;
  template_prompt: string;
  template_params?: Record<string, any>;
  platform_type: ImagePlatformType;
  is_public: boolean;
}

// 模板更新请求
export interface ImageTemplateUpdateRequest {
  template_id: number;
  template_name?: string;
  template_description?: string;
  template_prompt?: string;
  template_params?: Record<string, any>;
  is_public?: boolean;
}

// 批量生成请求
export interface ImageBatchGenerationRequest {
  prompts: Array<{
    prompt: string;
    negative_prompt?: string;
    image_title?: string;
  }>;
  common_params?: Partial<ImageGenerationRequest>;
  batch_size?: number;
}

// 平台模型列表响应
export interface PlatformModelListResponse {
  platform_type: ImagePlatformType;
  models: Array<{
    model_id: string;
    model_name: string;
    model_description?: string;
    supported_features: string[];
    max_resolution: {
      width: number;
      height: number;
    };
    supported_ratios: ImageRatio[];
    is_premium?: boolean;
  }>;
}

// 使用统计响应
export interface ImageUsageStatsResponse {
  period: string;
  total_generation_count: number;
  total_images_generated: number;
  total_credits_used: number;
  total_cost: number;
  platform_usage: Record<ImagePlatformType, {
    generation_count: number;
    images_generated: number;
    credits_used: number;
    cost: number;
  }>;
  style_usage: Array<{
    style: ImageStyle;
    usage_count: number;
    percentage: number;
  }>;
  resolution_usage: Array<{
    resolution: string;
    usage_count: number;
    percentage: number;
  }>;
}

// ================================
// Image Service API 类
// ================================

class ImageServiceApiService {
  
  // ================================
  // 图像生成相关 API
  // ================================
  
  /**
   * 图像生成
   */
  async image_service_api_generate_image(
    request: ImageGenerationRequest
  ): Promise<ApiResponse<ImageGenerationResponse>> {
    const response = await axiosInstance.post('/image/generate', request);
    return response.data;
  }

  /**
   * 获取图像列表
   */
  async image_service_api_get_image_list(
    page: number = 1,
    pageSize: number = 20,
    filters?: {
      platform_type?: ImagePlatformType;
      image_status?: ImageStatus;
      style?: ImageStyle;
      date_range?: [string, string];
    }
  ): Promise<ApiResponse<PaginatedResponse<ImageContentBasic>>> {
    const response = await axiosInstance.get('/image/list', {
      params: {
        page,
        page_size: pageSize,
        ...filters
      }
    });
    return response.data;
  }

  /**
   * 获取图像详情
   */
  async image_service_api_get_image_detail(
    imageId: number
  ): Promise<ApiResponse<ImageContentBasic>> {
    const response = await axiosInstance.get(`/image/${imageId}`);
    return response.data;
  }

  /**
   * 删除图像
   */
  async image_service_api_delete_image(
    imageId: number
  ): Promise<ApiResponse<boolean>> {
    const response = await axiosInstance.delete(`/image/${imageId}`);
    return response.data;
  }

  // ================================
  // 图像编辑相关 API
  // ================================

  /**
   * 图像编辑
   */
  async image_service_api_edit_image(
    request: ImageEditRequest
  ): Promise<ApiResponse<ImageEditResponse>> {
    const response = await axiosInstance.post('/image/edit', request);
    return response.data;
  }

  /**
   * 图像变体生成
   */
  async image_service_api_create_variation(
    imageId: number,
    params?: {
      num_variations?: number;
      variation_strength?: number;
      preserve_style?: boolean;
    }
  ): Promise<ApiResponse<ImageGenerationResponse>> {
    const response = await axiosInstance.post(`/image/${imageId}/variation`, params);
    return response.data;
  }

  /**
   * 图像放大
   */
  async image_service_api_upscale_image(
    imageId: number,
    params?: {
      scale_factor?: number;  // 2x, 4x, 8x
      enhance_quality?: boolean;
    }
  ): Promise<ApiResponse<ImageEditResponse>> {
    const response = await axiosInstance.post(`/image/${imageId}/upscale`, params);
    return response.data;
  }

  // ================================
  // 模板管理相关 API
  // ================================

  /**
   * 获取模板列表
   */
  async image_service_api_get_template_list(
    page: number = 1,
    pageSize: number = 20,
    filters?: {
      template_type?: 'style' | 'prompt' | 'composition';
      platform_type?: ImagePlatformType;
      is_public?: boolean;
    }
  ): Promise<ApiResponse<PaginatedResponse<ImageTemplateBasic>>> {
    const response = await axiosInstance.get('/image/template/list', {
      params: {
        page,
        page_size: pageSize,
        ...filters
      }
    });
    return response.data;
  }

  /**
   * 获取模板详情
   */
  async image_service_api_get_template_detail(
    templateId: number
  ): Promise<ApiResponse<ImageTemplateBasic>> {
    const response = await axiosInstance.get(`/image/template/${templateId}`);
    return response.data;
  }

  /**
   * 创建模板
   */
  async image_service_api_create_template(
    request: ImageTemplateCreateRequest
  ): Promise<ApiResponse<ImageTemplateBasic>> {
    const response = await axiosInstance.post('/image/template/create', request);
    return response.data;
  }

  /**
   * 更新模板
   */
  async image_service_api_update_template(
    request: ImageTemplateUpdateRequest
  ): Promise<ApiResponse<ImageTemplateBasic>> {
    const response = await axiosInstance.put('/image/template/update', request);
    return response.data;
  }

  /**
   * 删除模板
   */
  async image_service_api_delete_template(
    templateId: number
  ): Promise<ApiResponse<boolean>> {
    const response = await axiosInstance.delete(`/image/template/${templateId}`);
    return response.data;
  }

  /**
   * 使用模板生成图像
   */
  async image_service_api_generate_from_template(
    templateId: number,
    overrideParams?: Partial<ImageGenerationRequest>
  ): Promise<ApiResponse<ImageGenerationResponse>> {
    const response = await axiosInstance.post(`/image/template/${templateId}/generate`, overrideParams);
    return response.data;
  }

  // ================================
  // 平台管理相关 API
  // ================================

  /**
   * 获取平台模型列表
   */
  async image_service_api_get_platform_models(
    platformType: ImagePlatformType
  ): Promise<ApiResponse<PlatformModelListResponse>> {
    const response = await axiosInstance.get(`/image/platform/${platformType}/models`);
    return response.data;
  }

  /**
   * 测试平台连接
   */
  async image_service_api_test_platform_connection(
    platformType: ImagePlatformType
  ): Promise<ApiResponse<{
    is_connected: boolean;
    response_time: number;
    error_message?: string;
    platform_info?: Record<string, any>;
  }>> {
    const response = await axiosInstance.post(`/image/platform/${platformType}/test`);
    return response.data;
  }

  // ================================
  // 图像分析相关 API
  // ================================

  /**
   * 图像分析
   */
  async image_service_api_analyse_image(
    request: ImageAnalyseRequest
  ): Promise<ApiResponse<ImageAnalyseResponse>> {
    const response = await axiosInstance.post('/image/analyse', request);
    return response.data;
  }

  // ================================
  // 统计分析相关 API
  // ================================

  /**
   * 获取使用统计
   */
  async image_service_api_get_usage_stats(
    period: 'day' | 'week' | 'month' | 'year' = 'month'
  ): Promise<ApiResponse<ImageUsageStatsResponse>> {
    const response = await axiosInstance.get('/image/stats/usage', {
      params: { period }
    });
    return response.data;
  }

  // ================================
  // 批量操作 API
  // ================================

  /**
   * 批量生成图像
   */
  async image_service_api_batch_generate(
    request: ImageBatchGenerationRequest
  ): Promise<ApiResponse<{
    task_id: string;
    total_count: number;
    estimated_time: number;
  }>> {
    const response = await axiosInstance.post('/image/batch/generate', request);
    return response.data;
  }

  /**
   * 获取批量任务状态
   */
  async image_service_api_get_batch_status(
    taskId: string
  ): Promise<ApiResponse<{
    task_id: string;
    status: 'processing' | 'completed' | 'failed' | 'partial';
    progress: number;
    completed_count: number;
    failed_count: number;
    results?: ImageGenerationResponse[];
  }>> {
    const response = await axiosInstance.get(`/image/batch/status/${taskId}`);
    return response.data;
  }

  // ================================
  // 文件上传相关 API
  // ================================

  /**
   * 上传参考图像
   */
  async image_service_api_upload_reference(
    file: File,
    purpose: 'reference' | 'mask' | 'source' = 'reference'
  ): Promise<ApiResponse<{
    file_id: string;
    file_url: string;
    file_name: string;
    file_size: number;
  }>> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('purpose', purpose);

    const response = await axiosInstance.post('/image/upload/reference', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }
}

// 导出服务实例
export const imageServiceApiService = new ImageServiceApiService();
export default imageServiceApiService;