/**
 * Text Content Workspace Page
 * 文本内容工作台页面 - [pages][text_content][text_content_workspace]
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
  Divider
} from 'antd';
import {
  FileTextOutlined,
  BulbOutlined,
  UnorderedListOutlined,
  EditOutlined,
  TemplateOutlined,
  BarChartOutlined,
  PlusOutlined,
  SearchOutlined
} from '@ant-design/icons';

import { useTextContentStore } from '../../stores/text_content/text_content_store';
import { textContentApiService } from '../../services/api/text_content_api';
import {
  TextContentGenerator,
  TextContentList,
  TextContentEditor
} from '../../components/text_content';
import type { TextContentBasic } from '../../services/api/text_content_api';
import { AuthGuard, PermissionGuard } from '../../router/guards';

const { Sider, Content } = Layout;
const { Title, Text } = Typography;
const { TabPane } = Tabs;

type WorkspaceMode = 'generator' | 'list' | 'editor' | 'templates' | 'analytics';

interface TextContentWorkspaceProps {
  className?: string;
}

export const TextContentWorkspace: React.FC<TextContentWorkspaceProps> = ({
  className
}) => {
  const [currentMode, setCurrentMode] = useState<WorkspaceMode>('generator');
  const [editingContent, setEditingContent] = useState<TextContentBasic | null>(null);
  const [siderCollapsed, setSiderCollapsed] = useState(false);
  const [usageStats, setUsageStats] = useState<any>(null);

  const {
    contentList,
    generationLoading,
    lastGenerationResult,
    text_content_store_load_content_list
  } = useTextContentStore();

  // 加载数据
  useEffect(() => {
    text_content_store_load_content_list();
    loadUsageStats();
  }, []);

  const loadUsageStats = async () => {
    try {
      const response = await textContentApiService.text_content_api_get_usage_stats('month');
      if (response.success && response.data) {
        setUsageStats(response.data);
      }
    } catch (error) {
      console.error('Failed to load usage stats:', error);
    }
  };

  const handleModeChange = (mode: WorkspaceMode) => {
    setCurrentMode(mode);
    setEditingContent(null);
  };

  const handleCreateNew = () => {
    setCurrentMode('editor');
    setEditingContent(null);
  };

  const handleEditContent = (content: TextContentBasic) => {
    setCurrentMode('editor');
    setEditingContent(content);
  };

  const handleContentSaved = (content: TextContentBasic) => {
    // 保存成功后返回列表
    setCurrentMode('list');
    setEditingContent(null);
    // 刷新列表
    text_content_store_load_content_list();
  };

  const handleGeneratorResult = (result: any) => {
    // 生成成功后可以选择编辑或保存
    if (result.content_id) {
      // 如果已保存到内容库，刷新列表
      text_content_store_load_content_list();
    }
  };

  const menuItems = [
    {
      key: 'generator',
      icon: <BulbOutlined />,
      label: 'AI生成器',
      permission: 'text:generate'
    },
    {
      key: 'list',
      icon: <UnorderedListOutlined />,
      label: '内容列表',
      permission: 'text:read'
    },
    {
      key: 'editor',
      icon: <EditOutlined />,
      label: '编辑器',
      permission: 'text:create'
    },
    {
      key: 'templates',
      icon: <TemplateOutlined />,
      label: '模板库',
      permission: 'text:template'
    },
    {
      key: 'analytics',
      icon: <BarChartOutlined />,
      label: '数据分析',
      permission: 'text:analytics'
    }
  ];

  const renderSider = () => (
    <Sider
      collapsible
      collapsed={siderCollapsed}
      onCollapse={setSiderCollapsed}
      theme="light"
      width={200}
      style={{ 
        borderRight: '1px solid #f0f0f0',
        background: '#fafafa'
      }}
    >
      <div style={{ padding: '16px', textAlign: 'center' }}>
        <FileTextOutlined style={{ fontSize: '24px', color: '#1976d2' }} />
        {!siderCollapsed && (
          <div style={{ marginTop: '8px' }}>
            <Text strong>文本工作台</Text>
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

      {/* 统计信息 */}
      {!siderCollapsed && usageStats && (
        <div style={{ padding: '16px', marginTop: '16px' }}>
          <Divider />
          <div style={{ textAlign: 'center' }}>
            <Statistic
              title="本月内容"
              value={usageStats.total_content_count}
              valueStyle={{ fontSize: '16px' }}
            />
            <Statistic
              title="AI生成"
              value={usageStats.total_generation_count}
              valueStyle={{ fontSize: '16px' }}
              style={{ marginTop: '8px' }}
            />
          </div>
        </div>
      )}
    </Sider>
  );

  const renderContent = () => {
    switch (currentMode) {
      case 'generator':
        return (
          <AuthGuard requirePermissions={['text:generate']}>
            <div>
              <div style={{ marginBottom: '24px' }}>
                <Title level={3}>
                  <BulbOutlined /> AI文本生成器
                </Title>
                <Text type="secondary">
                  使用人工智能快速生成高质量文本内容
                </Text>
              </div>
              
              <TextContentGenerator
                onGenerated={handleGeneratorResult}
              />
            </div>
          </AuthGuard>
        );

      case 'list':
        return (
          <AuthGuard requirePermissions={['text:read']}>
            <div>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                marginBottom: '24px'
              }}>
                <div>
                  <Title level={3}>
                    <UnorderedListOutlined /> 内容列表
                  </Title>
                  <Text type="secondary">
                    管理和查看所有文本内容
                  </Text>
                </div>
                
                <Space>
                  <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={handleCreateNew}
                  >
                    新建内容
                  </Button>
                </Space>
              </div>

              <TextContentList
                onItemEdit={handleEditContent}
                onItemClick={(content) => {
                  // 点击查看详情
                  setEditingContent(content);
                  setCurrentMode('editor');
                }}
              />
            </div>
          </AuthGuard>
        );

      case 'editor':
        return (
          <AuthGuard requirePermissions={['text:create', 'text:edit']}>
            <div>
              <div style={{ marginBottom: '24px' }}>
                <Title level={3}>
                  <EditOutlined /> 内容编辑器
                </Title>
                <Text type="secondary">
                  {editingContent ? '编辑现有内容' : '创建新的文本内容'}
                </Text>
              </div>

              <TextContentEditor
                contentId={editingContent?.content_id}
                mode={editingContent ? 'edit' : 'create'}
                onSave={handleContentSaved}
                onCancel={() => handleModeChange('list')}
              />
            </div>
          </AuthGuard>
        );

      case 'templates':
        return (
          <AuthGuard requirePermissions={['text:template']}>
            <div>
              <div style={{ marginBottom: '24px' }}>
                <Title level={3}>
                  <TemplateOutlined /> 模板库
                </Title>
                <Text type="secondary">
                  管理和使用文本生成模板
                </Text>
              </div>
              
              <Card>
                <div style={{ textAlign: 'center', padding: '60px 0' }}>
                  <TemplateOutlined style={{ fontSize: '48px', color: '#d9d9d9' }} />
                  <div style={{ marginTop: '16px' }}>
                    <Title level={4} type="secondary">模板功能开发中</Title>
                    <Text type="secondary">敬请期待模板管理功能</Text>
                  </div>
                </div>
              </Card>
            </div>
          </AuthGuard>
        );

      case 'analytics':
        return (
          <AuthGuard requirePermissions={['text:analytics']}>
            <div>
              <div style={{ marginBottom: '24px' }}>
                <Title level={3}>
                  <BarChartOutlined /> 数据分析
                </Title>
                <Text type="secondary">
                  查看文本内容相关的统计数据和分析报告
                </Text>
              </div>

              {usageStats && (
                <Row gutter={24}>
                  <Col span={6}>
                    <Card>
                      <Statistic
                        title="总内容数"
                        value={usageStats.total_content_count}
                        prefix={<FileTextOutlined />}
                      />
                    </Card>
                  </Col>
                  <Col span={6}>
                    <Card>
                      <Statistic
                        title="AI生成次数"
                        value={usageStats.total_generation_count}
                        prefix={<BulbOutlined />}
                      />
                    </Card>
                  </Col>
                  <Col span={6}>
                    <Card>
                      <Statistic
                        title="Token使用量"
                        value={usageStats.total_tokens_used}
                        suffix="tokens"
                      />
                    </Card>
                  </Col>
                  <Col span={6}>
                    <Card>
                      <Statistic
                        title="平均内容长度"
                        value={usageStats.total_content_count > 0 ? 
                          Math.round(usageStats.total_tokens_used / usageStats.total_content_count) : 0}
                        suffix="字符"
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

      default:
        return null;
    }
  };

  return (
    <AuthGuard requirePermissions={['text:read']}>
      <div className={`text-content-workspace ${className || ''}`}>
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

export default TextContentWorkspace;