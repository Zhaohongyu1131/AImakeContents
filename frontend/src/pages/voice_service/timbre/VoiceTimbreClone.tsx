/**
 * Voice Timbre Clone Component
 * 音色克隆组件 - [Voice][Timbre][Clone]
 */

import React, { useState, useRef, useEffect } from 'react'
import {
  Card,
  Steps,
  Form,
  Input,
  Upload,
  Button,
  Progress,
  Alert,
  Typography,
  Row,
  Col,
  Space,
  Divider,
  Radio,
  Slider,
  Switch,
  message,
  Modal,
  Table,
  Tag,
  Tooltip,
  Timeline,
  Statistic,
  Result,
  Spin
} from 'antd'
import {
  UploadOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  SoundOutlined,
  RobotOutlined,
  CheckCircleOutlined,
  LoadingOutlined,
  ExclamationCircleOutlined,
  ReloadOutlined,
  DownloadOutlined,
  EyeOutlined,
  DeleteOutlined,
  AudioOutlined,
  ThunderboltOutlined,
  SettingOutlined,
  BulbOutlined
} from '@ant-design/icons'

const { Title, Paragraph, Text } = Typography
const { TextArea } = Input
const { Step } = Steps

interface AudioClip {
  id: string
  file: File
  name: string
  duration: number
  size: number
  url: string
  quality: number
  signal_to_noise: number
  voice_clarity: number
  isValid: boolean
  issues: string[]
}

interface CloneTask {
  id: string
  name: string
  status: 'pending' | 'processing' | 'training' | 'completed' | 'failed'
  progress: number
  audio_clips: AudioClip[]
  created_at: string
  estimated_completion: string
  quality_score: number
  similarity_score: number
  error_message?: string
}

interface CloneConfig {
  name: string
  description: string
  gender: 'male' | 'female' | 'auto'
  language: string
  style: string
  emotion: string
  quality_level: 'standard' | 'high' | 'ultra'
  training_iterations: number
  data_augmentation: boolean
  noise_reduction: boolean
  pitch_stabilization: boolean
  speed_normalization: boolean
}

