/**
 * Application Header Component
 * 应用头部组件 - [App][Header]
 */

import React from 'react'
import { Layout, Button, Space, Avatar, Dropdown, Typography, theme } from 'antd'
import { useNavigate } from 'react-router-dom'
import { 
  MenuFoldOutlined, 
  MenuUnfoldOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
  BulbOutlined,
  BulbFilled
} from '@ant-design/icons'
import type { MenuProps } from 'antd'

import { useAppStore } from '@/stores/app/appStore'

const { Header } = Layout
const { Text } = Typography

const AppHeader: React.FC = () => {
  const navigate = useNavigate()
  const { 
    theme: appTheme, 
    layout, 
    appThemeToggle, 
    appLayoutSiderToggle 
  } = useAppStore()
  
  const { token } = theme.useToken()

  // 用户菜单
  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人资料',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '设置',
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
    },
  ]

  const handleUserMenuClick: MenuProps['onClick'] = ({ key }) => {
    switch (key) {
      case 'profile':
        navigate('/profile')
        break
      case 'settings':
        navigate('/settings')
        break
      case 'logout':
        // TODO: 执行登出操作
        break
    }
  }

  return (
    <Header 
      className="layout-header"
      style={{
        background: token.colorBgContainer,
        borderBottom: `1px solid ${token.colorBorder}`,
        boxShadow: '0 1px 4px rgba(0, 21, 41, 0.08)',
      }}
    >
      {/* 左侧：菜单折叠按钮和标题 */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <Button
          type="text"
          icon={layout.siderCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          onClick={appLayoutSiderToggle}
          style={{
            fontSize: '16px',
            width: 32,
            height: 32,
          }}
        />
        
        <Text strong style={{ fontSize: 16 }}>
          DataSay 内容创作平台
        </Text>
      </div>

      {/* 右侧：主题切换、用户信息等 */}
      <Space size="middle">
        {/* 主题切换按钮 */}
        <Button
          type="text"
          icon={appTheme === 'light' ? <BulbOutlined /> : <BulbFilled />}
          onClick={appThemeToggle}
          style={{
            fontSize: '16px',
            width: 32,
            height: 32,
          }}
          title={appTheme === 'light' ? '切换到深色主题' : '切换到浅色主题'}
        />

        {/* 用户信息下拉菜单 */}
        <Dropdown
          menu={{
            items: userMenuItems,
            onClick: handleUserMenuClick,
          }}
          placement="bottomRight"
          arrow={{ pointAtCenter: true }}
        >
          <Space style={{ cursor: 'pointer' }}>
            <Avatar icon={<UserOutlined />} />
            <Text>用户名</Text>
          </Space>
        </Dropdown>
      </Space>
    </Header>
  )
}

export default AppHeader