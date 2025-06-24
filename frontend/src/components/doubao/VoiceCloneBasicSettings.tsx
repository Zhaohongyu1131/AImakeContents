/**
 * Voice Clone Basic Settings Component
 * 音色克隆基础设置组件 - [components][doubao][voice_clone_basic_settings]
 */

import React, { useState, useCallback } from 'react';
import {
  Card,
  Form,
  Input,
  Select,
  Upload,
  Button,
  Space,
  Typography,
  message,
  Progress,
  Divider
} from 'antd';
import {
  UploadOutlined,
  SoundOutlined,
  InfoCircleOutlined
} from '@ant-design/icons';
import type { UploadFile, UploadProps } from 'antd';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { TextArea } = Input;

interface VoiceCloneBasicSettingsProps {
  onSubmit?: (values: VoiceCloneFormData) => void;
  loading?: boolean;
  onAdvancedToggle?: () => void;
  showAdvanced?: boolean;
}

interface VoiceCloneFormData {
  timbre_name: string;
  timbre_description?: string;
  language: number;
  model_type: number;
  audio_file?: File;
}

const VoiceCloneBasicSettings: React.FC<VoiceCloneBasicSettingsProps> = ({
  onSubmit,
  loading = false,
  onAdvancedToggle,
  showAdvanced = false
}) => {
  const [form] = Form.useForm();
  const [audioFile, setAudioFile] = useState<UploadFile | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  // 语言选项配置
  const languageOptions = [
    { value: 0, label: '中文', description: '支持普通话和部分方言' },
    { value: 1, label: '英文', description: '美式和英式英语' },
    { value: 2, label: '日语', description: '标准日本语' },
    { value: 3, label: '西班牙语', description: '拉丁美洲西班牙语' },
    { value: 4, label: '印尼语', description: '标准印尼语' },
    { value: 5, label: '葡萄牙语', description: '巴西葡萄牙语' }
  ];

  // 模型类型配置
  const modelTypeOptions = [
    { 
      value: 1, 
      label: '2.0效果(ICL) - 推荐', 
      description: '最新模型，音质最佳，训练速度快',
      recommended: true
    },
    { 
      value: 0, 
      label: '1.0效果', 
      description: '经典模型，稳定可靠'
    },
    { 
      value: 2, 
      label: 'DiT标准版(音色)', 
      description: '专注音色还原'
    },
    { 
      value: 3, 
      label: 'DiT还原版(音色+风格)', 
      description: '音色和说话风格双重还原'
    }
  ];

  // 音频文件上传配置
  const uploadProps: UploadProps = {
    name: 'audio',
    multiple: false,
    maxCount: 1,
    accept: '.wav,.mp3,.m4a,.flac,.aac',
    beforeUpload: (file) => {
      const isAudio = file.type.startsWith('audio/');
      if (!isAudio) {
        message.error('只能上传音频文件！');
        return false;
      }
      
      const isLt50M = file.size / 1024 / 1024 < 50;
      if (!isLt50M) {
        message.error('音频文件大小不能超过 50MB！');
        return false;
      }

      setAudioFile(file as UploadFile);
      return false; // 阻止自动上传
    },
    onRemove: () => {
      setAudioFile(null);
      setUploadProgress(0);
    },
    fileList: audioFile ? [audioFile] : [],
    progress: {
      size: 'default',
      strokeColor: uploadProgress === 100 ? '#52c41a' : '#1890ff'
    }
  };

  // 表单提交处理
  const handleSubmit = useCallback(async (values: any) => {
    if (!audioFile) {
      message.error('请上传音频文件');
      return;
    }

    const formData: VoiceCloneFormData = {
      timbre_name: values.timbre_name,
      timbre_description: values.timbre_description,
      language: values.language,
      model_type: values.model_type,
      audio_file: audioFile?.originFileObj as File
    };

    if (onSubmit) {
      try {
        await onSubmit(formData);
        message.success('音色克隆任务已提交！');
        form.resetFields();
        setAudioFile(null);
      } catch (error) {
        message.error('提交失败，请重试');
      }
    }
  }, [audioFile, onSubmit, form]);


  // 音频文件信息显示
  const renderAudioInfo = () => {
    if (!audioFile) return null;

    return (
      <Card size="small" style={{ marginTop: 8, backgroundColor: '#f6ffed' }}>
        <Space direction="vertical" size="small" style={{ width: '100%' }}>
          <Text strong>
            <SoundOutlined /> 音频文件信息
          </Text>
          <div>
            <Text>文件名：{audioFile.name}</Text>
          </div>
          <div>
            <Text>文件大小：{((audioFile.size || 0) / 1024 / 1024).toFixed(2)} MB</Text>
          </div>
          {uploadProgress > 0 && (
            <Progress 
              percent={uploadProgress} 
              size="small" 
              status={uploadProgress === 100 ? 'success' : 'active'}
            />
          )}
        </Space>
      </Card>
    );
  };

  return (
    <Card 
      title={
        <Space>
          <SoundOutlined />
          <span>音色克隆 - 基础设置</span>
        </Space>
      }
      extra={
        <Button 
          type="link" 
          onClick={onAdvancedToggle}
          icon={<InfoCircleOutlined />}
        >
          {showAdvanced ? '隐藏高级设置' : '显示高级设置'}
        </Button>
      }
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={{
          language: 0,
          model_type: 1
        }}
      >
        {/* 基本信息 */}
        <Title level={5}>基本信息</Title>
        
        <Form.Item
          name="timbre_name"
          label="音色名称"
          rules={[
            { required: true, message: '请输入音色名称' },
            { min: 1, max: 50, message: '音色名称长度应在1-50个字符之间' }
          ]}
          extra="为您的音色起一个易识别的名称"
        >
          <Input placeholder="例如：我的专属音色" />
        </Form.Item>

        <Form.Item
          name="timbre_description"
          label="音色描述"
          rules={[
            { max: 200, message: '描述长度不能超过200个字符' }
          ]}
          extra="描述音色的特点和用途（可选）"
        >
          <TextArea 
            placeholder="例如：温暖亲切的女声，适合有声书朗读"
            rows={3}
            showCount
            maxLength={200}
          />
        </Form.Item>

        <Divider />

        {/* 训练设置 */}
        <Title level={5}>训练设置</Title>

        <Form.Item
          name="language"
          label="语言类型"
          rules={[{ required: true, message: '请选择语言类型' }]}
          extra="选择音色主要支持的语言"
        >
          <Select placeholder="请选择语言">
            {languageOptions.map(option => (
              <Option key={option.value} value={option.value}>
                <div>
                  <Text strong>{option.label}</Text>
                  <br />
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {option.description}
                  </Text>
                </div>
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item
          name="model_type"
          label="模型类型"
          rules={[{ required: true, message: '请选择模型类型' }]}
          extra="选择音色训练使用的模型版本"
        >
          <Select placeholder="请选择模型">
            {modelTypeOptions.map(option => (
              <Option key={option.value} value={option.value}>
                <div>
                  <Text strong style={{ color: option.recommended ? '#52c41a' : undefined }}>
                    {option.label}
                  </Text>
                  <br />
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {option.description}
                  </Text>
                </div>
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Divider />

        {/* 音频上传 */}
        <Title level={5}>音频上传</Title>
        
        <Form.Item
          label="音频文件"
          required
          extra={
            <Paragraph type="secondary" style={{ fontSize: '12px', margin: 0 }}>
              支持格式：WAV, MP3, M4A, FLAC, AAC<br />
              文件大小：最大50MB<br />
              推荐时长：10-60秒的清晰语音
            </Paragraph>
          }
        >
          <Upload.Dragger {...uploadProps}>
            <p className="ant-upload-drag-icon">
              <UploadOutlined />
            </p>
            <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
            <p className="ant-upload-hint">
              请上传清晰的语音文件，避免背景噪音
            </p>
          </Upload.Dragger>
        </Form.Item>

        {renderAudioInfo()}

        <Divider />

        {/* 提交按钮 */}
        <Form.Item style={{ marginBottom: 0 }}>
          <Space size="middle">
            <Button 
              type="primary" 
              htmlType="submit" 
              loading={loading}
              disabled={!audioFile}
              size="large"
            >
              开始训练音色
            </Button>
            <Button onClick={() => form.resetFields()}>
              重置表单
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default VoiceCloneBasicSettings;