/**
 * Voice Audio List Page Component
 * 音频列表页面组件 - [Voice][Audio][List]
 */

import React from 'react'
import { Card, Typography, Empty, Button } from 'antd'
import { PlusOutlined } from '@ant-design/icons'

const { Title } = Typography

const VoiceAudioList: React.FC = () => {
  return (
    <div>
      <Card
        title={<Title level={3}>音频管理</Title>}
        extra={
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
          >
            合成音频
          </Button>
        }
      >
        <Empty
          description="暂无音频数据"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        >
          <Button type="primary">
            合成第一个音频
          </Button>
        </Empty>
      </Card>
    </div>
  )
}

export default VoiceAudioList