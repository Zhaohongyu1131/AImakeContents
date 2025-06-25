/**
 * User Profile Store
 * 用户档案状态管理 - [stores][user_profile][user_profile_store]
 */

import { create } from 'zustand';
import { devtools, subscribeWithSelector } from 'zustand/middleware';
import { userProfileApiService } from '../../services/api/user_profile_api';
import type {
  UserProfileBasic,
  UserPreferenceSettings,
  UserSecuritySettings,
  UserActivityRecord,
  UserSubscriptionInfo,
  UserUsageStatsResponse,
  DataExportResponse,
  UserProfileUpdateRequest,
  AvatarUploadRequest,
  PasswordChangeRequest,
  EmailChangeRequest,
  PhoneChangeRequest,
  PreferenceUpdateRequest,
  TwoFactorSetupRequest,
  TwoFactorVerifyRequest,
  AccountDeleteRequest,
  DataExportRequest,
  ActivityType,
  NotificationChannel
} from '../../services/api/user_profile_api';
import type { PaginatedResponse } from '../../services/api/base_api_types';

// ================================
// State 接口定义
// ================================

interface UserProfileState {
  // ================================
  // 用户信息状态
  // ================================
  userProfile: UserProfileBasic | null;
  profileLoading: boolean;
  profileUpdateLoading: boolean;
  
  // ================================
  // 头像管理状态
  // ================================
  avatarUploadLoading: boolean;
  avatarPreview: string | null;

  // ================================
  // 安全设置状态
  // ================================
  securitySettings: UserSecuritySettings | null;
  securityLoading: boolean;
  passwordChangeLoading: boolean;
  emailChangeLoading: boolean;
  phoneChangeLoading: boolean;
  twoFactorSetupLoading: boolean;
  twoFactorSetupData: {
    qr_code?: string;
    backup_codes: string[];
    secret?: string;
  } | null;

  // ================================
  // 偏好设置状态
  // ================================
  preferences: UserPreferenceSettings | null;
  preferencesLoading: boolean;
  preferencesUpdateLoading: boolean;

  // ================================
  // 活动记录状态
  // ================================
  activities: PaginatedResponse<UserActivityRecord> | null;
  activitiesLoading: boolean;

  // ================================
  // 订阅和使用统计状态
  // ================================
  subscription: UserSubscriptionInfo | null;
  usageStats: UserUsageStatsResponse | null;
  subscriptionLoading: boolean;
  usageStatsLoading: boolean;

  // ================================
  // 数据导出状态
  // ================================
  dataExports: DataExportResponse[];
  exportLoading: boolean;
  currentExport: DataExportResponse | null;

  // ================================
  // 账户删除状态
  // ================================
  accountDeletionLoading: boolean;
  deletionToken: string | null;
  deletionDate: string | null;

  // ================================
  // 通知管理状态
  // ================================
  notificationHistory: PaginatedResponse<{
    notification_id: number;
    title: string;
    content: string;
    channel: NotificationChannel;
    status: 'sent' | 'failed' | 'pending';
    created_at: string;
  }> | null;
  notificationLoading: boolean;

  // ================================
  // 通用状态
  // ================================
  error: string | null;
  loading: boolean;
  successMessage: string | null;

  // ================================
  // Actions - 用户信息管理
  // ================================
  user_profile_store_load_profile: () => Promise<void>;
  
  user_profile_store_update_profile: (
    request: UserProfileUpdateRequest
  ) => Promise<boolean>;

  user_profile_store_upload_avatar: (
    request: AvatarUploadRequest
  ) => Promise<boolean>;

  user_profile_store_delete_avatar: () => Promise<boolean>;

  user_profile_store_set_avatar_preview: (url: string | null) => void;

  // ================================
  // Actions - 安全设置管理
  // ================================
  user_profile_store_load_security_settings: () => Promise<void>;

  user_profile_store_change_password: (
    request: PasswordChangeRequest
  ) => Promise<boolean>;

