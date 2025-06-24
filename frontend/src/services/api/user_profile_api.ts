/**
 * User Profile API Layer
 * 用户档案API层 - [services][api][user_profile_api]
 */

import { axiosInstance } from '../axios/axios_instance';
import type { ApiResponse, PaginatedResponse } from './base_api_types';

// ================================
// 基础类型定义 - User Profile Types
// ================================

export type UserStatus = 'active' | 'inactive' | 'suspended' | 'pending';
export type AccountType = 'individual' | 'business' | 'enterprise' | 'trial';
export type SubscriptionStatus = 'active' | 'expired' | 'canceled' | 'pending';
export type NotificationChannel = 'email' | 'sms' | 'push' | 'in_app';
export type PrivacyLevel = 'public' | 'friends' | 'private';
export type ActivityType = 'login' | 'logout' | 'profile_update' | 'password_change' | 'api_call' | 'file_upload' | 'content_generate';

// 用户基础信息
export interface UserProfileBasic {
  user_id: number;
  username: string;
  email: string;
  phone?: string;
  display_name: string;
  avatar_url?: string;
  bio?: string;
  location?: string;
  website?: string;
  birth_date?: string;
  gender?: 'male' | 'female' | 'other' | 'prefer_not_to_say';
  user_status: UserStatus;
  account_type: AccountType;
  email_verified: boolean;
  phone_verified: boolean;
  created_at: string;
  updated_at: string;
  last_login_at?: string;
}

// 用户偏好设置
export interface UserPreferenceSettings {
  preference_id: number;
  user_id: number;
  language: string;
  timezone: string;
  theme: 'light' | 'dark' | 'auto';
  notification_settings: {
    email_notifications: boolean;
    sms_notifications: boolean;
    push_notifications: boolean;
    marketing_emails: boolean;
    security_alerts: boolean;
    feature_updates: boolean;
  };
  privacy_settings: {
    profile_visibility: PrivacyLevel;
    activity_visibility: PrivacyLevel;
    search_visibility: boolean;
    data_sharing: boolean;
  };
  ui_preferences: {
    sidebar_collapsed: boolean;
    table_density: 'compact' | 'middle' | 'large';
    default_page_size: number;
    auto_save: boolean;
  };
  created_at: string;
  updated_at: string;
}

// 用户活动记录
export interface UserActivityRecord {
  activity_id: number;
  user_id: number;
  activity_type: ActivityType;
  activity_description: string;
  ip_address: string;
  user_agent: string;
  device_info?: {
    device_type: string;
    browser: string;
    os: string;
    location?: string;
  };
  metadata?: Record<string, any>;
  created_at: string;
}

// 用户订阅信息
export interface UserSubscriptionInfo {
  subscription_id: number;
  user_id: number;
  plan_name: string;
  plan_type: AccountType;
  subscription_status: SubscriptionStatus;
  start_date: string;
  end_date?: string;
  auto_renewal: boolean;
  features: string[];
  quota_limits: {
    text_generation: number;
    image_generation: number;
    voice_synthesis: number;
    storage_space: number;
    api_calls: number;
  };
  usage_stats: {
    text_generation_used: number;
    image_generation_used: number;
    voice_synthesis_used: number;
    storage_used: number;
    api_calls_used: number;
  };
  billing_cycle: 'monthly' | 'yearly' | 'lifetime';
  amount: number;
  currency: string;
  created_at: string;
  updated_at: string;
}

// 用户安全设置
export interface UserSecuritySettings {
  security_id: number;
  user_id: number;
  two_factor_enabled: boolean;
  backup_codes: string[];
  trusted_devices: Array<{
    device_id: string;
    device_name: string;
    last_used: string;
    trusted_at: string;
  }>;
  login_sessions: Array<{
    session_id: string;
    ip_address: string;
    user_agent: string;
    location?: string;
    created_at: string;
    last_activity: string;
    is_current: boolean;
  }>;
  password_changed_at: string;
  security_questions: Array<{
    question: string;
    answer_hash: string;
  }>;
  created_at: string;
  updated_at: string;
}

