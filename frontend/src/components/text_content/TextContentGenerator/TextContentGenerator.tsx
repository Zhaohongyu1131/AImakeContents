/**
 * Text Content Generator Component
 * 文本内容生成器组件 - [components][text_content][text_content_generator]
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  Form,
  Input,
  Select,
  Button,
  Row,
  Col,
  Space,
  Divider,
  Alert,
  Typography,
  Slider,
  Switch,
  Tag,
  Spin,
  message
} from 'antd';
import {
  SendOutlined,
  CopyOutlined,
  SaveOutlined,
  ReloadOutlined,
  SettingOutlined,
  BulbOutlined,
  FileTextOutlined
} from '@ant-design/icons';

import { useTextContentStore } from '../../../stores/text_content/text_content_store';
import { textContentApiService } from '../../../services/api/text_content_api';
import type { TextGenerationRequest, TextGenerationResponse } from '../../../services/api/text_content_api';

const { TextArea } = Input;
const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

interface TextContentGeneratorProps {
  className?: string;
  onGenerated?: (result: TextGenerationResponse) => void;
  defaultPrompt?: string;
  defaultType?: 'article' | 'prompt' | 'script' | 'description';
}

export const TextContentGenerator: React.FC<TextContentGeneratorProps> = ({
  className,
  onGenerated,
  defaultPrompt = '',
  defaultType = 'article'
}) => {
  const [form] = Form.useForm();
  const [generatedText, setGeneratedText] = useState<string>('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [availableModels, setAvailableModels] = useState<any[]>([]);
  const [modelsLoading, setModelsLoading] = useState(false);

  const {
    generationLoading,
    generationError,
    lastGenerationResult,
    text_content_store_generate_text,
    text_content_store_create_content,
    text_content_store_clear_errors
  } = useTextContentStore();

  // 加载可用模型
  useEffect(() => {
    const loadAvailableModels = async () => {
      setModelsLoading(true);
      try {
        const response = await textContentApiService.text_content_api_get_available_models();
        if (response.success && response.data) {
          setAvailableModels(response.data);
        }
      } catch (error) {
        console.error('Failed to load models:', error);
      } finally {
        setModelsLoading(false);
      }
    };

    loadAvailableModels();
  }, []);

  // 初始化表单
  useEffect(() => {
    form.setFieldsValue({
      prompt: defaultPrompt,
      content_type: defaultType,
      model_provider: 'doubao',
      temperature: 0.7,
      max_tokens: 2000,
      save_to_content: false
    });
  }, [form, defaultPrompt, defaultType]);

  // 处理生成结果
  useEffect(() => {
    if (lastGenerationResult) {
      setGeneratedText(lastGenerationResult.generated_text);
      if (onGenerated) {
        onGenerated(lastGenerationResult);
      }
    }
  }, [lastGenerationResult, onGenerated]);

  const handleGenerate = async () => {
    try {
      const values = await form.validateFields();
      
      const request: TextGenerationRequest = {
        prompt: values.prompt,
        model_provider: values.model_provider,
        model_name: values.model_name,
        temperature: values.temperature,
        max_tokens: values.max_tokens,
        content_type: values.content_type,
        save_to_content: values.save_to_content,
        content_title: values.content_title,
        content_tags: values.content_tags?.split(',').map((tag: string) => tag.trim()).filter(Boolean)
      };

      const result = await text_content_store_generate_text(request);
      
      if (result) {
        message.success('文本生成成功！');
      }
    } catch (error) {
      console.error('Generation failed:', error);
    }
  };

  const handleCopyText = () => {
    if (generatedText) {
      navigator.clipboard.writeText(generatedText);
      message.success('文本已复制到剪贴板');
    }
  };

  const handleSaveAsContent = async () => {
    if (!generatedText) {
      message.warning('没有可保存的内容');
      return;
    }

    try {
      const values = await form.validateFields(['content_title', 'content_type']);
      
      const success = await text_content_store_create_content({
        content_title: values.content_title || '生成的文本内容',
        content_body: generatedText,
        content_type: values.content_type,
        content_tags: values.content_tags?.split(',').map((tag: string) => tag.trim()).filter(Boolean),
        content_status: 'draft'
      });

      if (success) {
        message.success('内容已保存到内容库');
      }
    } catch (error) {
      console.error('Save failed:', error);
    }
  };

  const handleClearErrors = () => {
    text_content_store_clear_errors();
    setGeneratedText('');
  };

  const promptTemplates = [
    { label: '文章写作', value: '请写一篇关于{主题}的文章，要求内容详实、逻辑清晰、语言流畅。' },
    { label: '产品描述', value: '请为{产品名称}写一份产品描述，突出其{特点}和{优势}。' },
    { label: '社交媒体', value: '请为{品牌}写一条{平台}的社交媒体文案，风格要{风格特点}。' },
    { label: '邮件营销', value: '请写一封{目的}的营销邮件，目标用户是{用户群体}。' },
    { label: '脚本创作', value: '请为{场景}写一个{时长}的脚本，风格要{风格}。' }
  ];

  const renderModelSelector = () => {
    if (modelsLoading) {
      return <Spin size="small" />;
    }

    return (
      <Form.Item
        name="model_provider"
        label="AI模型"
        rules={[{ required: true, message: '请选择AI模型' }]}
      >
        <Select
          placeholder="选择AI模型提供商"
          onChange={(provider) => {
            // 重置模型选择
            form.setFieldValue('model_name', undefined);
          }}
        >
          {availableModels.map((provider) => (
            <Option key={provider.provider} value={provider.provider}>
              <Space>
                <Tag color={provider.provider === 'doubao' ? 'blue' : provider.provider === 'openai' ? 'green' : 'orange'}>
                  {provider.provider.toUpperCase()}
                </Tag>
                {provider.provider === 'doubao' ? '豆包大模型' : 
                 provider.provider === 'openai' ? 'OpenAI GPT' : 
                 provider.provider === 'azure' ? 'Azure OpenAI' : provider.provider}
              </Space>
            </Option>
          ))}
        </Select>
      </Form.Item>
    );
  };

  const renderSpecificModelSelector = () => {
    const selectedProvider = form.getFieldValue('model_provider');
    const providerData = availableModels.find(p => p.provider === selectedProvider);
    
    if (!providerData || !showAdvanced) {
      return null;
    }

    return (
      <Form.Item
        name="model_name"
        label="具体模型"
      >
        <Select placeholder="选择具体模型（可选）">
          {providerData.models.map((model: any) => (
            <Option key={model.name} value={model.name}>
              <div>
                <div>{model.display_name}</div>
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  {model.description} (最大 {model.max_tokens} tokens)
                </Text>
              </div>
            </Option>
          ))}
        </Select>
      </Form.Item>
    );
  };

  return (
    <div className={`text-content-generator ${className || ''}`}>
      <Row gutter={24}>
        {/* 左侧：生成器配置 */}
        <Col xs={24} lg={12}>
          <Card
            title={
              <Space>
                <BulbOutlined />
                <span>AI文本生成器</span>
              </Space>
            }
            extra={
              <Button
                type="text"
                icon={<SettingOutlined />}
                onClick={() => setShowAdvanced(!showAdvanced)}
              >
                {showAdvanced ? '隐藏高级设置' : '高级设置'}
              </Button>
            }
          >
            <Form
              form={form}
              layout="vertical"
              onFinish={handleGenerate}
            >
              {/* 提示词输入 */}
              <Form.Item
                name="prompt"
                label={
                  <Space>
                    <span>提示词</span>
                    <Select
                      placeholder="选择模板"
                      style={{ width: 120 }}
                      size="small"
                      allowClear
                      onChange={(value) => {
                        if (value) {
                          form.setFieldValue('prompt', value);
                        }
                      }}
                    >
                      {promptTemplates.map((template, index) => (
                        <Option key={index} value={template.value}>
                          {template.label}
                        </Option>
                      ))}
                    </Select>
                  </Space>
                }
                rules={[{ required: true, message: '请输入提示词' }]}
              >
                <TextArea
                  rows={6}
                  placeholder="请描述您要生成的文本内容..."
                  showCount
                  maxLength={2000}
                />
              </Form.Item>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name="content_type"
                    label="内容类型"
                    rules={[{ required: true, message: '请选择内容类型' }]}
                  >
                    <Select placeholder="选择内容类型">
                      <Option value="article">文章</Option>
                      <Option value="prompt">提示词</Option>
                      <Option value="script">脚本</Option>
                      <Option value="description">描述</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  {renderModelSelector()}
                </Col>
              </Row>

              {/* 高级设置 */}
              {showAdvanced && (
                <>
                  <Divider>高级设置</Divider>
                  
                  {renderSpecificModelSelector()}

                  <Row gutter={16}>
                    <Col span={12}>
                      <Form.Item
                        name="temperature"
                        label="创造性 (Temperature)"
                      >
                        <Slider
                          min={0}
                          max={1}
                          step={0.1}
                          marks={{
                            0: '保守',
                            0.5: '平衡',
                            1: '创新'
                          }}
                        />
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item
                        name="max_tokens"
                        label="最大长度"
                      >
                        <Slider
                          min={100}
                          max={4000}
                          step={100}
                          marks={{
                            100: '100',
                            2000: '2000',
                            4000: '4000'
                          }}
                        />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Form.Item
                    name="save_to_content"
                    valuePropName="checked"
                  >
                    <Switch checkedChildren="保存到内容库" unCheckedChildren="仅生成" />
                  </Form.Item>

                  <Form.Item
                    noStyle
                    shouldUpdate={(prevValues, currentValues) => 
                      prevValues.save_to_content !== currentValues.save_to_content
                    }
                  >
                    {({ getFieldValue }) => {
                      const saveToContent = getFieldValue('save_to_content');
                      
                      if (!saveToContent) return null;

                      return (
                        <>
                          <Form.Item
                            name="content_title"
                            label="内容标题"
                            rules={[{ required: true, message: '请输入内容标题' }]}
                          >
                            <Input placeholder="生成内容的标题" />
                          </Form.Item>

                          <Form.Item
                            name="content_tags"
                            label="标签"
                          >
                            <Input placeholder="多个标签用逗号分隔" />
                          </Form.Item>
                        </>
                      );
                    }}
                  </Form.Item>
                </>
              )}

              {/* 错误提示 */}
              {generationError && (
                <Alert
                  message="生成失败"
                  description={generationError}
                  type="error"
                  showIcon
                  closable
                  onClose={handleClearErrors}
                  style={{ marginBottom: 16 }}
                />
              )}

              {/* 操作按钮 */}
              <Space style={{ width: '100%', justifyContent: 'center' }}>
                <Button
                  type="primary"
                  icon={<SendOutlined />}
                  htmlType="submit"
                  loading={generationLoading}
                  size="large"
                >
                  {generationLoading ? '生成中...' : '生成文本'}
                </Button>
                <Button
                  icon={<ReloadOutlined />}
                  onClick={() => {
                    form.resetFields();
                    setGeneratedText('');
                    handleClearErrors();
                  }}
                >
                  重置
                </Button>
              </Space>
            </Form>
          </Card>
        </Col>

        {/* 右侧：生成结果 */}
        <Col xs={24} lg={12}>
          <Card
            title={
              <Space>
                <FileTextOutlined />
                <span>生成结果</span>
              </Space>
            }
            extra={
              generatedText && (
                <Space>
                  <Button
                    type="text"
                    icon={<CopyOutlined />}
                    onClick={handleCopyText}
                  >
                    复制
                  </Button>
                  <Button
                    type="text"
                    icon={<SaveOutlined />}
                    onClick={handleSaveAsContent}
                  >
                    保存为内容
                  </Button>
                </Space>
              )
            }
          >
            {generationLoading ? (
              <div style={{ textAlign: 'center', padding: '60px 0' }}>
                <Spin size="large" />
                <div style={{ marginTop: 16 }}>
                  <Text>AI正在为您生成内容，请稍候...</Text>
                </div>
              </div>
            ) : generatedText ? (
              <div>
                <TextArea
                  value={generatedText}
                  onChange={(e) => setGeneratedText(e.target.value)}
                  rows={20}
                  style={{ marginBottom: 16 }}
                />
                
                {/* 生成统计信息 */}
                {lastGenerationResult && (
                  <div style={{ 
                    background: '#f5f5f5', 
                    padding: '12px', 
                    borderRadius: '6px',
                    fontSize: '12px'
                  }}>
                    <Row gutter={16}>
                      <Col span={8}>
                        <Text type="secondary">
                          模型: {lastGenerationResult.model_provider}/{lastGenerationResult.model_name}
                        </Text>
                      </Col>
                      <Col span={8}>
                        <Text type="secondary">
                          字符数: {generatedText.length}
                        </Text>
                      </Col>
                      <Col span={8}>
                        <Text type="secondary">
                          Token: {lastGenerationResult.usage_stats?.total_tokens || 'N/A'}
                        </Text>
                      </Col>
                    </Row>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ 
                textAlign: 'center', 
                padding: '60px 0',
                color: '#999'
              }}>
                <BulbOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
                <div>
                  <Title level={4} type="secondary">等待生成</Title>
                  <Paragraph type="secondary">
                    在左侧输入提示词，点击"生成文本"按钮开始创作
                  </Paragraph>
                </div>
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default TextContentGenerator;