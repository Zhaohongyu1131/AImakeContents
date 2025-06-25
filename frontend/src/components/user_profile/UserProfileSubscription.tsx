/**
 * User Profile Subscription Component
 * 用户订阅管理组件 - [components][user_profile][user_profile_subscription]
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Button,
  Space,
  Typography,
  Progress,
  Tag,
  Alert,
  Divider,
  List,
  Modal,
  message,
  Statistic,
  Badge,
  Table,
  Empty
} from 'antd';
import {
  CrownOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  DollarOutlined,
  CalendarOutlined,
  FileTextOutlined,
  SoundOutlined,
  PictureOutlined,
  CloudOutlined,
  StarOutlined,
  GiftOutlined,
  HistoryOutlined,
  CreditCardOutlined
} from '@ant-design/icons';
import dayjs from 'dayjs';

import { userProfileApiService } from '../../services/api/user_profile_api';
import type { SubscriptionInfo, BillingHistory, UsageQuota } from '../../services/api/user_profile_api';

const { Title, Text, Paragraph } = Typography;

interface UserProfileSubscriptionProps {
  className?: string;
}

export const UserProfileSubscription: React.FC<UserProfileSubscriptionProps> = ({
  className
}) => {
  const [subscription, setSubscription] = useState<SubscriptionInfo | null>(null);
  const [usage, setUsage] = useState<UsageQuota | null>(null);
  const [billingHistory, setBillingHistory] = useState<BillingHistory[]>([]);
  const [loading, setLoading] = useState(false);
  const [upgradeModalVisible, setUpgradeModalVisible] = useState(false);

  // 加载订阅信息
  useEffect(() => {
    loadSubscriptionInfo();
    loadUsageQuota();
    loadBillingHistory();
  }, []);

  const loadSubscriptionInfo = async () => {
    try {
      const response = await userProfileApiService.user_profile_api_get_subscription_info();
      if (response.success && response.data) {
        setSubscription(response.data);
      }
    } catch (error) {
      console.error('Failed to load subscription info:', error);
    }
  };

  const loadUsageQuota = async () => {
    try {
      const response = await userProfileApiService.user_profile_api_get_usage_quota();
      if (response.success && response.data) {
        setUsage(response.data);
      }
    } catch (error) {
      console.error('Failed to load usage quota:', error);
    }
  };

  const loadBillingHistory = async () => {
    try {
      const response = await userProfileApiService.user_profile_api_get_billing_history({
        page: 1,
        page_size: 10
      });
      if (response.success && response.data) {
        setBillingHistory(response.data.items || []);
      }
    } catch (error) {
      console.error('Failed to load billing history:', error);
    }
  };

  const handleUpgrade = async (planId: string) => {
    setLoading(true);
    try {
      const response = await userProfileApiService.user_profile_api_upgrade_subscription(planId);
      if (response.success) {
        message.success('升级申请已提交');
        setUpgradeModalVisible(false);
        loadSubscriptionInfo();
      } else {
        message.error(response.message || '升级失败');
      }
    } catch (error) {
      console.error('Failed to upgrade subscription:', error);
      message.error('升级失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async () => {
    Modal.confirm({
      title: '取消订阅',
      content: '确定要取消当前订阅吗？取消后将在下个计费周期结束时生效。',
      onOk: async () => {
        try {
          const response = await userProfileApiService.user_profile_api_cancel_subscription();
          if (response.success) {
            message.success('订阅取消成功');
            loadSubscriptionInfo();
          }
        } catch (error) {
          console.error('Failed to cancel subscription:', error);
          message.error('取消失败，请重试');
        }
      }
    });
  };

  const getPlanBadge = (planType: string) => {
    switch (planType) {
      case 'free':
        return <Tag>免费版</Tag>;
      case 'basic':
        return <Tag color="blue">基础版</Tag>;
      case 'pro':
        return <Tag color="gold">专业版</Tag>;
      case 'enterprise':
        return <Tag color="purple">企业版</Tag>;
      default:
        return <Tag>未知</Tag>;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge status="success" text="正常" />;
      case 'cancelled':
        return <Badge status="warning" text="已取消" />;
      case 'expired':
        return <Badge status="error" text="已过期" />;
      case 'suspended':
        return <Badge status="default" text="已暂停" />;
      default:
        return <Badge status="default" text="未知" />;
    }
  };

  const planFeatures = {
    free: [
      '每月 1,000 个文本 token',
      '每月 10 分钟语音合成',
      '每月 5 张图像生成',
      '基础模板',
      '社区支持'
    ],
    basic: [
      '每月 10,000 个文本 token',
      '每月 60 分钟语音合成',
      '每月 50 张图像生成',
      '所有模板',
      '邮件支持',
      '数据导出'
    ],
    pro: [
      '每月 100,000 个文本 token',
      '每月 300 分钟语音合成',
      '每月 200 张图像生成',
      '高级模板',
      '优先支持',
      'API 访问',
      '团队协作'
    ],
    enterprise: [
      '无限文本 token',
      '无限语音合成',
      '无限图像生成',
      '定制模板',
      '专属支持',
      '私有部署',
      '高级分析'
    ]
  };

  const billingColumns = [
    {
      title: '日期',
      dataIndex: 'billing_date',
      key: 'billing_date',
      render: (date: string) => dayjs(date).format('YYYY-MM-DD')
    },
    {
      title: '类型',
      dataIndex: 'billing_type',
      key: 'billing_type',
      render: (type: string) => {
        const typeMap: Record<string, string> = {
          'subscription': '订阅费用',
          'upgrade': '升级费用',
          'usage': '超额使用',
          'refund': '退款'
        };
        return typeMap[type] || type;
      }
    },
    {
      title: '金额',
      dataIndex: 'amount',
      key: 'amount',
      render: (amount: number) => `¥${amount.toFixed(2)}`
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const color = status === 'paid' ? 'success' : status === 'pending' ? 'processing' : 'error';
        const text = status === 'paid' ? '已支付' : status === 'pending' ? '待支付' : '失败';
        return <Tag color={color}>{text}</Tag>;
      }
    }
  ];

  return (
    <div className={className}>
      {/* 当前订阅状态 */}
      <Card style={{ marginBottom: '24px' }}>
        <Row align="middle">
          <Col flex="auto">
            <Space direction="vertical" size="small">
              <div>
                <Space align="center">
                  <CrownOutlined style={{ fontSize: '24px', color: '#faad14' }} />
                  <Title level={4} style={{ margin: 0 }}>
                    当前套餐
                  </Title>
                  {subscription && getPlanBadge(subscription.plan_type)}
                </Space>
              </div>
              <div>
                {subscription && getStatusBadge(subscription.status)}
                {subscription && subscription.next_billing_date && (
                  <Text type="secondary" style={{ marginLeft: '12px' }}>
                    下次计费：{dayjs(subscription.next_billing_date).format('YYYY-MM-DD')}
                  </Text>
                )}
              </div>
            </Space>
          </Col>
          <Col flex="none">
            <Space>
              {subscription?.plan_type !== 'enterprise' && (
                <Button
                  type="primary"
                  icon={<StarOutlined />}
                  onClick={() => setUpgradeModalVisible(true)}
                >
                  升级套餐
                </Button>
              )}
              {subscription?.plan_type !== 'free' && subscription?.status === 'active' && (
                <Button
                  danger
                  onClick={handleCancel}
                >
                  取消订阅
                </Button>
              )}
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 使用情况 */}
      {usage && (
        <Card title="本月使用情况" style={{ marginBottom: '24px' }}>
          <Row gutter={24}>
            <Col span={8}>
              <Card size="small">
                <Statistic
                  title="文本 Token"
                  value={usage.text_tokens_used}
                  suffix={`/ ${usage.text_tokens_limit}`}
                  prefix={<FileTextOutlined />}
                />
                <Progress
                  percent={Math.round((usage.text_tokens_used / usage.text_tokens_limit) * 100)}
                  size="small"
                  style={{ marginTop: '8px' }}
                />
              </Card>
            </Col>
            <Col span={8}>
              <Card size="small">
                <Statistic
                  title="语音合成 (分钟)"
                  value={usage.voice_minutes_used}
                  suffix={`/ ${usage.voice_minutes_limit}`}
                  prefix={<SoundOutlined />}
                />
                <Progress
                  percent={Math.round((usage.voice_minutes_used / usage.voice_minutes_limit) * 100)}
                  size="small"
                  style={{ marginTop: '8px' }}
                />
              </Card>
            </Col>
            <Col span={8}>
              <Card size="small">
                <Statistic
                  title="图像生成"
                  value={usage.image_count_used}
                  suffix={`/ ${usage.image_count_limit}`}
                  prefix={<PictureOutlined />}
                />
                <Progress
                  percent={Math.round((usage.image_count_used / usage.image_count_limit) * 100)}
                  size="small"
                  style={{ marginTop: '8px' }}
                />
              </Card>
            </Col>
          </Row>
          
          {usage.storage_used && (
            <div style={{ marginTop: '16px' }}>
              <Row gutter={24}>
                <Col span={12}>
                  <Text type="secondary">存储空间使用：</Text>
                  <Progress
                    percent={Math.round((usage.storage_used / usage.storage_limit) * 100)}
                    format={() => `${Math.round(usage.storage_used / 1024 / 1024)}MB / ${Math.round(usage.storage_limit / 1024 / 1024)}MB`}
                  />
                </Col>
              </Row>
            </div>
          )}
        </Card>
      )}

      {/* 账单历史 */}
      <Card
        title="账单历史"
        extra={
          <Button
            type="link"
            icon={<HistoryOutlined />}
            size="small"
          >
            查看全部
          </Button>
        }
        style={{ marginBottom: '24px' }}
      >
        {billingHistory.length > 0 ? (
          <Table
            dataSource={billingHistory}
            columns={billingColumns}
            pagination={false}
            size="small"
          />
        ) : (
          <Empty description="暂无账单记录" image={Empty.PRESENTED_IMAGE_SIMPLE} />
        )}
      </Card>

      {/* 升级套餐弹窗 */}
      <Modal
        title="升级套餐"
        open={upgradeModalVisible}
        onCancel={() => setUpgradeModalVisible(false)}
        footer={null}
        width={800}
      >
        <Row gutter={24}>
          {Object.entries(planFeatures).map(([planType, features]) => (
            <Col span={12} key={planType} style={{ marginBottom: '24px' }}>
              <Card
                title={
                  <Space>
                    <CrownOutlined />
                    {planType === 'free' ? '免费版' : 
                     planType === 'basic' ? '基础版' : 
                     planType === 'pro' ? '专业版' : '企业版'}
                  </Space>
                }
                extra={
                  planType === subscription?.plan_type ? (
                    <Tag color="blue">当前套餐</Tag>
                  ) : (
                    <Button
                      type="primary"
                      size="small"
                      onClick={() => handleUpgrade(planType)}
                      loading={loading}
                      disabled={planType === 'free'}
                    >
                      {planType === 'free' ? '免费' : '升级'}
                    </Button>
                  )
                }
                size="small"
              >
                <div style={{ marginBottom: '16px' }}>
                  <Text strong style={{ fontSize: '24px' }}>
                    {planType === 'free' ? '¥0' : 
                     planType === 'basic' ? '¥29' : 
                     planType === 'pro' ? '¥99' : '联系我们'}
                  </Text>
                  {planType !== 'free' && planType !== 'enterprise' && (
                    <Text type="secondary">/月</Text>
                  )}
                </div>
                
                <List
                  dataSource={features}
                  renderItem={(feature) => (
                    <List.Item style={{ padding: '4px 0', border: 'none' }}>
                      <Space size="small">
                        <CheckCircleOutlined style={{ color: '#52c41a' }} />
                        <Text style={{ fontSize: '12px' }}>{feature}</Text>
                      </Space>
                    </List.Item>
                  )}
                />
              </Card>
            </Col>
          ))}
        </Row>
        
        <Alert
          message="升级说明"
          description="升级后立即生效，费用按剩余天数计算。如需更多定制功能，请联系我们的销售团队。"
          type="info"
          showIcon
          style={{ marginTop: '16px' }}
        />
      </Modal>
    </div>
  );
};

export default UserProfileSubscription;