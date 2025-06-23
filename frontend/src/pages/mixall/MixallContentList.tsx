/**
 * Mixall Content List Page Component
 * 混合内容列表页面组件 - [Mixall][Content][List]
 */

import React from 'react'
import { Card, Typography, Empty, Button } from 'antd'
import { PlusOutlined } from '@ant-design/icons'

const { Title } = Typography

const MixallContentList: React.FC = () => {
  return (
    <div>
      <Card
        title={<Title level={3}>混合内容管理</Title>}
        extra={
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
          >
            创建作品
          </Button>
        }
      >
        <Empty
          description="暂无混合内容作品"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        >
          <Button type="primary">
            创建第一个作品
          </Button>
        </Empty>
      </Card>
    </div>
  )
}

export default MixallContentList