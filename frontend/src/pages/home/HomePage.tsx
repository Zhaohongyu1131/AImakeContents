/**
 * Home Page Component
 * 首页组件 - [Home][Page]
 */

import React from 'react'
import { Card, Row, Col, Statistic, Typography, Button, Space } from 'antd'
import {
  FileTextOutlined,
  SoundOutlined,
  PictureOutlined,
  AppstoreOutlined,
  PlusOutlined,
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'

const { Title, Paragraph } = Typography

const HomePage: React.FC = () => {
  const navigate = useNavigate()

  // 快捷操作
  const quickActions = [
    {
      key: 'text',
      title: '创建文本',
      icon: <FileTextOutlined />,
      description: '使用AI生成高质量文本内容',
      path: '/text/content/create',
      color: '#1890ff',
    },
    {
      key: 'voice',
      title: '合成语音', 
      icon: <SoundOutlined />,
      description: '将文本转换为自然的语音',
      path: '/voice/audio',
      color: '#52c41a',
    },
    {
      key: 'image',
      title: '生成图像',
      icon: <PictureOutlined />,
      description: '创建精美的图像和视频',
      path: '/image/content',
      color: '#faad14',
    },
    {
      key: 'mixall',
      title: '混合创作',
      icon: <AppstoreOutlined />,
      description: '组合多种媒体创建完整作品',
      path: '/mixall/content',
      color: '#722ed1',
    },
  ]

  // 统计数据（模拟）
  const statistics = [
    { title: '文本作品', value: 156, suffix: '篇' },
    { title: '语音作品', value: 89, suffix: '个' },
    { title: '图像作品', value: 234, suffix: '张' },
    { title: '混合作品', value: 67, suffix: '个' },
  ]

  return (
    <div>
      {/* 欢迎区域 */}
      <Card style={{ marginBottom: 24 }}>
        <Row align="middle">
          <Col span={16}>
            <Title level={2} style={{ marginBottom: 8 }}>
              欢迎使用 DataSay 内容创作平台
            </Title>
            <Paragraph type="secondary" style={{ fontSize: 16, marginBottom: 0 }}>
              通过AI技术，轻松创建文本、语音、图像和视频内容，提升您的创作效率
            </Paragraph>
          </Col>
          <Col span={8} style={{ textAlign: 'right' }}>
            <Button 
              type="primary" 
              size="large" 
              icon={<PlusOutlined />}
              onClick={() => navigate('/text/content/create')}
            >
              开始创作
            </Button>
          </Col>
        </Row>
      </Card>

      {/* 统计数据 */}
      <Row gutter={24} style={{ marginBottom: 24 }}>
        {statistics.map((stat, index) => (
          <Col span={6} key={index}>
            <Card>
              <Statistic
                title={stat.title}
                value={stat.value}
                suffix={stat.suffix}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
        ))}
      </Row>

      {/* 快捷操作 */}
      <Card title="快捷操作" style={{ marginBottom: 24 }}>
        <Row gutter={[24, 24]}>
          {quickActions.map((action) => (
            <Col span={6} key={action.key}>
              <Card
                hoverable
                onClick={() => navigate(action.path)}
                style={{
                  textAlign: 'center',
                  cursor: 'pointer',
                  borderColor: action.color,
                }}
                bodyStyle={{ padding: '24px 16px' }}
              >
                <div
                  style={{
                    fontSize: 32,
                    color: action.color,
                    marginBottom: 16,
                  }}
                >
                  {action.icon}
                </div>
                <Title level={4} style={{ marginBottom: 8 }}>
                  {action.title}
                </Title>
                <Paragraph type="secondary" style={{ marginBottom: 0 }}>
                  {action.description}
                </Paragraph>
              </Card>
            </Col>
          ))}
        </Row>
      </Card>

      {/* 最近活动 */}
      <Card title="最近活动">
        <div style={{ textAlign: 'center', padding: '40px 0' }}>
          <Paragraph type="secondary">
            暂无最近活动，开始您的第一个创作吧！
          </Paragraph>
          <Button type="primary" onClick={() => navigate('/text/content/create')}>
            立即开始
          </Button>
        </div>
      </Card>
    </div>
  )
}

export default HomePage