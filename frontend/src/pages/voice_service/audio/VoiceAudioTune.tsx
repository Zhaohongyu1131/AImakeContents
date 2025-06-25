/**
 * Voice Audio Tune Component
 * 语音参数调优组件 - [Voice][Audio][Tune]
 */

import React, { useState, useRef, useEffect } from 'react'
import {
  Card,
  Form,
  Input,
  Select,
  Button,
  Typography,
  Row,
  Col,
  Space,
  Divider,
  Slider,
  Switch,
  message,
  Modal,
  Table,
  Tag,
  Progress,
  Collapse,
  InputNumber,
  Radio,
  Tooltip,
  Popover,
  Alert,
  Tabs
} from 'antd'
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  SoundOutlined,
  SettingOutlined,
  SaveOutlined,
  ReloadOutlined,
  DownloadOutlined,
  EyeOutlined,
  ExperimentOutlined,
  TuneOutlined,
  AudioOutlined,
  ThunderboltOutlined,
  BulbOutlined,
  StarOutlined,
  HistoryOutlined
} from '@ant-design/icons'

const { Title, Paragraph, Text } = Typography
const { TextArea } = Input
const { Option } = Select
const { Panel } = Collapse
const { TabPane } = Tabs

interface TTSParameters {
  speaker_id: string
  text: string
  speed: number
  pitch: number
  volume: number
  emotion: string
  style: string
  pause_time: number
  breath_length: number
  word_gap: number
  sentence_gap: number
  emphasis_words: string[]
  tone_curve: number[]
  noise_scale: number
  noise_scale_w: number
  length_scale: number
  energy_scale: number
}

interface VoicePreset {
  id: string
  name: string
  description: string
  parameters: Partial<TTSParameters>
  category: string
  is_default: boolean
  usage_count: number
  rating: number
}

interface GenerationResult {
  id: string
  text: string
  audio_url: string
  parameters: TTSParameters
  created_at: string
  duration: number
  file_size: number
  quality_score: number
}

