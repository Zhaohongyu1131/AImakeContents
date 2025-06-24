/**
 * Voice Service Workspace Page
 * 语音服务工作台页面 - [pages][voice_service][voice_service_workspace]
 */

import React, { useState, useEffect } from 'react';
import {
  Layout,
  Menu,
  Card,
  Button,
  Space,
  Typography,
  Tabs,
  Row,
  Col,
  Statistic,
  Badge,
  Divider,
  Alert,
  Progress,
  Tag,
  Avatar,
  List,
  Empty
} from 'antd';
import {
  SoundOutlined,
  ThunderboltOutlined,
  UnorderedListOutlined,
  SettingOutlined,
  BarChartOutlined,
  PlusOutlined,
  PlayCircleOutlined,
  UserOutlined,
  GlobalOutlined,
  ExperimentOutlined,
  CloudOutlined,
  ApiOutlined,
  FileTextOutlined
} from '@ant-design/icons';

import { useVoiceServiceStore } from '../../stores/voice_service/voice_service_store';
import { useAuthStore } from '../../stores/auth/auth_store';
import {
  VoiceAudioCreate,
  VoiceTimbreManage
} from '../../components/voice_service';
import type { VoiceAudioBasic, VoiceSynthesisResponse } from '../../services/api/voice_service_api';
import { AuthGuard, PermissionGuard } from '../../router/guards';

const { Sider, Content } = Layout;
const { Title, Text } = Typography;
const { TabPane } = Tabs;

type WorkspaceMode = 'synthesize' | 'timbre' | 'audio_list' | 'analytics' | 'settings';

interface VoiceServiceWorkspaceProps {
  className?: string;
}

