/**
 * Image Service Workspace Page
 * 图像服务工作台页面 - [pages][image_service][image_service_workspace]
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
  Empty,
  Image,
  Grid
} from 'antd';
import {
  PictureOutlined,
  ThunderboltOutlined,
  UnorderedListOutlined,
  BulbOutlined,
  BarChartOutlined,
  PlusOutlined,
  EyeOutlined,
  DownloadOutlined,
  CopyOutlined,
  SettingOutlined,
  CloudOutlined,
  ApiOutlined,
  FileTextOutlined,
  EditOutlined
} from '@ant-design/icons';

import { useImageServiceStore } from '../../stores/image_service/image_service_store';
import { useAuthStore } from '../../stores/auth/auth_store';
import {
  ImageContentGenerate,
  ImageTemplateManage
} from '../../components/image_service';
import type { ImageContentBasic, ImageGenerationResponse } from '../../services/api/image_service_api';
import { AuthGuard, PermissionGuard } from '../../router/guards';

const { Sider, Content } = Layout;
const { Title, Text } = Typography;
const { useBreakpoint } = Grid;

type WorkspaceMode = 'generate' | 'templates' | 'gallery' | 'analytics' | 'settings';

interface ImageServiceWorkspaceProps {
  className?: string;
}

export const ImageServiceWorkspace: React.FC<ImageServiceWorkspaceProps> = ({
  className
}) => {
  const [currentMode, setCurrentMode] = useState<WorkspaceMode>('generate');
  const [siderCollapsed, setSiderCollapsed] = useState(false);
  const [selectedTemplateId, setSelectedTemplateId] = useState<number | undefined>();

  const screens = useBreakpoint();

  const {
    imageList,
    templateList,
    usageStats,
    generationLoading,
    lastGenerationResult,
    batchGenerationStatus,
    platformConnectionStatus,
    image_service_store_load_image_list,
    image_service_store_load_template_list,
    image_service_store_load_usage_stats,
    image_service_store_test_platform_connection,
    image_service_store_delete_image
  } = useImageServiceStore();

  const { userInfo } = useAuthStore();

  // 初始化数据加载
  useEffect(() => {
    image_service_store_load_image_list(1, 12);
    image_service_store_load_template_list(1, 10, { is_public: true });
    image_service_store_load_usage_stats('month');

    // 测试平台连接状态
    image_service_store_test_platform_connection('doubao');
    image_service_store_test_platform_connection('dalle');
    image_service_store_test_platform_connection('stable_diffusion');
  }, []);

  const handleModeChange = (mode: WorkspaceMode) => {
    setCurrentMode(mode);
  };

  const handleGenerationResult = (result: ImageGenerationResponse) => {
    // 生成成功后刷新图像库
    image_service_store_load_image_list(1, 12);
  };

  const handleTemplateGenerate = (result: ImageGenerationResponse) => {
    // 模板生成成功后刷新图像库
    image_service_store_load_image_list(1, 12);
  };

  // 下载图像
  const handleDownloadImage = (imageUrl: string, fileName: string) => {
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
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
      key: 'generate',
      icon: <ThunderboltOutlined />,
      label: 'AI生成',
      permission: 'image:generate'
    },
    {
      key: 'templates',
      icon: <BulbOutlined />,
      label: '模板库',
      permission: 'image:template'
    },
    {
      key: 'gallery',
      icon: <UnorderedListOutlined />,
      label: '图像库',
      permission: 'image:read'
    },
    {
      key: 'analytics',
      icon: <BarChartOutlined />,
      label: '数据分析',
      permission: 'image:analytics'
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '平台设置',
      permission: 'image:settings'
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
      breakpoint="lg"
      collapsedWidth={screens.xs ? 0 : 80}
    >
      <div style={{ padding: '16px', textAlign: 'center' }}>
        <PictureOutlined style={{ fontSize: '24px', color: '#eb2f96' }} />
        {!siderCollapsed && (
          <div style={{ marginTop: '8px' }}>
            <Text strong>图像工作台</Text>
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
              title="本月生成"
              value={usageStats?.total_generation_count || 0}
              valueStyle={{ fontSize: '16px' }}
              suffix="张"
            />
            <Statistic
              title="模板库"
              value={templateList?.total || 0}
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
      case 'generate':
        return (
          <AuthGuard requirePermissions={['image:generate']}>
            <div>
              <div style={{ marginBottom: '24px' }}>
                <Title level={3}>
                  <ThunderboltOutlined /> AI图像生成
                </Title>
                <Text type="secondary">
                  使用先进的人工智能技术创造精美图像
                </Text>
              </div>
              
              <ImageContentGenerate
                onGenerated={handleGenerationResult}
              />
            </div>
          </AuthGuard>
        );

      case 'templates':
        return (
          <AuthGuard requirePermissions={['image:template']}>
            <div>
              <div style={{ marginBottom: '24px' }}>
                <Title level={3}>
                  <BulbOutlined /> 图像模板库
                </Title>
                <Text type="secondary">
                  智能模板，一键生成专业级图像
                </Text>
              </div>

              <ImageTemplateManage
                onTemplateGenerate={handleTemplateGenerate}
              />
            </div>
          </AuthGuard>
        );

      case 'gallery':
        return (
          <AuthGuard requirePermissions={['image:read']}>
            <div>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                marginBottom: '24px'
              }}>
                <div>
                  <Title level={3}>
                    <UnorderedListOutlined /> 图像库
                  </Title>
                  <Text type="secondary">
                    查看和管理所有生成的图像
                  </Text>
                </div>
                
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => setCurrentMode('generate')}
                >
                  生成新图像
                </Button>
              </div>

              <Card>
                {imageList && imageList.items.length > 0 ? (
                  <Row gutter={[16, 16]}>
                    {imageList.items.map((item: ImageContentBasic) => (
                      <Col xs={24} sm={12} md={8} lg={6} xl={4} key={item.image_id}>
                        <Card
                          size="small"
                          cover={
                            <div style={{ position: 'relative', overflow: 'hidden' }}>
                              <Image
                                src={item.thumbnail_url || item.image_url}
                                alt={item.image_title}
                                style={{ 
                                  width: '100%', 
                                  height: 200, 
                                  objectFit: 'cover' 
                                }}
                                preview={{
                                  src: item.image_url
                                }}
                              />
                              <div style={{
                                position: 'absolute',
                                top: 8,
                                right: 8,
                                display: 'flex',
                                gap: 4
                              }}>
                                <Button
                                  type="primary"
                                  size="small"
                                  icon={<DownloadOutlined />}
                                  onClick={() => handleDownloadImage(
                                    item.image_url || '',
                                    `${item.image_title}.${item.image_format}`
                                  )}
                                />
                              </div>
                            </div>
                          }
                          actions={[
                            <EyeOutlined key="view" />,
                            <EditOutlined key="edit" />,
                            <DownloadOutlined key="download" />
                          ]}
                        >
                          <Card.Meta
                            title={
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <Text ellipsis style={{ flex: 1 }}>{item.image_title}</Text>
                                <Tag color="blue" size="small">
                                  {item.platform_type.toUpperCase()}
                                </Tag>
                              </div>
                            }
                            description={
                              <Space direction="vertical" size="small" style={{ width: '100%' }}>
                                <div>
                                  <Text type="secondary" style={{ fontSize: '12px' }}>
                                    {item.image_width}×{item.image_height} • {item.image_format.toUpperCase()}
                                  </Text>
                                </div>
                                <div>
                                  <Badge 
                                    status={item.image_status === 'completed' ? 'success' : 'processing'}
                                    text={item.image_status}
                                  />
                                </div>
                                <Text type="secondary" style={{ fontSize: '11px' }}>
                                  {new Date(item.created_at).toLocaleDateString()}
                                </Text>
                              </Space>
                            }
                          />
                        </Card>
                      </Col>
                    ))}
                  </Row>
                ) : (
                  <Empty 
                    description="暂无图像"
                    image={Empty.PRESENTED_IMAGE_SIMPLE}
                  />
                )}
              </Card>
            </div>
          </AuthGuard>
        );

      case 'analytics':
        return (
          <AuthGuard requirePermissions={['image:analytics']}>
            <div>
              <div style={{ marginBottom: '24px' }}>
                <Title level={3}>
                  <BarChartOutlined /> 数据分析
                </Title>
                <Text type="secondary">
                  查看图像生成相关的统计数据和分析报告
                </Text>
              </div>

              {usageStats && (
                <Row gutter={24}>
                  <Col span={6}>
                    <Card>
                      <Statistic
                        title="总生成次数"
                        value={usageStats.total_generation_count}
                        prefix={<ThunderboltOutlined />}
                      />
                    </Card>
                  </Col>
                  <Col span={6}>
                    <Card>
                      <Statistic
                        title="总图像数量"
                        value={usageStats.total_images_generated}
                        prefix={<PictureOutlined />}
                      />
                    </Card>
                  </Col>
                  <Col span={6}>
                    <Card>
                      <Statistic
                        title="积分使用量"
                        value={usageStats.total_credits_used}
                        suffix="credits"
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

              {/* 风格使用统计 */}
              {usageStats?.style_usage && (
                <Card title="热门风格" style={{ marginTop: 24 }}>
                  <Row gutter={16}>
                    {usageStats.style_usage.slice(0, 6).map((style, index) => (
                      <Col span={4} key={style.style}>
                        <Card size="small">
                          <Statistic
                            title={
                              style.style === 'realistic' ? '写实' :
                              style.style === 'anime' ? '动漫' :
                              style.style === 'cartoon' ? '卡通' :
                              style.style === 'oil_painting' ? '油画' :
                              style.style === 'watercolor' ? '水彩' :
                              style.style === 'sketch' ? '素描' : '数字艺术'
                            }
                            value={style.percentage}
                            suffix="%"
                            valueStyle={{ fontSize: '16px' }}
                          />
                        </Card>
                      </Col>
                    ))}
                  </Row>
                </Card>
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
          <AuthGuard requirePermissions={['image:settings']}>
            <div>
              <div style={{ marginBottom: '24px' }}>
                <Title level={3}>
                  <SettingOutlined /> 平台设置
                </Title>
                <Text type="secondary">
                  管理和配置图像生成平台连接
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
                            onClick={() => image_service_store_test_platform_connection(platform as any)}
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
    <AuthGuard requirePermissions={['image:read']}>
      <div className={`image-service-workspace ${className || ''}`}>
        <Layout style={{ minHeight: '100vh', background: '#fff' }}>
          {renderSider()}
          
          <Content style={{ padding: screens.xs ? '16px' : '24px', background: '#fff' }}>
            {/* 批量生成状态提示 */}
            {batchGenerationStatus && batchGenerationStatus.status === 'processing' && (
              <Alert
                message="批量生成进行中"
                description={
                  <div>
                    <div>任务ID: {batchGenerationStatus.task_id}</div>
                    <Progress 
                      percent={batchGenerationStatus.progress} 
                      status="active" 
                      showInfo={false} 
                    />
                    <div>
                      已完成: {batchGenerationStatus.completed_count} | 
                      失败: {batchGenerationStatus.failed_count}
                    </div>
                  </div>
                }
                type="info"
                showIcon
                style={{ marginBottom: '16px' }}
              />
            )}
            
            {renderContent()}
          </Content>
        </Layout>
      </div>
    </AuthGuard>
  );
};

export default ImageServiceWorkspace;