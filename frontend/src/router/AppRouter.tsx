/**
 * App Router Component
 * 应用路由组件 - [router][app_router]
 */

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthGuard, GuestGuard, AdminGuard } from './guards';

// 页面组件（暂时使用占位符）
const Dashboard = () => <div>Dashboard - 仪表板</div>;
const LoginPage = () => <div>Login Page - 登录页面</div>;
const RegisterPage = () => <div>Register Page - 注册页面</div>;
const TextContentPage = () => <div>Text Content - 文本内容</div>;
const VoiceContentPage = () => <div>Voice Content - 语音内容</div>;
const ImageContentPage = () => <div>Image Content - 图像内容</div>;
const ProfilePage = () => <div>Profile - 个人资料</div>;
const AdminPanel = () => <div>Admin Panel - 管理面板</div>;
const NotFoundPage = () => <div>404 - 页面未找到</div>;
const ForbiddenPage = () => <div>403 - 权限不足</div>;
const DisabledAccountPage = () => <div>Account Disabled - 账户已禁用</div>;

const AppRouter: React.FC = () => {
  return (
    <Routes>
      {/* 公共路由 */}
      <Route path=\"/\" element={<Navigate to=\"/dashboard\" replace />} />
      
      {/* 认证相关路由 - 只有未登录用户可访问 */}
      <Route path=\"/auth/login\" element={
        <GuestGuard>
          <LoginPage />
        </GuestGuard>
      } />
      
      <Route path=\"/auth/register\" element={
        <GuestGuard>
          <RegisterPage />
        </GuestGuard>
      } />
      
      <Route path=\"/auth/disabled\" element={<DisabledAccountPage />} />
      
      {/* 需要认证的路由 */}
      <Route path=\"/dashboard\" element={
        <AuthGuard>
          <Dashboard />
        </AuthGuard>
      } />
      
      <Route path=\"/profile\" element={
        <AuthGuard>
          <ProfilePage />
        </AuthGuard>
      } />
      
      {/* 文本内容相关路由 */}
      <Route path=\"/text/*\" element={
        <AuthGuard requirePermissions={['text:read']}>
          <TextContentPage />
        </AuthGuard>
      } />
      
      {/* 语音内容相关路由 */}
      <Route path=\"/voice/*\" element={
        <AuthGuard requirePermissions={['voice:read']}>
          <VoiceContentPage />
        </AuthGuard>
      } />
      
      {/* 图像内容相关路由 */}
      <Route path=\"/image/*\" element={
        <AuthGuard requirePermissions={['image:read']}>
          <ImageContentPage />
        </AuthGuard>
      } />
      
      {/* 管理员路由 */}
      <Route path=\"/admin/*\" element={
        <AdminGuard>
          <AdminPanel />
        </AdminGuard>
      } />
      
      {/* 错误页面 */}
      <Route path=\"/403\" element={<ForbiddenPage />} />
      <Route path=\"/404\" element={<NotFoundPage />} />
      
      {/* 404 兜底 */}
      <Route path=\"*\" element={<Navigate to=\"/404\" replace />} />
    </Routes>
  );
};

export default AppRouter;"