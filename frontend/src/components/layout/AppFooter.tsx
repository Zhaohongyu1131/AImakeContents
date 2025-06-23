/**
 * Application Footer Component
 * 应用底部组件 - [App][Footer]
 */

import React from 'react'
import { Layout, Typography, Space, Divider } from 'antd'
import { CopyrightOutlined } from '@ant-design/icons'

const { Footer } = Layout
const { Text, Link } = Typography

const AppFooter: React.FC = () => {
  const currentYear = new Date().getFullYear()

  return (
    <Footer className="layout-footer">
      <Space split={<Divider type="vertical" />} size="middle">
        <Space>
          <CopyrightOutlined />
          <Text type="secondary">
            {currentYear} DataSay. All rights reserved.
          </Text>
        </Space>
        
        <Link href="#" type="secondary">
          帮助文档
        </Link>
        
        <Link href="#" type="secondary">
          联系我们
        </Link>
        
        <Link href="#" type="secondary">
          隐私政策
        </Link>
      </Space>
    </Footer>
  )
}

export default AppFooter