/**
 * Text Content List Page Component
 * 文本内容列表页面组件 - [Text][Content][List]
 */

import React from 'react'
import { Card, Typography, Empty, Button } from 'antd'
import { PlusOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'

const { Title } = Typography

const TextContentList: React.FC = () => {
  const navigate = useNavigate()

  return (
    <div>
      <Card
        title={<Title level={3}>文本内容管理</Title>}
        extra={
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
            onClick={() => navigate('/text/content/create')}
          >
            创建文本
          </Button>
        }
      >
        <Empty
          description="暂无文本内容"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        >
          <Button 
            type="primary" 
            onClick={() => navigate('/text/content/create')}
          >
            创建第一个文本
          </Button>
        </Empty>
      </Card>
    </div>
  )
}

export default TextContentList