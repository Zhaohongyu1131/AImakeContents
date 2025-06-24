/**
 * Doubao Demo Page
 * 豆包演示页面 - [pages][doubao][demo]
 */

import React from 'react';
import { Layout } from 'antd';
import { DoubaoMainContainer } from '../../components/doubao';

const { Content } = Layout;

/**
 * 豆包演示页面组件
 * [pages][doubao][demo][DoubaoPage]
 */
const DoubaoPage: React.FC = () => {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Content>
        <DoubaoMainContainer />
      </Content>
    </Layout>
  );
};

export default DoubaoPage;