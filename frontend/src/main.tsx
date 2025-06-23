/**
 * Frontend Application Entry Point
 * 前端应用入口 - [app][main]
 */

import React from 'react'
import ReactDOM from 'react-dom/client'
import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'

import App from './App'
import './index.css'

// 设置dayjs中文语言
dayjs.locale('zh-cn')

// 渲染应用
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider
      locale={zhCN}
      theme={{
        token: {
          // DataSay主题色配置
          colorPrimary: '#1890ff',
          colorSuccess: '#52c41a',
          colorWarning: '#faad14',
          colorError: '#ff4d4f',
          borderRadius: 6,
          fontSize: 14,
        },
        components: {
          Button: {
            borderRadius: 6,
          },
          Input: {
            borderRadius: 6,
          },
          Card: {
            borderRadius: 8,
          },
        },
      }}
    >
      <App />
    </ConfigProvider>
  </React.StrictMode>
)