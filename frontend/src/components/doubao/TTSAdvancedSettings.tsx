/**
 * TTS Advanced Settings Component
 * TTS高级设置组件 - [components][doubao][tts_advanced_settings]
 */

import React, { useState, useCallback } from 'react';
import {
  Card,
  Form,
  Select,
  Switch,
  Collapse,
  Space,
  Typography,
  Tooltip,
  Alert,
  Tag,
  Divider,
  Radio,
  InputNumber
} from 'antd';
import {
  ExperimentOutlined,
  InfoCircleOutlined,
  WarningOutlined,
  SettingOutlined,
  GlobalOutlined,
  ThunderboltOutlined
} from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;

interface TTSAdvancedSettingsProps {
  visible?: boolean;
  onChange?: (values: TTSAdvancedSettings) => void;
  initialValues?: Partial<TTSAdvancedSettings>;
}

interface TTSAdvancedSettings {
  explicit_language?: string;
  context_language?: string;
  text_type: string;
  with_timestamp: boolean;
  split_sentence: boolean;
  cache_enabled: boolean;
  cluster: string;
  streaming_mode: boolean;
  chunk_size?: number;
  emotion_control?: string;
  prosody_rate?: string;
  prosody_pitch?: string;
  prosody_volume?: string;
}

const TTSAdvancedSettings: React.FC<TTSAdvancedSettingsProps> = ({
  visible = true,
  onChange,
  initialValues = {}
}) => {
  const [form] = Form.useForm();
  const [ssmlEnabled, setSsmlEnabled] = useState(false);
  const [streamingEnabled, setStreamingEnabled] = useState(false);

  // 默认值配置
  const defaultValues: TTSAdvancedSettings = {
    explicit_language: 'zh',
    context_language: '',
    text_type: 'plain',
    with_timestamp: false,
    split_sentence: false,
    cache_enabled: false,
    cluster: 'volcano_icl',
    streaming_mode: false,
    chunk_size: 1024,
    ...initialValues
  };

  // 语种控制选项
  const languageOptions = [
    { 
      value: '', 
      label: '自动检测', 
      description: '自动识别文本语种'
    },
    { 
      value: 'crosslingual', 
      label: '多语种混合', 
      description: '支持多种语言混合文本'
    },
    { 
      value: 'zh', 
      label: '中文为主', 
      description: '以中文为主的文本',
      recommended: true
    },
    { 
      value: 'en', 
      label: '仅英文', 
      description: '纯英文文本'
    },
    { 
      value: 'ja', 
      label: '仅日文', 
      description: '纯日文文本'
    },
    { 
      value: 'es-mx', 
      label: '仅墨西哥语', 
      description: '墨西哥西班牙语'
    },
    { 
      value: 'id', 
      label: '仅印尼语', 
      description: '印尼语文本'
    },
    { 
      value: 'pt-br', 
      label: '仅巴西葡萄牙语', 
      description: '巴西葡萄牙语'
    }
  ];

  // 参考语种选项
  const contextLanguageOptions = [
    { 
      value: '', 
      label: '默认(英语)', 
      description: '使用英语作为参考语言'
    },
    { 
      value: 'id', 
      label: '印尼语参考', 
      description: '使用印尼语发音规则'
    },
    { 
      value: 'es', 
      label: '西班牙语参考', 
      description: '使用西班牙语发音规则'
    },
    { 
      value: 'pt', 
      label: '葡萄牙语参考', 
      description: '使用葡萄牙语发音规则'
    }
  ];

  // 集群选项
  const clusterOptions = [
    {
      value: 'volcano_icl',
      label: '标准集群',
      description: '标准处理集群，稳定可靠',
      recommended: true
    },
    {
      value: 'volcano_icl_concurr',
      label: '并发集群', 
      description: '高并发处理集群，适合大量请求'
    }
  ];

  // SSML情感控制选项
  const emotionOptions = [
    { value: 'neutral', label: '中性', description: '标准语调' },
    { value: 'happy', label: '开心', description: '愉悦语调' },
    { value: 'sad', label: '悲伤', description: '低沉语调' },
    { value: 'angry', label: '愤怒', description: '激动语调' },
    { value: 'fear', label: '恐惧', description: '紧张语调' },
    { value: 'disgust', label: '厌恶', description: '厌恶语调' },
    { value: 'surprise', label: '惊讶', description: '惊讶语调' }
  ];

  // 韵律控制选项
  const prosodyOptions = [
    { value: 'x-slow', label: '极慢' },
    { value: 'slow', label: '慢' },
    { value: 'medium', label: '正常' },
    { value: 'fast', label: '快' },
    { value: 'x-fast', label: '极快' }
  ];

  // 表单值变化处理
  const handleValuesChange = useCallback((changedValues: any, allValues: any) => {
    // 处理文本类型变化
    if (changedValues.text_type) {
      setSsmlEnabled(changedValues.text_type === 'ssml');
    }

    // 处理流式模式变化
    if (changedValues.streaming_mode !== undefined) {
      setStreamingEnabled(changedValues.streaming_mode);
    }

    if (onChange) {
      onChange(allValues);
    }
  }, [onChange]);

  if (!visible) return null;

  return (
    <Card 
      title={
        <Space>
          <SettingOutlined />
          <span>TTS高级设置</span>
          <Tag color="blue">专业功能</Tag>
        </Space>
      }
      style={{ marginTop: 16 }}
    >
      <Alert
        message="高级设置说明"
        description="高级设置提供更精细的语音合成控制。这些选项主要面向专业用户，修改前请确保了解其影响。"
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
        <Collapse defaultActiveKey={['language']} ghost>
          {/* 语言设置 */}
          <Panel 
            header={
              <Space>
                <GlobalOutlined />
                <span>语言设置</span>
              </Space>
            } 
            key="language"
          >
            <Form.Item
              name="explicit_language"
              label={
                <Space>
                  <span>语种控制</span>
                  <Tooltip title="精确控制文本语种识别，提高合成准确性">
                    <InfoCircleOutlined style={{ color: '#1890ff' }} />
                  </Tooltip>
                </Space>
              }
              extra="精确控制文本语种识别"
            >
              <Select>
                {languageOptions.map(option => (
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

            <Form.Item
              name="context_language"
              label={
                <Space>
                  <span>参考语种</span>
                  <Tooltip title="为西欧语种提供发音参考，改善多语言文本的合成效果">
                    <InfoCircleOutlined style={{ color: '#1890ff' }} />
                  </Tooltip>
                </Space>
              }
              extra="为西欧语种提供参考语言"
            >
              <Select>
                {contextLanguageOptions.map(option => (
                  <Select.Option key={option.value} value={option.value}>
                    <div>
                      <Text strong>{option.label}</Text>
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

          {/* 文本处理 */}
          <Panel 
            header={
              <Space>
                <SettingOutlined />
                <span>文本处理</span>
              </Space>
            } 
            key="text"
          >
            <Form.Item
              name="text_type"
              label="文本类型"
              extra="选择文本标记语言类型"
            >
              <Radio.Group>
                <Radio value="plain">纯文本</Radio>
                <Radio value="ssml">
                  <Space>
                    <span>SSML标记语言</span>
                    <Tag color="orange">高级</Tag>
                  </Space>
                </Radio>
              </Radio.Group>
            </Form.Item>

            {ssmlEnabled && (
              <div style={{ padding: 16, backgroundColor: '#fff7e6', borderRadius: 6, marginTop: 8 }}>
                <Title level={5}>
                  <ExperimentOutlined /> SSML控制选项
                </Title>
                
                <Form.Item
                  name="emotion_control"
                  label="情感控制"
                  extra="控制语音的情感表达"
                >
                  <Select placeholder="选择情感">
                    {emotionOptions.map(option => (
                      <Select.Option key={option.value} value={option.value}>
                        <div>
                          <Text strong>{option.label}</Text>
                          <br />
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            {option.description}
                          </Text>
                        </div>
                      </Select.Option>
                    ))}
                  </Select>
                </Form.Item>

                <Form.Item
                  name="prosody_rate"
                  label="韵律速度"
                  extra="控制语音韵律节奏"
                >
                  <Select placeholder="选择韵律速度">
                    {prosodyOptions.map(option => (
                      <Select.Option key={option.value} value={option.value}>
                        {option.label}
                      </Select.Option>
                    ))}
                  </Select>
                </Form.Item>

                <Alert
                  message="SSML使用提示"
                  description="使用SSML时，请在文本中包含适当的SSML标记。例如：<speak><prosody rate='slow'>这是慢速语音</prosody></speak>"
                  type="info"
                />
              </div>
            )}

            <Form.Item
              name="split_sentence"
              label="分句处理"
              valuePropName="checked"
              extra="针对1.0音色的语速优化，解决语速过快问题"
            >
              <Switch />
            </Form.Item>
          </Panel>

          {/* 输出选项 */}
          <Panel 
            header={
              <Space>
                <InfoCircleOutlined />
                <span>输出选项</span>
              </Space>
            } 
            key="output"
          >
            <Form.Item
              name="with_timestamp"
              label="时间戳"
              valuePropName="checked"
              extra="返回原文本的时间戳信息，用于字幕同步等应用"
            >
              <Switch />
            </Form.Item>

            <Form.Item
              name="streaming_mode"
              label="流式输出"
              valuePropName="checked"
              extra="启用流式输出，实时获取音频数据"
            >
              <Switch />
            </Form.Item>

            {streamingEnabled && (
              <Form.Item
                name="chunk_size"
                label="数据块大小"
                extra="流式输出时每个数据块的大小（字节）"
              >
                <InputNumber
                  min={512}
                  max={8192}
                  step={512}
                  style={{ width: '100%' }}
                  formatter={(value) => `${value} bytes`}
                  parser={(value) => value?.replace(' bytes', '') as any}
                />
              </Form.Item>
            )}
          </Panel>

          {/* 性能优化 */}
          <Panel 
            header={
              <Space>
                <ThunderboltOutlined />
                <span>性能优化</span>
              </Space>
            } 
            key="performance"
          >
            <Form.Item
              name="cache_enabled"
              label="启用缓存"
              valuePropName="checked"
              extra="缓存相同文本的合成结果，提高响应速度"
            >
              <Switch />
            </Form.Item>

            <Form.Item
              name="cluster"
              label="集群选择"
              extra="选择处理集群类型"
            >
              <Select>
                {clusterOptions.map(option => (
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
              message={
                <Space>
                  <WarningOutlined />
                  <span>实验性功能可能不稳定</span>
                </Space>
              }
              description="以下功能处于测试阶段，可能影响合成质量或稳定性。"
              type="warning"
              style={{ marginBottom: 16 }}
            />

            <Paragraph type="secondary">
              实验性功能包括：
            </Paragraph>
            <ul style={{ color: '#8c8c8c' }}>
              <li>实时语音合成优化</li>
              <li>自适应音质调整</li>
              <li>智能标点处理</li>
              <li>多说话人支持（开发中）</li>
            </ul>
          </Panel>
        </Collapse>

        <Divider />

        <div style={{ textAlign: 'center' }}>
          <Space>
            <Text type="secondary">
              <InfoCircleOutlined /> 高级设置将在合成时应用
            </Text>
          </Space>
        </div>
      </Form>
    </Card>
  );
};

export default TTSAdvancedSettings;