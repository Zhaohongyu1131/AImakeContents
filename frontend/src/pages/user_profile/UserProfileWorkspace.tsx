/**
 * User Profile Workspace Page
 * 用户个人中心工作台页面 - [pages][user_profile][user_profile_workspace]
 */

import React, { useState, useEffect } from 'react';
import {
  Layout,
  Menu,
  Card,
  Button,
  Space,
  Typography,
  Row,
  Col,
  Statistic,
  Badge,
  Divider,
  Avatar,
  Progress
} from 'antd';
import {
  UserOutlined,
  SettingOutlined,
  SafetyOutlined,
  BellOutlined,
  FileTextOutlined,
  SoundOutlined,
  PictureOutlined,
  DashboardOutlined,
  HistoryOutlined,
  CrownOutlined
} from '@ant-design/icons';

import { useUserProfileStore } from '../../stores/user_profile/user_profile_store';
import { userProfileApiService } from '../../services/api/user_profile_api';
import {
  UserProfileBasic,
  UserProfileSecurity,
  UserProfilePreference,
  UserProfileActivity,
  UserProfileSubscription
} from '../../components/user_profile';
import type { UserProfile } from '../../services/api/user_profile_api';
import { AuthGuard } from '../../router/guards';

const { Sider, Content } = Layout;
const { Title, Text } = Typography;

type WorkspaceMode = 'basic' | 'security' | 'preference' | 'activity' | 'subscription' | 'dashboard';

interface UserProfileWorkspaceProps {
  className?: string;
}

