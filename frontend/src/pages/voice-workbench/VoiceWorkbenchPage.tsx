/**
 * Voice Workbench Page
 * 语音工作台页面 - [pages][voice_workbench]
 */

import React from 'react';
import { Layout } from 'antd';
import VoiceWorkbench from '../../components/voice-workbench/VoiceWorkbench';

const { Content } = Layout;

/**
 * 语音工作台页面组件
 * [pages][voice_workbench][VoiceWorkbenchPage]
 */
const VoiceWorkbenchPage: React.FC = () => {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Content>
        <VoiceWorkbench />
      </Content>
    </Layout>
  );
};

export default VoiceWorkbenchPage;