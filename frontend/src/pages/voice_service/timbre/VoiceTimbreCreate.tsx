/**
 * Voice Timbre Create Component
 * 音色创建组件 - [Voice][Timbre][Create]
 */

import React, { useState, useRef } from 'react'
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
  Modal
} from 'antd'
import {
  UploadOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  SoundOutlined,
  SaveOutlined,
  EyeOutlined,
  DeleteOutlined
} from '@ant-design/icons'

const { Title, Paragraph, Text } = Typography
const { Option } = Select
const { TextArea } = Input

interface VoiceTimbreFormData {
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

const VoiceTimbreCreate: React.FC = () => {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [audioClips, setAudioClips] = useState<AudioClip[]>([])
  const [previewVisible, setPreviewVisible] = useState(false)
  const [previewAudio, setPreviewAudio] = useState<AudioClip | null>(null)
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
      
      setAudioClips(prev => [...prev, newClip])
    })

    return false // 阻止默认上传行为
  }

  const handlePlayAudio = (clipId: string) => {
    const clip = audioClips.find(c => c.id === clipId)
    if (!clip) return

    if (clip.isPlaying) {
      audioRef.current?.pause()
    } else {
      if (audioRef.current) {
        audioRef.current.src = clip.url
        audioRef.current.play()
      }
    }

    setAudioClips(prev => prev.map(c => ({
      ...c,
      isPlaying: c.id === clipId ? !c.isPlaying : false
    })))
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

  const handlePreview = (clip: AudioClip) => {
    setPreviewAudio(clip)
    setPreviewVisible(true)
  }

  const handleSubmit = async (values: VoiceTimbreFormData) => {
    if (audioClips.length === 0) {
      message.error('请至少上传一个音频文件')
      return
    }

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

      // 添加音频文件
      audioClips.forEach((clip, index) => {
        formData.append(`audio_${index}`, clip.file)
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
      // const response = await voiceTimbreService.create(formData)
      
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      clearInterval(progressInterval)
      setUploadProgress(100)
      
      message.success('音色创建成功！')
      form.resetFields()
      setAudioClips([])
      
    } catch (error) {
      message.error('音色创建失败，请重试')
      console.error('Voice timbre creation error:', error)
    } finally {
      setLoading(false)
      setTimeout(() => setUploadProgress(0), 1000)
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

  return (
    <div className="voice-timbre-create">
      <Card>
        <Title level={2}>
          <SoundOutlined /> 创建音色
        </Title>
        <Paragraph>
          上传高质量的音频样本，创建个性化的语音音色。建议上传时长15-30秒的清晰音频文件。
        </Paragraph>

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            gender: 'neutral',
            age_range: 'young_adult',
            language: 'zh-CN',
            accent: 'standard',
            style: 'neutral',
            emotion: 'neutral',
            speed: 1.0,
            pitch: 1.0,
            volume: 1.0,
            quality: 'high',
            is_public: false,
            category: 'original',
            tags: []
          }}
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

          <Card title="音频上传" size="small">
            <Alert
              message="音频要求"
              description="支持 MP3、WAV、M4A 格式，单个文件不超过 50MB，建议时长 15-30 秒，采样率 16kHz 以上。"
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />

            <Upload
              beforeUpload={handleAudioUpload}
              showUploadList={false}
              accept=".mp3,.wav,.m4a"
              disabled={loading}
            >
              <Button icon={<UploadOutlined />} size="large">
                选择音频文件
              </Button>
            </Upload>

            {audioClips.length > 0 && (
              <div style={{ marginTop: 16 }}>
                <Title level={5}>已上传的音频文件</Title>
                <Space direction="vertical" style={{ width: '100%' }}>
                  {audioClips.map(clip => (
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
                              icon={clip.isPlaying ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
                              onClick={() => handlePlayAudio(clip.id)}
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
                              onClick={() => handleRemoveAudio(clip.id)}
                            />
                          </Space>
                        </Col>
                      </Row>
                    </Card>
                  ))}
                </Space>
              </div>
            )}
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
              >
                创建音色
              </Button>
              <Button size="large">
                取消
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
    </div>
  )
}

export default VoiceTimbreCreate