export const UserProfileWorkspace: React.FC<UserProfileWorkspaceProps> = ({
  className
}) => {
  const [currentMode, setCurrentMode] = useState<WorkspaceMode>('dashboard');
  const [siderCollapsed, setSiderCollapsed] = useState(false);
  const [usageStats, setUsageStats] = useState<any>(null);

  const {
    profile,
    loading,
    user_profile_store_load_profile,
    user_profile_store_get_display_info
  } = useUserProfileStore();

  const displayInfo = user_profile_store_get_display_info();

  // 加载数据
  useEffect(() => {
    user_profile_store_load_profile();
    loadUsageStats();
  }, []);

  const loadUsageStats = async () => {
    try {
      const response = await userProfileApiService.user_profile_api_get_usage_statistics('month');
      if (response.success && response.data) {
        setUsageStats(response.data);
      }
    } catch (error) {
      console.error('Failed to load usage stats:', error);
    }
  };

  const handleModeChange = (mode: WorkspaceMode) => {
    setCurrentMode(mode);
  };

  const menuItems = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: '个人概览'
    },
    {
      key: 'basic',
      icon: <UserOutlined />,
      label: '基本信息'
    },
    {
      key: 'security',
      icon: <SafetyOutlined />,
      label: '安全设置'
    },
    {
      key: 'preference',
      icon: <SettingOutlined />,
      label: '偏好设置'
    },
    {
      key: 'activity',
      icon: <HistoryOutlined />,
      label: '活动记录'
    },
    {
      key: 'subscription',
      icon: <CrownOutlined />,
      label: '订阅管理'
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
        <Avatar
          size={siderCollapsed ? 32 : 64}
          src={displayInfo.avatarUrl}
          icon={!displayInfo.avatarUrl && <UserOutlined />}
          style={{ backgroundColor: '#1976d2' }}
        />
        {!siderCollapsed && (
          <div style={{ marginTop: '8px' }}>
            <Text strong>{displayInfo.displayName}</Text>
            <br />
            <Text type="secondary" style={{ fontSize: '12px' }}>
              {displayInfo.email}
            </Text>
          </div>
        )}
      </div>
      
      <Menu
        mode="inline"
        selectedKeys={[currentMode]}
        style={{ border: 'none', background: 'transparent' }}
      >
        {menuItems.map(item => (
          <Menu.Item
            key={item.key}
            icon={item.icon}
            onClick={() => handleModeChange(item.key as WorkspaceMode)}
          >
            {item.label}
          </Menu.Item>
        ))}
      </Menu>

      {/* 存储使用情况 */}
      {!siderCollapsed && usageStats && (
        <div style={{ padding: '16px', marginTop: '16px' }}>
          <Divider />
          <div>
            <Text type="secondary" style={{ fontSize: '12px' }}>存储使用</Text>
            <Progress
              percent={Math.round((usageStats.storage_used / usageStats.storage_limit) * 100)}
              size="small"
              style={{ marginTop: '4px' }}
            />
            <Text type="secondary" style={{ fontSize: '11px' }}>
              {Math.round(usageStats.storage_used / 1024 / 1024)}MB / {Math.round(usageStats.storage_limit / 1024 / 1024)}MB
            </Text>
          </div>
        </div>
      )}
    </Sider>
  );

  const renderContent = () => {
    switch (currentMode) {
      case 'dashboard':
        return (
          <div>
            <div style={{ marginBottom: '24px' }}>
              <Title level={3}>
                <DashboardOutlined /> 个人概览
              </Title>
              <Text type="secondary">
                查看您的账户概览和使用情况
              </Text>
            </div>

            {/* 用户信息卡片 */}
            <Card style={{ marginBottom: '24px' }}>
              <Row align="middle" gutter={24}>
                <Col flex="none">
                  <Avatar
                    size={80}
                    src={displayInfo.avatarUrl}
                    icon={!displayInfo.avatarUrl && <UserOutlined />}
                    style={{ backgroundColor: '#1976d2' }}
                  />
                </Col>
                <Col flex="auto">
                  <Title level={4} style={{ margin: 0 }}>{displayInfo.displayName}</Title>
                  <Text type="secondary">{displayInfo.email}</Text>
                  <br />
                  <Space style={{ marginTop: '8px' }}>
                    <Badge status={profile?.is_active ? 'success' : 'default'} text={profile?.is_active ? '活跃' : '未激活'} />
                    <Badge status="processing" text={`${displayInfo.roleName}`} />
                    {profile?.is_verified && <Badge status="success" text="已认证" />}
                  </Space>
                </Col>
              </Row>
            </Card>

            {/* 使用统计 */}
            {usageStats && (
              <Row gutter={24}>
                <Col span={6}>
                  <Card>
                    <Statistic
                      title="文本内容"
                      value={usageStats.text_count || 0}
                      prefix={<FileTextOutlined />}
                    />
                  </Card>
                </Col>
                <Col span={6}>
                  <Card>
                    <Statistic
                      title="语音合成"
                      value={usageStats.voice_count || 0}
                      prefix={<SoundOutlined />}
                    />
                  </Card>
                </Col>
                <Col span={6}>
                  <Card>
                    <Statistic
                      title="图像生成"
                      value={usageStats.image_count || 0}
                      prefix={<PictureOutlined />}
                    />
                  </Card>
                </Col>
                <Col span={6}>
                  <Card>
                    <Statistic
                      title="本月使用"
                      value={usageStats.monthly_usage || 0}
                      suffix="次"
                    />
                  </Card>
                </Col>
              </Row>
            )}

            {/* 快速操作 */}
            <Card style={{ marginTop: '24px' }} title="快速操作">
              <Row gutter={16}>
                <Col span={6}>
                  <Button
                    type="default"
                    block
                    icon={<UserOutlined />}
                    onClick={() => setCurrentMode('basic')}
                  >
                    编辑资料
                  </Button>
                </Col>
                <Col span={6}>
                  <Button
                    type="default"
                    block
                    icon={<SafetyOutlined />}
                    onClick={() => setCurrentMode('security')}
                  >
                    安全设置
                  </Button>
                </Col>
                <Col span={6}>
                  <Button
                    type="default"
                    block
                    icon={<BellOutlined />}
                    onClick={() => setCurrentMode('preference')}
                  >
                    通知设置
                  </Button>
                </Col>
                <Col span={6}>
                  <Button
                    type="default"
                    block
                    icon={<CrownOutlined />}
                    onClick={() => setCurrentMode('subscription')}
                  >
                    升级套餐
                  </Button>
                </Col>
              </Row>
            </Card>
          </div>
        );

      case 'basic':
        return (
          <div>
            <div style={{ marginBottom: '24px' }}>
              <Title level={3}>
                <UserOutlined /> 基本信息
              </Title>
              <Text type="secondary">
                管理您的个人资料信息
              </Text>
            </div>
            
            <UserProfileBasic />
          </div>
        );

      case 'security':
        return (
          <div>
            <div style={{ marginBottom: '24px' }}>
              <Title level={3}>
                <SafetyOutlined /> 安全设置
              </Title>
              <Text type="secondary">
                管理账户安全相关设置
              </Text>
            </div>

            <UserProfileSecurity />
          </div>
        );

      case 'preference':
        return (
          <div>
            <div style={{ marginBottom: '24px' }}>
              <Title level={3}>
                <SettingOutlined /> 偏好设置
              </Title>
              <Text type="secondary">
                自定义您的使用偏好
              </Text>
            </div>

            <UserProfilePreference />
          </div>
        );

      case 'activity':
        return (
          <div>
            <div style={{ marginBottom: '24px' }}>
              <Title level={3}>
                <HistoryOutlined /> 活动记录
              </Title>
              <Text type="secondary">
                查看您的账户活动历史
              </Text>
            </div>

            <UserProfileActivity />
          </div>
        );

      case 'subscription':
        return (
          <div>
            <div style={{ marginBottom: '24px' }}>
              <Title level={3}>
                <CrownOutlined /> 订阅管理
              </Title>
              <Text type="secondary">
                管理您的订阅套餐和账单
              </Text>
            </div>

            <UserProfileSubscription />
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <AuthGuard>
      <div className={`user-profile-workspace ${className || ''}`}>
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

export default UserProfileWorkspace;