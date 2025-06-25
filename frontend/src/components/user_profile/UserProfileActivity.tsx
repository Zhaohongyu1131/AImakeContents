/**
 * User Profile Activity Component
 * 用户活动记录组件 - [components][user_profile][user_profile_activity]
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  List,
  Timeline,
  Space,
  Typography,
  Button,
  Select,
  DatePicker,
  Row,
  Col,
  Tag,
  Avatar,
  Statistic,
  Empty,
  Spin
} from 'antd';
import {
  HistoryOutlined,
  FileTextOutlined,
  SoundOutlined,
  PictureOutlined,
  LoginOutlined,
  EditOutlined,
  DeleteOutlined,
  DownloadOutlined,
  UploadOutlined,
  UserOutlined,
  CalendarOutlined,
  ClockCircleOutlined,
  GlobalOutlined
} from '@ant-design/icons';
import dayjs from 'dayjs';

import { userProfileApiService } from '../../services/api/user_profile_api';
import type { ActivityRecord, LoginHistory } from '../../services/api/user_profile_api';

const { Title, Text } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;

interface UserProfileActivityProps {
  className?: string;
}

export const UserProfileActivity: React.FC<UserProfileActivityProps> = ({
  className
}) => {
  const [activities, setActivities] = useState<ActivityRecord[]>([]);
  const [loginHistory, setLoginHistory] = useState<LoginHistory[]>([]);
  const [loading, setLoading] = useState(false);
  const [currentTab, setCurrentTab] = useState<'activities' | 'logins'>('activities');
  const [activityType, setActivityType] = useState<string>('all');
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs] | null>(null);
  const [pagination, setPagination] = useState({ page: 1, pageSize: 20, total: 0 });

  // 加载活动记录
  useEffect(() => {
    if (currentTab === 'activities') {
      loadActivities();
    } else {
      loadLoginHistory();
    }
  }, [currentTab, activityType, dateRange, pagination.page]);

  const loadActivities = async () => {
    setLoading(true);
    try {
      const response = await userProfileApiService.user_profile_api_get_activity_history({
        page: pagination.page,
        page_size: pagination.pageSize,
        activity_type: activityType === 'all' ? undefined : activityType,
        start_date: dateRange?.[0]?.format('YYYY-MM-DD'),
        end_date: dateRange?.[1]?.format('YYYY-MM-DD')
      });
      
      if (response.success && response.data) {
        setActivities(response.data.items || []);
        setPagination(prev => ({
          ...prev,
          total: response.data.total || 0
        }));
      }
    } catch (error) {
      console.error('Failed to load activities:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadLoginHistory = async () => {
    setLoading(true);
    try {
      const response = await userProfileApiService.user_profile_api_get_login_history({
        page: pagination.page,
        page_size: pagination.pageSize,
        start_date: dateRange?.[0]?.format('YYYY-MM-DD'),
        end_date: dateRange?.[1]?.format('YYYY-MM-DD')
      });
      
      if (response.success && response.data) {
        setLoginHistory(response.data.items || []);
        setPagination(prev => ({
          ...prev,
          total: response.data.total || 0
        }));
      }
    } catch (error) {
      console.error('Failed to load login history:', error);
    } finally {
      setLoading(false);
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'text_create':
      case 'text_edit':
      case 'text_delete':
        return <FileTextOutlined style={{ color: '#1976d2' }} />;
      case 'voice_create':
      case 'voice_edit':
      case 'voice_delete':
        return <SoundOutlined style={{ color: '#ff9800' }} />;
      case 'image_create':
      case 'image_edit':
      case 'image_delete':
        return <PictureOutlined style={{ color: '#4caf50' }} />;
      case 'profile_edit':
        return <EditOutlined style={{ color: '#9c27b0' }} />;
      case 'login':
        return <LoginOutlined style={{ color: '#2196f3' }} />;
      case 'upload':
        return <UploadOutlined style={{ color: '#ff5722' }} />;
      case 'download':
        return <DownloadOutlined style={{ color: '#607d8b' }} />;
      default:
        return <HistoryOutlined style={{ color: '#666' }} />;
    }
  };

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'create':
        return 'success';
      case 'edit':
        return 'processing';
      case 'delete':
        return 'error';
      case 'login':
        return 'blue';
      default:
        return 'default';
    }
  };

  const getActivityDescription = (activity: ActivityRecord) => {
    const actionMap: Record<string, string> = {
      'text_create': '创建了文本内容',
      'text_edit': '编辑了文本内容',
      'text_delete': '删除了文本内容',
      'voice_create': '创建了语音内容',
      'voice_edit': '编辑了语音内容',
      'voice_delete': '删除了语音内容',
      'image_create': '创建了图像内容',
      'image_edit': '编辑了图像内容',
      'image_delete': '删除了图像内容',
      'profile_edit': '更新了个人资料',
      'login': '登录了系统',
      'upload': '上传了文件',
      'download': '下载了文件'
    };
    
    const baseDescription = actionMap[activity.activity_type] || activity.activity_type;
    return activity.description || baseDescription;
  };

  const handleTabChange = (tab: 'activities' | 'logins') => {
    setCurrentTab(tab);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handleFilterChange = () => {
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handlePageChange = (page: number, pageSize?: number) => {
    setPagination(prev => ({
      ...prev,
      page,
      pageSize: pageSize || prev.pageSize
    }));
  };

  const renderActivities = () => (
    <div>
      {/* 筛选器 */}
      <Card size="small" style={{ marginBottom: '16px' }}>
        <Row gutter={16} align="middle">
          <Col span={6}>
            <Select
              value={activityType}
              onChange={(value) => {
                setActivityType(value);
                handleFilterChange();
              }}
              style={{ width: '100%' }}
              placeholder="活动类型"
            >
              <Option value="all">全部活动</Option>
              <Option value="text">文本相关</Option>
              <Option value="voice">语音相关</Option>
              <Option value="image">图像相关</Option>
              <Option value="profile">资料修改</Option>
              <Option value="login">登录记录</Option>
            </Select>
          </Col>
          <Col span={10}>
            <RangePicker
              value={dateRange}
              onChange={(dates) => {
                setDateRange(dates);
                handleFilterChange();
              }}
              style={{ width: '100%' }}
              placeholder={['开始日期', '结束日期']}
            />
          </Col>
          <Col span={4}>
            <Button
              onClick={() => {
                setActivityType('all');
                setDateRange(null);
                handleFilterChange();
              }}
            >
              重置
            </Button>
          </Col>
        </Row>
      </Card>

      {/* 活动列表 */}
      <Timeline
        mode="left"
        items={activities.map((activity, index) => ({
          dot: getActivityIcon(activity.activity_type),
          children: (
            <Card size="small" key={activity.activity_id || index}>
              <Row align="middle">
                <Col flex="auto">
                  <Space direction="vertical" size={4}>
                    <div>
                      <Text strong>{getActivityDescription(activity)}</Text>
                      {activity.target_name && (
                        <Text type="secondary"> - {activity.target_name}</Text>
                      )}
                    </div>
                    <Space size="small">
                      <Tag
                        color={getActivityColor(activity.activity_type.split('_')[1] || 'default')}
                      >
                        {activity.activity_type}
                      </Tag>
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        <ClockCircleOutlined /> {activity.created_at}
                      </Text>
                      {activity.ip_address && (
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          <GlobalOutlined /> {activity.ip_address}
                        </Text>
                      )}
                    </Space>
                  </Space>
                </Col>
              </Row>
            </Card>
          )
        }))}
      />

      {activities.length === 0 && !loading && (
        <Empty
          description="暂无活动记录"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      )}
    </div>
  );

  const renderLoginHistory = () => (
    <div>
      {/* 筛选器 */}
      <Card size="small" style={{ marginBottom: '16px' }}>
        <Row gutter={16} align="middle">
          <Col span={10}>
            <RangePicker
              value={dateRange}
              onChange={(dates) => {
                setDateRange(dates);
                handleFilterChange();
              }}
              style={{ width: '100%' }}
              placeholder={['开始日期', '结束日期']}
            />
          </Col>
          <Col span={4}>
            <Button
              onClick={() => {
                setDateRange(null);
                handleFilterChange();
              }}
            >
              重置
            </Button>
          </Col>
        </Row>
      </Card>

      {/* 登录历史列表 */}
      <List
        dataSource={loginHistory}
        renderItem={(item) => (
          <List.Item>
            <List.Item.Meta
              avatar={
                <Avatar icon={<GlobalOutlined />} style={{ backgroundColor: '#1976d2' }} />
              }
              title={
                <Space>
                  <Text strong>{item.device_name || '未知设备'}</Text>
                  {item.is_current && <Tag color="blue">当前设备</Tag>}
                  {item.login_status === 'success' ? (
                    <Tag color="success">登录成功</Tag>
                  ) : (
                    <Tag color="error">登录失败</Tag>
                  )}
                </Space>
              }
              description={
                <Space direction="vertical" size={4}>
                  <Text type="secondary">
                    {item.browser} · {item.os}
                  </Text>
                  <Text type="secondary">
                    IP: {item.ip_address} · {item.location || '未知位置'}
                  </Text>
                  <Text type="secondary">
                    <ClockCircleOutlined /> {item.login_time}
                  </Text>
                </Space>
              }
            />
          </List.Item>
        )}
      />

      {loginHistory.length === 0 && !loading && (
        <Empty
          description="暂无登录记录"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      )}
    </div>
  );

  return (
    <div className={className}>
      {/* 概览统计 */}
      <Row gutter={24} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总活动次数"
              value={pagination.total}
              prefix={<HistoryOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="本月活动"
              value={activities.filter(a => 
                dayjs(a.created_at).isAfter(dayjs().startOf('month'))
              ).length}
              prefix={<CalendarOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="今日活动"
              value={activities.filter(a => 
                dayjs(a.created_at).isToday()
              ).length}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="最近登录"
              value={loginHistory[0]?.login_time || '-'}
              formatter={(value) => 
                value === '-' ? value : dayjs(value as string).fromNow()
              }
              prefix={<LoginOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 选项卡 */}
      <Card>
        <div style={{ marginBottom: '24px' }}>
          <Space size="large">
            <Button
              type={currentTab === 'activities' ? 'primary' : 'default'}
              icon={<HistoryOutlined />}
              onClick={() => handleTabChange('activities')}
            >
              活动记录
            </Button>
            <Button
              type={currentTab === 'logins' ? 'primary' : 'default'}
              icon={<LoginOutlined />}
              onClick={() => handleTabChange('logins')}
            >
              登录历史
            </Button>
          </Space>
        </div>

        <Spin spinning={loading}>
          {currentTab === 'activities' ? renderActivities() : renderLoginHistory()}
        </Spin>
      </Card>
    </div>
  );
};

export default UserProfileActivity;