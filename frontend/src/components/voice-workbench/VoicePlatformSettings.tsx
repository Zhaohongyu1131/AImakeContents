/**
 * Voice Platform Settings Component
 * 语音平台设置组件 - [voice-workbench][platform-settings]
 */

import React, { useState, useEffect } from 'react'
import {
  Card,
  Form,
  Input,
  Switch,
  Button,
  Select,
  Space,
  Typography,
  Alert,
  Row,
  Col,
  Divider,
  InputNumber,
  Tabs,
  Modal,
  message,
  Tooltip,
  Tag,
  List,
  Collapse
} from 'antd'
import {
  SettingOutlined,
  SaveOutlined,
  ReloadOutlined,
  ApiOutlined,
  SecurityScanOutlined,
  InfoCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  EyeInvisibleOutlined,
  EyeOutlined
} from '@ant-design/icons'

const { Option } = Select
const { Text, Title } = Typography
const { TextArea } = Input
const { TabPane } = Tabs
const { Panel } = Collapse

// 平台配置类型定义
interface PlatformConfig {
  type: string
  name: string
  isEnabled: boolean
  priority: number
  costPerMinute: number
  maxDailyRequests: number
  apiConfig: Record<string, any>
  featureSupport: Record<string, boolean>
  limitations: {
    maxTextLength: number
    maxFileSize: number
    supportedFormats: string[]
  }
}

interface VoicePlatformSettingsProps {
  platform: PlatformConfig | null
  onSave: (config: PlatformConfig) => Promise<void>
  onTest: (config: PlatformConfig) => Promise<boolean>
  onClose: () => void
  loading?: boolean
  visible: boolean
}

