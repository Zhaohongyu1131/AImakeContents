/**
 * Main Application Component
 * 主应用组件 - [App]
 */

import React from 'react'
import { BrowserRouter } from 'react-router-dom'
import { App as AntdApp } from 'antd'

import AppRouter from '@/components/layout/AppRouter'
import { useAppStore } from '@/stores/app/appStore'

const App: React.FC = () => {
  const { theme } = useAppStore()

  return (
    <AntdApp>
      <BrowserRouter>
        <div className={`app ${theme}`}>
          <AppRouter />
        </div>
      </BrowserRouter>
    </AntdApp>
  )
}

export default App