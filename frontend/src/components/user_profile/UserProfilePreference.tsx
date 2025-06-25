/**
 * User Profile Preference Component
 * 用户偏好设置组件 - [components][user_profile][user_profile_preference]
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  Form,
  Switch,
  Select,
  Slider,
  Button,
  Space,
  Typography,
  Divider,
  Row,
  Col,
  message,
  Radio,
  InputNumber,
  Checkbox,
  TimePicker,
  Alert
} from 'antd';
import {
  SettingOutlined,
  BellOutlined,
  GlobalOutlined,
  EyeOutlined,
  SoundOutlined,
  MoonOutlined,
  BulbOutlined,
  NotificationOutlined,
  MailOutlined,
  MobileOutlined,
  SaveOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import dayjs from 'dayjs';

import { useUserProfileStore } from '../../stores/user_profile/user_profile_store';
import { userProfileApiService } from '../../services/api/user_profile_api';
import type { UserPreferences } from '../../services/api/user_profile_api';

const { Title, Text } = Typography;
const { Option } = Select;

interface UserProfilePreferenceProps {
  className?: string;
}

export const UserProfilePreference: React.FC<UserProfilePreferenceProps> = ({
  className
}) => {
  const [form] = Form.useForm();
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  const { profile } = useUserProfileStore();

  // 加载用户偏好设置
  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    setLoading(true);
    try {
      const response = await userProfileApiService.user_profile_api_get_preferences();
      if (response.success && response.data) {
        setPreferences(response.data);
        // 设置表单初始值
        form.setFieldsValue({
          // 系统设置
          theme: response.data.theme || 'auto',
          language: response.data.language || 'zh-CN',
          timezone: response.data.timezone || 'Asia/Shanghai',
          date_format: response.data.date_format || 'YYYY-MM-DD',
          time_format: response.data.time_format || '24h',
          
          // 通知设置
          email_notifications: response.data.email_notifications || false,
          sms_notifications: response.data.sms_notifications || false,
          push_notifications: response.data.push_notifications || true,
          notification_sound: response.data.notification_sound || true,
          quiet_hours_enabled: response.data.quiet_hours_enabled || false,
          quiet_hours_start: response.data.quiet_hours_start ? dayjs(response.data.quiet_hours_start, 'HH:mm') : dayjs('22:00', 'HH:mm'),
          quiet_hours_end: response.data.quiet_hours_end ? dayjs(response.data.quiet_hours_end, 'HH:mm') : dayjs('08:00', 'HH:mm'),
          
          // 界面设置
          sidebar_collapsed: response.data.sidebar_collapsed || false,
          page_size: response.data.page_size || 20,
          auto_save: response.data.auto_save || true,
          auto_save_interval: response.data.auto_save_interval || 60,
          
          // AI设置
          ai_suggestions: response.data.ai_suggestions !== false,
          auto_generate_titles: response.data.auto_generate_titles !== false,
          content_language: response.data.content_language || 'zh-CN',
          voice_speed: response.data.voice_speed || 1.0,
          voice_pitch: response.data.voice_pitch || 1.0,
          
          // 隐私设置
          profile_visibility: response.data.profile_visibility || 'private',
          activity_visibility: response.data.activity_visibility || 'private',
          usage_analytics: response.data.usage_analytics !== false
        });
      }
    } catch (error) {
      console.error('Failed to load preferences:', error);
      message.error('加载偏好设置失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      setSaving(true);
      
      const preferencesData: UserPreferences = {
        // 系统设置
        theme: values.theme,
        language: values.language,
        timezone: values.timezone,
        date_format: values.date_format,
        time_format: values.time_format,
        
        // 通知设置
        email_notifications: values.email_notifications,
        sms_notifications: values.sms_notifications,
        push_notifications: values.push_notifications,
        notification_sound: values.notification_sound,
        quiet_hours_enabled: values.quiet_hours_enabled,
        quiet_hours_start: values.quiet_hours_start?.format('HH:mm'),
        quiet_hours_end: values.quiet_hours_end?.format('HH:mm'),
        
        // 界面设置
        sidebar_collapsed: values.sidebar_collapsed,
        page_size: values.page_size,
        auto_save: values.auto_save,
        auto_save_interval: values.auto_save_interval,
        
        // AI设置
        ai_suggestions: values.ai_suggestions,
        auto_generate_titles: values.auto_generate_titles,
        content_language: values.content_language,
        voice_speed: values.voice_speed,
        voice_pitch: values.voice_pitch,
        
        // 隐私设置
        profile_visibility: values.profile_visibility,
        activity_visibility: values.activity_visibility,
        usage_analytics: values.usage_analytics
      };

      const response = await userProfileApiService.user_profile_api_update_preferences(preferencesData);
      
      if (response.success) {
        setPreferences(preferencesData);
        message.success('偏好设置已保存');
      } else {
        message.error(response.message || '保存失败');
      }
    } catch (error) {
      console.error('Failed to save preferences:', error);
      message.error('保存失败，请重试');
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    if (preferences) {
      form.setFieldsValue(preferences);
      message.info('已重置为上次保存的设置');
    }
  };

  return (
    <div className={className}>
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSave}
      >
        {/* 系统设置 */}
        <Card title="系统设置" style={{ marginBottom: '24px' }}>
          <Row gutter={24}>
            <Col span={8}>
              <Form.Item
                label="主题外观"
                name="theme"
                tooltip="选择您喜欢的界面主题"
              >
                <Select>
                  <Option value="light">
                    <BulbOutlined /> 浅色主题
                  </Option>
                  <Option value="dark">
                    <MoonOutlined /> 深色主题
                  </Option>
                  <Option value="auto">
                    <EyeOutlined /> 跟随系统
                  </Option>
                </Select>
              </Form.Item>
            </Col>
            
            <Col span={8}>
              <Form.Item
                label="界面语言"
                name="language"
              >
                <Select>
                  <Option value="zh-CN">简体中文</Option>
                  <Option value="zh-TW">繁體中文</Option>
                  <Option value="en-US">English</Option>
                  <Option value="ja-JP">日本語</Option>
                </Select>
              </Form.Item>
            </Col>
            
            <Col span={8}>
              <Form.Item
                label="时区"
                name="timezone"
              >
                <Select>
                  <Option value="Asia/Shanghai">北京时间 (UTC+8)</Option>
                  <Option value="America/New_York">纽约时间 (UTC-5)</Option>
                  <Option value="Europe/London">伦敦时间 (UTC+0)</Option>
                  <Option value="Asia/Tokyo">东京时间 (UTC+9)</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={24}>
            <Col span={12}>
              <Form.Item
                label="日期格式"
                name="date_format"
              >
                <Select>
                  <Option value="YYYY-MM-DD">2024-01-01</Option>
                  <Option value="DD/MM/YYYY">01/01/2024</Option>
                  <Option value="MM/DD/YYYY">01/01/2024</Option>
                  <Option value="YYYY年MM月DD日">2024年01月01日</Option>
                </Select>
              </Form.Item>
            </Col>
            
            <Col span={12}>
              <Form.Item
                label="时间格式"
                name="time_format"
              >
                <Radio.Group>
                  <Radio value="24h">24小时制</Radio>
                  <Radio value="12h">12小时制</Radio>
                </Radio.Group>
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* 通知设置 */}
        <Card title="通知设置" style={{ marginBottom: '24px' }}>
          <Row gutter={24}>
            <Col span={12}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Form.Item
                  name="email_notifications"
                  valuePropName="checked"
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Space>
                      <MailOutlined />
                      <span>邮件通知</span>
                    </Space>
                    <Switch size="small" />
                  </div>
                </Form.Item>
                
                <Form.Item
                  name="sms_notifications"
                  valuePropName="checked"
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Space>
                      <MobileOutlined />
                      <span>短信通知</span>
                    </Space>
                    <Switch size="small" />
                  </div>
                </Form.Item>
                
                <Form.Item
                  name="push_notifications"
                  valuePropName="checked"
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Space>
                      <NotificationOutlined />
                      <span>推送通知</span>
                    </Space>
                    <Switch size="small" />
                  </div>
                </Form.Item>
                
                <Form.Item
                  name="notification_sound"
                  valuePropName="checked"
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Space>
                      <SoundOutlined />
                      <span>通知声音</span>
                    </Space>
                    <Switch size="small" />
                  </div>
                </Form.Item>
              </Space>
            </Col>
            
            <Col span={12}>
              <Form.Item
                name="quiet_hours_enabled"
                valuePropName="checked"
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                  <Text strong>免打扰时间</Text>
                  <Switch size="small" />
                </div>
              </Form.Item>
              
              <Form.Item
                noStyle
                shouldUpdate={(prevValues, currentValues) => 
                  prevValues.quiet_hours_enabled !== currentValues.quiet_hours_enabled
                }
              >
                {({ getFieldValue }) => 
                  getFieldValue('quiet_hours_enabled') && (
                    <Row gutter={16}>
                      <Col span={12}>
                        <Form.Item
                          label="开始时间"
                          name="quiet_hours_start"
                        >
                          <TimePicker
                            format="HH:mm"
                            style={{ width: '100%' }}
                          />
                        </Form.Item>
                      </Col>
                      <Col span={12}>
                        <Form.Item
                          label="结束时间"
                          name="quiet_hours_end"
                        >
                          <TimePicker
                            format="HH:mm"
                            style={{ width: '100%' }}
                          />
                        </Form.Item>
                      </Col>
                    </Row>
                  )
                }
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* 界面设置 */}
        <Card title="界面设置" style={{ marginBottom: '24px' }}>
          <Row gutter={24}>
            <Col span={12}>
              <Form.Item
                name="sidebar_collapsed"
                valuePropName="checked"
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Text>默认折叠侧边栏</Text>
                  <Switch size="small" />
                </div>
              </Form.Item>
              
              <Form.Item
                label="每页显示条数"
                name="page_size"
              >
                <Select>
                  <Option value={10}>10条</Option>
                  <Option value={20}>20条</Option>
                  <Option value={50}>50条</Option>
                  <Option value={100}>100条</Option>
                </Select>
              </Form.Item>
            </Col>
            
            <Col span={12}>
              <Form.Item
                name="auto_save"
                valuePropName="checked"
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Text>自动保存</Text>
                  <Switch size="small" />
                </div>
              </Form.Item>
              
              <Form.Item
                noStyle
                shouldUpdate={(prevValues, currentValues) => 
                  prevValues.auto_save !== currentValues.auto_save
                }
              >
                {({ getFieldValue }) => 
                  getFieldValue('auto_save') && (
                    <Form.Item
                      label="自动保存间隔（秒）"
                      name="auto_save_interval"
                    >
                      <InputNumber
                        min={30}
                        max={600}
                        step={30}
                        style={{ width: '100%' }}
                      />
                    </Form.Item>
                  )
                }
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* AI设置 */}
        <Card title="AI助手设置" style={{ marginBottom: '24px' }}>
          <Row gutter={24}>
            <Col span={12}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Form.Item
                  name="ai_suggestions"
                  valuePropName="checked"
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Text>AI智能建议</Text>
                    <Switch size="small" />
                  </div>
                </Form.Item>
                
                <Form.Item
                  name="auto_generate_titles"
                  valuePropName="checked"
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Text>自动生成标题</Text>
                    <Switch size="small" />
                  </div>
                </Form.Item>
                
                <Form.Item
                  label="内容生成语言"
                  name="content_language"
                >
                  <Select>
                    <Option value="zh-CN">简体中文</Option>
                    <Option value="zh-TW">繁體中文</Option>
                    <Option value="en-US">English</Option>
                  </Select>
                </Form.Item>
              </Space>
            </Col>
            
            <Col span={12}>
              <Form.Item
                label="语音速度"
                name="voice_speed"
              >
                <Slider
                  min={0.5}
                  max={2.0}
                  step={0.1}
                  marks={{
                    0.5: '0.5x',
                    1.0: '1.0x',
                    1.5: '1.5x',
                    2.0: '2.0x'
                  }}
                />
              </Form.Item>
              
              <Form.Item
                label="语音音调"
                name="voice_pitch"
              >
                <Slider
                  min={0.5}
                  max={2.0}
                  step={0.1}
                  marks={{
                    0.5: '低',
                    1.0: '标准',
                    2.0: '高'
                  }}
                />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* 隐私设置 */}
        <Card title="隐私设置" style={{ marginBottom: '24px' }}>
          <Row gutter={24}>
            <Col span={12}>
              <Form.Item
                label="个人资料可见性"
                name="profile_visibility"
              >
                <Radio.Group>
                  <Radio value="public">公开</Radio>
                  <Radio value="friends">仅好友</Radio>
                  <Radio value="private">私密</Radio>
                </Radio.Group>
              </Form.Item>
              
              <Form.Item
                label="活动记录可见性"
                name="activity_visibility"
              >
                <Radio.Group>
                  <Radio value="public">公开</Radio>
                  <Radio value="friends">仅好友</Radio>
                  <Radio value="private">私密</Radio>
                </Radio.Group>
              </Form.Item>
            </Col>
            
            <Col span={12}>
              <Form.Item
                name="usage_analytics"
                valuePropName="checked"
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <Text>使用情况分析</Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      帮助我们改进产品体验
                    </Text>
                  </div>
                  <Switch size="small" />
                </div>
              </Form.Item>
            </Col>
          </Row>
          
          <Alert
            message="隐私说明"
            description="我们严格保护您的隐私信息，所有数据仅用于改进产品体验，不会与第三方分享。"
            type="info"
            showIcon
            style={{ marginTop: '16px' }}
          />
        </Card>

        {/* 操作按钮 */}
        <Card>
          <div style={{ textAlign: 'center' }}>
            <Space size="large">
              <Button
                type="primary"
                size="large"
                icon={<SaveOutlined />}
                onClick={handleSave}
                loading={saving}
              >
                保存设置
              </Button>
              <Button
                size="large"
                icon={<ReloadOutlined />}
                onClick={handleReset}
              >
                重置
              </Button>
            </Space>
          </div>
        </Card>
      </Form>
    </div>
  );
};

export default UserProfilePreference;