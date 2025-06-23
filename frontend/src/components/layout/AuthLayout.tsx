/**
 * Authentication Layout Component
 * 认证布局组件 - [Auth][Layout]
 */

import React from 'react'
import { Outlet } from 'react-router-dom'
import { Layout, Card, Typography } from 'antd'

const { Content } = Layout
const { Title } = Typography

const AuthLayout: React.FC = () => {
  return (
    <Layout className="full-height">
      <Content
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          minHeight: '100vh',
        }}
      >
        <Card
          style={{
            width: 400,
            maxWidth: '90vw',
            boxShadow: '0 8px 24px rgba(0, 0, 0, 0.12)',
          }}
        >
          <div style={{ textAlign: 'center', marginBottom: 32 }}>
            <Title level={2} style={{ color: '#1890ff', marginBottom: 8 }}>
              DataSay
            </Title>
            <Typography.Text type="secondary">
              企业级多模态内容创作平台
            </Typography.Text>
          </div>
          
          <Outlet />
        </Card>
      </Content>
    </Layout>
  )
}

export default AuthLayout