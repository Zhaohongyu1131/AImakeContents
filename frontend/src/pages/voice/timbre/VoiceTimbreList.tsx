/**
 * Voice Timbre List Page Component
 * 音色列表页面组件 - [Voice][Timbre][List]
 */

import React from 'react'
import { Card, Typography, Empty, Button } from 'antd'
import { PlusOutlined } from '@ant-design/icons'

const { Title } = Typography

const VoiceTimbreList: React.FC = () => {
  return (
    <div>
      <Card
        title={<Title level={3}>音色管理</Title>}
        extra={
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
          >
            添加音色
          </Button>
        }
      >
        <Empty
          description="暂无音色数据"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        >
          <Button type="primary">
            创建第一个音色
          </Button>
        </Empty>
      </Card>
    </div>
  )
}

export default VoiceTimbreList