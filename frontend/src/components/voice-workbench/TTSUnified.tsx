/**
 * Unified TTS Component
 * 统一语音合成组件 - [voice-workbench][tts-unified]
 */

import React, { useState, useRef } from 'react'
import {
  Card,
  Form,
  Input,
  Button,
  Select,
  Radio,
  Slider,
  Typography,
  Space,
  Alert,
  Row,
  Col,
  Collapse,
  Progress,
  message,
  Divider,
  Upload,
  Tooltip
} from 'antd'
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  DownloadOutlined,
  DeleteOutlined,
  SoundOutlined,
  UploadOutlined,
  SettingOutlined,
  InfoCircleOutlined
} from '@ant-design/icons'

const { TextArea } = Input
const { Option } = Select
const { Text, Title } = Typography
const { Panel } = Collapse

// 平台相关类型定义
interface VoicePlatform {
  type: string
  name: string
  description: string
  isEnabled: boolean
  features: string[]
  voiceModels: VoiceModel[]
  limitations: {
    maxTextLength: number
    maxFileSize: number
    supportedFormats: string[]
  }
}

interface VoiceModel {
  id: string
  name: string
  description: string
  language: string
  gender: 'male' | 'female' | 'neutral'
  category: 'standard' | 'premium' | 'neural' | 'custom'
  isCustom?: boolean
}

interface TTSRequest {
  text: string
  voiceModel: string
  speed: number
  pitch: number
  volume: number
  outputFormat: string
  emotion?: string
  style?: string
  enableSSML: boolean
  customParameters?: Record<string, any>
}

interface TTSUnifiedProps {
  selectedPlatform: VoicePlatform | null
  platforms: VoicePlatform[]
  onSubmit: (request: TTSRequest) => Promise<void>
  loading: boolean
  className?: string
}

