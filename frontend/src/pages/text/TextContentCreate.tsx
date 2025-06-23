/**
 * Text Content Create Page Component
 * 文本内容创建页面组件 - [Text][Content][Create]
 */

import React from 'react'
import { Card, Typography, Empty, Button } from 'antd'
import { ArrowLeftOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'

const { Title } = Typography

const TextContentCreate: React.FC = () => {
  const navigate = useNavigate()

  return (
    <div>
      <Card
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <Button 
              type="text" 
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate('/text/content')}
            />
            <Title level={3} style={{ marginBottom: 0 }}>创建文本内容</Title>
          </div>
        }
      >
        <Empty
          description="文本创作功能开发中"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        >
          <Button onClick={() => navigate('/text/content')}>
            返回列表
          </Button>
        </Empty>
      </Card>
    </div>
  )
}

export default TextContentCreate