const VoiceAudioTune: React.FC = () => {
  const [form] = Form.useForm()
  const [parameters, setParameters] = useState<TTSParameters>({
    speaker_id: '',
    text: '',
    speed: 1.0,
    pitch: 1.0,
    volume: 1.0,
    emotion: 'neutral',
    style: 'normal',
    pause_time: 0.8,
    breath_length: 0.3,
    word_gap: 0.05,
    sentence_gap: 0.8,
    emphasis_words: [],
    tone_curve: [0, 0.2, 0.5, 0.8, 1.0],
    noise_scale: 0.667,
    noise_scale_w: 0.8,
    length_scale: 1.0,
    energy_scale: 1.0
  })

  const [generating, setGenerating] = useState(false)
  const [playing, setPlaying] = useState(false)
  const [currentAudio, setCurrentAudio] = useState<string | null>(null)
  const [presets, setPresets] = useState<VoicePreset[]>([])
  const [selectedPreset, setSelectedPreset] = useState<string>('')
  const [history, setHistory] = useState<GenerationResult[]>([])
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [presetModalVisible, setPresetModalVisible] = useState(false)
  const [historyModalVisible, setHistoryModalVisible] = useState(false)
  const [realTimeMode, setRealTimeMode] = useState(false)
  const audioRef = useRef<HTMLAudioElement>(null)

  const speakerOptions = [
    { label: '温柔女声', value: 'gentle_female', category: 'female' },
    { label: '磁性男声', value: 'magnetic_male', category: 'male' },
    { label: '活泼童声', value: 'lively_child', category: 'child' },
    { label: '知性女声', value: 'intellectual_female', category: 'female' },
    { label: '稳重男声', value: 'stable_male', category: 'male' },
    { label: '甜美少女', value: 'sweet_girl', category: 'young' }
  ]

  const emotionOptions = [
    { label: '中性', value: 'neutral', description: '平和自然的语调' },
    { label: '愉快', value: 'happy', description: '开心愉悦的语调' },
    { label: '悲伤', value: 'sad', description: '低沉忧郁的语调' },
    { label: '兴奋', value: 'excited', description: '充满活力的语调' },
    { label: '平静', value: 'calm', description: '安静祥和的语调' },
    { label: '严肃', value: 'serious', description: '正式严谨的语调' },
    { label: '温柔', value: 'gentle', description: '柔和亲切的语调' },
    { label: '愤怒', value: 'angry', description: '激烈愤怒的语调' }
  ]

  const styleOptions = [
    { label: '正常', value: 'normal', description: '标准语音合成' },
    { label: '新闻播报', value: 'news', description: '新闻主播风格' },
    { label: '故事讲述', value: 'storytelling', description: '生动的故事叙述' },
    { label: '客服对话', value: 'customer_service', description: '礼貌的客服语调' },
    { label: '广告配音', value: 'advertisement', description: '吸引人的广告语调' },
    { label: '诗歌朗诵', value: 'poetry', description: '富有韵律的朗诵' },
    { label: '儿童故事', value: 'children_story', description: '适合儿童的语调' }
  ]

  useEffect(() => {
    loadPresets()
    loadHistory()
  }, [])

  useEffect(() => {
    if (realTimeMode && parameters.text && parameters.text.length > 0) {
      // 实时模式下自动生成预览
      const debounceTimer = setTimeout(() => {
        handleGenerate(true)
      }, 1000)
      
      return () => clearTimeout(debounceTimer)
    }
  }, [parameters, realTimeMode])

  const loadPresets = async () => {
    try {
      // 模拟加载预设
      const mockPresets: VoicePreset[] = [
        {
          id: '1',
          name: '新闻播报',
          description: '适合新闻播报的专业语调',
          parameters: {
            speed: 0.9,
            pitch: 1.0,
            volume: 1.0,
            emotion: 'serious',
            style: 'news',
            pause_time: 1.0,
            sentence_gap: 1.2
          },
          category: 'professional',
          is_default: true,
          usage_count: 1250,
          rating: 4.8
        },
        {
          id: '2',
          name: '温柔女声',
          description: '温和甜美的女性声音',
          parameters: {
            speed: 0.95,
            pitch: 1.1,
            volume: 0.9,
            emotion: 'gentle',
            style: 'normal',
            pause_time: 0.9,
            breath_length: 0.4
          },
          category: 'casual',
          is_default: false,
          usage_count: 890,
          rating: 4.9
        },
        {
          id: '3',
          name: '故事讲述',
          description: '生动有趣的故事叙述风格',
          parameters: {
            speed: 1.05,
            pitch: 1.05,
            volume: 1.0,
            emotion: 'happy',
            style: 'storytelling',
            pause_time: 0.7,
            sentence_gap: 0.9
          },
          category: 'entertainment',
          is_default: false,
          usage_count: 674,
          rating: 4.7
        }
      ]
      
      setPresets(mockPresets)
    } catch (error) {
      console.error('Load presets error:', error)
    }
  }

  const loadHistory = async () => {
    try {
      // 模拟加载历史记录
      const mockHistory: GenerationResult[] = [
        {
          id: '1',
          text: '这是一段测试文本，用于演示语音合成效果。',
          audio_url: '/audio/sample1.mp3',
          parameters: { ...parameters },
          created_at: '2024-06-24T10:30:00Z',
          duration: 8.5,
          file_size: 136000,
          quality_score: 92
        }
      ]
      
      setHistory(mockHistory)
    } catch (error) {
      console.error('Load history error:', error)
    }
  }

  const handleParameterChange = (key: keyof TTSParameters, value: any) => {
    setParameters(prev => ({
      ...prev,
      [key]: value
    }))
    
    // 更新表单
    form.setFieldValue(key, value)
  }

  const handlePresetSelect = (presetId: string) => {
    const preset = presets.find(p => p.id === presetId)
    if (preset) {
      const newParams = { ...parameters, ...preset.parameters }
      setParameters(newParams)
      form.setFieldsValue(newParams)
      setSelectedPreset(presetId)
      message.success(`已应用预设: ${preset.name}`)
    }
  }

  const handleGenerate = async (isPreview = false) => {
    if (!parameters.text || !parameters.speaker_id) {
      message.error('请输入文本内容并选择说话人')
      return
    }

    setGenerating(true)
    
    try {
      // 模拟语音生成
      await new Promise(resolve => setTimeout(resolve, isPreview ? 500 : 2000))
      
      const audioUrl = '/audio/generated_' + Date.now() + '.mp3'
      
      if (!isPreview) {
        const result: GenerationResult = {
          id: Date.now().toString(),
          text: parameters.text,
          audio_url: audioUrl,
          parameters: { ...parameters },
          created_at: new Date().toISOString(),
          duration: Math.random() * 10 + 5,
          file_size: Math.floor(Math.random() * 200000 + 100000),
          quality_score: Math.floor(Math.random() * 20 + 80)
        }
        
        setHistory(prev => [result, ...prev])
        message.success('语音生成成功！')
      }
      
      setCurrentAudio(audioUrl)
      
    } catch (error) {
      message.error('语音生成失败')
      console.error('Generation error:', error)
    } finally {
      setGenerating(false)
    }
  }

  const handlePlay = () => {
    if (!currentAudio) {
      message.warning('请先生成语音')
      return
    }

    if (audioRef.current) {
      if (playing) {
        audioRef.current.pause()
      } else {
        audioRef.current.src = currentAudio
        audioRef.current.play()
      }
      setPlaying(!playing)
    }
  }

  const handleSavePreset = async (values: any) => {
    try {
      const newPreset: VoicePreset = {
        id: Date.now().toString(),
        name: values.name,
        description: values.description,
        parameters: { ...parameters },
        category: values.category,
        is_default: false,
        usage_count: 0,
        rating: 5.0
      }
      
      setPresets(prev => [...prev, newPreset])
      setPresetModalVisible(false)
      message.success('预设保存成功！')
    } catch (error) {
      message.error('保存预设失败')
    }
  }

  const handleReset = () => {
    const defaultParams: TTSParameters = {
      speaker_id: '',
      text: '',
      speed: 1.0,
      pitch: 1.0,
      volume: 1.0,
      emotion: 'neutral',
      style: 'normal',
      pause_time: 0.8,
      breath_length: 0.3,
      word_gap: 0.05,
      sentence_gap: 0.8,
      emphasis_words: [],
      tone_curve: [0, 0.2, 0.5, 0.8, 1.0],
      noise_scale: 0.667,
      noise_scale_w: 0.8,
      length_scale: 1.0,
      energy_scale: 1.0
    }
    
    setParameters(defaultParams)
    form.setFieldsValue(defaultParams)
    setSelectedPreset('')
    message.info('参数已重置')
  }

  const historyColumns = [
    {
      title: '文本内容',
      dataIndex: 'text',
      key: 'text',
      ellipsis: true,
      width: 200
    },
    {
      title: '生成时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (time: string) => new Date(time).toLocaleString(),
      width: 150
    },
    {
      title: '时长',
      dataIndex: 'duration',
      key: 'duration',
      render: (duration: number) => `${duration.toFixed(1)}s`,
      width: 80
    },
    {
      title: '质量分',
      dataIndex: 'quality_score',
      key: 'quality_score',
      render: (score: number) => (
        <div>
          <Progress
            percent={score}
            size="small"
            showInfo={false}
            strokeColor={score >= 90 ? '#52c41a' : score >= 80 ? '#faad14' : '#ff4d4f'}
            style={{ width: 60 }}
          />
          <Text style={{ marginLeft: 8 }}>{score}</Text>
        </div>
      ),
      width: 100
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: any, record: GenerationResult) => (
        <Space>
          <Button
            type="text"
            icon={<PlayCircleOutlined />}
            onClick={() => {
              setCurrentAudio(record.audio_url)
              handlePlay()
            }}
          />
          <Button
            type="text"
            icon={<DownloadOutlined />}
            onClick={() => {
              // 下载音频文件
              const link = document.createElement('a')
              link.href = record.audio_url
              link.download = `voice_${record.id}.mp3`
              link.click()
            }}
          />
          <Button
            type="text"
            icon={<ReloadOutlined />}
            onClick={() => {
              setParameters(record.parameters)
              form.setFieldsValue(record.parameters)
              message.success('参数已恢复')
            }}
          />
        </Space>
      ),
      width: 120
    }
  ]

  return (
    <div className="voice-audio-tune">
      <Card>
        <Title level={2}>
          <TuneOutlined /> 语音参数调优
        </Title>
        <Paragraph>
          精确调整语音合成参数，创造完美的语音效果。支持实时预览和参数预设。
        </Paragraph>

        <Row gutter={24}>
          <Col xs={24} lg={16}>
            <Form form={form} layout="vertical">
              <Card title="基础参数" size="small">
                <Row gutter={16}>
                  <Col xs={24} md={12}>
                    <Form.Item
                      name="speaker_id"
                      label="说话人"
                      rules={[{ required: true, message: '请选择说话人' }]}
                    >
                      <Select
                        placeholder="选择说话人"
                        onChange={value => handleParameterChange('speaker_id', value)}
                      >
                        {speakerOptions.map(option => (
                          <Option key={option.value} value={option.value}>
                            <div>
                              <Text>{option.label}</Text>
                              <Tag size="small" style={{ marginLeft: 8 }}>
                                {option.category}
                              </Tag>
                            </div>
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </Col>
                  <Col xs={24} md={12}>
                    <Form.Item label="预设模板">
                      <Select
                        placeholder="选择预设模板"
                        value={selectedPreset}
                        onChange={handlePresetSelect}
                        allowClear
                      >
                        {presets.map(preset => (
                          <Option key={preset.id} value={preset.id}>
                            <div>
                              <Text>{preset.name}</Text>
                              <Tag size="small" style={{ marginLeft: 8 }}>
                                {preset.category}
                              </Tag>
                              {preset.is_default && (
                                <Tag color="blue" size="small" style={{ marginLeft: 4 }}>
                                  默认
                                </Tag>
                              )}
                            </div>
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </Col>
                </Row>

                <Form.Item
                  name="text"
                  label="文本内容"
                  rules={[{ required: true, message: '请输入文本内容' }]}
                >
                  <TextArea
                    rows={4}
                    placeholder="请输入要合成的文本内容..."
                    onChange={e => handleParameterChange('text', e.target.value)}
                    showCount
                    maxLength={1000}
                  />
                </Form.Item>

                <Row gutter={16}>
                  <Col xs={24} md={8}>
                    <Form.Item
                      name="emotion"
                      label="情感"
                    >
                      <Select
                        onChange={value => handleParameterChange('emotion', value)}
                      >
                        {emotionOptions.map(option => (
                          <Option key={option.value} value={option.value}>
                            <Tooltip title={option.description}>
                              {option.label}
                            </Tooltip>
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </Col>
                  <Col xs={24} md={8}>
                    <Form.Item
                      name="style"
                      label="风格"
                    >
                      <Select
                        onChange={value => handleParameterChange('style', value)}
                      >
                        {styleOptions.map(option => (
                          <Option key={option.value} value={option.value}>
                            <Tooltip title={option.description}>
                              {option.label}
                            </Tooltip>
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </Col>
                  <Col xs={24} md={8}>
                    <Form.Item label="实时预览">
                      <Switch
                        checked={realTimeMode}
                        onChange={setRealTimeMode}
                        checkedChildren="开"
                        unCheckedChildren="关"
                      />
                      <Text type="secondary" style={{ marginLeft: 8, fontSize: 12 }}>
                        参数变化时自动生成预览
                      </Text>
                    </Form.Item>
                  </Col>
                </Row>
              </Card>

              <Card title="音质调节" size="small" style={{ marginTop: 16 }}>
                <Row gutter={24}>
                  <Col xs={24} md={8}>
                    <Form.Item
                      name="speed"
                      label={`语速: ${parameters.speed.toFixed(2)}x`}
                    >
                      <Slider
                        min={0.5}
                        max={2.0}
                        step={0.05}
                        value={parameters.speed}
                        onChange={value => handleParameterChange('speed', value)}
                        marks={{
                          0.5: '慢',
                          1.0: '正常',
                          2.0: '快'
                        }}
                      />
                    </Form.Item>
                  </Col>
                  <Col xs={24} md={8}>
                    <Form.Item
                      name="pitch"
                      label={`音调: ${parameters.pitch.toFixed(2)}x`}
                    >
                      <Slider
                        min={0.5}
                        max={2.0}
                        step={0.05}
                        value={parameters.pitch}
                        onChange={value => handleParameterChange('pitch', value)}
                        marks={{
                          0.5: '低',
                          1.0: '正常',
                          2.0: '高'
                        }}
                      />
                    </Form.Item>
                  </Col>
                  <Col xs={24} md={8}>
                    <Form.Item
                      name="volume"
                      label={`音量: ${parameters.volume.toFixed(2)}x`}
                    >
                      <Slider
                        min={0.1}
                        max={2.0}
                        step={0.1}
                        value={parameters.volume}
                        onChange={value => handleParameterChange('volume', value)}
                        marks={{
                          0.1: '轻',
                          1.0: '正常',
                          2.0: '响'
                        }}
                      />
                    </Form.Item>
                  </Col>
                </Row>
              </Card>

              <Collapse style={{ marginTop: 16 }}>
                <Panel
                  header={
                    <div>
                      <ExperimentOutlined style={{ marginRight: 8 }} />
                      高级参数调节
                    </div>
                  }
                  key="advanced"
                >
                  <Tabs defaultActiveKey="timing">
                    <TabPane tab="时间控制" key="timing">
                      <Row gutter={16}>
                        <Col xs={24} md={12}>
                          <Form.Item
                            name="pause_time"
                            label={`停顿时长: ${parameters.pause_time.toFixed(2)}s`}
                          >
                            <Slider
                              min={0.1}
                              max={2.0}
                              step={0.1}
                              value={parameters.pause_time}
                              onChange={value => handleParameterChange('pause_time', value)}
                            />
                          </Form.Item>
                        </Col>
                        <Col xs={24} md={12}>
                          <Form.Item
                            name="breath_length"
                            label={`换气时长: ${parameters.breath_length.toFixed(2)}s`}
                          >
                            <Slider
                              min={0.1}
                              max={1.0}
                              step={0.1}
                              value={parameters.breath_length}
                              onChange={value => handleParameterChange('breath_length', value)}
                            />
                          </Form.Item>
                        </Col>
                        <Col xs={24} md={12}>
                          <Form.Item
                            name="word_gap"
                            label={`词间距: ${parameters.word_gap.toFixed(3)}s`}
                          >
                            <Slider
                              min={0.01}
                              max={0.2}
                              step={0.01}
                              value={parameters.word_gap}
                              onChange={value => handleParameterChange('word_gap', value)}
                            />
                          </Form.Item>
                        </Col>
                        <Col xs={24} md={12}>
                          <Form.Item
                            name="sentence_gap"
                            label={`句间距: ${parameters.sentence_gap.toFixed(2)}s`}
                          >
                            <Slider
                              min={0.2}
                              max={2.0}
                              step={0.1}
                              value={parameters.sentence_gap}
                              onChange={value => handleParameterChange('sentence_gap', value)}
                            />
                          </Form.Item>
                        </Col>
                      </Row>
                    </TabPane>

                    <TabPane tab="音质控制" key="quality">
                      <Row gutter={16}>
                        <Col xs={24} md={12}>
                          <Form.Item
                            name="noise_scale"
                            label={`噪声尺度: ${parameters.noise_scale.toFixed(3)}`}
                          >
                            <Slider
                              min={0.1}
                              max={1.0}
                              step={0.001}
                              value={parameters.noise_scale}
                              onChange={value => handleParameterChange('noise_scale', value)}
                            />
                          </Form.Item>
                        </Col>
                        <Col xs={24} md={12}>
                          <Form.Item
                            name="noise_scale_w"
                            label={`噪声权重: ${parameters.noise_scale_w.toFixed(3)}`}
                          >
                            <Slider
                              min={0.1}
                              max={1.0}
                              step={0.001}
                              value={parameters.noise_scale_w}
                              onChange={value => handleParameterChange('noise_scale_w', value)}
                            />
                          </Form.Item>
                        </Col>
                        <Col xs={24} md={12}>
                          <Form.Item
                            name="length_scale"
                            label={`长度尺度: ${parameters.length_scale.toFixed(3)}`}
                          >
                            <Slider
                              min={0.5}
                              max={2.0}
                              step={0.01}
                              value={parameters.length_scale}
                              onChange={value => handleParameterChange('length_scale', value)}
                            />
                          </Form.Item>
                        </Col>
                        <Col xs={24} md={12}>
                          <Form.Item
                            name="energy_scale"
                            label={`能量尺度: ${parameters.energy_scale.toFixed(3)}`}
                          >
                            <Slider
                              min={0.5}
                              max={2.0}
                              step={0.01}
                              value={parameters.energy_scale}
                              onChange={value => handleParameterChange('energy_scale', value)}
                            />
                          </Form.Item>
                        </Col>
                      </Row>
                    </TabPane>

                    <TabPane tab="重点词语" key="emphasis">
                      <Form.Item
                        name="emphasis_words"
                        label="需要强调的词语"
                        help="输入需要强调的词语，用逗号分隔"
                      >
                        <Select
                          mode="tags"
                          placeholder="输入需要强调的词语"
                          value={parameters.emphasis_words}
                          onChange={value => handleParameterChange('emphasis_words', value)}
                          tokenSeparators={[',']}
                        />
                      </Form.Item>
                    </TabPane>
                  </Tabs>
                </Panel>
              </Collapse>
            </Form>
          </Col>

          <Col xs={24} lg={8}>
            <Card title="预览控制" size="small">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Button
                  type="primary"
                  size="large"
                  icon={<AudioOutlined />}
                  loading={generating}
                  onClick={() => handleGenerate()}
                  block
                  disabled={!parameters.text || !parameters.speaker_id}
                >
                  生成语音
                </Button>

                <Button
                  size="large"
                  icon={playing ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
                  onClick={handlePlay}
                  disabled={!currentAudio}
                  block
                >
                  {playing ? '暂停播放' : '播放预览'}
                </Button>

                <Row gutter={8}>
                  <Col span={12}>
                    <Button
                      icon={<SaveOutlined />}
                      onClick={() => setPresetModalVisible(true)}
                      block
                    >
                      保存预设
                    </Button>
                  </Col>
                  <Col span={12}>
                    <Button
                      icon={<ReloadOutlined />}
                      onClick={handleReset}
                      block
                    >
                      重置参数
                    </Button>
                  </Col>
                </Row>

                <Button
                  icon={<HistoryOutlined />}
                  onClick={() => setHistoryModalVisible(true)}
                  block
                >
                  查看历史
                </Button>
              </Space>
            </Card>

            <Card title="实时建议" size="small" style={{ marginTop: 16 }}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Alert
                  message="参数建议"
                  description="当前配置适合正式场景使用，建议适当降低语速以提高清晰度。"
                  type="info"
                  showIcon
                  style={{ fontSize: 12 }}
                />

                <div>
                  <Text strong style={{ fontSize: 12 }}>质量评估:</Text>
                  <Progress
                    percent={88}
                    size="small"
                    strokeColor="#52c41a"
                    style={{ marginTop: 4 }}
                  />
                </div>

                <div>
                  <Text strong style={{ fontSize: 12 }}>推荐场景:</Text>
                  <div style={{ marginTop: 4 }}>
                    <Tag size="small">新闻播报</Tag>
                    <Tag size="small">正式演讲</Tag>
                  </div>
                </div>
              </Space>
            </Card>

            <Card title="常用预设" size="small" style={{ marginTop: 16 }}>
              <Space direction="vertical" style={{ width: '100%' }}>
                {presets.slice(0, 3).map(preset => (
                  <Button
                    key={preset.id}
                    type={selectedPreset === preset.id ? 'primary' : 'default'}
                    size="small"
                    onClick={() => handlePresetSelect(preset.id)}
                    block
                    style={{ textAlign: 'left', height: 'auto', padding: '8px 16px' }}
                  >
                    <div>
                      <div style={{ fontWeight: 'bold' }}>{preset.name}</div>
                      <div style={{ fontSize: 11, opacity: 0.7 }}>{preset.description}</div>
                      <div style={{ fontSize: 11, marginTop: 2 }}>
                        <StarOutlined style={{ marginRight: 4 }} />
                        {preset.rating} · {preset.usage_count} 次使用
                      </div>
                    </div>
                  </Button>
                ))}
              </Space>
            </Card>
          </Col>
        </Row>
      </Card>

      <audio ref={audioRef} />

      {/* 保存预设模态框 */}
      <Modal
        title="保存参数预设"
        open={presetModalVisible}
        onCancel={() => setPresetModalVisible(false)}
        footer={null}
        width={500}
      >
        <Form layout="vertical" onFinish={handleSavePreset}>
          <Form.Item
            name="name"
            label="预设名称"
            rules={[{ required: true, message: '请输入预设名称' }]}
          >
            <Input placeholder="为您的预设起一个名字" />
          </Form.Item>

          <Form.Item
            name="description"
            label="预设描述"
          >
            <TextArea rows={3} placeholder="描述这个预设的特点和用途..." />
          </Form.Item>

          <Form.Item
            name="category"
            label="预设分类"
            rules={[{ required: true, message: '请选择分类' }]}
          >
            <Select placeholder="选择分类">
              <Option value="professional">专业</Option>
              <Option value="casual">休闲</Option>
              <Option value="entertainment">娱乐</Option>
              <Option value="education">教育</Option>
            </Select>
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                保存预设
              </Button>
              <Button onClick={() => setPresetModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 历史记录模态框 */}
      <Modal
        title="生成历史"
        open={historyModalVisible}
        onCancel={() => setHistoryModalVisible(false)}
        footer={null}
        width={800}
      >
        <Table
          dataSource={history}
          columns={historyColumns}
          pagination={{ pageSize: 10 }}
          size="small"
          rowKey="id"
        />
      </Modal>
    </div>
  )
}

export default VoiceAudioTune