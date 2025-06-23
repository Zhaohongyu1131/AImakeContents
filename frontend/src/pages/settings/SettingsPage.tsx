/**
 * Settings Page Component
 * 设置页面组件 - [Settings][Page]
 */

import React from 'react'
import { Card, Typography, Empty } from 'antd'

const { Title } = Typography

const SettingsPage: React.FC = () => {
  return (
    <div>
      <Card title={<Title level={3}>系统设置</Title>}>
        <Empty
          description="设置功能开发中"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </Card>
    </div>
  )
}

export default SettingsPage