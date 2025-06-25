/**
 * Application Router Component
 * 应用路由组件 - [App][Router]
 */

import React, { Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Spin } from 'antd'

import MainLayout from './MainLayout'
import AuthLayout from './AuthLayout'

// 懒加载页面组件
const HomePage = React.lazy(() => import('@/pages/home/HomePage'))
const LoginPage = React.lazy(() => import('@/pages/auth/LoginPage'))
const RegisterPage = React.lazy(() => import('@/pages/auth/RegisterPage'))

// 文本相关页面
const TextContentList = React.lazy(() => import('@/pages/text_content/TextContentList'))
const TextContentCreate = React.lazy(() => import('@/pages/text_content/TextContentCreate'))

// 语音相关页面
const VoiceWorkbenchPage = React.lazy(() => import('@/pages/voice_service/VoiceWorkbenchPage'))
const VoiceTimbreList = React.lazy(() => import('@/pages/voice_service/timbre/VoiceTimbreList'))
const VoiceAudioList = React.lazy(() => import('@/pages/voice_service/audio/VoiceAudioList'))

// 图像相关页面
const ImageContentList = React.lazy(() => import('@/pages/image_service/ImageContentList'))

// 混合内容页面
const MixallContentList = React.lazy(() => import('@/pages/mixall/MixallContentList'))

// 设置页面
const SettingsPage = React.lazy(() => import('@/pages/settings/SettingsPage'))

// 用户个人中心页面
const UserProfileWorkspace = React.lazy(() => import('@/pages/user_profile/UserProfileWorkspace'))

// 错误页面
const NotFoundPage = React.lazy(() => import('@/pages/error/NotFoundPage'))

const AppRouter: React.FC = () => {
  return (
    <Suspense
      fallback={
        <div className="loading-container">
          <Spin size="large" tip="加载中..." />
        </div>
      }
    >
      <Routes>
        {/* 认证相关路由 */}
        <Route path="/auth" element={<AuthLayout />}>
          <Route path="login" element={<LoginPage />} />
          <Route path="register" element={<RegisterPage />} />
          <Route index element={<Navigate to="login" replace />} />
        </Route>

        {/* 主应用路由 */}
        <Route path="/" element={<MainLayout />}>
          {/* 首页 */}
          <Route index element={<HomePage />} />
          
          {/* 文本内容模块 */}
          <Route path="text">
            <Route index element={<Navigate to="content" replace />} />
            <Route path="content" element={<TextContentList />} />
            <Route path="content/create" element={<TextContentCreate />} />
          </Route>
          
          {/* 语音内容模块 */}
          <Route path="voice">
            <Route index element={<Navigate to="workbench" replace />} />
            <Route path="workbench" element={<VoiceWorkbenchPage />} />
            <Route path="timbre" element={<VoiceTimbreList />} />
            <Route path="audio" element={<VoiceAudioList />} />
          </Route>
          
          {/* 图像视频模块 */}
          <Route path="image">
            <Route index element={<Navigate to="content" replace />} />
            <Route path="content" element={<ImageContentList />} />
          </Route>
          
          {/* 混合内容模块 */}
          <Route path="mixall">
            <Route index element={<Navigate to="content" replace />} />
            <Route path="content" element={<MixallContentList />} />
          </Route>
          
          {/* 设置页面 */}
          <Route path="settings" element={<SettingsPage />} />
          
          {/* 用户个人中心 */}
          <Route path="profile" element={<UserProfileWorkspace />} />
        </Route>

        {/* 404页面 */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Suspense>
  )
}

export default AppRouter