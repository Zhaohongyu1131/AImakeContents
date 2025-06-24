/**
 * Voice Clone Unified Component
 * 统一音色克隆组件 - [components][voice_workbench][voice_clone_unified]
 */

import React, { useState, useCallback, useEffect } from 'react';
import {
  Card,
  Form,
  Input,
  Upload,
  Button,
  Select,
  Space,
  Typography,
  Collapse,
  Row,
  Col,
  Slider,
  Switch,
  Alert,
  Progress,
  Tag,
  Tooltip,
  Divider
} from 'antd';
import {
  InboxOutlined,
  SoundOutlined,
  SettingOutlined,
  InfoCircleOutlined,
  CloudUploadOutlined,
  ExperimentOutlined
} from '@ant-design/icons';

import type { UploadFile } from 'antd/es/upload/interface';
import type { VoicePlatformInfo } from '../../services/voice-workbench/types';

const { TextArea } = Input;
const { Text, Title, Paragraph } = Typography;
const { Panel } = Collapse;
const { Option } = Select;

interface VoiceCloneUnifiedProps {
  selectedPlatform: string | null;
  platforms: VoicePlatformInfo[];
  onSubmit: (formData: any) => Promise<void>;
  loading: boolean;
  disabled?: boolean;
}

/**
 * 统一音色克隆组件
 * [components][voice_workbench][VoiceCloneUnified]
 */
