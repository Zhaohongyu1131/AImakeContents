/**
 * Application Sider Component
 * 应用侧边栏组件 - [App][Sider]
 */

import React from 'react'
import { Layout, Menu, theme } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  HomeOutlined,
  FileTextOutlined,
  SoundOutlined,
  PictureOutlined,
  AppstoreOutlined,
  SettingOutlined,
} from '@ant-design/icons'
import type { MenuProps } from 'antd'

import { useAppStore } from '@/stores/app/appStore'

const { Sider } = Layout

type MenuItem = Required<MenuProps>['items'][number]

const AppSider: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { layout } = useAppStore()
  const { token } = theme.useToken()

  // 创建菜单项辅助函数
  const createMenuItem = (
    key: string,
    label: string,
    icon?: React.ReactNode,
    children?: MenuItem[]
  ): MenuItem => ({
    key,
    icon,
    children,
    label,
  })

  // 菜单配置
  const menuItems: MenuItem[] = [
    createMenuItem('/', '首页', <HomeOutlined />),
    
    createMenuItem('text', '文本内容', <FileTextOutlined />, [
      createMenuItem('/text/content', '内容管理'),
      createMenuItem('/text/content/create', '创建文本'),
    ]),
    
    createMenuItem('voice', '语音内容', <SoundOutlined />, [
      createMenuItem('/voice/timbre', '音色管理'),
      createMenuItem('/voice/audio', '音频管理'),
    ]),
    
    createMenuItem('image', '图像视频', <PictureOutlined />, [
      createMenuItem('/image/content', '内容管理'),
    ]),
    
    createMenuItem('mixall', '混合内容', <AppstoreOutlined />, [
      createMenuItem('/mixall/content', '作品管理'),
    ]),
    
    createMenuItem('/settings', '系统设置', <SettingOutlined />),
  ]

  // 获取当前选中的菜单项
  const getSelectedKeys = () => {
    const path = location.pathname
    
    // 精确匹配
    if (path === '/') return ['/']
    
    // 匹配最长路径
    const matchedKeys = menuItems.flatMap(item => {
      if (item && 'children' in item && item.children) {
        return item.children.map(child => child?.key as string).filter(key => 
          key && path.startsWith(key)
        )
      }
      return item?.key as string
    }).filter(Boolean)
    
    if (matchedKeys.length > 0) {
      // 返回最长匹配的路径
      return [matchedKeys.reduce((a, b) => a.length >= b.length ? a : b)]
    }
    
    return [path]
  }

  // 获取展开的菜单项
  const getOpenKeys = () => {
    const path = location.pathname
    const openKeys: string[] = []
    
    if (path.startsWith('/text')) openKeys.push('text')
    if (path.startsWith('/voice')) openKeys.push('voice')
    if (path.startsWith('/image')) openKeys.push('image')
    if (path.startsWith('/mixall')) openKeys.push('mixall')
    
    return openKeys
  }

  // 处理菜单点击
  const handleMenuClick: MenuProps['onClick'] = ({ key }) => {
    navigate(key)
  }

  return (
    <Sider
      className="layout-sider"
      trigger={null}
      collapsible
      collapsed={layout.siderCollapsed}
      width={layout.siderWidth}
      style={{
        position: 'fixed',
        left: 0,
        top: 0,
        bottom: 0,
        zIndex: 100,
        background: token.colorBgContainer,
        borderRight: `1px solid ${token.colorBorder}`,
        boxShadow: '2px 0 8px rgba(0, 21, 41, 0.15)',
      }}
    >
      {/* Logo区域 */}
      <div
        style={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderBottom: `1px solid ${token.colorBorder}`,
          background: token.colorBgContainer,
        }}
      >
        {layout.siderCollapsed ? (
          <div
            style={{
              fontSize: 20,
              fontWeight: 'bold',
              color: token.colorPrimary,
            }}
          >
            DS
          </div>
        ) : (
          <div
            style={{
              fontSize: 18,
              fontWeight: 'bold',
              color: token.colorPrimary,
            }}
          >
            DataSay
          </div>
        )}
      </div>

      {/* 菜单 */}
      <Menu
        mode="inline"
        selectedKeys={getSelectedKeys()}
        defaultOpenKeys={getOpenKeys()}
        items={menuItems}
        onClick={handleMenuClick}
        style={{
          height: 'calc(100% - 64px)',
          borderRight: 0,
          background: token.colorBgContainer,
        }}
      />
    </Sider>
  )
}

export default AppSider