const TTSUnified: React.FC<TTSUnifiedProps> = ({
  selectedPlatform,
  platforms,
  onSubmit,
  loading,
  className
}) => {
  const [form] = Form.useForm()
  const [isPlaying, setIsPlaying] = useState(false)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [progress, setProgress] = useState(0)
  const [selectedVoice, setSelectedVoice] = useState<VoiceModel | null>(null)
  const [enableAdvanced, setEnableAdvanced] = useState(false)
  const [textLength, setTextLength] = useState(0)
  const audioRef = useRef<HTMLAudioElement>(null)

  // 获取当前平台配置
  const currentPlatform = selectedPlatform || platforms.find(p => p.isEnabled)

  // 获取可用音色
  const getAvailableVoices = (): VoiceModel[] => {
    if (!currentPlatform) return []
    return currentPlatform.voiceModels || []
  }

  // 按分类分组音色
  const getVoicesByCategory = () => {
    const voices = getAvailableVoices()
    return voices.reduce((acc, voice) => {
      if (!acc[voice.category]) {
        acc[voice.category] = []
      }
      acc[voice.category].push(voice)
      return acc
    }, {} as Record<string, VoiceModel[]>)
  }

  // 处理文本变化
  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const text = e.target.value
    setTextLength(text.length)
    
    // 检查文本长度限制
    if (currentPlatform && text.length > currentPlatform.limitations.maxTextLength) {
      message.warning(`文本长度超出限制（最大${currentPlatform.limitations.maxTextLength}字符）`)
    }
  }

  // 处理音色选择
  const handleVoiceSelect = (voiceId: string) => {
    const voice = getAvailableVoices().find(v => v.id === voiceId)
    setSelectedVoice(voice || null)
  }

  // 播放/暂停音频
  const togglePlayback = () => {
    if (!audioRef.current || !audioUrl) return

    if (isPlaying) {
      audioRef.current.pause()
    } else {
      audioRef.current.play()
    }
    setIsPlaying(!isPlaying)
  }

  // 下载音频
  const downloadAudio = () => {
    if (!audioUrl) return

    const link = document.createElement('a')
    link.href = audioUrl
    link.download = `tts_output_${Date.now()}.mp3`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  // 提交TTS请求
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      
      const request: TTSRequest = {
        text: values.text,
        voiceModel: values.voiceModel,
        speed: values.speed || 1.0,
        pitch: values.pitch || 1.0,
        volume: values.volume || 1.0,
        outputFormat: values.outputFormat || 'mp3',
        emotion: values.emotion,
        style: values.style,
        enableSSML: values.enableSSML || false,
        customParameters: enableAdvanced ? values.customParameters : undefined
      }

      await onSubmit(request)
      message.success('语音合成请求已提交')
    } catch (error) {
      console.error('TTS request failed:', error)
      message.error('语音合成失败，请重试')
    }
  }

  // 平台特定的表单项
  const renderPlatformSpecificFields = () => {
    if (!currentPlatform) return null

    switch (currentPlatform.type) {
      case 'volcano':
        return (
          <>
            <Form.Item name="emotion" label="情感风格">
              <Select placeholder="选择情感风格（可选）" allowClear>
                <Option value="neutral">自然</Option>
                <Option value="happy">开心</Option>
                <Option value="sad">悲伤</Option>
                <Option value="angry">愤怒</Option>
                <Option value="gentle">温柔</Option>
              </Select>
            </Form.Item>
            <Form.Item name="style" label="语音风格">
              <Select placeholder="选择语音风格（可选）" allowClear>
                <Option value="news">新闻播报</Option>
                <Option value="story">故事讲述</Option>
                <Option value="customer_service">客服</Option>
                <Option value="assistant">助手</Option>
              </Select>
            </Form.Item>
          </>
        )
      
      case 'azure':
        return (
          <>
            <Form.Item name="style" label="语音风格">
              <Select placeholder="选择语音风格（可选）" allowClear>
                <Option value="newscast">新闻播报</Option>
                <Option value="customerservice">客服</Option>
                <Option value="assistant">助手</Option>
                <Option value="chat">聊天</Option>
                <Option value="cheerful">愉快</Option>
                <Option value="empathetic">同理心</Option>
              </Select>
            </Form.Item>
            <Form.Item name="role" label="角色扮演">
              <Select placeholder="选择角色（可选）" allowClear>
                <Option value="narrator">旁白</Option>
                <Option value="youngadultfemale">年轻女性</Option>
                <Option value="youngadultmale">年轻男性</Option>
                <Option value="olderadultfemale">成熟女性</Option>
                <Option value="olderadultmale">成熟男性</Option>
              </Select>
            </Form.Item>
          </>
        )

      case 'openai':
        return (
          <Alert
            message="OpenAI TTS"
            description="OpenAI的TTS服务提供高质量的语音合成，支持多种内置音色。"
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
          />
        )

      default:
        return null
    }
  }

  if (!currentPlatform) {
    return (
      <Card className={className}>
        <Alert
          message="无可用平台"
          description="请先配置并启用至少一个语音平台"
          type="warning"
          showIcon
        />
      </Card>
    )
  }

  const voicesByCategory = getVoicesByCategory()

  return (
    <Card 
      title={
        <Space>
          <SoundOutlined />
          <span>文本转语音</span>
          <Text type="secondary">({currentPlatform.name})</Text>
        </Space>
      }
      className={className}
      extra={
        <Space>
          <Tooltip title="平台信息">
            <Button icon={<InfoCircleOutlined />} size="small" />
          </Tooltip>
          <Tooltip title="高级设置">
            <Button 
              icon={<SettingOutlined />} 
              size="small"
              type={enableAdvanced ? 'primary' : 'default'}
              onClick={() => setEnableAdvanced(!enableAdvanced)}
            />
          </Tooltip>
        </Space>
      }
    >
      <Form form={form} layout="vertical" onFinish={handleSubmit}>
        {/* 文本输入区域 */}
        <Form.Item
          name="text"
          label={
            <Space>
              <span>合成文本</span>
              <Text type="secondary">
                ({textLength}/{currentPlatform.limitations.maxTextLength})
              </Text>
            </Space>
          }
          rules={[
            { required: true, message: '请输入要合成的文本' },
            { 
              max: currentPlatform.limitations.maxTextLength, 
              message: `文本长度不能超过${currentPlatform.limitations.maxTextLength}字符` 
            }
          ]}
        >
          <TextArea
            rows={4}
            placeholder="请输入要转换为语音的文本内容..."
            onChange={handleTextChange}
            showCount
            maxLength={currentPlatform.limitations.maxTextLength}
          />
        </Form.Item>

        {/* 音色选择 */}
        <Form.Item
          name="voiceModel"
          label="选择音色"
          rules={[{ required: true, message: '请选择音色' }]}
        >
          <Select
            placeholder="请选择音色"
            onChange={handleVoiceSelect}
            optionLabelProp="label"
            size="large"
          >
            {Object.entries(voicesByCategory).map(([category, voices]) => (
              <Select.OptGroup key={category} label={category}>
                {voices.map(voice => (
                  <Option 
                    key={voice.id} 
                    value={voice.id}
                    label={voice.name}
                  >
                    <Space direction="vertical" size="small">
                      <Text strong>{voice.name}</Text>
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        {voice.language} • {voice.gender} • {voice.description}
                      </Text>
                    </Space>
                  </Option>
                ))}
              </Select.OptGroup>
            ))}
          </Select>
        </Form.Item>

        {/* 基础参数调节 */}
        <Row gutter={16}>
          <Col span={8}>
            <Form.Item name="speed" label="语速" initialValue={1.0}>
              <Slider
                min={0.5}
                max={2.0}
                step={0.1}
                marks={{
                  0.5: '慢',
                  1.0: '正常',
                  2.0: '快'
                }}
              />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item name="pitch" label="音调" initialValue={1.0}>
              <Slider
                min={0.5}
                max={2.0}
                step={0.1}
                marks={{
                  0.5: '低',
                  1.0: '正常',
                  2.0: '高'
                }}
              />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item name="volume" label="音量" initialValue={1.0}>
              <Slider
                min={0.1}
                max={2.0}
                step={0.1}
                marks={{
                  0.1: '小',
                  1.0: '正常',
                  2.0: '大'
                }}
              />
            </Form.Item>
          </Col>
        </Row>

        {/* 输出格式 */}
        <Form.Item name="outputFormat" label="输出格式" initialValue="mp3">
          <Radio.Group>
            {currentPlatform.limitations.supportedFormats.map(format => (
              <Radio.Button key={format} value={format}>
                {format.toUpperCase()}
              </Radio.Button>
            ))}
          </Radio.Group>
        </Form.Item>

        {/* 平台特定字段 */}
        {renderPlatformSpecificFields()}

        {/* 高级设置 */}
        {enableAdvanced && (
          <Collapse ghost>
            <Panel header="高级设置" key="advanced">
              <Form.Item name="enableSSML" valuePropName="checked">
                <Radio.Group>
                  <Radio value={false}>纯文本</Radio>
                  <Radio value={true}>SSML标记</Radio>
                </Radio.Group>
              </Form.Item>
              
              {currentPlatform.type === 'volcano' && (
                <>
                  <Form.Item name="cluster" label="集群选择" initialValue="volcano_icl">
                    <Select>
                      <Option value="volcano_icl">标准集群</Option>
                      <Option value="volcano_icl_concurr">并发集群</Option>
                    </Select>
                  </Form.Item>
                  <Form.Item name="enableCache" valuePropName="checked">
                    <Radio.Group>
                      <Radio value={false}>禁用缓存</Radio>
                      <Radio value={true}>启用缓存</Radio>
                    </Radio.Group>
                  </Form.Item>
                </>
              )}
            </Panel>
          </Collapse>
        )}

        {/* 操作按钮 */}
        <Form.Item>
          <Space>
            <Button
              type="primary"
              size="large"
              loading={loading}
              onClick={handleSubmit}
              icon={<SoundOutlined />}
            >
              开始合成
            </Button>
            
            {audioUrl && (
              <>
                <Button
                  size="large"
                  icon={isPlaying ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
                  onClick={togglePlayback}
                >
                  {isPlaying ? '暂停' : '播放'}
                </Button>
                
                <Button
                  size="large"
                  icon={<DownloadOutlined />}
                  onClick={downloadAudio}
                >
                  下载
                </Button>
                
                <Button
                  size="large"
                  icon={<DeleteOutlined />}
                  onClick={() => {
                    setAudioUrl(null)
                    setIsPlaying(false)
                    setProgress(0)
                  }}
                >
                  清除
                </Button>
              </>
            )}
          </Space>
        </Form.Item>

        {/* 进度条 */}
        {loading && (
          <Progress
            percent={progress}
            status="active"
            strokeColor={{
              from: '#108ee9',
              to: '#87d068',
            }}
          />
        )}

        {/* 音频播放器 */}
        {audioUrl && (
          <audio
            ref={audioRef}
            src={audioUrl}
            onEnded={() => setIsPlaying(false)}
            onTimeUpdate={(e) => {
              const audio = e.target as HTMLAudioElement
              const progress = (audio.currentTime / audio.duration) * 100
              setProgress(progress)
            }}
            style={{ display: 'none' }}
          />
        )}

        {/* 选中音色信息 */}
        {selectedVoice && (
          <Alert
            message={`当前音色: ${selectedVoice.name}`}
            description={`${selectedVoice.description} | ${selectedVoice.language} | ${selectedVoice.gender}`}
            type="info"
            showIcon
            style={{ marginTop: 16 }}
          />
        )}
      </Form>
    </Card>
  )
}

export default TTSUnified