/**
 * Voice Timbre Edit Component
 * 音色编辑组件 - [Voice][Timbre][Edit]
 */

import React, { useState, useEffect, useRef } from 'react'
import {
  Card,
  Form,
  Input,
  Select,
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
  Spin,
  Tag,
  Popconfirm
} from 'antd'
import {
  UploadOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  SoundOutlined,
  SaveOutlined,
  EyeOutlined,
  DeleteOutlined,
  EditOutlined,
  ReloadOutlined,
  HistoryOutlined
} from '@ant-design/icons'
import { useParams, useNavigate } from 'react-router-dom'

const { Title, Paragraph, Text } = Typography
const { Option } = Select
const { TextArea } = Input

interface VoiceTimbre {
  id: string
  name: string
  description: string
  gender: 'male' | 'female' | 'neutral'
  age_range: string
  language: string
  accent: string
  style: string
  emotion: string
  speed: number
  pitch: number
  volume: number
  quality: string
  tags: string[]
  is_public: boolean
  category: string
  created_at: string
  updated_at: string
  usage_count: number
  rating: number
  status: 'active' | 'inactive' | 'training' | 'failed'
  audio_samples: AudioSample[]
}

interface AudioSample {
  id: string
  name: string
  url: string
  duration: number
  size: number
  created_at: string
  is_primary: boolean
}

interface AudioClip {
  id: string
  file: File
  name: string
  duration: number
  size: number
  url: string
  isPlaying: boolean
}