const VoicePlatformSettings: React.FC<VoicePlatformSettingsProps> = ({
  platform,
  onSave,
  onTest,
  onClose,
  loading = false,
  visible
}) => {
  const [form] = Form.useForm()
  const [testLoading, setTestLoading] = useState(false)
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null)
  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({})
  const [activeTab, setActiveTab] = useState('basic')

  useEffect(() => {
    if (platform && visible) {
      form.setFieldsValue({
        ...platform,
        ...platform.apiConfig,
        features: platform.featureSupport
      })
      setTestResult(null)
    }
  }, [platform, visible, form])

  // 测试平台连接
  const handleTest = async () => {
    try {
      setTestLoading(true)
      const values = await form.validateFields()
      
      const testConfig: PlatformConfig = {
        ...platform!,
        ...values,
        apiConfig: {
          ...platform!.apiConfig,
          ...values
        },
        featureSupport: values.features || platform!.featureSupport
      }

      const success = await onTest(testConfig)
      setTestResult({
        success,
        message: success ? '连接测试成功' : '连接测试失败，请检查配置'
      })
    } catch (error) {
      setTestResult({
        success: false,
        message: '配置验证失败，请检查必填项'
      })
    } finally {
      setTestLoading(false)
    }
  }

  // 保存配置
  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      
      const updatedConfig: PlatformConfig = {
        ...platform!,
        ...values,
        apiConfig: {
          ...platform!.apiConfig,
          ...values
        },
        featureSupport: values.features || platform!.featureSupport
      }

      await onSave(updatedConfig)
      message.success('配置保存成功')
      onClose()
    } catch (error) {
      message.error('配置保存失败')
    }
  }

  // 重置配置
  const handleReset = () => {
    Modal.confirm({
      title: '确认重置',
      content: '是否重置为默认配置？此操作不可恢复。',
      onOk: () => {
        if (platform) {
          form.setFieldsValue({
            ...platform,
            ...platform.apiConfig,
            features: platform.featureSupport
          })
        }
        setTestResult(null)
        message.info('配置已重置')
      }
    })
  }

  // 切换密钥显示
  const toggleSecretVisibility = (fieldName: string) => {
    setShowSecrets(prev => ({
      ...prev,
      [fieldName]: !prev[fieldName]
    }))
  }

  // 渲染基础设置
  const renderBasicSettings = () => (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Row gutter={24}>
        <Col span={12}>
          <Form.Item
            name="isEnabled"
            label="启用状态"
            valuePropName="checked"
          >
            <Switch checkedChildren="启用" unCheckedChildren="禁用" />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item
            name="priority"
            label="优先级"
            rules={[{ required: true, message: '请输入优先级' }]}
          >
            <InputNumber
              min={1}
              max={10}
              placeholder="数字越小优先级越高"
              style={{ width: '100%' }}
            />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={24}>
        <Col span={12}>
          <Form.Item
            name="costPerMinute"
            label="每分钟费用"
            rules={[{ required: true, message: '请输入费用' }]}
          >
            <InputNumber
              min={0}
              step={0.001}
              precision={3}
              addonBefore="¥"
              placeholder="0.001"
              style={{ width: '100%' }}
            />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item
            name="maxDailyRequests"
            label="每日最大请求数"
            rules={[{ required: true, message: '请输入最大请求数' }]}
          >
            <InputNumber
              min={1}
              placeholder="10000"
              style={{ width: '100%' }}
            />
          </Form.Item>
        </Col>
      </Row>
    </Space>
  )

  // 渲染API配置
  const renderApiConfig = () => {
    if (!platform) return null

    const renderField = (key: string, value: any, isSecret = false) => {
      const fieldName = key
      const isSecretField = isSecret || key.toLowerCase().includes('key') || 
                           key.toLowerCase().includes('token') || 
                           key.toLowerCase().includes('secret')

      return (
        <Form.Item
          key={key}
          name={key}
          label={key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
          rules={[{ required: true, message: `请输入${key}` }]}
        >
          {isSecretField ? (
            <Input
              type={showSecrets[fieldName] ? 'text' : 'password'}
              placeholder={`请输入${key}`}
              addonAfter={
                <Button
                  type="text"
                  size="small"
                  icon={showSecrets[fieldName] ? <EyeInvisibleOutlined /> : <EyeOutlined />}
                  onClick={() => toggleSecretVisibility(fieldName)}
                />
              }
            />
          ) : (
            <Input placeholder={`请输入${key}`} />
          )}
        </Form.Item>
      )
    }

    const apiFields = Object.entries(platform.apiConfig)

    return (
      <Space direction="vertical" style={{ width: '100%' }}>
        {platform.type === 'volcano' && (
          <>
            {renderField('appid', platform.apiConfig.appid)}
            {renderField('access_token', platform.apiConfig.access_token, true)}
            <Form.Item
              name="cluster"
              label="集群配置"
              rules={[{ required: true, message: '请选择集群' }]}
            >
              <Select placeholder="选择集群">
                <Option value="volcano_icl">标准集群 (volcano_icl)</Option>
                <Option value="volcano_icl_concurr">并发集群 (volcano_icl_concurr)</Option>
              </Select>
            </Form.Item>
            {renderField('base_url', platform.apiConfig.base_url)}
          </>
        )}

        {platform.type === 'azure' && (
          <>
            {renderField('subscription_key', platform.apiConfig.subscription_key, true)}
            <Form.Item
              name="region"
              label="区域"
              rules={[{ required: true, message: '请选择区域' }]}
            >
              <Select placeholder="选择Azure区域">
                <Option value="eastus">East US</Option>
                <Option value="westus">West US</Option>
                <Option value="eastasia">East Asia</Option>
                <Option value="southeastasia">Southeast Asia</Option>
                <Option value="westeurope">West Europe</Option>
              </Select>
            </Form.Item>
            {renderField('resource_name', platform.apiConfig.resource_name)}
            {renderField('base_url', platform.apiConfig.base_url)}
          </>
        )}

        {platform.type === 'openai' && (
          <>
            {renderField('api_key', platform.apiConfig.api_key, true)}
            {renderField('base_url', platform.apiConfig.base_url)}
            <Form.Item
              name="model"
              label="默认模型"
              rules={[{ required: true, message: '请选择模型' }]}
            >
              <Select placeholder="选择OpenAI模型">
                <Option value="tts-1">TTS-1 (标准质量)</Option>
                <Option value="tts-1-hd">TTS-1-HD (高清质量)</Option>
              </Select>
            </Form.Item>
            <Form.Item name="organization" label="组织ID (可选)">
              <Input placeholder="请输入组织ID (可选)" />
            </Form.Item>
          </>
        )}
      </Space>
    )
  }

  // 渲染功能设置
  const renderFeatureSettings = () => {
    if (!platform) return null

    const features = [
      { key: 'voice_clone', label: '音色克隆', description: '支持自定义音色训练' },
      { key: 'tts_synthesis', label: '语音合成', description: '基本文本转语音功能' },
      { key: 'stream_tts', label: '流式合成', description: '实时流式语音输出' },
      { key: 'ssml_support', label: 'SSML支持', description: '支持语音合成标记语言' },
      { key: 'custom_voice', label: '自定义音色', description: '支持用户自定义音色' },
      { key: 'batch_processing', label: '批量处理', description: '支持批量文本处理' }
    ]

    return (
      <Space direction="vertical" style={{ width: '100%' }}>
        <Alert
          message="功能配置"
          description="启用或禁用平台支持的功能特性"
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />
        
        <List
          dataSource={features}
          renderItem={feature => (
            <List.Item>
              <List.Item.Meta
                title={
                  <Space>
                    <Form.Item
                      name={['features', feature.key]}
                      valuePropName="checked"
                      style={{ margin: 0 }}
                    >
                      <Switch size="small" />
                    </Form.Item>
                    <span>{feature.label}</span>
                  </Space>
                }
                description={feature.description}
              />
            </List.Item>
          )}
        />
      </Space>
    )
  }

  // 渲染限制设置
  const renderLimitations = () => (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Row gutter={24}>
        <Col span={12}>
          <Form.Item
            name={['limitations', 'maxTextLength']}
            label="最大文本长度"
            rules={[{ required: true, message: '请输入最大文本长度' }]}
          >
            <InputNumber
              min={1}
              max={10000}
              addonAfter="字符"
              style={{ width: '100%' }}
            />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item
            name={['limitations', 'maxFileSize']}
            label="最大文件大小"
            rules={[{ required: true, message: '请输入最大文件大小' }]}
          >
            <InputNumber
              min={1}
              max={100}
              addonAfter="MB"
              style={{ width: '100%' }}
            />
          </Form.Item>
        </Col>
      </Row>

      <Form.Item
        name={['limitations', 'supportedFormats']}
        label="支持格式"
        rules={[{ required: true, message: '请选择支持的格式' }]}
      >
        <Select
          mode="multiple"
          placeholder="选择支持的音频格式"
          style={{ width: '100%' }}
        >
          <Option value="mp3">MP3</Option>
          <Option value="wav">WAV</Option>
          <Option value="ogg">OGG</Option>
          <Option value="flac">FLAC</Option>
          <Option value="aac">AAC</Option>
          <Option value="opus">OPUS</Option>
        </Select>
      </Form.Item>
    </Space>
  )

  if (!platform) return null

  return (
    <Modal
      title={
        <Space>
          <SettingOutlined />
          <span>{platform.name} 平台设置</span>
          <Tag color="blue">{platform.type}</Tag>
        </Space>
      }
      open={visible}
      onCancel={onClose}
      width={800}
      footer={[
        <Button key="reset" onClick={handleReset}>
          <ReloadOutlined /> 重置
        </Button>,
        <Button
          key="test"
          loading={testLoading}
          onClick={handleTest}
          icon={<ApiOutlined />}
        >
          测试连接
        </Button>,
        <Button key="cancel" onClick={onClose}>
          取消
        </Button>,
        <Button
          key="save"
          type="primary"
          loading={loading}
          onClick={handleSave}
          icon={<SaveOutlined />}
        >
          保存配置
        </Button>
      ]}
    >
      <Form form={form} layout="vertical">
        {/* 测试结果显示 */}
        {testResult && (
          <Alert
            message={testResult.success ? '连接成功' : '连接失败'}
            description={testResult.message}
            type={testResult.success ? 'success' : 'error'}
            showIcon
            icon={testResult.success ? <CheckCircleOutlined /> : <ExclamationCircleOutlined />}
            style={{ marginBottom: 16 }}
            closable
          />
        )}

        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane tab="基础设置" key="basic">
            {renderBasicSettings()}
          </TabPane>
          
          <TabPane tab="API配置" key="api">
            {renderApiConfig()}
          </TabPane>
          
          <TabPane tab="功能特性" key="features">
            {renderFeatureSettings()}
          </TabPane>
          
          <TabPane tab="限制设置" key="limitations">
            {renderLimitations()}
          </TabPane>
        </Tabs>

        {/* 安全提示 */}
        <Alert
          message="安全提示"
          description="API密钥等敏感信息将被加密存储。建议定期更换密钥以确保安全。"
          type="warning"
          showIcon
          icon={<SecurityScanOutlined />}
          style={{ marginTop: 16 }}
        />
      </Form>
    </Modal>
  )
}

export default VoicePlatformSettings