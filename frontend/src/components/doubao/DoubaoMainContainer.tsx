/**
 * Doubao Main Container Component
 * 豆包主容器组件 - [components][doubao][main_container]
 */

import React, { useState, useEffect } from 'react';
import {
  Layout,
  Tabs,
  Card,
  Space,
  Typography,
  Button,
  message,
  Result,
  Badge
} from 'antd';
import {
  SoundOutlined,
  FileTextOutlined,
  PictureOutlined,
  SettingOutlined,
  CloudServerOutlined
} from '@ant-design/icons';

// 导入子组件
import VoiceCloneBasicSettings from './VoiceCloneBasicSettings';
import VoiceCloneAdvancedSettings from './VoiceCloneAdvancedSettings';
import TTSBasicSettings from './TTSBasicSettings';
import TTSAdvancedSettings from './TTSAdvancedSettings';

// 导入服务
import { useDoubaoService } from '../../services/doubao/useDoubaoService';

const { Content } = Layout;
const { Title, Paragraph } = Typography;
const { TabPane } = Tabs;

interface DoubaoMainContainerProps {
  className?: string;
}

const DoubaoMainContainer: React.FC<DoubaoMainContainerProps> = ({
  className
}) => {
  // 使用豆包服务
  const {
    // 状态
    voiceCloneLoading,
    ttsLoading,
    ttsPreviewLoading,
    healthCheckLoading,
    userVoices,
    healthStatus,
    lastHealthCheck,
    error,
    
    // 操作函数
    checkHealth,
    fetchUserVoices,
    submitVoiceClone,
    synthesizeTTS,
    previewTTS,
    clearError
  } = useDoubaoService();

  // 本地状态管理
  const [activeTab, setActiveTab] = useState('voice-clone');
  const [showVoiceAdvanced, setShowVoiceAdvanced] = useState(false);
  const [showTtsAdvanced, setShowTtsAdvanced] = useState(false);

  // 初始化加载用户音色列表
  useEffect(() => {
    fetchUserVoices();
  }, [fetchUserVoices]);

  // 错误处理
  useEffect(() => {
    if (error) {
      message.error(error);
      clearError();
    }
  }, [error, clearError]);

  // 页面头部
  const renderHeader = () => (
    <Card style={{ marginBottom: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Title level={2} style={{ margin: 0 }}>
            <Space>
              <CloudServerOutlined style={{ color: '#1890ff' }} />
              豆包AI语音服务
            </Space>
          </Title>
          <Paragraph type="secondary" style={{ margin: '8px 0 0 0' }}>
            企业级语音合成与音色克隆平台，支持多语言、多音色、高质量语音生成
          </Paragraph>
        </div>
        
        <Space>
          <Badge 
            status={healthStatus === 'healthy' ? 'success' : 
                   healthStatus === 'unhealthy' ? 'error' : 'default'} 
            text={`服务状态: ${healthStatus === 'healthy' ? '正常' : 
                  healthStatus === 'unhealthy' ? '异常' : '未知'}`}
          />
          {lastHealthCheck && (
            <span style={{ fontSize: '12px', color: '#666' }}>
              最后检查: {lastHealthCheck}
            </span>
          )}
          <Button onClick={checkHealth} size="small" loading={healthCheckLoading}>
            检查状态
          </Button>
        </Space>
      </div>
    </Card>
  );

  // 标签页配置
  const tabItems = [
    {
      key: 'voice-clone',
      tab: (
        <Space>
          <SoundOutlined />
          <span>音色克隆</span>
        </Space>
      ),
      content: (
        <div>
          <VoiceCloneBasicSettings
            onSubmit={submitVoiceClone}
            loading={voiceCloneLoading}
            onAdvancedToggle={() => setShowVoiceAdvanced(!showVoiceAdvanced)}
            showAdvanced={showVoiceAdvanced}
          />
          
          <VoiceCloneAdvancedSettings
            visible={showVoiceAdvanced}
            onChange={(values) => console.log('Voice advanced settings:', values)}
          />
        </div>
      )
    },
    {
      key: 'tts',
      tab: (
        <Space>
          <FileTextOutlined />
          <span>文本转语音</span>
        </Space>
      ),
      content: (
        <div>
          <TTSBasicSettings
            onSynthesize={synthesizeTTS}
            onPreview={previewTTS}
            loading={ttsLoading}
            previewLoading={ttsPreviewLoading}
            onAdvancedToggle={() => setShowTtsAdvanced(!showTtsAdvanced)}
            showAdvanced={showTtsAdvanced}
            voiceList={userVoices}
          />
          
          <TTSAdvancedSettings
            visible={showTtsAdvanced}
            onChange={(values) => console.log('TTS advanced settings:', values)}
          />
        </div>
      )
    },
    {
      key: 'image',
      tab: (
        <Space>
          <PictureOutlined />
          <span>图像处理</span>
          <Badge count="开发中" style={{ backgroundColor: '#faad14' }} />
        </Space>
      ),
      content: (
        <Result
          icon={<PictureOutlined style={{ color: '#faad14' }} />}
          title="图像处理功能"
          subTitle="图像生成、分析和增强功能正在开发中，敬请期待"
          extra={
            <Button type="primary" disabled>
              即将推出
            </Button>
          }
        />
      )
    },
    {
      key: 'settings',
      tab: (
        <Space>
          <SettingOutlined />
          <span>系统设置</span>
        </Space>
      ),
      content: (
        <Result
          icon={<SettingOutlined style={{ color: '#52c41a' }} />}
          title="系统设置"
          subTitle="API配置、用户偏好设置等功能正在开发中"
          extra={
            <Button type="primary" disabled>
              配置选项
            </Button>
          }
        />
      )
    }
  ];

  return (
    <Layout className={className}>
      <Content style={{ padding: '24px', minHeight: '100vh' }}>
        {renderHeader()}
        
        <Card>
          <Tabs
            activeKey={activeTab}
            onChange={setActiveTab}
            size="large"
            type="card"
          >
            {tabItems.map(item => (
              <TabPane tab={item.tab} key={item.key}>
                <div style={{ minHeight: '500px' }}>
                  {item.content}
                </div>
              </TabPane>
            ))}
          </Tabs>
        </Card>
      </Content>
    </Layout>
  );
};

export default DoubaoMainContainer;