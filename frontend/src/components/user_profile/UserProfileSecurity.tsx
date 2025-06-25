/**
 * User Profile Security Component
 * 用户安全设置组件 - [components][user_profile][user_profile_security]
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  Form,
  Input,
  Button,
  Space,
  Switch,
  Typography,
  Divider,
  Alert,
  List,
  Tag,
  Modal,
  message,
  Row,
  Col,
  Statistic
} from 'antd';
import {
  LockOutlined,
  SafetyOutlined,
  MobileOutlined,
  MailOutlined,
  GoogleOutlined,
  GithubOutlined,
  WechatOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  DeleteOutlined,
  HistoryOutlined,
  GlobalOutlined
} from '@ant-design/icons';

import { useUserProfileStore } from '../../stores/user_profile/user_profile_store';
import { userProfileApiService } from '../../services/api/user_profile_api';
import type { SecuritySettings, LoginHistory } from '../../services/api/user_profile_api';

const { Title, Text, Paragraph } = Typography;
const { Password } = Input;

interface UserProfileSecurityProps {
  className?: string;
}

export const UserProfileSecurity: React.FC<UserProfileSecurityProps> = ({
  className
}) => {
  const [passwordForm] = Form.useForm();
  const [securitySettings, setSecuritySettings] = useState<SecuritySettings | null>(null);
  const [loginHistory, setLoginHistory] = useState<LoginHistory[]>([]);
  const [changingPassword, setChangingPassword] = useState(false);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [loading2FA, setLoading2FA] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);

  const { profile } = useUserProfileStore();

  // 加载安全设置和登录历史
  useEffect(() => {
    loadSecuritySettings();
    loadLoginHistory();
  }, []);

  const loadSecuritySettings = async () => {
    try {
      const response = await userProfileApiService.user_profile_api_get_security_settings();
      if (response.success && response.data) {
        setSecuritySettings(response.data);
      }
    } catch (error) {
      console.error('Failed to load security settings:', error);
      message.error('加载安全设置失败');
    }
  };

  const loadLoginHistory = async () => {
    setLoadingHistory(true);
    try {
      const response = await userProfileApiService.user_profile_api_get_login_history({
        page: 1,
        page_size: 5
      });
      if (response.success && response.data) {
        setLoginHistory(response.data.items || []);
      }
    } catch (error) {
      console.error('Failed to load login history:', error);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handlePasswordChange = async (values: any) => {
    setChangingPassword(true);
    try {
      const response = await userProfileApiService.user_profile_api_change_password({
        current_password: values.current_password,
        new_password: values.new_password
      });
      
      if (response.success) {
        message.success('密码修改成功');
        setShowPasswordModal(false);
        passwordForm.resetFields();
      } else {
        message.error(response.message || '密码修改失败');
      }
    } catch (error) {
      console.error('Failed to change password:', error);
      message.error('密码修改失败，请重试');
    } finally {
      setChangingPassword(false);
    }
  };

  const handleToggle2FA = async (enabled: boolean) => {
    setLoading2FA(true);
    try {
      let response;
      if (enabled) {
        response = await userProfileApiService.user_profile_api_enable_two_factor();
        if (response.success && response.data) {
          // 显示二维码让用户扫描
          Modal.info({
            title: '启用两步验证',
            content: (
              <div>
                <Paragraph>请使用验证器应用扫描下方二维码：</Paragraph>
                <img src={response.data.qr_code} alt="2FA QR Code" style={{ width: '200px' }} />
                <Paragraph>或手动输入密钥：</Paragraph>
                <Text code copyable>{response.data.secret}</Text>
              </div>
            ),
            width: 400
          });
        }
      } else {
        response = await userProfileApiService.user_profile_api_disable_two_factor();
      }
      
      if (response.success) {
        message.success(enabled ? '两步验证已启用' : '两步验证已关闭');
        loadSecuritySettings(); // 重新加载设置
      }
    } catch (error) {
      console.error('Failed to toggle 2FA:', error);
      message.error('操作失败，请重试');
    } finally {
      setLoading2FA(false);
    }
  };

  const handleRemoveDevice = async (deviceId: string) => {
    Modal.confirm({
      title: '移除设备',
      content: '确定要移除这个登录设备吗？',
      onOk: async () => {
        try {
          const response = await userProfileApiService.user_profile_api_remove_login_device(deviceId);
          if (response.success) {
            message.success('设备已移除');
            loadLoginHistory();
          }
        } catch (error) {
          console.error('Failed to remove device:', error);
          message.error('移除失败，请重试');
        }
      }
    });
  };

  return (
    <div className={className}>
      {/* 账户安全状态 */}
      <Card style={{ marginBottom: '24px' }}>
        <Row gutter={24} align="middle">
          <Col flex="auto">
            <Space direction="vertical" size="small">
              <Title level={4} style={{ margin: 0 }}>
                <SafetyOutlined /> 账户安全等级
              </Title>
              <Text type="secondary">
                根据您的安全设置评估
              </Text>
            </Space>
          </Col>
          <Col flex="none">
            <Statistic
              value={securitySettings?.security_score || 0}
              suffix="/ 100"
              valueStyle={{
                color: (securitySettings?.security_score || 0) >= 80 ? '#52c41a' : '#faad14'
              }}
            />
          </Col>
        </Row>
        
        {securitySettings?.security_suggestions && securitySettings.security_suggestions.length > 0 && (
          <>
            <Divider />
            <Alert
              message="安全建议"
              description={
                <ul style={{ marginBottom: 0, paddingLeft: '20px' }}>
                  {securitySettings.security_suggestions.map((suggestion, index) => (
                    <li key={index}>{suggestion}</li>
                  ))}
                </ul>
              }
              type="info"
              showIcon
            />
          </>
        )}
      </Card>

      {/* 密码设置 */}
      <Card title="密码设置" style={{ marginBottom: '24px' }}>
        <Row align="middle">
          <Col flex="auto">
            <Space direction="vertical" size="small">
              <Text strong>登录密码</Text>
              <Text type="secondary">
                上次修改时间：{securitySettings?.last_password_change || '从未修改'}
              </Text>
            </Space>
          </Col>
          <Col flex="none">
            <Button
              type="primary"
              icon={<LockOutlined />}
              onClick={() => setShowPasswordModal(true)}
            >
              修改密码
            </Button>
          </Col>
        </Row>
      </Card>

      {/* 两步验证 */}
      <Card title="两步验证" style={{ marginBottom: '24px' }}>
        <Row align="middle">
          <Col flex="auto">
            <Space direction="vertical" size="small">
              <Text strong>两步验证 (2FA)</Text>
              <Text type="secondary">
                为您的账户添加额外的安全保护层
              </Text>
              {securitySettings?.two_factor_enabled && (
                <Tag icon={<CheckCircleOutlined />} color="success">
                  已启用
                </Tag>
              )}
            </Space>
          </Col>
          <Col flex="none">
            <Switch
              checked={securitySettings?.two_factor_enabled}
              onChange={handleToggle2FA}
              loading={loading2FA}
              checkedChildren="已启用"
              unCheckedChildren="已关闭"
            />
          </Col>
        </Row>
      </Card>

      {/* 绑定账号 */}
      <Card title="第三方账号绑定" style={{ marginBottom: '24px' }}>
        <List
          dataSource={[
            {
              key: 'email',
              icon: <MailOutlined />,
              name: '邮箱',
              status: profile?.email ? 'bound' : 'unbound',
              value: profile?.email
            },
            {
              key: 'phone',
              icon: <MobileOutlined />,
              name: '手机号',
              status: profile?.phone ? 'bound' : 'unbound',
              value: profile?.phone
            },
            {
              key: 'wechat',
              icon: <WechatOutlined style={{ color: '#07c160' }} />,
              name: '微信',
              status: securitySettings?.bound_accounts?.wechat ? 'bound' : 'unbound',
              value: securitySettings?.bound_accounts?.wechat
            },
            {
              key: 'github',
              icon: <GithubOutlined />,
              name: 'GitHub',
              status: securitySettings?.bound_accounts?.github ? 'bound' : 'unbound',
              value: securitySettings?.bound_accounts?.github
            },
            {
              key: 'google',
              icon: <GoogleOutlined style={{ color: '#4285f4' }} />,
              name: 'Google',
              status: securitySettings?.bound_accounts?.google ? 'bound' : 'unbound',
              value: securitySettings?.bound_accounts?.google
            }
          ]}
          renderItem={(item) => (
            <List.Item
              actions={[
                item.status === 'bound' ? (
                  <Button size="small" danger>
                    解绑
                  </Button>
                ) : (
                  <Button size="small" type="primary">
                    绑定
                  </Button>
                )
              ]}
            >
              <List.Item.Meta
                avatar={item.icon}
                title={item.name}
                description={
                  item.status === 'bound' ? (
                    <Text type="secondary">{item.value}</Text>
                  ) : (
                    <Text type="secondary">未绑定</Text>
                  )
                }
              />
            </List.Item>
          )}
        />
      </Card>

      {/* 登录历史 */}
      <Card
        title="最近登录记录"
        extra={
          <Button
            type="link"
            icon={<HistoryOutlined />}
            size="small"
          >
            查看全部
          </Button>
        }
        loading={loadingHistory}
      >
        <List
          dataSource={loginHistory}
          renderItem={(item) => (
            <List.Item
              actions={[
                item.is_current ? (
                  <Tag color="blue">当前设备</Tag>
                ) : (
                  <Button
                    size="small"
                    danger
                    icon={<DeleteOutlined />}
                    onClick={() => handleRemoveDevice(item.device_id)}
                  >
                    移除
                  </Button>
                )
              ]}
            >
              <List.Item.Meta
                avatar={<GlobalOutlined />}
                title={
                  <Space>
                    <Text>{item.device_name || '未知设备'}</Text>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      {item.browser} · {item.os}
                    </Text>
                  </Space>
                }
                description={
                  <Space direction="vertical" size={0}>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      IP: {item.ip_address} · {item.location || '未知位置'}
                    </Text>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      <ClockCircleOutlined /> {item.login_time}
                    </Text>
                  </Space>
                }
              />
            </List.Item>
          )}
          locale={{ emptyText: '暂无登录记录' }}
        />
      </Card>

      {/* 修改密码弹窗 */}
      <Modal
        title="修改密码"
        open={showPasswordModal}
        onCancel={() => {
          setShowPasswordModal(false);
          passwordForm.resetFields();
        }}
        footer={null}
        width={400}
      >
        <Form
          form={passwordForm}
          layout="vertical"
          onFinish={handlePasswordChange}
        >
          <Form.Item
            name="current_password"
            label="当前密码"
            rules={[
              { required: true, message: '请输入当前密码' }
            ]}
          >
            <Password
              prefix={<LockOutlined />}
              placeholder="请输入当前密码"
            />
          </Form.Item>

          <Form.Item
            name="new_password"
            label="新密码"
            rules={[
              { required: true, message: '请输入新密码' },
              { min: 8, message: '密码至少8个字符' },
              {
                pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/,
                message: '密码必须包含大小写字母和数字'
              }
            ]}
          >
            <Password
              prefix={<LockOutlined />}
              placeholder="请输入新密码"
            />
          </Form.Item>

          <Form.Item
            name="confirm_password"
            label="确认新密码"
            dependencies={['new_password']}
            rules={[
              { required: true, message: '请确认新密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('new_password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('两次输入的密码不一致'));
                }
              })
            ]}
          >
            <Password
              prefix={<LockOutlined />}
              placeholder="请再次输入新密码"
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                loading={changingPassword}
              >
                确认修改
              </Button>
              <Button
                onClick={() => {
                  setShowPasswordModal(false);
                  passwordForm.resetFields();
                }}
              >
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default UserProfileSecurity;