// ================================
// 请求/响应类型 - User Profile DTOs
// ================================

// 用户信息更新请求
export interface UserProfileUpdateRequest {
  display_name?: string;
  bio?: string;
  location?: string;
  website?: string;
  birth_date?: string;
  gender?: 'male' | 'female' | 'other' | 'prefer_not_to_say';
  phone?: string;
}

// 头像上传请求
export interface AvatarUploadRequest {
  avatar_file: File;
  crop_params?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

// 密码修改请求
export interface PasswordChangeRequest {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

// 邮箱修改请求
export interface EmailChangeRequest {
  new_email: string;
  password: string;
}

// 手机号修改请求
export interface PhoneChangeRequest {
  new_phone: string;
  verification_code: string;
}

// 偏好设置更新请求
export interface PreferenceUpdateRequest {
  language?: string;
  timezone?: string;
  theme?: 'light' | 'dark' | 'auto';
  notification_settings?: Partial<UserPreferenceSettings['notification_settings']>;
  privacy_settings?: Partial<UserPreferenceSettings['privacy_settings']>;
  ui_preferences?: Partial<UserPreferenceSettings['ui_preferences']>;
}

// 两步验证设置请求
export interface TwoFactorSetupRequest {
  password: string;
  backup_method: 'sms' | 'email' | 'app';
  phone?: string;
}

// 两步验证验证请求
export interface TwoFactorVerifyRequest {
  verification_code: string;
  backup_code?: string;
}

// 账户删除请求
export interface AccountDeleteRequest {
  password: string;
  reason?: string;
  feedback?: string;
  delete_data: boolean;
}

// 数据导出请求
export interface DataExportRequest {
  data_types: ('profile' | 'activities' | 'content' | 'files' | 'settings')[];
  export_format: 'json' | 'csv' | 'xml';
  date_range?: {
    start_date: string;
    end_date: string;
  };
}

// 数据导出响应
export interface DataExportResponse {
  export_id: string;
  status: 'processing' | 'completed' | 'failed';
  download_url?: string;
  file_size?: number;
  created_at: string;
  expires_at: string;
}

// 使用统计响应
export interface UserUsageStatsResponse {
  period: string;
  subscription_info: UserSubscriptionInfo;
  daily_usage: Array<{
    date: string;
    text_generation: number;
    image_generation: number;
    voice_synthesis: number;
    api_calls: number;
    storage_used: number;
  }>;
  feature_usage: {
    most_used_features: Array<{
      feature: string;
      usage_count: number;
      percentage: number;
    }>;
    platform_distribution: Record<string, number>;
    peak_usage_hours: number[];
  };
  quota_alerts: Array<{
    feature: string;
    usage_percentage: number;
    alert_level: 'warning' | 'critical';
  }>;
}

// ================================
// User Profile API 类
// ================================

class UserProfileApiService {
  
  // ================================
  // 用户信息管理 API
  // ================================
  
  /**
   * 获取用户信息
   */
  async user_profile_api_get_profile(): Promise<ApiResponse<UserProfileBasic>> {
    const response = await axiosInstance.get('/user/profile');
    return response.data;
  }

  /**
   * 更新用户信息
   */
  async user_profile_api_update_profile(
    request: UserProfileUpdateRequest
  ): Promise<ApiResponse<UserProfileBasic>> {
    const response = await axiosInstance.put('/user/profile', request);
    return response.data;
  }

