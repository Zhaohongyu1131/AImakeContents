/**
 * TTS Basic Settings Component
 * TTS基础设置组件 - [components][doubao][tts_basic_settings]
 */

import React, { useState, useCallback } from 'react';
import {
  Card,
  Form,
  Input,
  Select,
  Slider,
  Button,
  Space,
  Typography,
  message,
  Divider,
  Row,
  Col,
  Tag,
  Tooltip
} from 'antd';
import {
  SoundOutlined,
  PlayCircleOutlined,
  DownloadOutlined,
  InfoCircleOutlined,
  SettingOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;
const { TextArea } = Input;

interface TTSBasicSettingsProps {
  onSynthesize?: (values: TTSFormData) => void;
  onPreview?: (values: TTSFormData) => void;
  loading?: boolean;
  previewLoading?: boolean;
  onAdvancedToggle?: () => void;
  showAdvanced?: boolean;
  voiceList?: VoiceOption[];
}

interface TTSFormData {
  text: string;
  voice_type: string;
  speed_ratio: number;
  volume_ratio: number;
  pitch_ratio: number;
  encoding: string;
  sample_rate: number;
}

interface VoiceOption {
  value: string;
  label: string;
  language: string;
  gender: string;
  style: string;
  description?: string;
  isCustom?: boolean;
}

const TTSBasicSettings: React.FC<TTSBasicSettingsProps> = ({
  onSynthesize,
  onPreview,
  loading = false,
  previewLoading = false,
  onAdvancedToggle,
  showAdvanced = false,
  voiceList = []
}) => {
  const [form] = Form.useForm();
  const [textLength, setTextLength] = useState(0);
  const [estimatedDuration, setEstimatedDuration] = useState(0);

  // 默认音色选项
  const defaultVoices: VoiceOption[] = [
    {
      value: 'BV001_streaming',
      label: '灿灿 - 女声',
      language: '中文',
      gender: '女',
      style: '亲切温暖',
      description: '温柔亲切的女声，适合有声书和客服'
    },
    {
      value: 'BV002_streaming', 
      label: '擎苍 - 男声',
      language: '中文',
      gender: '男',
      style: '沉稳磁性',
      description: '成熟稳重的男声，适合新闻播报'
    },
    {
      value: 'BV003_streaming',
      label: '小萝莉',
      language: '中文', 
      gender: '女',
      style: '活泼可爱',
      description: '年轻活泼的女声，适合儿童内容'
    },
    {
      value: 'BV004_streaming',
      label: '知性女声',
      language: '中文',
      gender: '女', 
      style: '知性专业',
      description: '专业知性的女声，适合教育培训'
    }
  ];

  // 合并默认音色和用户自定义音色
  const allVoices = [...defaultVoices, ...voiceList];

  // 音频格式选项
  const encodingOptions = [
    { 
      value: 'mp3', 
      label: 'MP3 - 推荐', 
      description: '通用格式，文件小，兼容性好',
      recommended: true
    },
    { 
      value: 'wav', 
      label: 'WAV - 高质量', 
      description: '无损格式，音质最佳，文件较大'
    },
    { 
      value: 'ogg_opus', 
      label: 'OGG Opus - 压缩', 
      description: '高压缩比，音质好，文件小'
    },
    { 
      value: 'pcm', 
      label: 'PCM - 原始', 
      description: '原始音频数据，用于特殊需求'
    }
  ];

  // 采样率选项
  const sampleRateOptions = [
    { 
      value: 8000, 
      label: '8kHz - 电话质量', 
      description: '适合语音通话'
    },
    { 
      value: 16000, 
      label: '16kHz - 标准质量', 
      description: '标准语音质量'
    },
    { 
      value: 24000, 
      label: '24kHz - 高质量', 
      description: '高质量语音，推荐使用',
      recommended: true
    }
  ];

  // 场景预设
  const scenePresets = [
    {
      name: '新闻播报',
      values: { speed_ratio: 1.0, volume_ratio: 1.0, pitch_ratio: 1.0 }
    },
    {
      name: '有声书',
      values: { speed_ratio: 0.9, volume_ratio: 0.9, pitch_ratio: 1.0 }
    },
    {
      name: '客服语音',
      values: { speed_ratio: 1.1, volume_ratio: 1.1, pitch_ratio: 1.05 }
    },
    {
      name: '儿童内容',
      values: { speed_ratio: 0.8, volume_ratio: 1.2, pitch_ratio: 1.1 }
    }
  ];

  // 文本变化处理
  const handleTextChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const text = e.target.value;
    setTextLength(text.length);
    
    // 估算时长（基于平均语速）
    const wordsPerMinute = 200; // 中文平均语速
    const characters = text.length;
    const estimatedMinutes = characters / wordsPerMinute;
    setEstimatedDuration(estimatedMinutes * 60); // 转换为秒
  }, []);

  // 应用场景预设
  const applyPreset = useCallback((preset: any) => {
    form.setFieldsValue(preset.values);
    message.success(`已应用"${preset.name}"预设`);
  }, [form]);

  // 表单提交
  const handleSubmit = useCallback(async (values: any) => {
    if (!values.text?.trim()) {
      message.error('请输入要合成的文本');
      return;
    }

    const formData: TTSFormData = {
      text: values.text.trim(),
      voice_type: values.voice_type,
      speed_ratio: values.speed_ratio,
      volume_ratio: values.volume_ratio,
      pitch_ratio: values.pitch_ratio,
      encoding: values.encoding,
      sample_rate: values.sample_rate
    };

    if (onSynthesize) {
      try {
        await onSynthesize(formData);
        message.success('音频合成成功！');
      } catch (error) {
        message.error('合成失败，请重试');
      }
    }
  }, [onSynthesize]);

  // 预览处理
  const handlePreview = useCallback(async () => {
    const values = form.getFieldsValue();
    if (!values.text?.trim()) {
      message.error('请输入要预览的文本');
      return;
    }

    if (onPreview) {
      const formData: TTSFormData = {
        text: values.text.trim().substring(0, 100), // 预览只取前100字
        voice_type: values.voice_type,
        speed_ratio: values.speed_ratio,
        volume_ratio: values.volume_ratio,
        pitch_ratio: values.pitch_ratio,
        encoding: 'mp3',
        sample_rate: values.sample_rate
      };

      try {
        await onPreview(formData);
      } catch (error) {
        message.error('预览失败，请重试');
      }
    }
  }, [form, onPreview]);

  return (
    <Card 
      title={
        <Space>
          <SoundOutlined />
          <span>文本转语音 - 基础设置</span>
        </Space>
      }
      extra={
        <Button 
          type="link" 
          onClick={onAdvancedToggle}
          icon={<SettingOutlined />}
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
          speed_ratio: 1.0,
          volume_ratio: 1.0,
          pitch_ratio: 1.0,
          encoding: 'mp3',
          sample_rate: 24000,
          voice_type: 'BV001_streaming'
        }}
      >
        {/* 文本输入 */}
        <Form.Item
          name="text"
          label="输入文本"
          rules={[
            { required: true, message: '请输入要合成的文本' },
            { max: 5000, message: '文本长度不能超过5000字符' }
          ]}
          extra={
            <Space>
              <Text type="secondary">
                当前字数：{textLength} / 5000
              </Text>
              {estimatedDuration > 0 && (
                <Text type="secondary">
                  预计时长：{Math.round(estimatedDuration)}秒
                </Text>
              )}
            </Space>
          }
        >
          <TextArea
            placeholder="请输入要转换为语音的文本内容..."
            rows={6}
            showCount
            maxLength={5000}
            onChange={handleTextChange}
          />
        </Form.Item>

        {/* 场景预设 */}
        <Form.Item label="快速预设">
          <Space wrap>
            {scenePresets.map((preset, index) => (
              <Button
                key={index}
                                onClick={() => applyPreset(preset)}
                type="dashed"
              >
                {preset.name}
              </Button>
            ))}
          </Space>
        </Form.Item>

        <Divider />

        {/* 音色选择 */}
        <Form.Item
          name="voice_type"
          label="选择音色"
          rules={[{ required: true, message: '请选择音色' }]}
        >
          <Select 
            placeholder="请选择音色"
            showSearch
            filterOption={(input, option) =>
              (option?.children as any)?.props?.children[0]?.props?.children
                ?.toLowerCase()
                ?.includes(input.toLowerCase())
            }
          >
            {allVoices.map(voice => (
              <Select.Option key={voice.value} value={voice.value}>
                <div>
                  <Space>
                    <Text strong>{voice.label}</Text>
                    <Tag color={voice.gender === '女' ? 'pink' : 'blue'}>
                      {voice.gender}
                    </Tag>
                    <Tag color="default">{voice.language}</Tag>
                    {voice.isCustom && <Tag color="orange">自定义</Tag>}
                  </Space>
                  <br />
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {voice.style} - {voice.description}
                  </Text>
                </div>
              </Select.Option>
            ))}
          </Select>
        </Form.Item>

        {/* 语音控制 */}
        <Title level={5}>语音控制</Title>
        
        <Row gutter={16}>
          <Col span={8}>
            <Form.Item
              name="speed_ratio"
              label={
                <Space>
                  <span>语速</span>
                  <Tooltip title="调整语音播放速度，1.0为正常速度">
                    <InfoCircleOutlined />
                  </Tooltip>
                </Space>
              }
            >
              <Slider
                min={0.2}
                max={3.0}
                step={0.1}
                marks={{
                  0.2: '0.2x',
                  1.0: '1.0x',
                  3.0: '3.0x'
                }}
                tooltip={{ formatter: (value) => `${value}x` }}
              />
            </Form.Item>
          </Col>
          
          <Col span={8}>
            <Form.Item
              name="volume_ratio"
              label={
                <Space>
                  <span>音量</span>
                  <Tooltip title="调整语音音量大小，1.0为正常音量">
                    <InfoCircleOutlined />
                  </Tooltip>
                </Space>
              }
            >
              <Slider
                min={0.1}
                max={2.0}
                step={0.1}
                marks={{
                  0.1: '0.1x',
                  1.0: '1.0x',
                  2.0: '2.0x'
                }}
                tooltip={{ formatter: (value) => `${value}x` }}
              />
            </Form.Item>
          </Col>
          
          <Col span={8}>
            <Form.Item
              name="pitch_ratio"
              label={
                <Space>
                  <span>音调</span>
                  <Tooltip title="调整语音音调高低，1.0为正常音调">
                    <InfoCircleOutlined />
                  </Tooltip>
                </Space>
              }
            >
              <Slider
                min={0.5}
                max={2.0}
                step={0.1}
                marks={{
                  0.5: '0.5x',
                  1.0: '1.0x',
                  2.0: '2.0x'
                }}
                tooltip={{ formatter: (value) => `${value}x` }}
              />
            </Form.Item>
          </Col>
        </Row>

        <Divider />

        {/* 输出设置 */}
        <Title level={5}>输出设置</Title>
        
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="encoding"
              label="音频格式"
              rules={[{ required: true, message: '请选择音频格式' }]}
            >
              <Select>
                {encodingOptions.map(option => (
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
          </Col>
          
          <Col span={12}>
            <Form.Item
              name="sample_rate"
              label="采样率"
              rules={[{ required: true, message: '请选择采样率' }]}
            >
              <Select>
                {sampleRateOptions.map(option => (
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
          </Col>
        </Row>

        <Divider />

        {/* 操作按钮 */}
        <Form.Item style={{ marginBottom: 0 }}>
          <Space size="middle">
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              icon={<DownloadOutlined />}
              size="large"
            >
              生成音频
            </Button>
            <Button
              onClick={handlePreview}
              loading={previewLoading}
              icon={<PlayCircleOutlined />}
            >
              预览效果
            </Button>
            <Button onClick={() => form.resetFields()}>
              重置设置
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default TTSBasicSettings;