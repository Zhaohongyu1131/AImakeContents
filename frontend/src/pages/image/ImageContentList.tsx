/**
 * Image Content List Page Component
 * 图像内容列表页面组件 - [Image][Content][List]
 */

import React from 'react'
import { Card, Typography, Empty, Button } from 'antd'
import { PlusOutlined } from '@ant-design/icons'

const { Title } = Typography

const ImageContentList: React.FC = () => {
  return (
    <div>
      <Card
        title={<Title level={3}>图像视频管理</Title>}
        extra={
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
          >
            生成图像
          </Button>
        }
      >
        <Empty
          description="暂无图像视频内容"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        >
          <Button type="primary">
            生成第一个图像
          </Button>
        </Empty>
      </Card>
    </div>
  )
}

export default ImageContentList