const VoiceTimbreClone: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0)
  const [form] = Form.useForm()
  const [audioClips, setAudioClips] = useState<AudioClip[]>([])
  const [cloneConfig, setCloneConfig] = useState<CloneConfig | null>(null)
  const [cloneTask, setCloneTask] = useState<CloneTask | null>(null)
  const [uploading, setUploading] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [training, setTraining] = useState(false)
  const [playingId, setPlayingId] = useState<string | null>(null)
  const [analysisResults, setAnalysisResults] = useState<any>(null)
  const [previewVisible, setPreviewVisible] = useState(false)
  const [selectedClip, setSelectedClip] = useState<AudioClip | null>(null)
  const audioRef = useRef<HTMLAudioElement>(null)

  const qualityLevels = [
    { label: '标准', value: 'standard', description: '适合一般用途，快速生成' },
    { label: '高质量', value: 'high', description: '平衡质量和速度，推荐选择' },
    { label: '超高质量', value: 'ultra', description: '最佳质量，训练时间较长' }
  ]

  const languageOptions = [
    { label: '中文（普通话）', value: 'zh-CN' },
    { label: '中文（粤语）', value: 'zh-HK' },
    { label: '英语（美式）', value: 'en-US' },
    { label: '英语（英式）', value: 'en-GB' },
    { label: '日语', value: 'ja-JP' }
  ]

  const styleOptions = [
    { label: '自然', value: 'natural' },
    { label: '正式', value: 'formal' },
    { label: '随意', value: 'casual' },
    { label: '新闻播报', value: 'news' },
    { label: '故事讲述', value: 'storytelling' }
  ]

  const emotionOptions = [
    { label: '中性', value: 'neutral' },
    { label: '愉快', value: 'happy' },
    { label: '平静', value: 'calm' },
    { label: '严肃', value: 'serious' }
  ]

  useEffect(() => {
    if (cloneTask && cloneTask.status === 'processing') {
      // 模拟训练进度更新
      const interval = setInterval(() => {
        setCloneTask(prev => {
          if (!prev || prev.status !== 'processing') return prev
          
          const newProgress = Math.min(prev.progress + Math.random() * 5, 100)
          
          if (newProgress >= 100) {
            return {
              ...prev,
              status: 'completed',
              progress: 100,
              quality_score: 92,
              similarity_score: 89
            }
          }
          
          return {
            ...prev,
            progress: newProgress
          }
        })
      }, 1000)

      return () => clearInterval(interval)
    }
  }, [cloneTask?.status])

  const handleAudioUpload = async (file: File) => {
    if (audioClips.length >= 10) {
      message.error('最多只能上传10个音频文件')
      return false
    }

    setUploading(true)

    try {
      const audioUrl = URL.createObjectURL(file)
      const audio = new Audio(audioUrl)
      
      await new Promise((resolve, reject) => {
        audio.addEventListener('loadedmetadata', resolve)
        audio.addEventListener('error', reject)
      })

      // 模拟音频质量分析
      const quality = Math.random() * 40 + 60 // 60-100
      const signalToNoise = Math.random() * 20 + 20 // 20-40 dB
      const voiceClarity = Math.random() * 30 + 70 // 70-100

      const issues: string[] = []
      if (audio.duration < 5) issues.push('音频时长过短，建议至少5秒')
      if (audio.duration > 60) issues.push('音频时长过长，建议不超过60秒')
      if (quality < 70) issues.push('音频质量偏低')
      if (signalToNoise < 25) issues.push('背景噪音过大')

      const newClip: AudioClip = {
        id: Date.now().toString(),
        file,
        name: file.name,
        duration: audio.duration,
        size: file.size,
        url: audioUrl,
        quality,
        signal_to_noise: signalToNoise,
        voice_clarity: voiceClarity,
        isValid: issues.length === 0,
        issues
      }
      
      setAudioClips(prev => [...prev, newClip])
      
      if (issues.length === 0) {
        message.success('音频文件上传成功，质量良好')
      } else {
        message.warning('音频文件上传成功，但存在一些质量问题')
      }

    } catch (error) {
      message.error('音频文件处理失败')
      console.error('Audio processing error:', error)
    } finally {
      setUploading(false)
    }

    return false
  }

  const handleRemoveAudio = (clipId: string) => {
    setAudioClips(prev => {
      const clip = prev.find(c => c.id === clipId)
      if (clip) {
        URL.revokeObjectURL(clip.url)
      }
      return prev.filter(c => c.id !== clipId)
    })
  }

  const handlePlayAudio = (clipId: string) => {
    const clip = audioClips.find(c => c.id === clipId)
    if (!clip) return

    if (playingId === clipId) {
      audioRef.current?.pause()
      setPlayingId(null)
    } else {
      if (audioRef.current) {
        audioRef.current.src = clip.url
        audioRef.current.play()
      }
      setPlayingId(clipId)
    }
  }

  const handlePreview = (clip: AudioClip) => {
    setSelectedClip(clip)
    setPreviewVisible(true)
  }

  const handleAnalyzeAudio = async () => {
    if (audioClips.length === 0) {
      message.error('请先上传音频文件')
      return
    }

    setAnalyzing(true)
    
    try {
      // 模拟音频分析
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      const validClips = audioClips.filter(clip => clip.isValid)
      const totalDuration = audioClips.reduce((sum, clip) => sum + clip.duration, 0)
      const avgQuality = audioClips.reduce((sum, clip) => sum + clip.quality, 0) / audioClips.length
      
      const results = {
        total_clips: audioClips.length,
        valid_clips: validClips.length,
        total_duration: totalDuration,
        average_quality: avgQuality,
        recommended_quality: avgQuality >= 80 ? 'ultra' : avgQuality >= 70 ? 'high' : 'standard',
        estimated_training_time: Math.ceil(totalDuration / 10) * (avgQuality >= 80 ? 3 : avgQuality >= 70 ? 2 : 1),
        success_probability: Math.min(validClips.length * 15 + avgQuality / 2, 95)
      }
      
      setAnalysisResults(results)
      
      if (validClips.length >= 3) {
        message.success('音频分析完成，数据质量良好，可以开始训练')
        setCurrentStep(1)
      } else {
        message.warning('建议上传更多高质量的音频文件以获得更好的克隆效果')
      }
      
    } catch (error) {
      message.error('音频分析失败')
      console.error('Audio analysis error:', error)
    } finally {
      setAnalyzing(false)
    }
  }

  const handleConfigSubmit = async (values: CloneConfig) => {
    setCloneConfig(values)
    setCurrentStep(2)
  }

  const handleStartTraining = async () => {
    if (!cloneConfig || audioClips.length === 0) {
      message.error('配置信息或音频文件缺失')
      return
    }

    setTraining(true)
    
    try {
      // 创建克隆任务
      const newTask: CloneTask = {
        id: Date.now().toString(),
        name: cloneConfig.name,
        status: 'processing',
        progress: 0,
        audio_clips: audioClips,
        created_at: new Date().toISOString(),
        estimated_completion: new Date(Date.now() + analysisResults.estimated_training_time * 60 * 1000).toISOString(),
        quality_score: 0,
        similarity_score: 0
      }
      
      setCloneTask(newTask)
      setCurrentStep(3)
      
      message.success('开始训练音色模型，请耐心等待...')
      
    } catch (error) {
      message.error('启动训练失败')
      console.error('Training start error:', error)
    } finally {
      setTraining(false)
    }
  }

  const handleRestart = () => {
    setCurrentStep(0)
    setAudioClips([])
    setCloneConfig(null)
    setCloneTask(null)
    setAnalysisResults(null)
    form.resetFields()
    message.info('已重置，可以重新开始')
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const getQualityColor = (quality: number) => {
    if (quality >= 85) return '#52c41a'
    if (quality >= 70) return '#faad14'
    return '#ff4d4f'
  }

  const audioColumns = [
    {
      title: '文件名',
      dataIndex: 'name',
      key: 'name',
      ellipsis: true
    },
    {
      title: '时长',
      dataIndex: 'duration',
      key: 'duration',
      render: (duration: number) => formatDuration(duration)
    },
    {
      title: '大小',
      dataIndex: 'size',
      key: 'size',
      render: (size: number) => formatFileSize(size)
    },
    {
      title: '质量',
      dataIndex: 'quality',
      key: 'quality',
      render: (quality: number) => (
        <div>
          <Progress
            percent={quality}
            size="small"
            strokeColor={getQualityColor(quality)}
            showInfo={false}
            style={{ width: 60 }}
          />
          <Text style={{ marginLeft: 8, color: getQualityColor(quality) }}>
            {quality.toFixed(0)}
          </Text>
        </div>
      )
    },
    {
      title: '状态',
      dataIndex: 'isValid',
      key: 'status',
      render: (isValid: boolean, record: AudioClip) => (
        <div>
          {isValid ? (
            <Tag color="green">良好</Tag>
          ) : (
            <Tooltip title={record.issues.join(', ')}>
              <Tag color="orange">需优化</Tag>
            </Tooltip>
          )}
        </div>
      )
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: any, record: AudioClip) => (
        <Space>
          <Button
            type="text"
            icon={playingId === record.id ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
            onClick={() => handlePlayAudio(record.id)}
          />
          <Button
            type="text"
            icon={<EyeOutlined />}
            onClick={() => handlePreview(record)}
          />
          <Button
            type="text"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleRemoveAudio(record.id)}
          />
        </Space>
      )
    }
  ]

  const steps = [
    {
      title: '上传音频',
      icon: <UploadOutlined />,
      description: '上传高质量的语音样本'
    },
    {
      title: '配置参数',
      icon: <SettingOutlined />,
      description: '设置音色克隆参数'
    },
    {
      title: '开始训练',
      icon: <RobotOutlined />,
      description: '启动AI训练过程'
    },
    {
      title: '完成克隆',
      icon: <CheckCircleOutlined />,
      description: '获取克隆后的音色'
    }
  ]

  return (
    <div className="voice-timbre-clone">
      <Card>
        <Title level={2}>
          <ThunderboltOutlined /> 音色克隆
        </Title>
        <Paragraph>
          使用先进的AI技术克隆语音，只需几分钟的音频样本就能生成高质量的个性化音色。
        </Paragraph>

        <Alert
          message="克隆须知"
          description="为了获得最佳克隆效果，请上传清晰、无噪音的语音文件，每个文件时长建议5-30秒，总时长不少于2分钟。"
          type="info"
          showIcon
          closable
          style={{ marginBottom: 24 }}
        />

        <Steps current={currentStep} style={{ marginBottom: 24 }}>
          {steps.map((step, index) => (
            <Step
              key={index}
              title={step.title}
              description={step.description}
              icon={step.icon}
            />
          ))}
        </Steps>

        {/* 第一步：上传音频 */}
        {currentStep === 0 && (
          <Card title="第一步：上传音频样本" size="small">
            <Row gutter={24}>
              <Col xs={24} lg={16}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Upload
                    beforeUpload={handleAudioUpload}
                    showUploadList={false}
                    accept=".mp3,.wav,.m4a,.flac"
                    disabled={uploading}
                    multiple
                  >
                    <Button
                      icon={<UploadOutlined />}
                      size="large"
                      loading={uploading}
                      block
                    >
                      选择音频文件（支持多选）
                    </Button>
                  </Upload>

                  {audioClips.length > 0 && (
                    <div>
                      <Title level={5}>已上传的音频文件</Title>
                      <Table
                        dataSource={audioClips}
                        columns={audioColumns}
                        pagination={false}
                        size="small"
                        rowKey="id"
                      />
                    </div>
                  )}
                </Space>
              </Col>

              <Col xs={24} lg={8}>
                <Card title="上传要求" size="small">
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <div>
                      <BulbOutlined style={{ color: '#1890ff' }} />
                      <Text style={{ marginLeft: 8 }}>
                        建议上传3-10个音频文件
                      </Text>
                    </div>
                    <div>
                      <BulbOutlined style={{ color: '#1890ff' }} />
                      <Text style={{ marginLeft: 8 }}>
                        单个文件时长5-30秒
                      </Text>
                    </div>
                    <div>
                      <BulbOutlined style={{ color: '#1890ff' }} />
                      <Text style={{ marginLeft: 8 }}>
                        总时长建议2-5分钟
                      </Text>
                    </div>
                    <div>
                      <BulbOutlined style={{ color: '#1890ff' }} />
                      <Text style={{ marginLeft: 8 }}>
                        支持 MP3、WAV、M4A、FLAC 格式
                      </Text>
                    </div>
                    <div>
                      <BulbOutlined style={{ color: '#1890ff' }} />
                      <Text style={{ marginLeft: 8 }}>
                        保证音频清晰无噪音
                      </Text>
                    </div>
                  </Space>
                </Card>

                {audioClips.length > 0 && (
                  <Card title="质量统计" size="small" style={{ marginTop: 16 }}>
                    <Row gutter={16}>
                      <Col span={12}>
                        <Statistic
                          title="文件数量"
                          value={audioClips.length}
                          suffix="个"
                        />
                      </Col>
                      <Col span={12}>
                        <Statistic
                          title="总时长"
                          value={formatDuration(audioClips.reduce((sum, clip) => sum + clip.duration, 0))}
                        />
                      </Col>
                      <Col span={12}>
                        <Statistic
                          title="平均质量"
                          value={(audioClips.reduce((sum, clip) => sum + clip.quality, 0) / audioClips.length).toFixed(0)}
                          suffix="%"
                        />
                      </Col>
                      <Col span={12}>
                        <Statistic
                          title="有效文件"
                          value={audioClips.filter(clip => clip.isValid).length}
                          suffix={`/${audioClips.length}`}
                        />
                      </Col>
                    </Row>
                  </Card>
                )}
              </Col>
            </Row>

            <Divider />

            <Space>
              <Button
                type="primary"
                size="large"
                onClick={handleAnalyzeAudio}
                loading={analyzing}
                disabled={audioClips.length === 0}
                icon={<AudioOutlined />}
              >
                分析音频质量
              </Button>
              <Button size="large" onClick={handleRestart}>
                重新开始
              </Button>
            </Space>

            {analysisResults && (
              <Card title="分析结果" style={{ marginTop: 16 }}>
                <Row gutter={16}>
                  <Col span={6}>
                    <Statistic
                      title="成功概率"
                      value={analysisResults.success_probability}
                      suffix="%"
                      valueStyle={{ color: analysisResults.success_probability >= 80 ? '#3f8600' : '#cf1322' }}
                    />
                  </Col>
                  <Col span={6}>
                    <Statistic
                      title="预计训练时间"
                      value={analysisResults.estimated_training_time}
                      suffix="分钟"
                    />
                  </Col>
                  <Col span={6}>
                    <Statistic
                      title="推荐质量等级"
                      value={analysisResults.recommended_quality}
                    />
                  </Col>
                  <Col span={6}>
                    <Statistic
                      title="平均质量分"
                      value={analysisResults.average_quality.toFixed(1)}
                      suffix="/100"
                    />
                  </Col>
                </Row>
              </Card>
            )}
          </Card>
        )}

        {/* 第二步：配置参数 */}
        {currentStep === 1 && (
          <Card title="第二步：配置克隆参数" size="small">
            <Form
              form={form}
              layout="vertical"
              onFinish={handleConfigSubmit}
              initialValues={{
                gender: 'auto',
                language: 'zh-CN',
                style: 'natural',
                emotion: 'neutral',
                quality_level: analysisResults?.recommended_quality || 'high',
                training_iterations: 1000,
                data_augmentation: true,
                noise_reduction: true,
                pitch_stabilization: true,
                speed_normalization: true
              }}
            >
              <Row gutter={24}>
                <Col xs={24} lg={12}>
                  <Card title="基本设置" size="small">
                    <Form.Item
                      name="name"
                      label="音色名称"
                      rules={[{ required: true, message: '请输入音色名称' }]}
                    >
                      <Input placeholder="为您的音色起一个名字" />
                    </Form.Item>

                    <Form.Item
                      name="description"
                      label="音色描述"
                    >
                      <TextArea rows={3} placeholder="描述这个音色的特点..." />
                    </Form.Item>

                    <Form.Item
                      name="gender"
                      label="性别识别"
                    >
                      <Radio.Group>
                        <Radio value="auto">自动识别</Radio>
                        <Radio value="male">男性</Radio>
                        <Radio value="female">女性</Radio>
                      </Radio.Group>
                    </Form.Item>

                    <Form.Item
                      name="language"
                      label="主要语言"
                    >
                      <Select>
                        {languageOptions.map(option => (
                          <Select.Option key={option.value} value={option.value}>
                            {option.label}
                          </Select.Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </Card>
                </Col>

                <Col xs={24} lg={12}>
                  <Card title="风格设置" size="small">
                    <Form.Item
                      name="style"
                      label="语音风格"
                    >
                      <Select>
                        {styleOptions.map(option => (
                          <Select.Option key={option.value} value={option.value}>
                            {option.label}
                          </Select.Option>
                        ))}
                      </Select>
                    </Form.Item>

                    <Form.Item
                      name="emotion"
                      label="情感基调"
                    >
                      <Select>
                        {emotionOptions.map(option => (
                          <Select.Option key={option.value} value={option.value}>
                            {option.label}
                          </Select.Option>
                        ))}
                      </Select>
                    </Form.Item>

                    <Form.Item
                      name="quality_level"
                      label="质量等级"
                    >
                      <Radio.Group>
                        {qualityLevels.map(level => (
                          <Radio key={level.value} value={level.value}>
                            <div>
                              <div>{level.label}</div>
                              <Text type="secondary" style={{ fontSize: 12 }}>
                                {level.description}
                              </Text>
                            </div>
                          </Radio>
                        ))}
                      </Radio.Group>
                    </Form.Item>
                  </Card>
                </Col>
              </Row>

              <Divider />

              <Card title="高级设置" size="small">
                <Row gutter={24}>
                  <Col xs={24} lg={12}>
                    <Form.Item
                      name="training_iterations"
                      label={`训练迭代次数: ${form.getFieldValue('training_iterations') || 1000}`}
                    >
                      <Slider
                        min={500}
                        max={3000}
                        step={100}
                        marks={{
                          500: '快速',
                          1000: '标准',
                          2000: '高质量',
                          3000: '极致'
                        }}
                      />
                    </Form.Item>
                  </Col>
                  <Col xs={24} lg={12}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <Form.Item
                        name="data_augmentation"
                        valuePropName="checked"
                        style={{ marginBottom: 8 }}
                      >
                        <Switch checkedChildren="开" unCheckedChildren="关" />
                        <Text style={{ marginLeft: 8 }}>数据增强</Text>
                      </Form.Item>

                      <Form.Item
                        name="noise_reduction"
                        valuePropName="checked"
                        style={{ marginBottom: 8 }}
                      >
                        <Switch checkedChildren="开" unCheckedChildren="关" />
                        <Text style={{ marginLeft: 8 }}>噪音抑制</Text>
                      </Form.Item>

                      <Form.Item
                        name="pitch_stabilization"
                        valuePropName="checked"
                        style={{ marginBottom: 8 }}
                      >
                        <Switch checkedChildren="开" unCheckedChildren="关" />
                        <Text style={{ marginLeft: 8 }}>音调稳定化</Text>
                      </Form.Item>

                      <Form.Item
                        name="speed_normalization"
                        valuePropName="checked"
                        style={{ marginBottom: 8 }}
                      >
                        <Switch checkedChildren="开" unCheckedChildren="关" />
                        <Text style={{ marginLeft: 8 }}>语速标准化</Text>
                      </Form.Item>
                    </Space>
                  </Col>
                </Row>
              </Card>

              <Divider />

              <Space>
                <Button
                  type="primary"
                  htmlType="submit"
                  size="large"
                  icon={<RobotOutlined />}
                >
                  下一步：开始训练
                </Button>
                <Button
                  size="large"
                  onClick={() => setCurrentStep(0)}
                >
                  上一步
                </Button>
              </Space>
            </Form>
          </Card>
        )}

        {/* 第三步：训练过程 */}
        {currentStep === 2 && (
          <Card title="第三步：开始AI训练" size="small">
            <Row gutter={24}>
              <Col xs={24} lg={16}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  {cloneConfig && (
                    <Card title="训练配置确认" size="small">
                      <Row gutter={16}>
                        <Col span={8}>
                          <Text strong>音色名称:</Text> {cloneConfig.name}
                        </Col>
                        <Col span={8}>
                          <Text strong>质量等级:</Text> {cloneConfig.quality_level}
                        </Col>
                        <Col span={8}>
                          <Text strong>训练迭代:</Text> {cloneConfig.training_iterations}
                        </Col>
                      </Row>
                    </Card>
                  )}

                  <Card size="small">
                    <Text strong>训练须知：</Text>
                    <ul style={{ marginTop: 8, marginBottom: 0 }}>
                      <li>训练过程中请勿关闭页面</li>
                      <li>根据配置不同，训练时间约需要 {analysisResults?.estimated_training_time} 分钟</li>
                      <li>训练完成后您将获得可用的音色模型</li>
                      <li>如果训练失败，可以调整参数重新尝试</li>
                    </ul>
                  </Card>

                  <Button
                    type="primary"
                    size="large"
                    onClick={handleStartTraining}
                    loading={training}
                    icon={<ThunderboltOutlined />}
                    block
                  >
                    开始训练音色模型
                  </Button>
                </Space>
              </Col>

              <Col xs={24} lg={8}>
                <Card title="预计效果" size="small">
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Statistic
                      title="相似度预期"
                      value={analysisResults?.success_probability || 85}
                      suffix="%"
                      valueStyle={{ color: '#3f8600' }}
                    />
                    <Statistic
                      title="质量评分预期"
                      value="85-95"
                      suffix="/100"
                    />
                    <Statistic
                      title="预计完成时间"
                      value={analysisResults?.estimated_training_time || 10}
                      suffix="分钟"
                    />
                  </Space>
                </Card>
              </Col>
            </Row>

            <Divider />

            <Space>
              <Button
                size="large"
                onClick={() => setCurrentStep(1)}
                disabled={training}
              >
                上一步
              </Button>
              <Button
                size="large"
                onClick={handleRestart}
                disabled={training}
              >
                重新开始
              </Button>
            </Space>
          </Card>
        )}

        {/* 第四步：训练进度和结果 */}
        {currentStep === 3 && cloneTask && (
          <Card title="第四步：训练进度" size="small">
            {cloneTask.status === 'processing' ? (
              <div>
                <Row gutter={24}>
                  <Col xs={24} lg={16}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <Card size="small">
                        <div style={{ textAlign: 'center', marginBottom: 16 }}>
                          <Spin size="large" />
                          <Title level={4} style={{ marginTop: 16 }}>
                            AI正在训练中...
                          </Title>
                          <Text type="secondary">
                            预计完成时间: {new Date(cloneTask.estimated_completion).toLocaleTimeString()}
                          </Text>
                        </div>

                        <Progress
                          percent={Math.round(cloneTask.progress)}
                          status="active"
                          strokeColor={{
                            from: '#108ee9',
                            to: '#87d068',
                          }}
                          style={{ marginBottom: 16 }}
                        />

                        <Timeline>
                          <Timeline.Item
                            color="green"
                            dot={<CheckCircleOutlined />}
                          >
                            音频预处理完成
                          </Timeline.Item>
                          <Timeline.Item
                            color={cloneTask.progress > 20 ? "green" : "blue"}
                            dot={cloneTask.progress > 20 ? <CheckCircleOutlined /> : <LoadingOutlined />}
                          >
                            特征提取 {cloneTask.progress > 20 && "完成"}
                          </Timeline.Item>
                          <Timeline.Item
                            color={cloneTask.progress > 50 ? "green" : "gray"}
                            dot={cloneTask.progress > 50 ? <CheckCircleOutlined /> : <LoadingOutlined />}
                          >
                            模型训练 {cloneTask.progress > 50 && "完成"}
                          </Timeline.Item>
                          <Timeline.Item
                            color={cloneTask.progress > 80 ? "green" : "gray"}
                            dot={cloneTask.progress > 80 ? <CheckCircleOutlined /> : <LoadingOutlined />}
                          >
                            模型优化 {cloneTask.progress > 80 && "完成"}
                          </Timeline.Item>
                          <Timeline.Item color="gray">
                            完成训练
                          </Timeline.Item>
                        </Timeline>
                      </Card>
                    </Space>
                  </Col>

                  <Col xs={24} lg={8}>
                    <Card title="训练信息" size="small">
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <div>
                          <Text strong>任务ID:</Text> {cloneTask.id}
                        </div>
                        <div>
                          <Text strong>开始时间:</Text> {new Date(cloneTask.created_at).toLocaleString()}
                        </div>
                        <div>
                          <Text strong>使用文件:</Text> {cloneTask.audio_clips.length} 个
                        </div>
                        <div>
                          <Text strong>总时长:</Text> {formatDuration(
                            cloneTask.audio_clips.reduce((sum, clip) => sum + clip.duration, 0)
                          )}
                        </div>
                      </Space>
                    </Card>
                  </Col>
                </Row>
              </div>
            ) : cloneTask.status === 'completed' ? (
              <Result
                status="success"
                title="音色克隆成功！"
                subTitle="您的个性化音色已经成功创建，现在可以使用了。"
                extra={[
                  <Row key="stats" gutter={16} style={{ marginBottom: 24 }}>
                    <Col span={8}>
                      <Card>
                        <Statistic
                          title="质量评分"
                          value={cloneTask.quality_score}
                          suffix="/100"
                          valueStyle={{ color: '#3f8600' }}
                        />
                      </Card>
                    </Col>
                    <Col span={8}>
                      <Card>
                        <Statistic
                          title="相似度"
                          value={cloneTask.similarity_score}
                          suffix="%"
                          valueStyle={{ color: '#3f8600' }}
                        />
                      </Card>
                    </Col>
                    <Col span={8}>
                      <Card>
                        <Statistic
                          title="训练时长"
                          value={Math.round((new Date().getTime() - new Date(cloneTask.created_at).getTime()) / 60000)}
                          suffix="分钟"
                        />
                      </Card>
                    </Col>
                  </Row>,
                  <Space key="actions">
                    <Button type="primary" size="large" icon={<PlayCircleOutlined />}>
                      试听音色
                    </Button>
                    <Button size="large" icon={<DownloadOutlined />}>
                      下载模型
                    </Button>
                    <Button size="large" onClick={handleRestart}>
                      创建新音色
                    </Button>
                  </Space>
                ]}
              />
            ) : (
              <Result
                status="error"
                title="训练失败"
                subTitle={cloneTask.error_message || "训练过程中出现错误，请检查音频质量后重试。"}
                extra={[
                  <Space key="actions">
                    <Button type="primary" onClick={() => setCurrentStep(1)}>
                      重新配置
                    </Button>
                    <Button onClick={handleRestart}>
                      重新开始
                    </Button>
                  </Space>
                ]}
              />
            )}
          </Card>
        )}
      </Card>

      <audio ref={audioRef} />

      {/* 音频预览模态框 */}
      <Modal
        title="音频预览"
        open={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        footer={null}
        width={600}
      >
        {selectedClip && (
          <div>
            <Title level={4}>{selectedClip.name}</Title>
            <audio controls style={{ width: '100%' }} src={selectedClip.url} />
            
            <Divider />
            
            <Row gutter={16}>
              <Col span={8}>
                <Statistic
                  title="音频质量"
                  value={selectedClip.quality.toFixed(1)}
                  suffix="/100"
                  valueStyle={{ color: getQualityColor(selectedClip.quality) }}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="信噪比"
                  value={selectedClip.signal_to_noise.toFixed(1)}
                  suffix="dB"
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="清晰度"
                  value={selectedClip.voice_clarity.toFixed(1)}
                  suffix="/100"
                />
              </Col>
            </Row>

            {selectedClip.issues.length > 0 && (
              <div style={{ marginTop: 16 }}>
                <Text strong>质量问题:</Text>
                <ul style={{ marginTop: 8 }}>
                  {selectedClip.issues.map((issue, index) => (
                    <li key={index}>
                      <Text type="secondary">{issue}</Text>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  )
}

export default VoiceTimbreClone