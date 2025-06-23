/**
 * Main Layout Component
 * 主布局组件 - [Main][Layout]
 */

import React from 'react'
import { Outlet } from 'react-router-dom'
import { Layout } from 'antd'

import AppHeader from './AppHeader'
import AppSider from './AppSider'
import AppFooter from './AppFooter'
import { useAppStore } from '@/stores/app/appStore'

const { Content } = Layout

const MainLayout: React.FC = () => {
  const { layout } = useAppStore()

  return (
    <Layout className="full-height">
      {/* 侧边栏 */}
      <AppSider />
      
      {/* 主内容区域 */}
      <Layout
        style={{
          marginLeft: layout.siderCollapsed ? 80 : layout.siderWidth,
          transition: 'margin-left 0.2s',
        }}
      >
        {/* 顶部导航 */}
        <AppHeader />
        
        {/* 内容区域 */}
        <Content className="layout-content">
          <Outlet />
        </Content>
        
        {/* 底部 */}
        <AppFooter />
      </Layout>
    </Layout>
  )
}

export default MainLayout