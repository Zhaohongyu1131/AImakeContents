/**
 * Image Content Generate Component
 * 图像内容生成组件 - [components][image_service][image_content_generate]
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  Card,
  Form,
  Input,
  Select,
  Button,
  Space,
  Row,
  Col,
  Typography,
  Slider,
  Switch,
  Alert,
  Progress,
  Divider,
  message,
  Upload,
  Tag,
  Tooltip,
  Badge,
  Collapse,
  Image,
  Modal,
  Spin,
  InputNumber,
  Radio
} from 'antd';
import {
  PictureOutlined,
  ThunderboltOutlined,
  UploadOutlined,
  SettingOutlined,
  EyeOutlined,
  DownloadOutlined,
  CopyOutlined,
  ReloadOutlined,
  SaveOutlined,
  ExperimentOutlined,
  BulbOutlined,
  StarOutlined,
  CloudUploadOutlined
} from '@ant-design/icons';

import { useImageServiceStore } from '../../../stores/image_service/image_service_store';
import type { 
  ImageGenerationRequest,
  ImageGenerationResponse,
  ImagePlatformType,
  ImageStyle,
  ImageRatio,
  ImageQuality 
} from '../../../services/api/image_service_api';

const { TextArea } = Input;
const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { Panel } = Collapse;
const { Dragger } = Upload;

interface ImageContentGenerateProps {
  initialPrompt?: string;
  onGenerated?: (result: ImageGenerationResponse) => void;
  onSaved?: (imageId: number) => void;
  className?: string;
}

export const ImageContentGenerate: React.FC<ImageContentGenerateProps> = ({
  initialPrompt = '',
  onGenerated,
  onSaved,
  className
}) => {
  const [form] = Form.useForm();
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);
  const [previewImages, setPreviewImages] = useState<string[]>([]);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [imagePreviewVisible, setImagePreviewVisible] = useState(false);
  const [promptWordCount, setPromptWordCount] = useState(0);
  const [estimatedCost, setEstimatedCost] = useState(0);
  const [referenceImages, setReferenceImages] = useState<string[]>([]);

  const {
    generationLoading,
    generationProgress,
    lastGenerationResult,
    platformConnectionStatus,
    uploadLoading,
    uploadedFiles,
    image_service_store_generate_image,
    image_service_store_upload_reference,
    image_service_store_test_platform_connection,
    image_service_store_clear_errors,
    image_service_store_clear_uploaded_files
  } = useImageServiceStore();

  // 初始化表单
  useEffect(() => {
    form.setFieldsValue({
      prompt: initialPrompt,
      generation_params: {
        style: 'realistic',
        aspect_ratio: '1:1',
        quality: 'high',
        steps: 30,
        guidance_scale: 7.5,
        num_images: 1,
        content_filter: 'moderate'
      },
      platform_type: 'doubao',
      save_to_library: true
    });
    
    if (initialPrompt) {
      setPromptWordCount(initialPrompt.length);
      calculateEstimatedCost(initialPrompt, 'doubao', 1);
    }

    // 测试平台连接
    image_service_store_test_platform_connection('doubao');
    image_service_store_test_platform_connection('dalle');
    image_service_store_test_platform_connection('stable_diffusion');
  }, [form, initialPrompt]);

  // 监听生成结果
  useEffect(() => {
    if (lastGenerationResult) {
      setPreviewImages(lastGenerationResult.image_urls);
      onGenerated?.(lastGenerationResult);
    }
  }, [lastGenerationResult, onGenerated]);

  // 监听提示词变化
  const handlePromptChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const prompt = e.target.value;
    setPromptWordCount(prompt.length);
    
    const platformType = form.getFieldValue('platform_type');
    const numImages = form.getFieldValue(['generation_params', 'num_images']);
    calculateEstimatedCost(prompt, platformType, numImages);
  };

  // 计算预估成本
  const calculateEstimatedCost = (prompt: string, platform: string, numImages: number) => {
    // 简单的成本估算逻辑
    const baseCost = {
      doubao: 0.02,
      dalle: 0.04,
      stable_diffusion: 0.01,
      midjourney: 0.03,
      azure: 0.035
    };
    
    const cost = (baseCost[platform as keyof typeof baseCost] || 0.02) * numImages;
    const complexityMultiplier = Math.min(prompt.length / 100, 2); // 复杂度影响
    setEstimatedCost(cost * (1 + complexityMultiplier));
  };

  // 上传参考图像
  const handleReferenceUpload = async (file: File) => {
    const url = await image_service_store_upload_reference(file, 'reference');
    if (url) {
      setReferenceImages(prev => [...prev, url]);
      message.success('参考图像上传成功');
    }
    return false; // 阻止自动上传
  };

  // 移除参考图像
  const handleRemoveReference = (index: number) => {
    setReferenceImages(prev => prev.filter((_, i) => i !== index));
  };

  // 生成图像
  const handleGenerate = async () => {
    try {
      const values = await form.validateFields();
      
      const request: ImageGenerationRequest = {
        prompt: values.prompt,
        negative_prompt: values.negative_prompt,
        platform_type: values.platform_type,
        generation_params: values.generation_params,
        reference_images: referenceImages,
        save_to_library: values.save_to_library,
        image_title: values.image_title || `AI生成图像_${new Date().getTime()}`
      };

      const result = await image_service_store_generate_image(request);
      if (result) {
        message.success(`成功生成 ${result.image_urls.length} 张图像`);
        
        // 清理上传的文件
        if (!values.save_to_library) {
          image_service_store_clear_uploaded_files();
        }
      }
    } catch (error) {
      console.error('Generation failed:', error);
    }
  };

  // 下载图像
  const handleDownload = (imageUrl: string, index: number) => {
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = `ai_generated_${Date.now()}_${index + 1}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // 复制图像URL
  const handleCopyUrl = (imageUrl: string) => {
    navigator.clipboard.writeText(imageUrl);
    message.success('图像URL已复制到剪贴板');
  };

  // 获取平台状态
  const getPlatformStatus = (platform: ImagePlatformType) => {
    const status = platformConnectionStatus[platform];
    return {
      connected: status?.is_connected || false,
      responseTime: status?.response_time,
      error: status?.error_message
    };
  };

  // 渲染平台状态
  const renderPlatformStatus = (platform: ImagePlatformType) => {
    const status = getPlatformStatus(platform);
    return (
      <Badge
        status={status.connected ? 'success' : 'error'}
        text={
          <Space>
            <Text>{platform.toUpperCase()}</Text>
            {status.responseTime && (
              <Text type="secondary">({status.responseTime}ms)</Text>
            )}
          </Space>
        }
      />
    );
  };

  // 渲染基础设置
  const renderBasicSettings = () => (
    <Row gutter={24}>
      <Col span={24}>
        <Form.Item
          name="prompt"
          label="图像描述"
          rules={[
            { required: true, message: '请输入图像描述' },
            { max: 2000, message: '描述长度不能超过2000字符' }
          ]}
        >
          <TextArea
            placeholder="详细描述您想要生成的图像，包括风格、构图、色彩等..."
            rows={6}
            showCount
            maxLength={2000}
            onChange={handlePromptChange}
            style={{ fontFamily: 'PingFang SC, Microsoft YaHei, sans-serif' }}
          />
        </Form.Item>
      </Col>

      <Col span={24}>
        <Form.Item
          name="negative_prompt"
          label="负面提示词"
          tooltip="描述您不希望在图像中出现的元素"
        >
          <TextArea
            placeholder="例如：低质量、模糊、变形、多余的肢体..."
            rows={2}
            maxLength={500}
          />
        </Form.Item>
      </Col>

      <Col span={8}>
        <Form.Item
          name="platform_type"
          label="生成平台"
          rules={[{ required: true, message: '请选择生成平台' }]}
        >
          <Select
            placeholder="选择AI平台"
            onChange={(value) => {
              const numImages = form.getFieldValue(['generation_params', 'num_images']);
              const prompt = form.getFieldValue('prompt');
              calculateEstimatedCost(prompt, value, numImages);
            }}
          >
            <Option value="doubao">
              <Space>
                <span>Doubao</span>
                {renderPlatformStatus('doubao')}
              </Space>
            </Option>
            <Option value="dalle">
              <Space>
                <span>DALL-E</span>
                {renderPlatformStatus('dalle')}
              </Space>
            </Option>
            <Option value="stable_diffusion">
              <Space>
                <span>Stable Diffusion</span>
                {renderPlatformStatus('stable_diffusion')}
              </Space>
            </Option>
            <Option value="midjourney">
              <Space>
                <span>Midjourney</span>
                {renderPlatformStatus('midjourney')}
              </Space>
            </Option>
          </Select>
        </Form.Item>
      </Col>

      <Col span={8}>
        <Form.Item
          name={['generation_params', 'style']}
          label="图像风格"
          rules={[{ required: true, message: '请选择图像风格' }]}
        >
          <Select placeholder="选择风格">
            <Option value="realistic">写实风格</Option>
            <Option value="anime">动漫风格</Option>
            <Option value="cartoon">卡通风格</Option>
            <Option value="oil_painting">油画风格</Option>
            <Option value="watercolor">水彩风格</Option>
            <Option value="sketch">素描风格</Option>
            <Option value="digital_art">数字艺术</Option>
          </Select>
        </Form.Item>
      </Col>

      <Col span={8}>
        <Form.Item
          name={['generation_params', 'aspect_ratio']}
          label="画面比例"
          rules={[{ required: true, message: '请选择画面比例' }]}
        >
          <Select placeholder="选择比例">
            <Option value="1:1">正方形 (1:1)</Option>
            <Option value="16:9">横屏 (16:9)</Option>
            <Option value="9:16">竖屏 (9:16)</Option>
            <Option value="4:3">标准 (4:3)</Option>
            <Option value="3:4">竖版 (3:4)</Option>
            <Option value="2:1">宽屏 (2:1)</Option>
          </Select>
        </Form.Item>
      </Col>

      <Col span={12}>
        <Form.Item
          name={['generation_params', 'quality']}
          label="生成质量"
          rules={[{ required: true, message: '请选择生成质量' }]}
        >
          <Radio.Group>
            <Radio value="draft">草图</Radio>
            <Radio value="standard">标准</Radio>
            <Radio value="high">高质量</Radio>
            <Radio value="ultra">超高质量</Radio>
          </Radio.Group>
        </Form.Item>
      </Col>

      <Col span={12}>
        <Form.Item
          name={['generation_params', 'num_images']}
          label="生成数量"
          rules={[{ required: true, message: '请选择生成数量' }]}
        >
          <Select
            placeholder="选择数量"
            onChange={(value) => {
              const platformType = form.getFieldValue('platform_type');
              const prompt = form.getFieldValue('prompt');
              calculateEstimatedCost(prompt, platformType, value);
            }}
          >
            <Option value={1}>1张</Option>
            <Option value={2}>2张</Option>
            <Option value={3}>3张</Option>
            <Option value={4}>4张</Option>
          </Select>
        </Form.Item>
      </Col>

      <Col span={12}>
        <Form.Item
          name="image_title"
          label="图像标题"
        >
          <Input placeholder="为生成的图像命名" />
        </Form.Item>
      </Col>

      <Col span={12}>
        <Form.Item
          name="save_to_library"
          label="保存到图像库"
          valuePropName="checked"
        >
          <Switch checkedChildren="保存" unCheckedChildren="不保存" />
        </Form.Item>
      </Col>
    </Row>
  );

  // 渲染高级参数设置
  const renderAdvancedSettings = () => (
    <Collapse
      ghost
      expandIconPosition="end"
      onChange={(keys) => setShowAdvancedSettings(keys.length > 0)}
    >
      <Panel header="高级参数设置" key="advanced">
        <Row gutter={24}>
          <Col span={8}>
            <Form.Item
              name={['generation_params', 'steps']}
              label="生成步数"
              tooltip="更多步数通常产生更高质量的图像，但需要更长时间"
            >
              <Slider
                min={10}
                max={100}
                marks={{
                  10: '10',
                  30: '30',
                  50: '50',
                  100: '100'
                }}
              />
            </Form.Item>
          </Col>

          <Col span={8}>
            <Form.Item
              name={['generation_params', 'guidance_scale']}
              label="引导强度"
              tooltip="控制AI对提示词的遵循程度"
            >
              <Slider
                min={1}
                max={20}
                step={0.5}
                marks={{
                  1: '1',
                  7.5: '7.5',
                  15: '15',
                  20: '20'
                }}
              />
            </Form.Item>
          </Col>

          <Col span={8}>
            <Form.Item
              name={['generation_params', 'seed']}
              label="随机种子"
              tooltip="使用相同种子可以生成相似的图像"
            >
              <InputNumber
                placeholder="留空则随机"
                style={{ width: '100%' }}
                min={0}
                max={999999999}
              />
            </Form.Item>
          </Col>

          <Col span={12}>
            <Form.Item
              name={['generation_params', 'content_filter']}
              label="内容过滤"
              tooltip="设置内容安全过滤级别"
            >
              <Select placeholder="选择过滤级别">
                <Option value="strict">严格</Option>
                <Option value="moderate">中等</Option>
                <Option value="permissive">宽松</Option>
              </Select>
            </Form.Item>
          </Col>
        </Row>
      </Panel>
    </Collapse>
  );

  // 渲染参考图像上传
  const renderReferenceUpload = () => (
    <Card size="small" title="参考图像" style={{ marginTop: 16 }}>
      <Row gutter={16}>
        <Col span={12}>
          <Dragger
            multiple
            accept="image/*"
            beforeUpload={handleReferenceUpload}
            showUploadList={false}
            loading={uploadLoading}
          >
            <p className="ant-upload-drag-icon">
              <CloudUploadOutlined />
            </p>
            <p className="ant-upload-text">上传参考图像</p>
            <p className="ant-upload-hint">
              支持JPG、PNG格式，最多5张
            </p>
          </Dragger>
        </Col>
        
        <Col span={12}>
          {referenceImages.length > 0 && (
            <div>
              <Text strong>已上传的参考图像:</Text>
              <div style={{ marginTop: 8 }}>
                {referenceImages.map((url, index) => (
                  <div key={index} style={{ marginBottom: 8 }}>
                    <Image
                      width={80}
                      height={80}
                      src={url}
                      style={{ objectFit: 'cover', borderRadius: 4 }}
                    />
                    <Button
                      type="text"
                      size="small"
                      danger
                      onClick={() => handleRemoveReference(index)}
                      style={{ marginLeft: 8 }}
                    >
                      删除
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </Col>
      </Row>
    </Card>
  );

  // 渲染操作区
  const renderActionArea = () => (
    <Row justify="space-between" align="middle">
      <Col>
        <Space>
          <Badge count={promptWordCount} showZero style={{ backgroundColor: '#52c41a' }}>
            <Text type="secondary">字符数</Text>
          </Badge>
          <Badge count={`¥${estimatedCost.toFixed(3)}`} style={{ backgroundColor: '#1890ff' }}>
            <Text type="secondary">预估成本</Text>
          </Badge>
        </Space>
      </Col>
      
      <Col>
        <Space>
          <Button
            type="primary"
            icon={<ThunderboltOutlined />}
            onClick={handleGenerate}
            loading={generationLoading}
            size="large"
          >
            {generationLoading ? '生成中...' : '开始生成'}
          </Button>
          
          <Button
            icon={<ReloadOutlined />}
            onClick={() => {
              form.resetFields();
              setReferenceImages([]);
              setPreviewImages([]);
              image_service_store_clear_errors();
              setPromptWordCount(0);
              setEstimatedCost(0);
            }}
          >
            重置
          </Button>
        </Space>
      </Col>
    </Row>
  );

  // 渲染生成进度
  const renderGenerationProgress = () => {
    if (!generationLoading) return null;

    return (
      <Card size="small" style={{ marginTop: 16 }}>
        <div style={{ textAlign: 'center' }}>
          <Spin size="large" />
          <div style={{ marginTop: 16 }}>
            <Progress 
              percent={generationProgress} 
              status="active"
              strokeColor="#722ed1"
            />
            <Text>正在生成图像，请稍候...</Text>
          </div>
        </div>
      </Card>
    );
  };

  // 渲染生成结果
  const renderGenerationResult = () => {
    if (!lastGenerationResult || previewImages.length === 0) return null;

    return (
      <Card
        title="生成结果"
        size="small"
        extra={
          <Space>
            <Text type="secondary">
              耗时: {lastGenerationResult.generation_time}ms
            </Text>
            <Tag color="blue">{lastGenerationResult.platform_used.toUpperCase()}</Tag>
          </Space>
        }
        style={{ marginTop: 24 }}
      >
        <Row gutter={16}>
          {previewImages.map((imageUrl, index) => (
            <Col span={6} key={index}>
              <div style={{ position: 'relative', marginBottom: 16 }}>
                <Image
                  width="100%"
                  height={200}
                  src={imageUrl}
                  style={{ objectFit: 'cover', borderRadius: 6 }}
                  preview={{
                    mask: (
                      <Space direction="vertical" align="center">
                        <EyeOutlined style={{ fontSize: 16 }} />
                        <Text style={{ color: 'white', fontSize: 12 }}>预览</Text>
                      </Space>
                    )
                  }}
                />
                
                <div style={{ 
                  position: 'absolute', 
                  top: 8, 
                  right: 8,
                  display: 'flex',
                  gap: 4
                }}>
                  <Button
                    type="primary"
                    size="small"
                    icon={<DownloadOutlined />}
                    onClick={() => handleDownload(imageUrl, index)}
                  />
                  <Button
                    type="default"
                    size="small"
                    icon={<CopyOutlined />}
                    onClick={() => handleCopyUrl(imageUrl)}
                  />
                </div>
              </div>
            </Col>
          ))}
        </Row>

        {/* 生成信息 */}
        <Alert
          message="生成信息"
          description={
            <div>
              <div><Text type="secondary">使用的提示词: </Text>{lastGenerationResult.prompt_used}</div>
              {lastGenerationResult.seed_used && (
                <div><Text type="secondary">随机种子: </Text>{lastGenerationResult.seed_used}</div>
              )}
              {lastGenerationResult.cost_info && (
                <div>
                  <Text type="secondary">消耗积分: </Text>
                  <Text strong>{lastGenerationResult.cost_info.credits_used}</Text>
                  <Text type="secondary"> | 费用: </Text>
                  <Text strong>
                    {lastGenerationResult.cost_info.cost_amount} {lastGenerationResult.cost_info.currency}
                  </Text>
                </div>
              )}
            </div>
          }
          type="info"
          showIcon={false}
          style={{ marginTop: 16 }}
        />

        {/* 安全检查结果 */}
        {lastGenerationResult.safety_results && !lastGenerationResult.safety_results.is_safe && (
          <Alert
            message="内容安全提醒"
            description={`检测到敏感内容类别: ${lastGenerationResult.safety_results.flagged_categories.join(', ')}`}
            type="warning"
            showIcon
            style={{ marginTop: 8 }}
          />
        )}
      </Card>
    );
  };

  return (
    <div className={`image-content-generate ${className || ''}`}>
      <Card
        title={
          <Space>
            <PictureOutlined />
            <span>AI图像生成</span>
            <Badge status="processing" text="创意无限" />
          </Space>
        }
        extra={
          <Space>
            <Text type="secondary">支持多种AI平台</Text>
          </Space>
        }
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            generation_params: {
              style: 'realistic',
              aspect_ratio: '1:1',
              quality: 'high',
              steps: 30,
              guidance_scale: 7.5,
              num_images: 1,
              content_filter: 'moderate'
            },
            platform_type: 'doubao',
            save_to_library: true
          }}
        >
          {/* 基础设置 */}
          {renderBasicSettings()}
          
          <Divider />
          
          {/* 高级设置 */}
          {renderAdvancedSettings()}
          
          {/* 参考图像上传 */}
          {renderReferenceUpload()}
          
          <Divider />
          
          {/* 操作区 */}
          {renderActionArea()}
        </Form>

        {/* 生成进度 */}
        {renderGenerationProgress()}
        
        {/* 生成结果 */}
        {renderGenerationResult()}
      </Card>
    </div>
  );
};

export default ImageContentGenerate;