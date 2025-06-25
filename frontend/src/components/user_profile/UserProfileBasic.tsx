/**
 * User Profile Basic Component
 * 用户基本信息组件 - [components][user_profile][user_profile_basic]
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  Form,
  Input,
  Button,
  Upload,
  Avatar,
  Space,
  Row,
  Col,
  DatePicker,
  Select,
  message,
  Spin,
  Typography,
  Divider
} from 'antd';
import {
  UserOutlined,
  UploadOutlined,
  SaveOutlined,
  EditOutlined,
  CameraOutlined,
  MailOutlined,
  PhoneOutlined,
  EnvironmentOutlined,
  CalendarOutlined,
  ManOutlined,
  WomanOutlined
} from '@ant-design/icons';
import type { UploadFile, RcFile } from 'antd/es/upload/interface';
import dayjs from 'dayjs';

import { useUserProfileStore } from '../../stores/user_profile/user_profile_store';
import { userProfileApiService } from '../../services/api/user_profile_api';
import type { UserProfile, UserProfileUpdateData } from '../../services/api/user_profile_api';

const { Text, Title } = Typography;
const { Option } = Select;
const { TextArea } = Input;

interface UserProfileBasicProps {
  className?: string;
  onUpdate?: (profile: UserProfile) => void;
}

export const UserProfileBasic: React.FC<UserProfileBasicProps> = ({
  className,
  onUpdate
}) => {
  const [form] = Form.useForm();
  const [isEditing, setIsEditing] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [avatarUrl, setAvatarUrl] = useState<string>('');
  const [fileList, setFileList] = useState<UploadFile[]>([]);

  const {
    profile,
    loading,
    user_profile_store_update_profile,
    user_profile_store_update_avatar
  } = useUserProfileStore();

  // 初始化表单数据
  useEffect(() => {
    if (profile) {
      form.setFieldsValue({
        username: profile.username,
        email: profile.email,
        nickname: profile.nickname,
        phone: profile.phone,
        bio: profile.bio,
        gender: profile.gender,
        birthday: profile.birthday ? dayjs(profile.birthday) : null,
        location: profile.location,
        website: profile.website,
        company: profile.company,
        position: profile.position
      });
      setAvatarUrl(profile.avatar || '');
    }
  }, [profile, form]);

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleCancel = () => {
    setIsEditing(false);
    // 重置表单到原始值
    if (profile) {
      form.setFieldsValue({
        username: profile.username,
        email: profile.email,
        nickname: profile.nickname,
        phone: profile.phone,
        bio: profile.bio,
        gender: profile.gender,
        birthday: profile.birthday ? dayjs(profile.birthday) : null,
        location: profile.location,
        website: profile.website,
        company: profile.company,
        position: profile.position
      });
    }
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      
      const updateData: UserProfileUpdateData = {
        nickname: values.nickname,
        phone: values.phone,
        bio: values.bio,
        gender: values.gender,
        birthday: values.birthday ? values.birthday.format('YYYY-MM-DD') : undefined,
        location: values.location,
        website: values.website,
        company: values.company,
        position: values.position
      };

      const updatedProfile = await user_profile_store_update_profile(updateData);
      
      if (updatedProfile) {
        message.success('个人信息更新成功');
        setIsEditing(false);
        onUpdate?.(updatedProfile);
      }
    } catch (error) {
      console.error('Failed to update profile:', error);
      message.error('更新失败，请重试');
    }
  };

  const handleAvatarUpload = async (file: RcFile) => {
    // 验证文件
    const isImage = file.type.startsWith('image/');
    if (!isImage) {
      message.error('只能上传图片文件！');
      return false;
    }

    const isLt5M = file.size / 1024 / 1024 < 5;
    if (!isLt5M) {
      message.error('图片大小不能超过5MB！');
      return false;
    }

    setUploading(true);
    
    try {
      const newAvatarUrl = await user_profile_store_update_avatar(file);
      if (newAvatarUrl) {
        setAvatarUrl(newAvatarUrl);
        message.success('头像上传成功');
      }
    } catch (error) {
      console.error('Avatar upload failed:', error);
      message.error('头像上传失败，请重试');
    } finally {
      setUploading(false);
    }

    return false; // 阻止默认上传行为
  };

  const uploadButton = (
    <div>
      {uploading ? <Spin /> : <CameraOutlined />}
      <div style={{ marginTop: 8 }}>更换头像</div>
    </div>
  );

  if (loading) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <Spin size="large" tip="加载中..." />
        </div>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <Row gutter={24}>
        {/* 左侧：头像区域 */}
        <Col xs={24} sm={8} md={6}>
          <div style={{ textAlign: 'center' }}>
            <Upload
              name="avatar"
              listType="picture-card"
              className="avatar-uploader"
              showUploadList={false}
              beforeUpload={handleAvatarUpload}
              disabled={!isEditing || uploading}
              style={{ marginBottom: '16px' }}
            >
              {avatarUrl ? (
                <Avatar
                  size={120}
                  src={avatarUrl}
                  icon={<UserOutlined />}
                  style={{ cursor: isEditing ? 'pointer' : 'default' }}
                />
              ) : (
                uploadButton
              )}
            </Upload>
            
            <Title level={4}>{profile?.nickname || profile?.username}</Title>
            <Text type="secondary">@{profile?.username}</Text>
            
            {!isEditing && (
              <div style={{ marginTop: '16px' }}>
                <Button
                  type="primary"
                  icon={<EditOutlined />}
                  onClick={handleEdit}
                  block
                >
                  编辑资料
                </Button>
              </div>
            )}
          </div>
        </Col>

        {/* 右侧：信息表单 */}
        <Col xs={24} sm={16} md={18}>
          <Form
            form={form}
            layout="vertical"
            disabled={!isEditing}
          >
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  label="用户名"
                  name="username"
                >
                  <Input
                    prefix={<UserOutlined />}
                    disabled
                    placeholder="用户名不可修改"
                  />
                </Form.Item>
              </Col>
              
              <Col span={12}>
                <Form.Item
                  label="邮箱"
                  name="email"
                >
                  <Input
                    prefix={<MailOutlined />}
                    disabled
                    placeholder="邮箱不可修改"
                  />
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  label="昵称"
                  name="nickname"
                  rules={[
                    { max: 50, message: '昵称最长50个字符' }
                  ]}
                >
                  <Input placeholder="请输入昵称" />
                </Form.Item>
              </Col>
              
              <Col span={12}>
                <Form.Item
                  label="手机号"
                  name="phone"
                  rules={[
                    { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号' }
                  ]}
                >
                  <Input
                    prefix={<PhoneOutlined />}
                    placeholder="请输入手机号"
                  />
                </Form.Item>
              </Col>
            </Row>

            <Form.Item
              label="个人简介"
              name="bio"
              rules={[
                { max: 200, message: '个人简介最长200个字符' }
              ]}
            >
              <TextArea
                rows={3}
                placeholder="介绍一下自己..."
                showCount
                maxLength={200}
              />
            </Form.Item>

            <Row gutter={16}>
              <Col span={8}>
                <Form.Item
                  label="性别"
                  name="gender"
                >
                  <Select placeholder="请选择性别">
                    <Option value="male">
                      <ManOutlined /> 男
                    </Option>
                    <Option value="female">
                      <WomanOutlined /> 女
                    </Option>
                    <Option value="other">其他</Option>
                  </Select>
                </Form.Item>
              </Col>
              
              <Col span={8}>
                <Form.Item
                  label="生日"
                  name="birthday"
                >
                  <DatePicker
                    style={{ width: '100%' }}
                    placeholder="选择生日"
                    disabledDate={(current) => current && current > dayjs().endOf('day')}
                  />
                </Form.Item>
              </Col>
              
              <Col span={8}>
                <Form.Item
                  label="所在地"
                  name="location"
                  rules={[
                    { max: 100, message: '地址最长100个字符' }
                  ]}
                >
                  <Input
                    prefix={<EnvironmentOutlined />}
                    placeholder="城市或地区"
                  />
                </Form.Item>
              </Col>
            </Row>

            <Divider />

            <Row gutter={16}>
              <Col span={8}>
                <Form.Item
                  label="公司"
                  name="company"
                  rules={[
                    { max: 100, message: '公司名称最长100个字符' }
                  ]}
                >
                  <Input placeholder="所在公司" />
                </Form.Item>
              </Col>
              
              <Col span={8}>
                <Form.Item
                  label="职位"
                  name="position"
                  rules={[
                    { max: 100, message: '职位名称最长100个字符' }
                  ]}
                >
                  <Input placeholder="职位头衔" />
                </Form.Item>
              </Col>
              
              <Col span={8}>
                <Form.Item
                  label="个人网站"
                  name="website"
                  rules={[
                    { type: 'url', message: '请输入有效的网址' },
                    { max: 200, message: '网址最长200个字符' }
                  ]}
                >
                  <Input placeholder="https://example.com" />
                </Form.Item>
              </Col>
            </Row>

            {isEditing && (
              <Form.Item>
                <Space>
                  <Button
                    type="primary"
                    icon={<SaveOutlined />}
                    onClick={handleSave}
                    loading={loading}
                  >
                    保存修改
                  </Button>
                  <Button onClick={handleCancel}>
                    取消
                  </Button>
                </Space>
              </Form.Item>
            )}
          </Form>
        </Col>
      </Row>
    </Card>
  );
};

export default UserProfileBasic;