/**
 * Voice Clone Advanced Settings Component
 * 音色克隆高级设置组件 - [components][doubao][voice_clone_advanced_settings]
 */

import React, { useState, useCallback } from 'react';
import {
  Card,
  Form,
  Input,
  Select,
  Switch,
  Slider,
  Collapse,
  Space,
  Typography,
  Tooltip,
  Alert,
  Tag,
  Divider
} from 'antd';
import {
  ExperimentOutlined,
  InfoCircleOutlined,
  WarningOutlined,
  SettingOutlined
} from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;
const { TextArea } = Input;

interface VoiceCloneAdvancedSettingsProps {
  visible?: boolean;
  onChange?: (values: AdvancedSettings) => void;
  initialValues?: Partial<AdvancedSettings>;
}

interface AdvancedSettings {
  reference_text?: string;
  audio_format: string;
  quality_enhancement: boolean;
  noise_reduction: boolean;
  voice_enhancement: boolean;
  training_iterations?: number;
  learning_rate?: number;
  batch_size?: number;
  experimental_features: boolean;
}

const VoiceCloneAdvancedSettings: React.FC<VoiceCloneAdvancedSettingsProps> = ({
  visible = true,
  onChange,
  initialValues = {}
}) => {
  const [form] = Form.useForm();
  const [experimentalEnabled, setExperimentalEnabled] = useState(false);

  // 默认值配置
  const defaultValues: AdvancedSettings = {
    audio_format: 'wav',
    quality_enhancement: true,
    noise_reduction: true,
    voice_enhancement: false,
    training_iterations: 100,
    learning_rate: 0.001,
    batch_size: 32,
    experimental_features: false,
    ...initialValues
  };

  // 音频格式选项
  const audioFormatOptions = [
    { 
      value: 'wav', 
      label: 'WAV', 
      description: '无损音频格式，最佳质量',
      recommended: true
    },
    { 
      value: 'mp3', 
      label: 'MP3', 
      description: '通用格式，文件较小'
    },
    { 
      value: 'ogg', 
      label: 'OGG', 
      description: '开源格式，压缩率高'
    },
    { 
      value: 'm4a', 
      label: 'M4A', 
      description: 'Apple格式，高质量'
    },
    { 
      value: 'aac', 
      label: 'AAC', 
      description: '先进音频编码'
    },
    { 
      value: 'pcm', 
      label: 'PCM', 
      description: '原始音频数据'
    }
  ];

  // 表单值变化处理
  const handleValuesChange = useCallback((_changedValues: any, allValues: any) => {
    if (onChange) {
      onChange(allValues);
    }
  }, [onChange]);

  // 实验性功能切换
  const handleExperimentalToggle = useCallback((checked: boolean) => {
    setExperimentalEnabled(checked);
    form.setFieldsValue({ experimental_features: checked });
  }, [form]);

  if (!visible) return null;

  return (
    <Card 
      title={
        <Space>
          <SettingOutlined />
          <span>高级设置</span>
          <Tag color="orange">实验性功能</Tag>
        </Space>
      }
      style={{ marginTop: 16 }}
    >
      <Alert
        message="高级设置说明"
        description="高级设置提供更精细的控制选项。修改这些参数可能影响训练效果，建议有经验的用户使用。"
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />

      <Form
        form={form}
        layout="vertical"
        initialValues={defaultValues}
        onValuesChange={handleValuesChange}
      >
        <Collapse defaultActiveKey={['quality']} ghost>
          {/* 质量优化 */}
          <Panel 
            header={
              <Space>
                <ExperimentOutlined />
                <span>质量优化</span>
              </Space>
            } 
            key="quality"
          >
            <Form.Item
              name="reference_text"
              label={
                <Space>
                  <span>参考文本</span>
                  <Tooltip title="提供参考文本可提高训练质量，音频内容应与此文本一致">
                    <InfoCircleOutlined style={{ color: '#1890ff' }} />
                  </Tooltip>
                </Space>
              }
              extra="音频内容应与此文本保持一致，有助于提升音色质量"
            >
              <TextArea
                placeholder="请输入与音频内容对应的文本..."
                rows={4}
                showCount
                maxLength={1000}
              />
            </Form.Item>

            <Form.Item
              name="quality_enhancement"
              label="质量增强"
              valuePropName="checked"
              extra="自动优化音频质量，减少失真"
            >
              <Switch />
            </Form.Item>

            <Form.Item
              name="noise_reduction"
              label="噪音抑制"
              valuePropName="checked"
              extra="自动降低背景噪音"
            >
              <Switch />
            </Form.Item>

            <Form.Item
              name="voice_enhancement"
              label="语音增强"
              valuePropName="checked"
              extra="增强语音清晰度（可能改变原始音色）"
            >
              <Switch />
            </Form.Item>
          </Panel>

          {/* 音频设置 */}
          <Panel 
            header={
              <Space>
                <SettingOutlined />
                <span>音频设置</span>
              </Space>
            } 
            key="audio"
          >
            <Form.Item
              name="audio_format"
              label="音频格式"
              extra="选择源音频文件格式，影响处理质量"
            >
              <Select>
                {audioFormatOptions.map(option => (
                  <Select.Option key={option.value} value={option.value}>
                    <div>
                      <Space>
                        <Text strong>{option.label}</Text>
                        {option.recommended && <Tag color="green">推荐</Tag>}
                      </Space>
                      <br />
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        {option.description}
                      </Text>
                    </div>
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>
          </Panel>

          {/* 训练参数 */}
          <Panel 
            header={
              <Space>
                <ExperimentOutlined />
                <span>训练参数</span>
                <Tag color="red">专家级</Tag>
              </Space>
            } 
            key="training"
          >
            <Alert
              message={
                <Space>
                  <WarningOutlined />
                  <span>警告：修改训练参数可能影响音色质量</span>
                </Space>
              }
              type="warning"
              style={{ marginBottom: 16 }}
            />

            <Form.Item
              name="training_iterations"
              label={
                <Space>
                  <span>训练迭代次数</span>
                  <Tooltip title="训练的迭代次数，更多迭代可能提高质量但增加训练时间">
                    <InfoCircleOutlined />
                  </Tooltip>
                </Space>
              }
              extra="范围：50-500，推荐：100"
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
                tooltip={{ formatter: (value) => `${value} 次` }}
              />
            </Form.Item>

            <Form.Item
              name="learning_rate"
              label={
                <Space>
                  <span>学习率</span>
                  <Tooltip title="控制模型学习速度，过高可能导致不稳定，过低训练缓慢">
                    <InfoCircleOutlined />
                  </Tooltip>
                </Space>
              }
              extra="范围：0.0001-0.01，推荐：0.001"
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

            <Form.Item
              name="batch_size"
              label={
                <Space>
                  <span>批次大小</span>
                  <Tooltip title="每次训练处理的样本数量，影响内存使用和训练稳定性">
                    <InfoCircleOutlined />
                  </Tooltip>
                </Space>
              }
              extra="范围：8-128，推荐：32"
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
          </Panel>

          {/* 实验性功能 */}
          <Panel 
            header={
              <Space>
                <ExperimentOutlined />
                <span>实验性功能</span>
                <Tag color="red">Beta</Tag>
              </Space>
            } 
            key="experimental"
          >
            <Alert
              message="实验性功能警告"
              description="以下功能处于实验阶段，可能不稳定或产生意外结果。仅供研究和测试使用。"
              type="error"
              showIcon
              style={{ marginBottom: 16 }}
            />

            <Form.Item
              name="experimental_features"
              label="启用实验性功能"
              valuePropName="checked"
              extra="启用最新的实验性算法和优化"
            >
              <Switch onChange={handleExperimentalToggle} />
            </Form.Item>

            {experimentalEnabled && (
              <div style={{ padding: 16, backgroundColor: '#fff7e6', borderRadius: 6 }}>
                <Title level={5}>
                  <ExperimentOutlined /> 实验性选项
                </Title>
                <Paragraph type="secondary">
                  实验性功能包括但不限于：
                </Paragraph>
                <ul style={{ color: '#8c8c8c' }}>
                  <li>神经网络架构优化</li>
                  <li>自适应学习率调整</li>
                  <li>多阶段训练策略</li>
                  <li>高级音频预处理</li>
                </ul>
                <Alert
                  message="使用实验性功能的风险由用户承担"
                  type="warning"
                />
              </div>
            )}
          </Panel>
        </Collapse>

        <Divider />

        <div style={{ textAlign: 'center' }}>
          <Space>
            <Text type="secondary">
              <InfoCircleOutlined /> 高级设置将在开始训练时应用
            </Text>
          </Space>
        </div>
      </Form>
    </Card>
  );
};

export default VoiceCloneAdvancedSettings;