  /**
   * 上传头像
   */
  async user_profile_api_upload_avatar(
    request: AvatarUploadRequest
  ): Promise<ApiResponse<{ avatar_url: string }>> {
    const formData = new FormData();
    formData.append('avatar_file', request.avatar_file);
    
    if (request.crop_params) {
      formData.append('crop_params', JSON.stringify(request.crop_params));
    }

    const response = await axiosInstance.post('/user/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  /**
   * 删除头像
   */
  async user_profile_api_delete_avatar(): Promise<ApiResponse<boolean>> {
    const response = await axiosInstance.delete('/user/avatar');
    return response.data;
  }

  // ================================
  // 账户安全管理 API
  // ================================

  /**
   * 修改密码
   */
  async user_profile_api_change_password(
    request: PasswordChangeRequest
  ): Promise<ApiResponse<boolean>> {
    const response = await axiosInstance.post('/user/password/change', request);
    return response.data;
  }

  /**
   * 修改邮箱
   */
  async user_profile_api_change_email(
    request: EmailChangeRequest
  ): Promise<ApiResponse<boolean>> {
    const response = await axiosInstance.post('/user/email/change', request);
    return response.data;
  }

  /**
   * 验证新邮箱
   */
  async user_profile_api_verify_email(
    verification_code: string
  ): Promise<ApiResponse<boolean>> {
    const response = await axiosInstance.post('/user/email/verify', {
      verification_code
    });
    return response.data;
  }

  /**
   * 修改手机号
   */
  async user_profile_api_change_phone(
    request: PhoneChangeRequest
  ): Promise<ApiResponse<boolean>> {
    const response = await axiosInstance.post('/user/phone/change', request);
    return response.data;
  }

  /**
   * 发送手机验证码
   */
  async user_profile_api_send_phone_code(
    phone: string
  ): Promise<ApiResponse<boolean>> {
    const response = await axiosInstance.post('/user/phone/send-code', { phone });
    return response.data;
  }

  /**
   * 验证手机号
   */
  async user_profile_api_verify_phone(
    verification_code: string
  ): Promise<ApiResponse<boolean>> {
    const response = await axiosInstance.post('/user/phone/verify', {
      verification_code
    });
    return response.data;
  }

  // ================================
  // 两步验证管理 API
  // ================================

  /**
   * 获取安全设置
   */
  async user_profile_api_get_security_settings(): Promise<ApiResponse<UserSecuritySettings>> {
    const response = await axiosInstance.get('/user/security');
    return response.data;
  }

  /**
   * 设置两步验证
   */
  async user_profile_api_setup_two_factor(
    request: TwoFactorSetupRequest
  ): Promise<ApiResponse<{
    qr_code?: string;
    backup_codes: string[];
    secret?: string;
  }>> {
    const response = await axiosInstance.post('/user/security/2fa/setup', request);
    return response.data;
  }

  /**
   * 验证两步验证设置
   */
  async user_profile_api_verify_two_factor_setup(
    request: TwoFactorVerifyRequest
  ): Promise<ApiResponse<boolean>> {
    const response = await axiosInstance.post('/user/security/2fa/verify-setup', request);
    return response.data;
  }

  /**
   * 禁用两步验证
   */
  async user_profile_api_disable_two_factor(
    password: string
  ): Promise<ApiResponse<boolean>> {
    const response = await axiosInstance.post('/user/security/2fa/disable', { password });
    return response.data;
  }

  /**
   * 生成新的备用代码
   */
  async user_profile_api_regenerate_backup_codes(
    password: string
  ): Promise<ApiResponse<{ backup_codes: string[] }>> {
    const response = await axiosInstance.post('/user/security/backup-codes', { password });
    return response.data;
  }

  /**
   * 撤销登录会话
   */
  async user_profile_api_revoke_session(
    sessionId: string
  ): Promise<ApiResponse<boolean>> {
    const response = await axiosInstance.delete(`/user/security/sessions/${sessionId}`);
    return response.data;
  }

  /**
   * 撤销所有其他会话
   */
  async user_profile_api_revoke_all_sessions(): Promise<ApiResponse<boolean>> {
    const response = await axiosInstance.delete('/user/security/sessions/all');
    return response.data;
  }

  // ================================
  // 偏好设置管理 API
  // ================================

  /**
   * 获取偏好设置
   */
  async user_profile_api_get_preferences(): Promise<ApiResponse<UserPreferenceSettings>> {
    const response = await axiosInstance.get('/user/preferences');
    return response.data;
  }

  /**
   * 更新偏好设置
   */
  async user_profile_api_update_preferences(
    request: PreferenceUpdateRequest
  ): Promise<ApiResponse<UserPreferenceSettings>> {
    const response = await axiosInstance.put('/user/preferences', request);
    return response.data;
  }

  /**
   * 重置偏好设置
   */
  async user_profile_api_reset_preferences(): Promise<ApiResponse<UserPreferenceSettings>> {
    const response = await axiosInstance.post('/user/preferences/reset');
    return response.data;
  }

  // ================================
  // 活动记录和统计 API
  // ================================

  /**
   * 获取活动记录
   */
  async user_profile_api_get_activities(
    page: number = 1,
    pageSize: number = 20,
    activityType?: ActivityType,
    dateRange?: { start_date: string; end_date: string }
  ): Promise<ApiResponse<PaginatedResponse<UserActivityRecord>>> {
    const response = await axiosInstance.get('/user/activities', {
      params: {
        page,
        page_size: pageSize,
        activity_type: activityType,
        ...dateRange
      }
    });
    return response.data;
  }

  /**
   * 获取使用统计
   */
  async user_profile_api_get_usage_stats(
    period: 'day' | 'week' | 'month' | 'year' = 'month'
  ): Promise<ApiResponse<UserUsageStatsResponse>> {
    const response = await axiosInstance.get('/user/usage-stats', {
      params: { period }
    });
    return response.data;
  }

  /**
   * 获取订阅信息
   */
  async user_profile_api_get_subscription(): Promise<ApiResponse<UserSubscriptionInfo>> {
    const response = await axiosInstance.get('/user/subscription');
    return response.data;
  }

  // ================================
  // 数据管理 API
  // ================================

  /**
   * 导出用户数据
   */
  async user_profile_api_export_data(
    request: DataExportRequest
  ): Promise<ApiResponse<DataExportResponse>> {
    const response = await axiosInstance.post('/user/data/export', request);
    return response.data;
  }

  /**
   * 获取数据导出状态
   */
  async user_profile_api_get_export_status(
    exportId: string
  ): Promise<ApiResponse<DataExportResponse>> {
    const response = await axiosInstance.get(`/user/data/export/${exportId}`);
    return response.data;
  }

  /**
   * 删除账户
   */
  async user_profile_api_delete_account(
    request: AccountDeleteRequest
  ): Promise<ApiResponse<{
    deletion_token: string;
    deletion_date: string;
  }>> {
    const response = await axiosInstance.post('/user/account/delete', request);
    return response.data;
  }

  /**
   * 取消账户删除
   */
  async user_profile_api_cancel_account_deletion(
    deletionToken: string
  ): Promise<ApiResponse<boolean>> {
    const response = await axiosInstance.post('/user/account/cancel-deletion', {
      deletion_token: deletionToken
    });
    return response.data;
  }

  // ================================
  // 通知管理 API
  // ================================

  /**
   * 测试通知设置
   */
  async user_profile_api_test_notification(
    channel: NotificationChannel
  ): Promise<ApiResponse<boolean>> {
    const response = await axiosInstance.post('/user/notifications/test', { channel });
    return response.data;
  }

  /**
   * 获取通知历史
   */
  async user_profile_api_get_notification_history(
    page: number = 1,
    pageSize: number = 20
  ): Promise<ApiResponse<PaginatedResponse<{
    notification_id: number;
    title: string;
    content: string;
    channel: NotificationChannel;
    status: 'sent' | 'failed' | 'pending';
    created_at: string;
  }>>> {
    const response = await axiosInstance.get('/user/notifications/history', {
      params: { page, page_size: pageSize }
    });
    return response.data;
  }
}

// 导出服务实例
export const userProfileApiService = new UserProfileApiService();
export default userProfileApiService;