const VoiceTimbreEdit: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [form] = Form.useForm()
  
  const [loading, setLoading] = useState(false)
  const [initialLoading, setInitialLoading] = useState(true)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [timbre, setTimbre] = useState<VoiceTimbre | null>(null)
  const [newAudioClips, setNewAudioClips] = useState<AudioClip[]>([])
  const [previewVisible, setPreviewVisible] = useState(false)
  const [previewAudio, setPreviewAudio] = useState<AudioSample | AudioClip | null>(null)
  const [historyVisible, setHistoryVisible] = useState(false)
  const [hasChanges, setHasChanges] = useState(false)
  const audioRef = useRef<HTMLAudioElement>(null)

  const genderOptions = [
    { label: '男性', value: 'male' },
    { label: '女性', value: 'female' },
    { label: '中性', value: 'neutral' }
  ]

  const ageRangeOptions = [
    { label: '儿童 (5-12岁)', value: 'child' },
    { label: '青少年 (13-17岁)', value: 'teen' },
    { label: '青年 (18-35岁)', value: 'young_adult' },
    { label: '中年 (36-55岁)', value: 'middle_aged' },
    { label: '老年 (55岁以上)', value: 'senior' }
  ]

  const languageOptions = [
    { label: '中文（普通话）', value: 'zh-CN' },
    { label: '中文（粤语）', value: 'zh-HK' },
    { label: '中文（台湾）', value: 'zh-TW' },
    { label: '英语（美式）', value: 'en-US' },
    { label: '英语（英式）', value: 'en-GB' },
    { label: '日语', value: 'ja-JP' },
    { label: '韩语', value: 'ko-KR' }
  ]

  const accentOptions = [
    { label: '标准', value: 'standard' },
    { label: '方言', value: 'dialect' },
    { label: '地方口音', value: 'regional' }
  ]

  const styleOptions = [
    { label: '正式', value: 'formal' },
    { label: '随意', value: 'casual' },
    { label: '新闻播报', value: 'news' },
    { label: '故事讲述', value: 'storytelling' },
    { label: '广告配音', value: 'commercial' },
    { label: '客服', value: 'customer_service' }
  ]

  const emotionOptions = [
    { label: '中性', value: 'neutral' },
    { label: '愉快', value: 'happy' },
    { label: '悲伤', value: 'sad' },
    { label: '兴奋', value: 'excited' },
    { label: '平静', value: 'calm' },
    { label: '严肃', value: 'serious' }
  ]

  const qualityOptions = [
    { label: '标清', value: 'standard' },
    { label: '高清', value: 'high' },
    { label: '超清', value: 'ultra' }
  ]

  const categoryOptions = [
    { label: '原创音色', value: 'original' },
    { label: '名人音色', value: 'celebrity' },
    { label: '角色音色', value: 'character' },
    { label: '专业配音', value: 'professional' }
  ]

  useEffect(() => {
    if (id) {
      loadTimbreData()
    }
  }, [id])

  const loadTimbreData = async () => {
    setInitialLoading(true)
    try {
      // 模拟API调用
      // const response = await voiceTimbreService.getById(id)
      
      // 模拟数据
      const mockTimbre: VoiceTimbre = {
        id: id!,
        name: '温柔女声',
        description: '温和甜美的女性声音，适合故事讲述和客服场景',
        gender: 'female',
        age_range: 'young_adult',
        language: 'zh-CN',
        accent: 'standard',
        style: 'storytelling',
        emotion: 'happy',
        speed: 1.0,
        pitch: 1.1,
        volume: 0.9,
        quality: 'high',
        tags: ['温柔', '甜美', '故事', '客服'],
        is_public: true,
        category: 'original',
        created_at: '2024-06-20T10:00:00Z',
        updated_at: '2024-06-22T15:30:00Z',
        usage_count: 245,
        rating: 4.8,
        status: 'active',
        audio_samples: [
          {
            id: 'sample1',
            name: '示例音频1.mp3',
            url: '/api/audio/sample1.mp3',
            duration: 23.5,
            size: 385024,
            created_at: '2024-06-20T10:00:00Z',
            is_primary: true
          },
          {
            id: 'sample2',
            name: '示例音频2.mp3',
            url: '/api/audio/sample2.mp3',
            duration: 18.2,
            size: 298345,
            created_at: '2024-06-21T14:20:00Z',
            is_primary: false
          }
        ]
      }

      setTimbre(mockTimbre)
      form.setFieldsValue(mockTimbre)
      
    } catch (error) {
      message.error('加载音色数据失败')
      console.error('Load timbre error:', error)
    } finally {
      setInitialLoading(false)
    }
  }

  const handleFormChange = () => {
    setHasChanges(true)
  }

  const handleAudioUpload = (file: File) => {
    const audioUrl = URL.createObjectURL(file)
    const audio = new Audio(audioUrl)
    
    audio.addEventListener('loadedmetadata', () => {
      const newClip: AudioClip = {
        id: Date.now().toString(),
        file,
        name: file.name,
        duration: audio.duration,
        size: file.size,
        url: audioUrl,
        isPlaying: false
      }
      
      setNewAudioClips(prev => [...prev, newClip])
      setHasChanges(true)
    })

    return false
  }

  const handlePlayAudio = (audio: AudioSample | AudioClip) => {
    if (audioRef.current) {
      audioRef.current.src = audio.url
      audioRef.current.play()
    }
  }

  const handleRemoveNewAudio = (clipId: string) => {
    setNewAudioClips(prev => {
      const clip = prev.find(c => c.id === clipId)
      if (clip) {
        URL.revokeObjectURL(clip.url)
      }
      return prev.filter(c => c.id !== clipId)
    })
    setHasChanges(true)
  }

  const handleRemoveExistingAudio = async (sampleId: string) => {
    try {
      // 这里应该调用API删除音频样本
      // await voiceTimbreService.removeAudioSample(id, sampleId)
      
      setTimbre(prev => prev ? {
        ...prev,
        audio_samples: prev.audio_samples.filter(s => s.id !== sampleId)
      } : null)
      
      setHasChanges(true)
      message.success('音频样本删除成功')
    } catch (error) {
      message.error('删除音频样本失败')
    }
  }

  const handleSetPrimaryAudio = async (sampleId: string) => {
    try {
      // 这里应该调用API设置主要音频样本
      // await voiceTimbreService.setPrimaryAudioSample(id, sampleId)
      
      setTimbre(prev => prev ? {
        ...prev,
        audio_samples: prev.audio_samples.map(s => ({
          ...s,
          is_primary: s.id === sampleId
        }))
      } : null)
      
      setHasChanges(true)
      message.success('已设置为主要音频样本')
    } catch (error) {
      message.error('设置失败')
    }
  }

  const handlePreview = (audio: AudioSample | AudioClip) => {
    setPreviewAudio(audio)
    setPreviewVisible(true)
  }

  const handleSubmit = async (values: any) => {
    setLoading(true)
    setUploadProgress(0)

    try {
      const formData = new FormData()
      
      // 添加表单数据
      Object.entries(values).forEach(([key, value]) => {
        if (Array.isArray(value)) {
          formData.append(key, JSON.stringify(value))
        } else {
          formData.append(key, String(value))
        }
      })

      // 添加新的音频文件
      newAudioClips.forEach((clip, index) => {
        formData.append(`new_audio_${index}`, clip.file)
      })

      // 模拟上传进度
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 200)

      // 这里应该调用实际的API
      // const response = await voiceTimbreService.update(id, formData)
      
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      clearInterval(progressInterval)
      setUploadProgress(100)
      
      message.success('音色更新成功！')
      setHasChanges(false)
      setNewAudioClips([])
      
      // 重新加载数据
      await loadTimbreData()
      
    } catch (error) {
      message.error('音色更新失败，请重试')
      console.error('Voice timbre update error:', error)
    } finally {
      setLoading(false)
      setTimeout(() => setUploadProgress(0), 1000)
    }
  }

  const handleResetForm = () => {
    if (timbre) {
      form.setFieldsValue(timbre)
      setNewAudioClips([])
      setHasChanges(false)
    }
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'green'
      case 'inactive': return 'default'
      case 'training': return 'blue'
      case 'failed': return 'red'
      default: return 'default'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return '活跃'
      case 'inactive': return '非活跃'
      case 'training': return '训练中'
      case 'failed': return '失败'
      default: return '未知'
    }
  }

  if (initialLoading) {
    return (
      <div style={{ padding: 50, textAlign: 'center' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>
          <Text>加载音色数据中...</Text>
        </div>
      </div>
    )
  }

  if (!timbre) {
    return (
      <Card>
        <Alert
          message="音色不存在"
          description="找不到指定的音色，可能已被删除或您没有访问权限。"
          type="error"
          showIcon
        />
      </Card>
    )
  }

  return (
    <div className="voice-timbre-edit">
      <Card>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
          <div>
            <Title level={2}>
              <EditOutlined /> 编辑音色
            </Title>
            <Space>
              <Text type="secondary">音色ID: {timbre.id}</Text>
              <Tag color={getStatusColor(timbre.status)}>
                {getStatusText(timbre.status)}
              </Tag>
              <Text type="secondary">使用次数: {timbre.usage_count}</Text>
              <Text type="secondary">评分: {timbre.rating}/5.0</Text>
            </Space>
          </div>
          <Space>
            <Button 
              icon={<HistoryOutlined />}
              onClick={() => setHistoryVisible(true)}
            >
              查看历史
            </Button>
            <Button 
              icon={<ReloadOutlined />}
              onClick={loadTimbreData}
            >
              刷新
            </Button>
          </Space>
        </div>

        {hasChanges && (
          <Alert
            message="有未保存的更改"
            description="您对音色进行了修改，请记得保存更改。"
            type="warning"
            showIcon
            closable
            style={{ marginBottom: 16 }}
          />
        )}

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          onValuesChange={handleFormChange}
        >
          <Row gutter={24}>
            <Col xs={24} lg={12}>
              <Card title="基本信息" size="small">
                <Form.Item
                  name="name"
                  label="音色名称"
                  rules={[
                    { required: true, message: '请输入音色名称' },
                    { min: 2, max: 50, message: '名称长度应在2-50字符之间' }
                  ]}
                >
                  <Input placeholder="为您的音色起一个独特的名字" />
                </Form.Item>

                <Form.Item
                  name="description"
                  label="音色描述"
                  rules={[
                    { max: 500, message: '描述不能超过500字符' }
                  ]}
                >
                  <TextArea
                    rows={3}
                    placeholder="描述这个音色的特点和适用场景..."
                  />
                </Form.Item>

                <Form.Item
                  name="category"
                  label="音色类型"
                  rules={[{ required: true, message: '请选择音色类型' }]}
                >
                  <Select placeholder="选择音色类型">
                    {categoryOptions.map(option => (
                      <Option key={option.value} value={option.value}>
                        {option.label}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>

                <Form.Item
                  name="tags"
                  label="标签"
                  help="添加标签便于分类和搜索"
                >
                  <Select
                    mode="tags"
                    placeholder="输入标签，按回车添加"
                    tokenSeparators={[',']}
                  />
                </Form.Item>

                <Form.Item
                  name="is_public"
                  label="公开设置"
                  valuePropName="checked"
                >
                  <Switch
                    checkedChildren="公开"
                    unCheckedChildren="私有"
                  />
                </Form.Item>
              </Card>
            </Col>

            <Col xs={24} lg={12}>
              <Card title="语音特征" size="small">
                <Form.Item
                  name="gender"
                  label="性别"
                  rules={[{ required: true, message: '请选择性别' }]}
                >
                  <Radio.Group>
                    {genderOptions.map(option => (
                      <Radio key={option.value} value={option.value}>
                        {option.label}
                      </Radio>
                    ))}
                  </Radio.Group>
                </Form.Item>

                <Form.Item
                  name="age_range"
                  label="年龄段"
                  rules={[{ required: true, message: '请选择年龄段' }]}
                >
                  <Select placeholder="选择年龄段">
                    {ageRangeOptions.map(option => (
                      <Option key={option.value} value={option.value}>
                        {option.label}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>

                <Form.Item
                  name="language"
                  label="语言"
                  rules={[{ required: true, message: '请选择语言' }]}
                >
                  <Select placeholder="选择语言">
                    {languageOptions.map(option => (
                      <Option key={option.value} value={option.value}>
                        {option.label}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>

                <Form.Item
                  name="accent"
                  label="口音"
                >
                  <Select placeholder="选择口音">
                    {accentOptions.map(option => (
                      <Option key={option.value} value={option.value}>
                        {option.label}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              </Card>
            </Col>
          </Row>

          <Divider />

          <Row gutter={24}>
            <Col xs={24} lg={12}>
              <Card title="语音风格" size="small">
                <Form.Item
                  name="style"
                  label="语音风格"
                >
                  <Select placeholder="选择语音风格">
                    {styleOptions.map(option => (
                      <Option key={option.value} value={option.value}>
                        {option.label}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>

                <Form.Item
                  name="emotion"
                  label="情感色彩"
                >
                  <Select placeholder="选择情感色彩">
                    {emotionOptions.map(option => (
                      <Option key={option.value} value={option.value}>
                        {option.label}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              </Card>
            </Col>

            <Col xs={24} lg={12}>
              <Card title="音质参数" size="small">
                <Form.Item
                  name="speed"
                  label={`语速: ${form.getFieldValue('speed') || 1.0}x`}
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
                  />
                </Form.Item>

                <Form.Item
                  name="pitch"
                  label={`音调: ${form.getFieldValue('pitch') || 1.0}x`}
                >
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

                <Form.Item
                  name="volume"
                  label={`音量: ${form.getFieldValue('volume') || 1.0}x`}
                >
                  <Slider
                    min={0.1}
                    max={2.0}
                    step={0.1}
                    marks={{
                      0.1: '轻',
                      1.0: '正常',
                      2.0: '响'
                    }}
                  />
                </Form.Item>

                <Form.Item
                  name="quality"
                  label="音质等级"
                >
                  <Select placeholder="选择音质等级">
                    {qualityOptions.map(option => (
                      <Option key={option.value} value={option.value}>
                        {option.label}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              </Card>
            </Col>
          </Row>

          <Divider />

          <Card title="音频样本管理" size="small">
            <Row gutter={16}>
              <Col xs={24} lg={12}>
                <Title level={5}>现有音频样本</Title>
                {timbre.audio_samples.length > 0 ? (
                  <Space direction="vertical" style={{ width: '100%' }}>
                    {timbre.audio_samples.map(sample => (
                      <Card key={sample.id} size="small">
                        <Row align="middle" gutter={16}>
                          <Col flex="auto">
                            <Space direction="vertical" size="small">
                              <div>
                                <Text strong>{sample.name}</Text>
                                {sample.is_primary && (
                                  <Tag color="blue" style={{ marginLeft: 8 }}>主要</Tag>
                                )}
                              </div>
                              <Text type="secondary">
                                时长: {formatDuration(sample.duration)} | 大小: {formatFileSize(sample.size)}
                              </Text>
                            </Space>
                          </Col>
                          <Col>
                            <Space>
                              <Button
                                type="text"
                                icon={<PlayCircleOutlined />}
                                onClick={() => handlePlayAudio(sample)}
                              />
                              <Button
                                type="text"
                                icon={<EyeOutlined />}
                                onClick={() => handlePreview(sample)}
                              />
                              {!sample.is_primary && (
                                <Button
                                  type="text"
                                  onClick={() => handleSetPrimaryAudio(sample.id)}
                                >
                                  设为主要
                                </Button>
                              )}
                              <Popconfirm
                                title="确认删除这个音频样本吗？"
                                onConfirm={() => handleRemoveExistingAudio(sample.id)}
                                okText="确认"
                                cancelText="取消"
                              >
                                <Button
                                  type="text"
                                  danger
                                  icon={<DeleteOutlined />}
                                />
                              </Popconfirm>
                            </Space>
                          </Col>
                        </Row>
                      </Card>
                    ))}
                  </Space>
                ) : (
                  <Alert
                    message="暂无音频样本"
                    description="请上传音频文件来创建音色样本"
                    type="info"
                  />
                )}
              </Col>

              <Col xs={24} lg={12}>
                <Title level={5}>添加新音频样本</Title>
                <Upload
                  beforeUpload={handleAudioUpload}
                  showUploadList={false}
                  accept=".mp3,.wav,.m4a"
                  disabled={loading}
                >
                  <Button icon={<UploadOutlined />}>
                    选择音频文件
                  </Button>
                </Upload>

                {newAudioClips.length > 0 && (
                  <div style={{ marginTop: 16 }}>
                    <Text strong>新上传的文件</Text>
                    <Space direction="vertical" style={{ width: '100%', marginTop: 8 }}>
                      {newAudioClips.map(clip => (
                        <Card key={clip.id} size="small">
                          <Row align="middle" gutter={16}>
                            <Col flex="auto">
                              <Space direction="vertical" size="small">
                                <Text strong>{clip.name}</Text>
                                <Text type="secondary">
                                  时长: {formatDuration(clip.duration)} | 大小: {formatFileSize(clip.size)}
                                </Text>
                              </Space>
                            </Col>
                            <Col>
                              <Space>
                                <Button
                                  type="text"
                                  icon={<PlayCircleOutlined />}
                                  onClick={() => handlePlayAudio(clip)}
                                />
                                <Button
                                  type="text"
                                  icon={<EyeOutlined />}
                                  onClick={() => handlePreview(clip)}
                                />
                                <Button
                                  type="text"
                                  danger
                                  icon={<DeleteOutlined />}
                                  onClick={() => handleRemoveNewAudio(clip.id)}
                                />
                              </Space>
                            </Col>
                          </Row>
                        </Card>
                      ))}
                    </Space>
                  </div>
                )}
              </Col>
            </Row>
          </Card>

          {uploadProgress > 0 && (
            <Card style={{ marginTop: 16 }}>
              <Progress
                percent={uploadProgress}
                status={uploadProgress === 100 ? 'success' : 'active'}
                format={percent => `${percent}% ${uploadProgress === 100 ? '完成' : '处理中...'}`}
              />
            </Card>
          )}

          <Divider />

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                size="large"
                icon={<SaveOutlined />}
                disabled={!hasChanges}
              >
                保存更改
              </Button>
              <Button 
                size="large"
                onClick={handleResetForm}
                disabled={!hasChanges}
              >
                重置
              </Button>
              <Button 
                size="large"
                onClick={() => navigate('/voice/timbre')}
              >
                返回列表
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      <audio ref={audioRef} />

      <Modal
        title="音频预览"
        open={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        footer={null}
        width={600}
      >
        {previewAudio && (
          <div>
            <Title level={4}>{previewAudio.name}</Title>
            <audio controls style={{ width: '100%' }} src={previewAudio.url} />
            <div style={{ marginTop: 16 }}>
              <Text type="secondary">
                时长: {formatDuration(previewAudio.duration)} | 
                大小: {formatFileSize(previewAudio.size)}
              </Text>
            </div>
          </div>
        )}
      </Modal>

      <Modal
        title="修改历史"
        open={historyVisible}
        onCancel={() => setHistoryVisible(false)}
        footer={null}
        width={800}
      >
        <div>
          <Text type="secondary">创建时间: {new Date(timbre.created_at).toLocaleString()}</Text>
          <br />
          <Text type="secondary">最后更新: {new Date(timbre.updated_at).toLocaleString()}</Text>
          {/* 这里可以添加更详细的历史记录 */}
        </div>
      </Modal>
    </div>
  )
}

export default VoiceTimbreEdit