export const VoiceServiceWorkspace: React.FC<VoiceServiceWorkspaceProps> = ({
  className
}) => {
  const [currentMode, setCurrentMode] = useState<WorkspaceMode>('synthesize');
  const [siderCollapsed, setSiderCollapsed] = useState(false);
  const [selectedTimbreId, setSelectedTimbreId] = useState<number | undefined>();

  const {
    audioList,
    timbreList,
    usageStats,
    synthesisLoading,
    lastSynthesisResult,
    currentCloneTask,
    platformConnectionStatus,
    voice_service_store_load_audio_list,
    voice_service_store_load_timbre_list,
    voice_service_store_load_usage_stats,
    voice_service_store_test_platform_connection
  } = useVoiceServiceStore();

  const { userInfo } = useAuthStore();

  // 初始化数据加载
  useEffect(() => {
    voice_service_store_load_audio_list(1, 10);
    voice_service_store_load_timbre_list(1, 10, { is_available: true });
    voice_service_store_load_usage_stats('month');

    // 测试平台连接状态
    voice_service_store_test_platform_connection('doubao');
    voice_service_store_test_platform_connection('azure');
  }, []);

  const handleModeChange = (mode: WorkspaceMode) => {
    setCurrentMode(mode);
  };

  const handleSynthesisResult = (result: VoiceSynthesisResponse) => {
    // 合成成功后刷新音频列表
    voice_service_store_load_audio_list(1, 10);
  };

  // 获取平台连接状态统计
  const getConnectionStats = () => {
    const platforms = Object.keys(platformConnectionStatus);
    const connected = platforms.filter(platform => 
      platformConnectionStatus[platform as keyof typeof platformConnectionStatus]?.is_connected
    ).length;
    return { total: platforms.length, connected };
  };

  const connectionStats = getConnectionStats();

  const menuItems = [
    {
      key: 'synthesize',
      icon: <ThunderboltOutlined />,
      label: '语音合成',
      permission: 'voice:synthesize'
    },
    {
      key: 'timbre',
      icon: <UserOutlined />,
      label: '音色管理',
      permission: 'voice:timbre'
    },
    {
      key: 'audio_list',
      icon: <UnorderedListOutlined />,
      label: '音频库',
      permission: 'voice:read'
    },
    {
      key: 'analytics',
      icon: <BarChartOutlined />,
      label: '数据分析',
      permission: 'voice:analytics'
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '平台设置',
      permission: 'voice:settings'
    }
  ];

  // 渲染侧边栏
  const renderSider = () => (
    <Sider
      collapsible
      collapsed={siderCollapsed}
      onCollapse={setSiderCollapsed}
      theme="light"
      width={220}
      style={{ 
        borderRight: '1px solid #f0f0f0',
        background: '#fafafa'
      }}
    >
      <div style={{ padding: '16px', textAlign: 'center' }}>
        <SoundOutlined style={{ fontSize: '24px', color: '#722ed1' }} />
        {!siderCollapsed && (
          <div style={{ marginTop: '8px' }}>
            <Text strong>语音工作台</Text>
          </div>
        )}
      </div>
      
      <Menu
        mode="inline"
        selectedKeys={[currentMode]}
        style={{ border: 'none', background: 'transparent' }}
      >
        {menuItems.map(item => (
          <PermissionGuard key={item.key} permissions={[item.permission]} fallback={null}>
            <Menu.Item
              key={item.key}
              icon={item.icon}
              onClick={() => handleModeChange(item.key as WorkspaceMode)}
            >
              {item.label}
            </Menu.Item>
          </PermissionGuard>
        ))}
      </Menu>

      {/* 快速统计 */}
      {!siderCollapsed && (
        <div style={{ padding: '16px', marginTop: '16px' }}>
          <Divider />
          <div style={{ textAlign: 'center' }}>
            <Statistic
              title="本月合成"
              value={usageStats?.total_synthesis_count || 0}
              valueStyle={{ fontSize: '16px' }}
              suffix="次"
            />
            <Statistic
              title="音色库"
              value={timbreList?.total || 0}
              valueStyle={{ fontSize: '16px' }}
              style={{ marginTop: '8px' }}
              suffix="个"
            />
            <div style={{ marginTop: '12px' }}>
              <Badge 
                status={connectionStats.connected > 0 ? 'success' : 'error'}
                text={`${connectionStats.connected}/${connectionStats.total} 平台在线`}
              />
            </div>
          </div>
        </div>
      )}
    </Sider>
  );

  // 渲染主要内容区
  const renderContent = () => {
    switch (currentMode) {
      case 'synthesize':
        return (
          <AuthGuard requirePermissions={['voice:synthesize']}>
            <div>
              <div style={{ marginBottom: '24px' }}>
                <Title level={3}>
                  <ThunderboltOutlined /> AI语音合成
                </Title>
                <Text type="secondary">
                  使用人工智能技术快速生成高质量语音内容
                </Text>
              </div>
              
              <VoiceAudioCreate
                onCreated={handleSynthesisResult}
                initialTimbreId={selectedTimbreId}
              />
            </div>
          </AuthGuard>
        );

      case 'timbre':
        return (
          <AuthGuard requirePermissions={['voice:timbre']}>
            <div>
              <div style={{ marginBottom: '24px' }}>
                <Title level={3}>
                  <UserOutlined /> 音色管理
                </Title>
                <Text type="secondary">
                  管理和创建语音音色，支持音色克隆功能
                </Text>
              </div>

              {/* 克隆任务状态 */}
              {currentCloneTask && currentCloneTask.status === 'processing' && (
                <Alert
                  message="音色克隆进行中"
                  description={
                    <div>
                      <div>任务ID: {currentCloneTask.clone_task_id}</div>
                      <Progress percent={50} status="active" showInfo={false} />
                    </div>
                  }
                  type="info"
                  showIcon
                  style={{ marginBottom: '16px' }}
                />
              )}
              
              <VoiceTimbreManage />
            </div>
          </AuthGuard>
        );

      case 'audio_list':
        return (
          <AuthGuard requirePermissions={['voice:read']}>
            <div>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                marginBottom: '24px'
              }}>
                <div>
                  <Title level={3}>
                    <UnorderedListOutlined /> 音频库
                  </Title>
                  <Text type="secondary">
                    查看和管理所有生成的语音音频
                  </Text>
                </div>
                
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => setCurrentMode('synthesize')}
                >
                  新建语音
                </Button>
              </div>

              <Card>
                {audioList && audioList.items.length > 0 ? (
                  <List
                    itemLayout="horizontal"
                    dataSource={audioList.items}
                    renderItem={(item: VoiceAudioBasic) => (
                      <List.Item
                        actions={[
                          <Button 
                            key="play" 
                            type="text" 
                            icon={<PlayCircleOutlined />}
                            onClick={() => {
                              if (item.audio_url) {
                                const audio = new Audio(item.audio_url);
                                audio.play();
                              }
                            }}
                          >
                            播放
                          </Button>
                        ]}
                      >
                        <List.Item.Meta
                          avatar={<Avatar icon={<SoundOutlined />} />}
                          title={
                            <Space>
                              <span>{item.audio_title}</span>
                              <Tag color="blue">{item.platform_type.toUpperCase()}</Tag>
                              <Badge 
                                status={item.audio_status === 'completed' ? 'success' : 'processing'}
                                text={item.audio_status}
                              />
                            </Space>
                          }
                          description={
                            <Space direction="vertical" size="small">
                              <div>
                                <Text type="secondary">时长: {item.audio_duration}秒</Text>
                                <Divider type="vertical" />
                                <Text type="secondary">格式: {item.audio_format.toUpperCase()}</Text>
                                <Divider type="vertical" />
                                <Text type="secondary">大小: {(item.audio_size || 0 / 1024).toFixed(1)}KB</Text>
                              </div>
                              <Text type="secondary">
                                创建时间: {new Date(item.created_at).toLocaleString()}
                              </Text>
                            </Space>
                          }
                        />
                      </List.Item>
                    )}
                  />
                ) : (
                  <Empty description="暂无音频文件" />
                )}
              </Card>
            </div>
          </AuthGuard>
        );

      case 'analytics':
        return (
          <AuthGuard requirePermissions={['voice:analytics']}>
            <div>
              <div style={{ marginBottom: '24px' }}>
                <Title level={3}>
                  <BarChartOutlined /> 数据分析
                </Title>
                <Text type="secondary">
                  查看语音服务相关的统计数据和分析报告
                </Text>
              </div>

              {usageStats && (
                <Row gutter={24}>
                  <Col span={6}>
                    <Card>
                      <Statistic
                        title="总合成次数"
                        value={usageStats.total_synthesis_count}
                        prefix={<ThunderboltOutlined />}
                      />
                    </Card>
                  </Col>
                  <Col span={6}>
                    <Card>
                      <Statistic
                        title="总语音时长"
                        value={usageStats.total_duration}
                        suffix="秒"
                        prefix={<SoundOutlined />}
                      />
                    </Card>
                  </Col>
                  <Col span={6}>
                    <Card>
                      <Statistic
                        title="Token使用量"
                        value={usageStats.total_tokens_used}
                        suffix="tokens"
                        prefix={<ApiOutlined />}
                      />
                    </Card>
                  </Col>
                  <Col span={6}>
                    <Card>
                      <Statistic
                        title="总费用"
                        value={usageStats.total_cost}
                        precision={2}
                        suffix="¥"
                        prefix={<FileTextOutlined />}
                      />
                    </Card>
                  </Col>
                </Row>
              )}

              <Card style={{ marginTop: '24px' }}>
                <div style={{ textAlign: 'center', padding: '60px 0' }}>
                  <BarChartOutlined style={{ fontSize: '48px', color: '#d9d9d9' }} />
                  <div style={{ marginTop: '16px' }}>
                    <Title level={4} type="secondary">详细分析功能开发中</Title>
                    <Text type="secondary">敬请期待更多数据分析功能</Text>
                  </div>
                </div>
              </Card>
            </div>
          </AuthGuard>
        );

      case 'settings':
        return (
          <AuthGuard requirePermissions={['voice:settings']}>
            <div>
              <div style={{ marginBottom: '24px' }}>
                <Title level={3}>
                  <SettingOutlined /> 平台设置
                </Title>
                <Text type="secondary">
                  管理和配置语音服务平台连接
                </Text>
              </div>

              <Row gutter={24}>
                {Object.entries(platformConnectionStatus).map(([platform, status]) => (
                  <Col span={6} key={platform}>
                    <Card
                      title={
                        <Space>
                          <CloudOutlined />
                          <span>{platform.toUpperCase()}</span>
                        </Space>
                      }
                      extra={
                        <Badge 
                          status={status.is_connected ? 'success' : 'error'}
                          text={status.is_connected ? '在线' : '离线'}
                        />
                      }
                    >
                      <div>
                        {status.response_time && (
                          <div>
                            <Text type="secondary">响应时间: </Text>
                            <Text>{status.response_time}ms</Text>
                          </div>
                        )}
                        {status.last_check && (
                          <div>
                            <Text type="secondary">最后检查: </Text>
                            <Text>{new Date(status.last_check).toLocaleString()}</Text>
                          </div>
                        )}
                        {status.error_message && (
                          <div style={{ marginTop: '8px' }}>
                            <Alert
                              message={status.error_message}
                              type="error"
                              size="small"
                            />
                          </div>
                        )}
                        <div style={{ marginTop: '12px' }}>
                          <Button
                            size="small"
                            onClick={() => voice_service_store_test_platform_connection(platform as any)}
                          >
                            测试连接
                          </Button>
                        </div>
                      </div>
                    </Card>
                  </Col>
                ))}
              </Row>

              <Card style={{ marginTop: '24px' }}>
                <div style={{ textAlign: 'center', padding: '60px 0' }}>
                  <SettingOutlined style={{ fontSize: '48px', color: '#d9d9d9' }} />
                  <div style={{ marginTop: '16px' }}>
                    <Title level={4} type="secondary">平台配置功能开发中</Title>
                    <Text type="secondary">敬请期待更多配置选项</Text>
                  </div>
                </div>
              </Card>
            </div>
          </AuthGuard>
        );

      default:
        return null;
    }
  };

  return (
    <AuthGuard requirePermissions={['voice:read']}>
      <div className={`voice-service-workspace ${className || ''}`}>
        <Layout style={{ minHeight: '100vh', background: '#fff' }}>
          {renderSider()}
          
          <Content style={{ padding: '24px', background: '#fff' }}>
            {renderContent()}
          </Content>
        </Layout>
      </div>
    </AuthGuard>
  );
};

export default VoiceServiceWorkspace;