  user_profile_store_change_email: (
    request: EmailChangeRequest
  ) => Promise<boolean>;

  user_profile_store_verify_email: (
    verificationCode: string
  ) => Promise<boolean>;

  user_profile_store_change_phone: (
    request: PhoneChangeRequest
  ) => Promise<boolean>;

  user_profile_store_send_phone_code: (phone: string) => Promise<boolean>;

  user_profile_store_verify_phone: (
    verificationCode: string
  ) => Promise<boolean>;

  user_profile_store_setup_two_factor: (
    request: TwoFactorSetupRequest
  ) => Promise<boolean>;

  user_profile_store_verify_two_factor_setup: (
    request: TwoFactorVerifyRequest
  ) => Promise<boolean>;

  user_profile_store_disable_two_factor: (password: string) => Promise<boolean>;

  user_profile_store_regenerate_backup_codes: (password: string) => Promise<boolean>;

  user_profile_store_revoke_session: (sessionId: string) => Promise<boolean>;

  user_profile_store_revoke_all_sessions: () => Promise<boolean>;

  // ================================
  // Actions - 偏好设置管理
  // ================================
  user_profile_store_load_preferences: () => Promise<void>;

  user_profile_store_update_preferences: (
    request: PreferenceUpdateRequest
  ) => Promise<boolean>;

  user_profile_store_reset_preferences: () => Promise<boolean>;

  // ================================
  // Actions - 活动记录和统计
  // ================================
  user_profile_store_load_activities: (
    page?: number,
    pageSize?: number,
    activityType?: ActivityType,
    dateRange?: { start_date: string; end_date: string }
  ) => Promise<void>;

  user_profile_store_load_usage_stats: (
    period?: 'day' | 'week' | 'month' | 'year'
  ) => Promise<void>;

  user_profile_store_load_subscription: () => Promise<void>;

  // ================================
  // Actions - 数据管理
  // ================================
  user_profile_store_export_data: (
    request: DataExportRequest
  ) => Promise<boolean>;

  user_profile_store_get_export_status: (exportId: string) => Promise<void>;

  user_profile_store_delete_account: (
    request: AccountDeleteRequest
  ) => Promise<boolean>;

  user_profile_store_cancel_account_deletion: (
    deletionToken: string
  ) => Promise<boolean>;

  // ================================
  // Actions - 通知管理
  // ================================
  user_profile_store_test_notification: (
    channel: NotificationChannel
  ) => Promise<boolean>;

  user_profile_store_load_notification_history: (
    page?: number,
    pageSize?: number
  ) => Promise<void>;

  // ================================
  // Actions - 工具方法
  // ================================
  user_profile_store_clear_errors: () => void;
  user_profile_store_clear_success_message: () => void;
  user_profile_store_clear_two_factor_setup: () => void;
}

// ================================
// Store 创建
// ================================

