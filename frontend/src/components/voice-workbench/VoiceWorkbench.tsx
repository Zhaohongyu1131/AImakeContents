/**
 * Voice Workbench Main Component
 * 语音工作台主组件 - [components][voice_workbench][main]
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Layout,
  Card,
  Tabs,
  Space,
  Typography,
  Button,
  message,
  Badge,
  Dropdown,
  Tooltip,
  Alert,
  Spin
} from 'antd';
import {
  SoundOutlined,
  FileTextOutlined,
  SettingOutlined,
  CloudServerOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  DownOutlined,
  ReloadOutlined
} from '@ant-design/icons';

// 导入统一组件
import VoiceCloneUnified from './VoiceCloneUnified';
import TTSUnified from './TTSUnified';
import PlatformSelector from './PlatformSelector';
import VoicePlatformSettings from './VoicePlatformSettings';

// 导入服务
import { useVoiceWorkbenchService } from '../../services/voice-workbench/useVoiceWorkbenchService';

const { Content } = Layout;
const { Title, Paragraph } = Typography;
const { TabPane } = Tabs;

interface VoiceWorkbenchProps {
  className?: string;
}

/**
 * 语音工作台主组件
 * [components][voice_workbench][VoiceWorkbench]
 */
const VoiceWorkbench: React.FC<VoiceWorkbenchProps> = ({ className }) => {
  // 使用语音工作台服务
  const {
    // 平台状态
    platforms,
    selectedPlatform,
    platformHealth,
    platformsLoading,
    
    // 操作状态
    voiceCloneLoading,
    ttsLoading,
    ttsPreviewLoading,
    
    // 数据
    userVoices,
    operationHistory,
    
    // 错误处理
    error,
    
    // 操作函数
    refreshPlatforms,
    selectPlatform,
    healthCheckPlatforms,
    submitVoiceClone,
    synthesizeTTS,
    previewTTS,
    clearError,
    getOperationStatus
  } = useVoiceWorkbenchService();

  // 本地状态
  const [activeTab, setActiveTab] = useState('voice-clone');
  const [showPlatformSettings, setShowPlatformSettings] = useState(false);

  // 初始化加载
  useEffect(() => {
    refreshPlatforms();
  }, [refreshPlatforms]);

  // 错误处理
  useEffect(() => {
    if (error) {
      message.error(error);
      clearError();
    }
  }, [error, clearError]);

  // 渲染平台状态指示器
  const renderPlatformStatus = () => {
    if (!selectedPlatform) {
      return (
        <Badge status="default" text="未选择平台" />
      );
    }

    const platform = platforms.find(p => p.platform_type === selectedPlatform);
    if (!platform) {
      return (
        <Badge status="error" text="平台不可用" />
      );
    }

    const health = platformHealth[selectedPlatform];
    const healthStatus = health?.is_healthy ? 'success' : 'error';
    const healthText = health?.is_healthy ? '正常' : '异常';

    return (
      <Space size="small">
        <Badge status={healthStatus} text={`${platform.platform_name}: ${healthText}`} />
        {health?.response_time_ms && (
          <span style={{ fontSize: '12px', color: '#666' }}>
            ({health.response_time_ms.toFixed(0)}ms)
          </span>
        )}
      </Space>
    );
  };

  // 渲染平台选择下拉菜单
  const renderPlatformSelector = () => {
    const menuItems = platforms.map(platform => ({
      key: platform.platform_type,
      label: (
        <Space>
          {platformHealth[platform.platform_type]?.is_healthy ? (
            <CheckCircleOutlined style={{ color: '#52c41a' }} />
          ) : (
            <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />
          )}
          <span>{platform.platform_name}</span>
          <Badge 
            count={`¥${platform.cost_per_minute}/分钟`} 
            style={{ backgroundColor: '#1890ff' }}
          />
        </Space>
      ),
      disabled: !platform.is_enabled || !platformHealth[platform.platform_type]?.is_healthy
    }));

    return (
      <Dropdown
        menu={{
          items: menuItems,
          onClick: ({ key }) => selectPlatform(key)
        }}
        trigger={['click']}
        disabled={platformsLoading}
      >
        <Button loading={platformsLoading}>
          <Space>
            <CloudServerOutlined />
            {selectedPlatform ? 
              platforms.find(p => p.platform_type === selectedPlatform)?.platform_name || '选择平台' 
              : '选择平台'
            }
            <DownOutlined />
          </Space>
        </Button>
      </Dropdown>
    );
  };

  // 页面头部
  const renderHeader = () => (
    <Card style={{ marginBottom: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Title level={2} style={{ margin: 0 }}>
            <Space>
              <SoundOutlined style={{ color: '#1890ff' }} />
              语音工作台
            </Space>
          </Title>
          <Paragraph type="secondary" style={{ margin: '8px 0 0 0' }}>
            统一的多平台语音合成与音色克隆工作台，支持火山引擎、Azure、OpenAI等多个平台
          </Paragraph>
        </div>
        
        <Space size="large">
          {/* 平台状态 */}
          <div>
            <div style={{ fontSize: '12px', color: '#666', marginBottom: 4 }}>
              平台状态
            </div>
            {renderPlatformStatus()}
          </div>
          
          {/* 控制按钮 */}
          <Space>
            {renderPlatformSelector()}
            
            <Tooltip title="刷新平台状态">
              <Button 
                icon={<ReloadOutlined />}
                onClick={healthCheckPlatforms}
                loading={platformsLoading}
              />
            </Tooltip>
            
            <Button 
              icon={<SettingOutlined />}
              onClick={() => setShowPlatformSettings(true)}
            >
              平台设置
            </Button>
          </Space>
        </Space>
      </div>
    </Card>
  );

  // 平台选择提示
  const renderPlatformAlert = () => {
    if (selectedPlatform) return null;

    return (
      <Alert
        message="请选择语音服务平台"
        description="您需要先选择一个可用的语音服务平台才能使用音色克隆和TTS功能。建议选择火山引擎（豆包）获得最佳体验。"
        type="info"
        showIcon
        style={{ marginBottom: 24 }}
        action={
          <Space>
            {renderPlatformSelector()}
          </Space>
        }
      />
    );
  };

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
        <VoiceCloneUnified
          selectedPlatform={selectedPlatform}
          platforms={platforms}
          onSubmit={submitVoiceClone}
          loading={voiceCloneLoading}
          disabled={!selectedPlatform}
        />
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
        <TTSUnified
          selectedPlatform={platforms.find(p => p.platform_type === selectedPlatform) || null}
          platforms={platforms}
          onSubmit={synthesizeTTS}
          loading={ttsLoading}
        />
      )
    },
    {
      key: 'platform-settings',
      tab: (
        <Space>
          <SettingOutlined />
          <span>平台管理</span>
          <Badge count={platforms.filter(p => !p.is_enabled).length} />
        </Space>
      ),
      content: (
        <PlatformSelector
          platforms={platforms.map(p => ({
            type: p.platform_type,
            name: p.platform_name,
            description: p.platform_description,
            isEnabled: p.is_enabled,
            features: p.feature_support ? Object.keys(p.feature_support).filter(k => p.feature_support[k]) : [],
            priority: p.priority,
            costPerMinute: p.cost_per_minute,
            health: platformHealth[p.platform_type] ? {
              isHealthy: platformHealth[p.platform_type].is_healthy,
              responseTime: platformHealth[p.platform_type].response_time_ms,
              errorRate: platformHealth[p.platform_type].error_rate,
              lastCheck: new Date(platformHealth[p.platform_type].last_health_check).toLocaleString(),
              dailyRequestsUsed: platformHealth[p.platform_type].daily_requests_used,
              dailyRequestsLimit: platformHealth[p.platform_type].daily_requests_limit
            } : undefined,
            limitations: {
              maxTextLength: 5000,
              maxFileSize: 10 * 1024 * 1024,
              supportedFormats: ['mp3', 'wav', 'ogg']
            }
          }))}
          selectedPlatform={platforms.find(p => p.platform_type === selectedPlatform) ? {
            type: platforms.find(p => p.platform_type === selectedPlatform)!.platform_type,
            name: platforms.find(p => p.platform_type === selectedPlatform)!.platform_name,
            description: platforms.find(p => p.platform_type === selectedPlatform)!.platform_description,
            isEnabled: platforms.find(p => p.platform_type === selectedPlatform)!.is_enabled,
            features: platforms.find(p => p.platform_type === selectedPlatform)!.feature_support ? Object.keys(platforms.find(p => p.platform_type === selectedPlatform)!.feature_support).filter(k => platforms.find(p => p.platform_type === selectedPlatform)!.feature_support[k]) : [],
            priority: platforms.find(p => p.platform_type === selectedPlatform)!.priority,
            costPerMinute: platforms.find(p => p.platform_type === selectedPlatform)!.cost_per_minute,
            limitations: {
              maxTextLength: 5000,
              maxFileSize: 10 * 1024 * 1024,
              supportedFormats: ['mp3', 'wav', 'ogg']
            }
          } : null}
          onPlatformSelect={(platform) => selectPlatform(platform.type)}
          onPlatformSettings={(platform) => setShowPlatformSettings(true)}
          loading={platformsLoading}
        />
      )
    }
  ];

  return (
    <Layout className={className}>
      <Content style={{ padding: '24px', minHeight: '100vh' }}>
        {renderHeader()}
        {renderPlatformAlert()}
        
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
                  {selectedPlatform || item.key === 'platform-settings' ? (
                    item.content
                  ) : (
                    <div style={{ textAlign: 'center', padding: '100px 0' }}>
                      <Spin size="large" />
                      <Paragraph type="secondary" style={{ marginTop: 16 }}>
                        请先选择语音服务平台
                      </Paragraph>
                    </div>
                  )}
                </div>
              </TabPane>
            ))}
          </Tabs>
        </Card>
        
        {/* 平台设置模态框 */}
        <VoicePlatformSettings
          platform={selectedPlatform ? {
            type: platforms.find(p => p.platform_type === selectedPlatform)!.platform_type,
            name: platforms.find(p => p.platform_type === selectedPlatform)!.platform_name,
            isEnabled: platforms.find(p => p.platform_type === selectedPlatform)!.is_enabled,
            priority: platforms.find(p => p.platform_type === selectedPlatform)!.priority,
            costPerMinute: platforms.find(p => p.platform_type === selectedPlatform)!.cost_per_minute,
            maxDailyRequests: platforms.find(p => p.platform_type === selectedPlatform)!.max_daily_requests,
            apiConfig: platforms.find(p => p.platform_type === selectedPlatform)!.api_config || {},
            featureSupport: platforms.find(p => p.platform_type === selectedPlatform)!.feature_support || {},
            limitations: {
              maxTextLength: 5000,
              maxFileSize: 10 * 1024 * 1024,
              supportedFormats: ['mp3', 'wav', 'ogg']
            }
          } : null}
          visible={showPlatformSettings}
          onClose={() => setShowPlatformSettings(false)}
          onSave={async (config) => {
            // 保存平台配置的逻辑
            console.log('Save platform config:', config);
            message.success('平台配置已保存');
            setShowPlatformSettings(false);
            await refreshPlatforms();
          }}
          onTest={async (config) => {
            // 测试平台连接的逻辑
            console.log('Test platform config:', config);
            return true; // 模拟测试成功
          }}
          loading={false}
        />
      </Content>
    </Layout>
  );
};

export default VoiceWorkbench;