const VoiceCloneUnified: React.FC<VoiceCloneUnifiedProps> = ({
  selectedPlatform,
  platforms,
  onSubmit,
  loading,
  disabled = false
}) => {
  const [form] = Form.useForm();
  const [audioFile, setAudioFile] = useState<UploadFile | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [estimatedCost, setEstimatedCost] = useState(0);

  // 获取当前平台信息
  const currentPlatform = platforms.find(p => p.platform_type === selectedPlatform);

  // 语言选项（基于平台支持）
  const languageOptions = [
    { value: 'zh-CN', label: '中文（简体）' },
    { value: 'zh-TW', label: '中文（繁体）' },
    { value: 'en-US', label: '英语（美国）' },
    { value: 'en-GB', label: '英语（英国）' },
    { value: 'ja-JP', label: '日语' },
    { value: 'ko-KR', label: '韩语' },
    { value: 'es-ES', label: '西班牙语' },
    { value: 'fr-FR', label: '法语' },
    { value: 'de-DE', label: '德语' },
    { value: 'it-IT', label: '意大利语' }
  ];

  // 模型类型选项（基于平台）
  const getModelTypeOptions = () => {
    if (!currentPlatform) return [];

    switch (currentPlatform.platform_type) {
      case 'volcano':
        return [
          { value: '1', label: '标准模型（快速）', recommended: false },
          { value: '2', label: '增强模型（推荐）', recommended: true },
          { value: '3', label: '专业模型（高质量）', recommended: false },
          { value: '4', label: '实时模型（低延迟）', recommended: false }
        ];
      case 'azure':
        return [
          { value: 'basic', label: '基础模型', recommended: false },
          { value: 'neural', label: '神经网络模型（推荐）', recommended: true },
          { value: 'premium', label: '高级模型', recommended: false }
        ];
      case 'openai':
        return [
          { value: 'tts-1', label: 'TTS-1（标准）', recommended: true },
          { value: 'tts-1-hd', label: 'TTS-1-HD（高清）', recommended: false }
        ];
      default:
        return [
          { value: 'default', label: '默认模型', recommended: true }
        ];
    }
  };

  // 音频上传配置
  const uploadProps = {
    name: 'audio',
    multiple: false,
    accept: '.wav,.mp3,.m4a,.flac,.aac',
    beforeUpload: (file: File) => {
      // 验证文件大小 (50MB限制)
      const isLimitSize = file.size / 1024 / 1024 < 50;
      if (!isLimitSize) {
        message.error('音频文件大小不能超过50MB');
        return false;
      }

      // 验证文件时长（这里模拟，实际需要读取音频）
      setAudioFile(file as any);
      setUploadProgress(100);
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

    if (!currentPlatform) {
      message.error('请选择语音平台');
      return;
    }

    const formData = {
      timbre_name: values.timbre_name,
      timbre_description: values.timbre_description,
      language: values.language,
      model_type: values.model_type,
      reference_text: values.reference_text,
      preferred_platform: selectedPlatform,
      audio_file: audioFile.originFileObj,
      advanced_params: showAdvanced ? {
        noise_reduction: values.noise_reduction,
        quality_enhancement: values.quality_enhancement,
        voice_enhancement: values.voice_enhancement,
        training_iterations: values.training_iterations,
        learning_rate: values.learning_rate,
        batch_size: values.batch_size,
        experimental_features: values.experimental_features
      } : null
    };

    try {
      await onSubmit(formData);
      form.resetFields();
      setAudioFile(null);
      setUploadProgress(0);
    } catch (error) {
      // 错误处理由父组件负责
    }
  }, [audioFile, currentPlatform, selectedPlatform, onSubmit, form, showAdvanced]);

  // 计算预估费用
  useEffect(() => {
    if (currentPlatform && audioFile) {
      // 模拟计算（实际需要根据音频时长）
      const estimatedDuration = 2; // 假设2分钟
      const cost = currentPlatform.cost_per_minute * estimatedDuration;
      setEstimatedCost(cost);
    } else {
      setEstimatedCost(0);
    }
  }, [currentPlatform, audioFile]);

  // 渲染平台特定说明
  const renderPlatformInfo = () => {
    if (!currentPlatform) return null;

    const platformTips = {
      volcano: {
        title: '火山引擎（豆包）音色克隆',
        description: '支持高质量音色克隆，建议使用清晰、无背景噪音的音频文件，时长2-10分钟最佳。',
        features: ['高质量音色还原', '支持多种语言', '快速训练', 'SSML支持'],
        tips: [
          '音频质量越高，克隆效果越好',
          '建议录制安静环境下的清晰语音',
          '参考文本有助于提升训练效果'
        ]
      },
      azure: {
        title: 'Microsoft Azure 音色克隆',
        description: 'Azure认知服务提供专业级音色克隆，支持神经网络模型训练。',
        features: ['神经网络模型', '多语言支持', '专业级质量', '云端训练'],
        tips: [
          '建议使用16kHz或以上采样率',
          '音频时长建议3-15分钟',
          '神经网络模型效果最佳'
        ]
      },
      openai: {
        title: 'OpenAI 语音合成',
        description: 'OpenAI暂不支持自定义音色克隆，但提供高质量的预设音色。',
        features: ['高质量合成', '快速响应', '稳定服务'],
        tips: [
          'OpenAI不支持音色克隆功能',
          '请使用文本转语音功能',
          '可选择多种预设音色'
        ]
      }
    };

    const info = platformTips[currentPlatform.platform_type as keyof typeof platformTips];
    if (!info) return null;

    return (
      <Alert
        message={info.title}
        description={
          <div>
            <Paragraph>{info.description}</Paragraph>
            <Row gutter={[16, 8]}>
              <Col span={12}>
                <Text strong>平台特性：</Text>
                <ul style={{ margin: '8px 0', paddingLeft: 20 }}>
                  {info.features.map((feature, index) => (
                    <li key={index}>{feature}</li>
                  ))}
                </ul>
              </Col>
              <Col span={12}>
                <Text strong>使用建议：</Text>
                <ul style={{ margin: '8px 0', paddingLeft: 20 }}>
                  {info.tips.map((tip, index) => (
                    <li key={index}>{tip}</li>
                  ))}
                </ul>
              </Col>
            </Row>
          </div>
        }
        type="info"
        showIcon
        style={{ marginBottom: 24 }}
      />
    );
  };

  // 检查平台是否支持音色克隆
  const platformSupportsCloning = currentPlatform?.supported_features.includes('voice_clone');

  if (!platformSupportsCloning) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '60px 0' }}>
          <ExperimentOutlined style={{ fontSize: 64, color: '#bfbfbf', marginBottom: 16 }} />
          <Title level={3} type="secondary">
            当前平台不支持音色克隆
          </Title>
          <Paragraph type="secondary">
            {currentPlatform?.platform_name} 平台暂不支持自定义音色克隆功能。
            <br />
            建议切换到火山引擎（豆包）或 Microsoft Azure 平台。
          </Paragraph>
          <Button type="primary" icon={<SoundOutlined />} disabled>
            音色克隆功能不可用
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <div>
      {renderPlatformInfo()}

      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        disabled={disabled}
        initialValues={{
          language: 'zh-CN',
          model_type: getModelTypeOptions().find(opt => opt.recommended)?.value || getModelTypeOptions()[0]?.value,
          noise_reduction: true,
          quality_enhancement: true,
          voice_enhancement: false,
          training_iterations: 100,
          learning_rate: 0.001,
          batch_size: 32,
          experimental_features: false
        }}
      >
        {/* 基础设置 */}
        <Card title="基础设置" style={{ marginBottom: 16 }}>
          <Row gutter={24}>
            <Col span={12}>
              <Form.Item
                name="timbre_name"
                label="音色名称"
                rules={[
                  { required: true, message: '请输入音色名称' },
                  { min: 2, max: 50, message: '音色名称长度为2-50个字符' }
                ]}
              >
                <Input placeholder="为您的音色起个名字" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="language"
                label="主要语言"
                rules={[{ required: true, message: '请选择主要语言' }]}
              >
                <Select placeholder="选择音频的主要语言">
                  {languageOptions.map(option => (
                    <Option key={option.value} value={option.value}>
                      {option.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="timbre_description"
            label="音色描述"
          >
            <TextArea
              placeholder="描述这个音色的特点，例如：温暖、专业、活泼等（可选）"
              rows={3}
              maxLength={200}
              showCount
            />
          </Form.Item>

          <Row gutter={24}>
            <Col span={12}>
              <Form.Item
                name="model_type"
                label={
                  <Space>
                    <span>训练模型</span>
                    <Tooltip title="不同模型在质量、速度和资源消耗上有所差异">
                      <InfoCircleOutlined />
                    </Tooltip>
                  </Space>
                }
                rules={[{ required: true, message: '请选择训练模型' }]}
              >
                <Select placeholder="选择音色训练模型">
                  {getModelTypeOptions().map(option => (
                    <Option key={option.value} value={option.value}>
                      <Space>
                        <span>{option.label}</span>
                        {option.recommended && <Tag color="green">推荐</Tag>}
                      </Space>
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              {estimatedCost > 0 && (
                <div style={{ padding: '8px 0' }}>
                  <Text type="secondary">预估费用：</Text>
                  <Text strong style={{ color: '#1890ff' }}>
                    ¥{estimatedCost.toFixed(4)}
                  </Text>
                </div>
              )}
            </Col>
          </Row>
        </Card>

        {/* 音频上传 */}
        <Card title="音频文件" style={{ marginBottom: 16 }}>
          <Form.Item
            name="audio_file"
            rules={[
              { required: true, message: '请上传音频文件' }
            ]}
          >
            <Upload.Dragger {...uploadProps}>
              <p className="ant-upload-drag-icon">
                <InboxOutlined style={{ color: '#1890ff' }} />
              </p>
              <p className="ant-upload-text">
                点击或拖拽音频文件到此区域
              </p>
              <p className="ant-upload-hint">
                支持 WAV、MP3、M4A、FLAC、AAC 格式，建议文件大小不超过50MB
                <br />
                为获得最佳效果，请使用清晰、无背景噪音的录音文件
              </p>
            </Upload.Dragger>
          </Form.Item>

          {audioFile && uploadProgress > 0 && (
            <Card size="small" style={{ backgroundColor: '#f6ffed' }}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Text strong>{audioFile.name}</Text>
                  <Text type="secondary">
                    {(audioFile.size! / 1024 / 1024).toFixed(2)} MB
                  </Text>
                </div>
                <Progress 
                  percent={uploadProgress} 
                  size="small" 
                  status={uploadProgress === 100 ? 'success' : 'active'}
                />
              </Space>
            </Card>
          )}

          <Form.Item
            name="reference_text"
            label={
              <Space>
                <span>参考文本</span>
                <Tooltip title="提供音频对应的文本内容有助于提升音色克隆质量">
                  <InfoCircleOutlined />
                </Tooltip>
              </Space>
            }
          >
            <TextArea
              placeholder="输入音频文件对应的文本内容（可选，但建议填写）"
              rows={4}
              maxLength={1000}
              showCount
            />
          </Form.Item>
        </Card>

        {/* 高级设置 */}
        <Collapse
          ghost
          onChange={(activeKey) => setShowAdvanced(activeKey.length > 0)}
        >
          <Panel
            header={
              <Space>
                <SettingOutlined />
                <span>高级设置</span>
                <Tag color="orange">可选</Tag>
              </Space>
            }
            key="advanced"
          >
            <Card>
              <Title level={5}>音频处理</Title>
              <Row gutter={24}>
                <Col span={8}>
                  <Form.Item
                    name="noise_reduction"
                    label="噪音抑制"
                    valuePropName="checked"
                  >
                    <Switch />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item
                    name="quality_enhancement"
                    label="质量增强"
                    valuePropName="checked"
                  >
                    <Switch />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item
                    name="voice_enhancement"
                    label="语音增强"
                    valuePropName="checked"
                  >
                    <Switch />
                  </Form.Item>
                </Col>
              </Row>

              <Divider />

              <Title level={5}>训练参数</Title>
              <Alert
                message="高级训练参数"
                description="修改这些参数可能影响训练时间和效果，建议保持默认值"
                type="warning"
                showIcon
                style={{ marginBottom: 16 }}
              />

              <Row gutter={24}>
                <Col span={8}>
                  <Form.Item
                    name="training_iterations"
                    label="训练迭代次数"
                  >
                    <Slider
                      min={50}
                      max={500}
                      step={10}
                      marks={{
                        50: '50',
                        100: '100(推荐)',
                        200: '200',
                        500: '500'
                      }}
                      tooltip={{ formatter: (value) => `${value}次` }}
                    />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item
                    name="learning_rate"
                    label="学习率"
                  >
                    <Slider
                      min={0.0001}
                      max={0.01}
                      step={0.0001}
                      marks={{
                        0.0001: '0.0001',
                        0.001: '0.001(推荐)',
                        0.005: '0.005',
                        0.01: '0.01'
                      }}
                      tooltip={{ formatter: (value) => value?.toFixed(4) }}
                    />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item
                    name="batch_size"
                    label="批次大小"
                  >
                    <Slider
                      min={8}
                      max={128}
                      step={8}
                      marks={{
                        8: '8',
                        32: '32(推荐)',
                        64: '64',
                        128: '128'
                      }}
                      tooltip={{ formatter: (value) => `${value}` }}
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Divider />

              <Form.Item
                name="experimental_features"
                label="实验性功能"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Card>
          </Panel>
        </Collapse>

        {/* 提交按钮 */}
        <div style={{ textAlign: 'center', marginTop: 24 }}>
          <Space size="middle">
            <Button size="large" onClick={() => form.resetFields()}>
              重置
            </Button>
            <Button 
              type="primary" 
              size="large"
              htmlType="submit"
              loading={loading}
              icon={<CloudUploadOutlined />}
            >
              {loading ? '正在创建音色...' : '开始音色克隆'}
            </Button>
          </Space>
        </div>
      </Form>
    </div>
  );
};

export default VoiceCloneUnified;