/**
 * Main App Component
 * 主应用组件 - [app]
 */

import React, { useEffect } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { ConfigProvider, App as AntdApp } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import dayjs from 'dayjs';
import 'dayjs/locale/zh-cn';

import { http_services_initialize } from './services/http';
import { useAuthStore } from './stores/auth/auth_user_store';
import AppRouter from './router/AppRouter';

// 设置dayjs中文
dayjs.locale('zh-cn');

const App: React.FC = () => {
  const { initializeAuth } = useAuthStore();

  useEffect(() => {
    // 初始化HTTP服务
    http_services_initialize();
    
    // 初始化认证状态
    initializeAuth();
  }, [initializeAuth]);

  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        token: {
          // 主色调
          colorPrimary: '#1976d2',
          colorSuccess: '#52c41a',
          colorWarning: '#faad14',
          colorError: '#ff4d4f',
          colorInfo: '#1976d2',
          
          // 字体
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
          fontSize: 14,
          
          // 圆角
          borderRadius: 6,
          
          // 间距
          sizeUnit: 4,
          sizeStep: 4,
          
          // 阴影
          boxShadow: '0 2px 8px 0 rgba(0, 0, 0, 0.12)',
        },
        components: {
          // 按钮组件定制
          Button: {
            borderRadius: 6,
            controlHeight: 36,
          },
          // 输入框组件定制
          Input: {
            borderRadius: 6,
            controlHeight: 36,
          },
          // 选择器组件定制
          Select: {
            borderRadius: 6,
            controlHeight: 36,
          },
          // 表格组件定制
          Table: {
            borderRadius: 6,
            headerBg: '#fafafa',
          },
          // 卡片组件定制
          Card: {
            borderRadius: 8,
          },
          // 消息组件定制
          Message: {
            borderRadius: 6,
          },
          // 通知组件定制
          Notification: {
            borderRadius: 8,
          },
        },
      }}
    >
      <AntdApp>
        <BrowserRouter>
          <AppRouter />
        </BrowserRouter>
      </AntdApp>
    </ConfigProvider>
  );
};

export default App;