export const useUserProfileStore = create<UserProfileState>()(
  devtools(
    subscribeWithSelector((set, get) => ({
      // ================================
      // 初始状态
      // ================================
      userProfile: null,
      profileLoading: false,
      profileUpdateLoading: false,
      
      avatarUploadLoading: false,
      avatarPreview: null,

      securitySettings: null,
      securityLoading: false,
      passwordChangeLoading: false,
      emailChangeLoading: false,
      phoneChangeLoading: false,
      twoFactorSetupLoading: false,
      twoFactorSetupData: null,

      preferences: null,
      preferencesLoading: false,
      preferencesUpdateLoading: false,

      activities: null,
      activitiesLoading: false,

      subscription: null,
      usageStats: null,
      subscriptionLoading: false,
      usageStatsLoading: false,

      dataExports: [],
      exportLoading: false,
      currentExport: null,

      accountDeletionLoading: false,
      deletionToken: null,
      deletionDate: null,

      notificationHistory: null,
      notificationLoading: false,

      error: null,
      loading: false,
      successMessage: null,

      // ================================
      // Actions 实现
      // ================================

      // 用户信息管理
      user_profile_store_load_profile: async () => {
        set({ profileLoading: true, error: null });
        try {
          const response = await userProfileApiService.user_profile_api_get_profile();
          if (response.success && response.data) {
            set({ userProfile: response.data });
          } else {
            set({ error: response.message || '获取用户信息失败' });
          }
        } catch (error) {
          set({ error: '网络错误：获取用户信息失败' });
        } finally {
          set({ profileLoading: false });
        }
      },

      user_profile_store_update_profile: async (request: UserProfileUpdateRequest) => {
        set({ profileUpdateLoading: true, error: null });
        try {
          const response = await userProfileApiService.user_profile_api_update_profile(request);
          if (response.success && response.data) {
            set({ 
              userProfile: response.data,
              successMessage: '个人信息更新成功'
            });
            return true;
          } else {
            set({ error: response.message || '更新个人信息失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：更新个人信息失败' });
          return false;
        } finally {
          set({ profileUpdateLoading: false });
        }
      },

      user_profile_store_upload_avatar: async (request: AvatarUploadRequest) => {
        set({ avatarUploadLoading: true, error: null });
        try {
          const response = await userProfileApiService.user_profile_api_upload_avatar(request);
          if (response.success && response.data) {
            const { userProfile } = get();
            if (userProfile) {
              set({ 
                userProfile: { ...userProfile, avatar_url: response.data.avatar_url },
                successMessage: '头像上传成功',
                avatarPreview: null
              });
            }
            return true;
          } else {
            set({ error: response.message || '头像上传失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：头像上传失败' });
          return false;
        } finally {
          set({ avatarUploadLoading: false });
        }
      },

      user_profile_store_delete_avatar: async () => {
        set({ loading: true, error: null });
        try {
          const response = await userProfileApiService.user_profile_api_delete_avatar();
          if (response.success) {
            const { userProfile } = get();
            if (userProfile) {
              set({ 
                userProfile: { ...userProfile, avatar_url: undefined },
                successMessage: '头像删除成功'
              });
            }
            return true;
          } else {
            set({ error: response.message || '头像删除失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：头像删除失败' });
          return false;
        } finally {
          set({ loading: false });
        }
      },

      user_profile_store_set_avatar_preview: (url: string | null) => {
        set({ avatarPreview: url });
      },

      // 安全设置管理
      user_profile_store_load_security_settings: async () => {
        set({ securityLoading: true, error: null });
        try {
          const response = await userProfileApiService.user_profile_api_get_security_settings();
          if (response.success && response.data) {
            set({ securitySettings: response.data });
          } else {
            set({ error: response.message || '获取安全设置失败' });
          }
        } catch (error) {
          set({ error: '网络错误：获取安全设置失败' });
        } finally {
          set({ securityLoading: false });
        }
      },

      user_profile_store_change_password: async (request: PasswordChangeRequest) => {
        set({ passwordChangeLoading: true, error: null });
        try {
          const response = await userProfileApiService.user_profile_api_change_password(request);
          if (response.success) {
            set({ successMessage: '密码修改成功' });
            return true;
          } else {
            set({ error: response.message || '密码修改失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：密码修改失败' });
          return false;
        } finally {
          set({ passwordChangeLoading: false });
        }
      },

      user_profile_store_change_email: async (request: EmailChangeRequest) => {
        set({ emailChangeLoading: true, error: null });
        try {
          const response = await userProfileApiService.user_profile_api_change_email(request);
          if (response.success) {
            set({ successMessage: '邮箱修改申请已发送，请查收验证邮件' });
            return true;
          } else {
            set({ error: response.message || '邮箱修改失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：邮箱修改失败' });
          return false;
        } finally {
          set({ emailChangeLoading: false });
        }
      },

      user_profile_store_verify_email: async (verificationCode: string) => {
        set({ loading: true, error: null });
        try {
          const response = await userProfileApiService.user_profile_api_verify_email(verificationCode);
          if (response.success) {
            set({ successMessage: '邮箱验证成功' });
            // 刷新用户信息
            get().user_profile_store_load_profile();
            return true;
          } else {
            set({ error: response.message || '邮箱验证失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：邮箱验证失败' });
          return false;
        } finally {
          set({ loading: false });
        }
      },

      user_profile_store_change_phone: async (request: PhoneChangeRequest) => {
        set({ phoneChangeLoading: true, error: null });
        try {
          const response = await userProfileApiService.user_profile_api_change_phone(request);
          if (response.success) {
            set({ successMessage: '手机号修改成功' });
            // 刷新用户信息
            get().user_profile_store_load_profile();
            return true;
          } else {
            set({ error: response.message || '手机号修改失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：手机号修改失败' });
          return false;
        } finally {
          set({ phoneChangeLoading: false });
        }
      },

      user_profile_store_send_phone_code: async (phone: string) => {
        set({ loading: true, error: null });
        try {
          const response = await userProfileApiService.user_profile_api_send_phone_code(phone);
          if (response.success) {
            set({ successMessage: '验证码已发送' });
            return true;
          } else {
            set({ error: response.message || '验证码发送失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：验证码发送失败' });
          return false;
        } finally {
          set({ loading: false });
        }
      },

      user_profile_store_verify_phone: async (verificationCode: string) => {
        set({ loading: true, error: null });
        try {
          const response = await userProfileApiService.user_profile_api_verify_phone(verificationCode);
          if (response.success) {
            set({ successMessage: '手机号验证成功' });
            // 刷新用户信息
            get().user_profile_store_load_profile();
            return true;
          } else {
            set({ error: response.message || '手机号验证失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：手机号验证失败' });
          return false;
        } finally {
          set({ loading: false });
        }
      },

      user_profile_store_setup_two_factor: async (request: TwoFactorSetupRequest) => {
        set({ twoFactorSetupLoading: true, error: null });
        try {
          const response = await userProfileApiService.user_profile_api_setup_two_factor(request);
          if (response.success && response.data) {
            set({ twoFactorSetupData: response.data });
            return true;
          } else {
            set({ error: response.message || '两步验证设置失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：两步验证设置失败' });
          return false;
        } finally {
          set({ twoFactorSetupLoading: false });
        }
      },

      user_profile_store_verify_two_factor_setup: async (request: TwoFactorVerifyRequest) => {
        set({ loading: true, error: null });
        try {
          const response = await userProfileApiService.user_profile_api_verify_two_factor_setup(request);
          if (response.success) {
            set({ 
              successMessage: '两步验证设置成功',
              twoFactorSetupData: null
            });
            // 刷新安全设置
            get().user_profile_store_load_security_settings();
            return true;
          } else {
            set({ error: response.message || '两步验证验证失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：两步验证验证失败' });
          return false;
        } finally {
          set({ loading: false });
        }
      },

      user_profile_store_disable_two_factor: async (password: string) => {
        set({ loading: true, error: null });
        try {
          const response = await userProfileApiService.user_profile_api_disable_two_factor(password);
          if (response.success) {
            set({ successMessage: '两步验证已禁用' });
            // 刷新安全设置
            get().user_profile_store_load_security_settings();
            return true;
          } else {
            set({ error: response.message || '禁用两步验证失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：禁用两步验证失败' });
          return false;
        } finally {
          set({ loading: false });
        }
      },

      user_profile_store_regenerate_backup_codes: async (password: string) => {
        set({ loading: true, error: null });
        try {
          const response = await userProfileApiService.user_profile_api_regenerate_backup_codes(password);
          if (response.success && response.data) {
            const { securitySettings } = get();
            if (securitySettings) {
              set({ 
                securitySettings: {
                  ...securitySettings,
                  backup_codes: response.data.backup_codes
                },
                successMessage: '备用代码已重新生成'
              });
            }
            return true;
          } else {
            set({ error: response.message || '备用代码生成失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：备用代码生成失败' });
          return false;
        } finally {
          set({ loading: false });
        }
      },

      user_profile_store_revoke_session: async (sessionId: string) => {
        set({ loading: true, error: null });
        try {
          const response = await userProfileApiService.user_profile_api_revoke_session(sessionId);
          if (response.success) {
            set({ successMessage: '会话已撤销' });
            // 刷新安全设置
            get().user_profile_store_load_security_settings();
            return true;
          } else {
            set({ error: response.message || '会话撤销失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：会话撤销失败' });
          return false;
        } finally {
          set({ loading: false });
        }
      },

      user_profile_store_revoke_all_sessions: async () => {
        set({ loading: true, error: null });
        try {
          const response = await userProfileApiService.user_profile_api_revoke_all_sessions();
          if (response.success) {
            set({ successMessage: '所有其他会话已撤销' });
            // 刷新安全设置
            get().user_profile_store_load_security_settings();
            return true;
          } else {
            set({ error: response.message || '会话撤销失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：会话撤销失败' });
          return false;
        } finally {
          set({ loading: false });
        }
      },

      // 偏好设置管理
      user_profile_store_load_preferences: async () => {
        set({ preferencesLoading: true, error: null });
        try {
          const response = await userProfileApiService.user_profile_api_get_preferences();
          if (response.success && response.data) {
            set({ preferences: response.data });
          } else {
            set({ error: response.message || '获取偏好设置失败' });
          }
        } catch (error) {
          set({ error: '网络错误：获取偏好设置失败' });
        } finally {
          set({ preferencesLoading: false });
        }
      },

      user_profile_store_update_preferences: async (request: PreferenceUpdateRequest) => {
        set({ preferencesUpdateLoading: true, error: null });
        try {
          const response = await userProfileApiService.user_profile_api_update_preferences(request);
          if (response.success && response.data) {
            set({ 
              preferences: response.data,
              successMessage: '偏好设置更新成功'
            });
            return true;
          } else {
            set({ error: response.message || '偏好设置更新失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：偏好设置更新失败' });
          return false;
        } finally {
          set({ preferencesUpdateLoading: false });
        }
      },

      user_profile_store_reset_preferences: async () => {
        set({ loading: true, error: null });
        try {
          const response = await userProfileApiService.user_profile_api_reset_preferences();
          if (response.success && response.data) {
            set({ 
              preferences: response.data,
              successMessage: '偏好设置已重置'
            });
            return true;
          } else {
            set({ error: response.message || '偏好设置重置失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：偏好设置重置失败' });
          return false;
        } finally {
          set({ loading: false });
        }
      },

      // 活动记录和统计
      user_profile_store_load_activities: async (page = 1, pageSize = 20, activityType, dateRange) => {
        set({ activitiesLoading: true, error: null });
        try {
          const response = await userProfileApiService.user_profile_api_get_activities(
            page,
            pageSize,
            activityType,
            dateRange
          );
          if (response.success && response.data) {
            set({ activities: response.data });
          } else {
            set({ error: response.message || '获取活动记录失败' });
          }
        } catch (error) {
          set({ error: '网络错误：获取活动记录失败' });
        } finally {
          set({ activitiesLoading: false });
        }
      },

      user_profile_store_load_usage_stats: async (period = 'month') => {
        set({ usageStatsLoading: true, error: null });
        try {
          const response = await userProfileApiService.user_profile_api_get_usage_stats(period);
          if (response.success && response.data) {
            set({ usageStats: response.data });
          } else {
            set({ error: response.message || '获取使用统计失败' });
          }
        } catch (error) {
          set({ error: '网络错误：获取使用统计失败' });
        } finally {
          set({ usageStatsLoading: false });
        }
      },

      user_profile_store_load_subscription: async () => {
        set({ subscriptionLoading: true, error: null });
        try {
          const response = await userProfileApiService.user_profile_api_get_subscription();
          if (response.success && response.data) {
            set({ subscription: response.data });
          } else {
            set({ error: response.message || '获取订阅信息失败' });
          }
        } catch (error) {
          set({ error: '网络错误：获取订阅信息失败' });
        } finally {
          set({ subscriptionLoading: false });
        }
      },

      // 数据管理
      user_profile_store_export_data: async (request: DataExportRequest) => {
        set({ exportLoading: true, error: null });
        try {
          const response = await userProfileApiService.user_profile_api_export_data(request);
          if (response.success && response.data) {
            set(state => ({
              dataExports: [response.data, ...state.dataExports],
              currentExport: response.data,
              successMessage: '数据导出任务已启动'
            }));
            return true;
          } else {
            set({ error: response.message || '数据导出失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：数据导出失败' });
          return false;
        } finally {
          set({ exportLoading: false });
        }
      },

      user_profile_store_get_export_status: async (exportId: string) => {
        try {
          const response = await userProfileApiService.user_profile_api_get_export_status(exportId);
          if (response.success && response.data) {
            set(state => ({
              dataExports: state.dataExports.map(exp => 
                exp.export_id === exportId ? response.data : exp
              ),
              currentExport: state.currentExport?.export_id === exportId ? response.data : state.currentExport
            }));
          }
        } catch (error) {
          console.warn('Failed to get export status:', error);
        }
      },

      user_profile_store_delete_account: async (request: AccountDeleteRequest) => {
        set({ accountDeletionLoading: true, error: null });
        try {
          const response = await userProfileApiService.user_profile_api_delete_account(request);
          if (response.success && response.data) {
            set({ 
              deletionToken: response.data.deletion_token,
              deletionDate: response.data.deletion_date,
              successMessage: '账户删除申请已提交'
            });
            return true;
          } else {
            set({ error: response.message || '账户删除失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：账户删除失败' });
          return false;
        } finally {
          set({ accountDeletionLoading: false });
        }
      },

      user_profile_store_cancel_account_deletion: async (deletionToken: string) => {
        set({ loading: true, error: null });
        try {
          const response = await userProfileApiService.user_profile_api_cancel_account_deletion(deletionToken);
          if (response.success) {
            set({ 
              deletionToken: null,
              deletionDate: null,
              successMessage: '账户删除已取消'
            });
            return true;
          } else {
            set({ error: response.message || '取消账户删除失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：取消账户删除失败' });
          return false;
        } finally {
          set({ loading: false });
        }
      },

      // 通知管理
      user_profile_store_test_notification: async (channel: NotificationChannel) => {
        set({ loading: true, error: null });
        try {
          const response = await userProfileApiService.user_profile_api_test_notification(channel);
          if (response.success) {
            set({ successMessage: `${channel}通知测试已发送` });
            return true;
          } else {
            set({ error: response.message || '通知测试失败' });
            return false;
          }
        } catch (error) {
          set({ error: '网络错误：通知测试失败' });
          return false;
        } finally {
          set({ loading: false });
        }
      },

      user_profile_store_load_notification_history: async (page = 1, pageSize = 20) => {
        set({ notificationLoading: true, error: null });
        try {
          const response = await userProfileApiService.user_profile_api_get_notification_history(page, pageSize);
          if (response.success && response.data) {
            set({ notificationHistory: response.data });
          } else {
            set({ error: response.message || '获取通知历史失败' });
          }
        } catch (error) {
          set({ error: '网络错误：获取通知历史失败' });
        } finally {
          set({ notificationLoading: false });
        }
      },

      // 工具方法
      user_profile_store_clear_errors: () => {
        set({ error: null });
      },

      user_profile_store_clear_success_message: () => {
        set({ successMessage: null });
      },

      user_profile_store_clear_two_factor_setup: () => {
        set({ twoFactorSetupData: null });
      }
    })),
    {
      name: 'user-profile-store',
    }
  )
);