/**
 * Mix All Content Create Component
 * 混合内容创作组件 - [MixAll][Content][Create]
 */

import React, { useState, useRef, useCallback, useEffect } from 'react'
import {
  Card,
  Steps,
  Form,
  Input,
  Select,
  Upload,
  Button,
  Typography,
  Row,
  Col,
  Space,
  Divider,
  Timeline,
  Progress,
  Alert,
  Modal,
  Table,
  Tag,
  Tooltip,
  Collapse,
  Switch,
  Slider,
  message,
  Tabs,
  List,
  Avatar,
  Badge,
  Popconfirm
} from 'antd'
import {
  PlusOutlined,
  DeleteOutlined,
  EditOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  SoundOutlined,
  FileImageOutlined,
  FileTextOutlined,
  VideoCameraOutlined,
  DownloadOutlined,
  UploadOutlined,
  EyeOutlined,
  CheckOutlined,
  LoadingOutlined,
  ThunderboltOutlined,
  SettingOutlined,
  BulbOutlined,
  StarOutlined,
  ClockCircleOutlined,
  TeamOutlined,
  RobotOutlined
} from '@ant-design/icons'
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd'
import { useVoiceService } from '../../hooks/voice/useVoiceService'

const { Title, Paragraph, Text } = Typography
const { TextArea } = Input
const { Option } = Select
const { Step } = Steps
const { Panel } = Collapse
const { TabPane } = Tabs

// ================================
// 类型定义 - Types
// ================================

type ContentType = 'text' | 'voice' | 'image' | 'video' | 'music'
type ContentStatus = 'draft' | 'processing' | 'completed' | 'failed'
type OutputFormat = 'video' | 'audio' | 'slideshow' | 'webpage' | 'ebook'

interface ContentBlock {
  id: string
  type: ContentType
  title: string
  content: any
  duration?: number
  file_url?: string
  file_size?: number
  position: number
  status: ContentStatus
  settings: Record<string, any>
  created_at: string
}

interface TextContentBlock extends ContentBlock {
  type: 'text'
  content: {
    text: string
    font_family?: string
    font_size?: number
    color?: string
    background_color?: string
    animation?: string
    display_duration?: number
  }
}

interface VoiceContentBlock extends ContentBlock {
  type: 'voice'
  content: {
    text: string
    voice_id: string
    voice_name: string
    speed: number
    pitch: number
    volume: number
    emotion: string
    style: string
  }
}

interface ImageContentBlock extends ContentBlock {
  type: 'image'
  content: {
    image_url: string
    alt_text?: string
    width?: number
    height?: number
    animation?: string
    display_duration?: number
    effects?: string[]
  }
}

interface VideoContentBlock extends ContentBlock {
  type: 'video'
  content: {
    video_url: string
    thumbnail_url?: string
    start_time?: number
    end_time?: number
    volume?: number
    effects?: string[]
  }
}

interface MixAllProject {
  id: string
  name: string
  description: string
  output_format: OutputFormat
  total_duration: number
  blocks: ContentBlock[]
  settings: {
    resolution?: string
    frame_rate?: number
    audio_quality?: string
    video_quality?: string
    background_music?: string
    transitions?: string
  }
  status: ContentStatus
  created_at: string
  updated_at: string
}

interface RenderProgress {
  total_steps: number
  current_step: number
  current_step_name: string
  progress_percentage: number
  estimated_time_remaining: number
  preview_url?: string
}

// ================================
// 主组件
// ================================

const MixAllContentCreate: React.FC = () => {
  const [form] = Form.useForm()
  const [currentStep, setCurrentStep] = useState(0)
  const [project, setProject] = useState<MixAllProject | null>(null)
  const [contentBlocks, setContentBlocks] = useState<ContentBlock[]>([])
  const [selectedBlock, setSelectedBlock] = useState<ContentBlock | null>(null)
  const [rendering, setRendering] = useState(false)
  const [renderProgress, setRenderProgress] = useState<RenderProgress | null>(null)
  const [previewVisible, setPreviewVisible] = useState(false)
  const [settingsVisible, setSettingsVisible] = useState(false)
  const [playingBlock, setPlayingBlock] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState('blocks')
  const fileInputRef = useRef<HTMLInputElement>(null)

  // 语音服务集成
  const {
    availableVoices,
    selectedVoice,
    synthesizing,
    playing,
    synthesizeText,
    loadAvailableVoices,
    selectVoice,
    playAudio,
    stopAudio
  } = useVoiceService()

  const outputFormatOptions = [
    { label: '视频 (MP4)', value: 'video', icon: <VideoCameraOutlined /> },
    { label: '音频 (MP3)', value: 'audio', icon: <SoundOutlined /> },
    { label: '幻灯片 (HTML)', value: 'slideshow', icon: <FileImageOutlined /> },
    { label: '网页 (HTML)', value: 'webpage', icon: <FileTextOutlined /> },
    { label: '电子书 (EPUB)', value: 'ebook', icon: <FileTextOutlined /> }
  ]

  const contentTypeOptions = [
    { label: '文本内容', value: 'text', icon: <FileTextOutlined />, color: 'blue' },
    { label: '语音合成', value: 'voice', icon: <SoundOutlined />, color: 'green' },
    { label: '图像素材', value: 'image', icon: <FileImageOutlined />, color: 'orange' },
    { label: '视频片段', value: 'video', icon: <VideoCameraOutlined />, color: 'red' },
    { label: '背景音乐', value: 'music', icon: <SoundOutlined />, color: 'purple' }
  ]

  const animationOptions = [
    { label: '无动画', value: 'none' },
    { label: '淡入淡出', value: 'fade' },
    { label: '滑动进入', value: 'slide' },
    { label: '缩放效果', value: 'zoom' },
    { label: '旋转效果', value: 'rotate' },
    { label: '弹跳效果', value: 'bounce' }
  ]

  const transitionOptions = [
    { label: '直接切换', value: 'cut' },
    { label: '淡入淡出', value: 'fade' },
    { label: '滑动过渡', value: 'slide' },
    { label: '擦除过渡', value: 'wipe' },
    { label: '溶解过渡', value: 'dissolve' }
  ]

  // ================================
  // 初始化和语音预览 - Initialization & Voice Preview
  // ================================

  useEffect(() => {
    // 组件挂载时加载可用音色
    loadAvailableVoices()
  }, [loadAvailableVoices])

  const handleVoicePreview = async (block: VoiceContentBlock) => {
    if (!block.content.text.trim()) {
      message.warning('请先输入要合成的文本')
      return
    }

    try {
      const result = await synthesizeText(block.content.text, {
        timbre_id: block.content.voice_id,
        speed: block.content.speed,
        pitch: block.content.pitch,
        volume: block.content.volume,
        emotion: block.content.emotion,
        style: block.content.style
      })

      if (result.audio_url) {
        await playAudio(result.audio_url)
      }
    } catch (error) {
      console.error('Voice preview failed:', error)
      message.error('语音预览失败')
    }
  }

  const handleBlockPlayToggle = async (block: ContentBlock) => {
    if (playingBlock === block.id) {
      stopAudio()
      setPlayingBlock(null)
    } else {
      if (block.type === 'voice') {
        await handleVoicePreview(block as VoiceContentBlock)
        setPlayingBlock(block.id)
      } else if (block.type === 'music' && block.content.audio_url) {
        await playAudio(block.content.audio_url)
        setPlayingBlock(block.id)
      }
    }
  }

  // ================================
  // 项目管理 - Project Management
  // ================================

  const handleProjectCreate = async (values: any) => {
    try {
      const newProject: MixAllProject = {
        id: Date.now().toString(),
        name: values.name,
        description: values.description || '',
        output_format: values.output_format,
        total_duration: 0,
        blocks: [],
        settings: {
          resolution: values.resolution || '1920x1080',
          frame_rate: values.frame_rate || 30,
          audio_quality: values.audio_quality || 'high',
          video_quality: values.video_quality || 'high',
          background_music: values.background_music || '',
          transitions: values.transitions || 'fade'
        },
        status: 'draft',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }

      setProject(newProject)
      setCurrentStep(1)
      message.success('项目创建成功！')
    } catch (error) {
      console.error('Project creation failed:', error)
      message.error('项目创建失败')
    }
  }

  const handleProjectSave = async () => {
    if (!project) return

    try {
      const updatedProject = {
        ...project,
        blocks: contentBlocks,
        total_duration: calculateTotalDuration(),
        updated_at: new Date().toISOString()
      }

      // 这里应该调用API保存项目
      // await mixAllContentService.saveProject(updatedProject)
      
      setProject(updatedProject)
      message.success('项目已保存')
    } catch (error) {
      console.error('Project save failed:', error)
      message.error('项目保存失败')
    }
  }

  // ================================
  // 内容块管理 - Content Block Management
  // ================================

  const handleAddContentBlock = (type: ContentType) => {
    const newBlock: ContentBlock = {
      id: `block_${Date.now()}`,
      type,
      title: `${getContentTypeLabel(type)} ${contentBlocks.length + 1}`,
      content: getDefaultContent(type),
      duration: type === 'text' ? 5 : undefined,
      position: contentBlocks.length,
      status: 'draft',
      settings: {},
      created_at: new Date().toISOString()
    }

    setContentBlocks(prev => [...prev, newBlock])
    setSelectedBlock(newBlock)
    message.success(`添加了${getContentTypeLabel(type)}`)
  }

  const handleUpdateContentBlock = (blockId: string, updates: Partial<ContentBlock>) => {
    setContentBlocks(prev => prev.map(block => 
      block.id === blockId 
        ? { ...block, ...updates, updated_at: new Date().toISOString() }
        : block
    ))

    if (selectedBlock?.id === blockId) {
      setSelectedBlock(prev => prev ? { ...prev, ...updates } : null)
    }
  }

  const handleDeleteContentBlock = (blockId: string) => {
    setContentBlocks(prev => prev.filter(block => block.id !== blockId))
    
    if (selectedBlock?.id === blockId) {
      setSelectedBlock(null)
    }
    
    message.success('内容块已删除')
  }

  const handleDragEnd = (result: any) => {
    if (!result.destination) return

    const items = Array.from(contentBlocks)
    const [reorderedItem] = items.splice(result.source.index, 1)
    items.splice(result.destination.index, 0, reorderedItem)

    // 重新设置位置
    const reorderedBlocks = items.map((block, index) => ({
      ...block,
      position: index
    }))

    setContentBlocks(reorderedBlocks)
  }

  const getDefaultContent = (type: ContentType): any => {
    switch (type) {
      case 'text':
        return {
          text: '请输入文本内容...',
          font_family: 'Arial',
          font_size: 24,
          color: '#000000',
          background_color: 'transparent',
          animation: 'fade',
          display_duration: 5
        }
      case 'voice':
        return {
          text: '请输入要合成的文本...',
          voice_id: '',
          voice_name: '',
          speed: 1.0,
          pitch: 1.0,
          volume: 1.0,
          emotion: 'neutral',
          style: 'normal'
        }
      case 'image':
        return {
          image_url: '',
          alt_text: '',
          animation: 'fade',
          display_duration: 5,
          effects: []
        }
      case 'video':
        return {
          video_url: '',
          start_time: 0,
          volume: 1.0,
          effects: []
        }
      case 'music':
        return {
          audio_url: '',
          volume: 0.5,
          loop: true,
          fade: false
        }
      default:
        return {}
    }
  }

  const getContentTypeLabel = (type: ContentType): string => {
    const option = contentTypeOptions.find(opt => opt.value === type)
    return option?.label || type
  }

  const getContentTypeIcon = (type: ContentType) => {
    const option = contentTypeOptions.find(opt => opt.value === type)
    return option?.icon || <FileTextOutlined />
  }

  const getContentTypeColor = (type: ContentType): string => {
    const option = contentTypeOptions.find(opt => opt.value === type)
    return option?.color || 'default'
  }

  // ================================
  // 渲染和导出 - Rendering and Export
  // ================================

  const handleStartRender = async () => {
    if (!project || contentBlocks.length === 0) {
      message.error('请先添加内容块')
      return
    }

    setRendering(true)
    setRenderProgress({
      total_steps: 5,
      current_step: 1,
      current_step_name: '准备渲染环境',
      progress_percentage: 0,
      estimated_time_remaining: 120
    })

    try {
      // 模拟渲染过程
      const steps = [
        { name: '准备渲染环境', duration: 2000 },
        { name: '处理文本内容', duration: 3000 },
        { name: '合成语音内容', duration: 5000 },
        { name: '处理图像和视频', duration: 4000 },
        { name: '合成最终输出', duration: 3000 }
      ]

      for (let i = 0; i < steps.length; i++) {
        const step = steps[i]
        const progress = ((i + 1) / steps.length) * 100

        setRenderProgress(prev => prev ? {
          ...prev,
          current_step: i + 1,
          current_step_name: step.name,
          progress_percentage: progress,
          estimated_time_remaining: Math.max(0, prev.estimated_time_remaining - step.duration / 1000)
        } : null)

        await new Promise(resolve => setTimeout(resolve, step.duration))
      }

      // 渲染完成
      setRenderProgress(prev => prev ? {
        ...prev,
        progress_percentage: 100,
        current_step_name: '渲染完成',
        estimated_time_remaining: 0,
        preview_url: '/output/preview.mp4'
      } : null)

      setCurrentStep(3)
      message.success('内容渲染完成！')
    } catch (error) {
      console.error('Rendering failed:', error)
      message.error('渲染失败，请重试')
    } finally {
      setRendering(false)
    }
  }

  const calculateTotalDuration = (): number => {
    return contentBlocks.reduce((total, block) => {
      return total + (block.duration || 0)
    }, 0)
  }

  const handleFileUpload = useCallback((file: File, type: ContentType) => {
    const fileUrl = URL.createObjectURL(file)
    
    if (type === 'image') {
      const img = new Image()
      img.onload = () => {
        handleAddContentBlock(type)
        const newBlockId = `block_${Date.now()}`
        handleUpdateContentBlock(newBlockId, {
          title: file.name,
          content: {
            image_url: fileUrl,
            alt_text: file.name,
            width: img.width,
            height: img.height,
            animation: 'fade',
            display_duration: 5,
            effects: []
          },
          file_url: fileUrl,
          file_size: file.size
        })
      }
      img.src = fileUrl
    } else if (type === 'video') {
      const video = document.createElement('video')
      video.onloadedmetadata = () => {
        handleAddContentBlock(type)
        const newBlockId = `block_${Date.now()}`
        handleUpdateContentBlock(newBlockId, {
          title: file.name,
          content: {
            video_url: fileUrl,
            thumbnail_url: fileUrl,
            volume: 1.0,
            effects: []
          },
          duration: video.duration,
          file_url: fileUrl,
          file_size: file.size
        })
      }
      video.src = fileUrl
    }

    return false // 阻止默认上传
  }, [])

  // ================================
  // 渲染组件
  // ================================

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return renderProjectSetup()
      case 1:
        return renderContentComposition()
      case 2:
        return renderRenderingProgress()
      case 3:
        return renderCompletedProject()
      default:
        return null
    }
  }

  const renderProjectSetup = () => (
    <Card title="项目设置" size="small">
      <Form form={form} layout="vertical" onFinish={handleProjectCreate}>
        <Row gutter={24}>
          <Col xs={24} lg={12}>
            <Form.Item
              name="name"
              label="项目名称"
              rules={[{ required: true, message: '请输入项目名称' }]}
            >
              <Input placeholder="为您的混合内容项目起一个名字" />
            </Form.Item>

            <Form.Item
              name="description"
              label="项目描述"
            >
              <TextArea
                rows={3}
                placeholder="描述这个项目的用途和特点..."
              />
            </Form.Item>

            <Form.Item
              name="output_format"
              label="输出格式"
              rules={[{ required: true, message: '请选择输出格式' }]}
              initialValue="video"
            >
              <Select placeholder="选择最终输出格式">
                {outputFormatOptions.map(option => (
                  <Option key={option.value} value={option.value}>
                    <Space>
                      {option.icon}
                      {option.label}
                    </Space>
                  </Option>
                ))}
              </Select>
            </Form.Item>
          </Col>

          <Col xs={24} lg={12}>
            <Form.Item
              name="resolution"
              label="分辨率"
              initialValue="1920x1080"
            >
              <Select>
                <Option value="1920x1080">1920x1080 (Full HD)</Option>
                <Option value="1280x720">1280x720 (HD)</Option>
                <Option value="3840x2160">3840x2160 (4K)</Option>
                <Option value="1080x1920">1080x1920 (竖屏)</Option>
              </Select>
            </Form.Item>

            <Form.Item
              name="frame_rate"
              label="帧率"
              initialValue={30}
            >
              <Select>
                <Option value={24}>24 FPS (电影)</Option>
                <Option value={30}>30 FPS (标准)</Option>
                <Option value={60}>60 FPS (高帧率)</Option>
              </Select>
            </Form.Item>

            <Form.Item
              name="transitions"
              label="默认过渡效果"
              initialValue="fade"
            >
              <Select>
                {transitionOptions.map(option => (
                  <Option key={option.value} value={option.value}>
                    {option.label}
                  </Option>
                ))}
              </Select>
            </Form.Item>
          </Col>
        </Row>

        <Form.Item>
          <Space>
            <Button type="primary" htmlType="submit" size="large">
              创建项目
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Card>
  )

  const renderContentComposition = () => (
    <Row gutter={16}>
      <Col xs={24} lg={18}>
        <Card title="内容编辑区" size="small">
          <Tabs activeKey={activeTab} onChange={setActiveTab}>
            <TabPane tab="内容块" key="blocks">
              <div style={{ marginBottom: 16 }}>
                <Space wrap>
                  {contentTypeOptions.map(option => (
                    <Button
                      key={option.value}
                      icon={option.icon}
                      onClick={() => handleAddContentBlock(option.value as ContentType)}
                    >
                      添加{option.label}
                    </Button>
                  ))}
                </Space>
              </div>

              <DragDropContext onDragEnd={handleDragEnd}>
                <Droppable droppableId="content-blocks">
                  {(provided) => (
                    <div {...provided.droppableProps} ref={provided.innerRef}>
                      {contentBlocks.map((block, index) => (
                        <Draggable key={block.id} draggableId={block.id} index={index}>
                          {(provided, snapshot) => (
                            <div
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              style={{
                                ...provided.draggableProps.style,
                                marginBottom: 8
                              }}
                            >
                              <Card
                                size="small"
                                style={{
                                  backgroundColor: snapshot.isDragging ? '#f0f0f0' : 'white',
                                  border: selectedBlock?.id === block.id ? '2px solid #1890ff' : '1px solid #d9d9d9'
                                }}
                                title={
                                  <Space>
                                    <div {...provided.dragHandleProps}>
                                      <Text type="secondary">⋮⋮</Text>
                                    </div>
                                    <Badge color={getContentTypeColor(block.type)} />
                                    {getContentTypeIcon(block.type)}
                                    <Text strong>{block.title}</Text>
                                    <Tag color={getContentTypeColor(block.type)}>
                                      {getContentTypeLabel(block.type)}
                                    </Tag>
                                    {block.duration && (
                                      <Tag>{block.duration}s</Tag>
                                    )}
                                  </Space>
                                }
                                extra={
                                  <Space>
                                    <Button
                                      type="text"
                                      icon={<EditOutlined />}
                                      onClick={() => setSelectedBlock(block)}
                                    />
                                    {(block.type === 'voice' || block.type === 'music') && (
                                      <Button
                                        type="text"
                                        icon={playingBlock === block.id ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
                                        loading={synthesizing && block.type === 'voice'}
                                        onClick={() => handleBlockPlayToggle(block)}
                                      />
                                    )}
                                    <Popconfirm
                                      title="确认删除这个内容块吗？"
                                      onConfirm={() => handleDeleteContentBlock(block.id)}
                                    >
                                      <Button
                                        type="text"
                                        danger
                                        icon={<DeleteOutlined />}
                                      />
                                    </Popconfirm>
                                  </Space>
                                }
                                onClick={() => setSelectedBlock(block)}
                              >
                                <div style={{ fontSize: 12, color: '#666' }}>
                                  {block.type === 'text' && block.content.text}
                                  {block.type === 'voice' && `"${block.content.text}" - ${block.content.voice_name || '未选择音色'}`}
                                  {block.type === 'image' && `图片: ${block.content.alt_text || '未命名'}`}
                                  {block.type === 'video' && `视频: ${block.title}`}
                                  {block.type === 'music' && `音乐: ${block.title}`}
                                </div>
                              </Card>
                            </div>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                    </div>
                  )}
                </Droppable>
              </DragDropContext>

              {contentBlocks.length === 0 && (
                <div style={{ textAlign: 'center', padding: 40 }}>
                  <RobotOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />
                  <div style={{ marginTop: 16 }}>
                    <Text type="secondary">还没有内容块，点击上方按钮开始添加</Text>
                  </div>
                </div>
              )}
            </TabPane>

            <TabPane tab="时间轴预览" key="timeline">
              <Timeline mode="left">
                {contentBlocks.map((block, index) => (
                  <Timeline.Item
                    key={block.id}
                    color={getContentTypeColor(block.type)}
                    dot={getContentTypeIcon(block.type)}
                    label={`${index * 5}s - ${(index + 1) * 5}s`}
                  >
                    <Space direction="vertical">
                      <Text strong>{block.title}</Text>
                      <Text type="secondary">
                        {getContentTypeLabel(block.type)} • {block.duration || 5}秒
                      </Text>
                    </Space>
                  </Timeline.Item>
                ))}
              </Timeline>
            </TabPane>
          </Tabs>
        </Card>
      </Col>

      <Col xs={24} lg={6}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Card title="项目信息" size="small">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>项目名称:</Text>
                <br />
                <Text>{project?.name}</Text>
              </div>
              <div>
                <Text strong>输出格式:</Text>
                <br />
                <Text>{project?.output_format}</Text>
              </div>
              <div>
                <Text strong>内容块数量:</Text>
                <br />
                <Text>{contentBlocks.length} 个</Text>
              </div>
              <div>
                <Text strong>总时长:</Text>
                <br />
                <Text>{calculateTotalDuration()} 秒</Text>
              </div>
            </Space>
          </Card>

          {selectedBlock && (
            <Card title="属性编辑" size="small">
              {renderBlockEditor(selectedBlock)}
            </Card>
          )}

          <Card title="操作" size="small">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Button
                type="primary"
                icon={<ThunderboltOutlined />}
                onClick={handleStartRender}
                disabled={contentBlocks.length === 0}
                block
              >
                开始渲染
              </Button>
              <Button
                icon={<SettingOutlined />}
                onClick={() => setSettingsVisible(true)}
                block
              >
                项目设置
              </Button>
              <Button
                icon={<EyeOutlined />}
                onClick={() => setPreviewVisible(true)}
                disabled={contentBlocks.length === 0}
                block
              >
                预览项目
              </Button>
            </Space>
          </Card>
        </Space>
      </Col>
    </Row>
  )

  const renderBlockEditor = (block: ContentBlock) => {
    switch (block.type) {
      case 'text':
        return (
          <Space direction="vertical" style={{ width: '100%' }}>
            <div>
              <Text strong>文本内容:</Text>
              <TextArea
                rows={3}
                value={block.content.text}
                onChange={e => handleUpdateContentBlock(block.id, {
                  content: { ...block.content, text: e.target.value }
                })}
              />
            </div>
            <div>
              <Text strong>显示时长 (秒):</Text>
              <Slider
                min={1}
                max={30}
                value={block.content.display_duration}
                onChange={value => handleUpdateContentBlock(block.id, {
                  content: { ...block.content, display_duration: value },
                  duration: value
                })}
              />
            </div>
            <div>
              <Text strong>字体大小:</Text>
              <Slider
                min={12}
                max={72}
                value={block.content.font_size}
                onChange={value => handleUpdateContentBlock(block.id, {
                  content: { ...block.content, font_size: value }
                })}
              />
            </div>
            <div>
              <Text strong>动画效果:</Text>
              <Select
                value={block.content.animation}
                onChange={value => handleUpdateContentBlock(block.id, {
                  content: { ...block.content, animation: value }
                })}
                style={{ width: '100%' }}
              >
                {animationOptions.map(option => (
                  <Option key={option.value} value={option.value}>
                    {option.label}
                  </Option>
                ))}
              </Select>
            </div>
          </Space>
        )
      
      case 'voice':
        return (
          <Space direction="vertical" style={{ width: '100%' }}>
            <div>
              <Text strong>文本内容:</Text>
              <TextArea
                rows={3}
                value={block.content.text}
                onChange={e => handleUpdateContentBlock(block.id, {
                  content: { ...block.content, text: e.target.value }
                })}
              />
            </div>
            <div>
              <Text strong>音色选择:</Text>
              <Select
                value={block.content.voice_id}
                onChange={value => {
                  const voice = availableVoices.find(v => v.timbre_id === value)
                  handleUpdateContentBlock(block.id, {
                    content: { 
                      ...block.content, 
                      voice_id: value,
                      voice_name: voice?.timbre_name || ''
                    }
                  })
                }}
                placeholder="选择音色"
                style={{ width: '100%' }}
                loading={!availableVoices.length}
              >
                {availableVoices.map(voice => (
                  <Option key={voice.timbre_id} value={voice.timbre_id}>
                    <Space>
                      <Text>{voice.timbre_name}</Text>
                      <Tag size="small" color={voice.voice_gender === 'female' ? 'pink' : 'blue'}>
                        {voice.voice_gender === 'female' ? '女声' : '男声'}
                      </Tag>
                      {voice.is_custom && <Tag size="small" color="orange">自定义</Tag>}
                    </Space>
                  </Option>
                ))}
              </Select>
            </div>
            <div>
              <Text strong>语速: {block.content.speed}x</Text>
              <Slider
                min={0.5}
                max={2.0}
                step={0.1}
                value={block.content.speed}
                onChange={value => handleUpdateContentBlock(block.id, {
                  content: { ...block.content, speed: value }
                })}
              />
            </div>
            <div>
              <Text strong>音调: {block.content.pitch}x</Text>
              <Slider
                min={0.5}
                max={2.0}
                step={0.1}
                value={block.content.pitch}
                onChange={value => handleUpdateContentBlock(block.id, {
                  content: { ...block.content, pitch: value }
                })}
              />
            </div>
            <div>
              <Text strong>音量: {Math.round(block.content.volume * 100)}%</Text>
              <Slider
                min={0}
                max={1}
                step={0.1}
                value={block.content.volume}
                onChange={value => handleUpdateContentBlock(block.id, {
                  content: { ...block.content, volume: value }
                })}
              />
            </div>
            <div>
              <Text strong>情感:</Text>
              <Select
                value={block.content.emotion}
                onChange={value => handleUpdateContentBlock(block.id, {
                  content: { ...block.content, emotion: value }
                })}
                style={{ width: '100%' }}
              >
                <Option value="neutral">中性</Option>
                <Option value="happy">开心</Option>
                <Option value="sad">悲伤</Option>
                <Option value="angry">愤怒</Option>
                <Option value="calm">平静</Option>
                <Option value="excited">兴奋</Option>
              </Select>
            </div>
            <div style={{ marginTop: 8 }}>
              <Button
                type="primary"
                size="small"
                icon={playing && playingBlock === block.id ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
                loading={synthesizing}
                onClick={() => handleVoicePreview(block as VoiceContentBlock)}
                disabled={!block.content.text.trim() || !block.content.voice_id}
                block
              >
                {playing && playingBlock === block.id ? '停止预览' : '预览语音'}
              </Button>
            </div>
          </Space>
        )
      
      case 'image':
        return (
          <Space direction="vertical" style={{ width: '100%' }}>
            <div>
              <Text strong>图片上传:</Text>
              <Upload
                listType="picture"
                beforeUpload={file => {
                  const imageUrl = URL.createObjectURL(file)
                  handleUpdateContentBlock(block.id, {
                    content: { 
                      ...block.content, 
                      image_url: imageUrl,
                      alt_text: file.name
                    },
                    file_url: imageUrl,
                    file_size: file.size
                  })
                  return false
                }}
                showUploadList={false}
              >
                <Button icon={<UploadOutlined />}>选择图片</Button>
              </Upload>
              {block.content.image_url && (
                <div style={{ marginTop: 8 }}>
                  <img 
                    src={block.content.image_url} 
                    alt={block.content.alt_text}
                    style={{ width: '100%', maxHeight: 100, objectFit: 'cover' }}
                  />
                </div>
              )}
            </div>
            <div>
              <Text strong>显示时长 (秒):</Text>
              <Slider
                min={1}
                max={30}
                value={block.content.display_duration}
                onChange={value => handleUpdateContentBlock(block.id, {
                  content: { ...block.content, display_duration: value },
                  duration: value
                })}
              />
            </div>
            <div>
              <Text strong>动画效果:</Text>
              <Select
                value={block.content.animation}
                onChange={value => handleUpdateContentBlock(block.id, {
                  content: { ...block.content, animation: value }
                })}
                style={{ width: '100%' }}
              >
                {animationOptions.map(option => (
                  <Option key={option.value} value={option.value}>
                    {option.label}
                  </Option>
                ))}
              </Select>
            </div>
            <div>
              <Text strong>特效:</Text>
              <Select
                mode="multiple"
                value={block.content.effects}
                onChange={value => handleUpdateContentBlock(block.id, {
                  content: { ...block.content, effects: value }
                })}
                placeholder="选择特效"
                style={{ width: '100%' }}
              >
                <Option value="blur">模糊</Option>
                <Option value="sepia">复古</Option>
                <Option value="grayscale">黑白</Option>
                <Option value="brightness">亮度增强</Option>
                <Option value="contrast">对比度增强</Option>
              </Select>
            </div>
          </Space>
        )
      
      case 'video':
        return (
          <Space direction="vertical" style={{ width: '100%' }}>
            <div>
              <Text strong>视频上传:</Text>
              <Upload
                beforeUpload={file => {
                  const videoUrl = URL.createObjectURL(file)
                  handleUpdateContentBlock(block.id, {
                    content: { 
                      ...block.content, 
                      video_url: videoUrl,
                      thumbnail_url: videoUrl
                    },
                    file_url: videoUrl,
                    file_size: file.size
                  })
                  return false
                }}
                showUploadList={false}
                accept="video/*"
              >
                <Button icon={<UploadOutlined />}>选择视频</Button>
              </Upload>
              {block.content.video_url && (
                <div style={{ marginTop: 8 }}>
                  <video 
                    src={block.content.video_url}
                    style={{ width: '100%', maxHeight: 100 }}
                    controls
                  />
                </div>
              )}
            </div>
            <div>
              <Text strong>开始时间 (秒):</Text>
              <Slider
                min={0}
                max={300}
                value={block.content.start_time || 0}
                onChange={value => handleUpdateContentBlock(block.id, {
                  content: { ...block.content, start_time: value }
                })}
              />
            </div>
            <div>
              <Text strong>结束时间 (秒):</Text>
              <Slider
                min={0}
                max={300}
                value={block.content.end_time || 30}
                onChange={value => handleUpdateContentBlock(block.id, {
                  content: { ...block.content, end_time: value },
                  duration: value - (block.content.start_time || 0)
                })}
              />
            </div>
            <div>
              <Text strong>音量: {Math.round((block.content.volume || 1) * 100)}%</Text>
              <Slider
                min={0}
                max={1}
                step={0.1}
                value={block.content.volume || 1}
                onChange={value => handleUpdateContentBlock(block.id, {
                  content: { ...block.content, volume: value }
                })}
              />
            </div>
            <div>
              <Text strong>特效:</Text>
              <Select
                mode="multiple"
                value={block.content.effects}
                onChange={value => handleUpdateContentBlock(block.id, {
                  content: { ...block.content, effects: value }
                })}
                placeholder="选择特效"
                style={{ width: '100%' }}
              >
                <Option value="fade_in">淡入</Option>
                <Option value="fade_out">淡出</Option>
                <Option value="zoom">缩放</Option>
                <Option value="rotate">旋转</Option>
                <Option value="blur">模糊</Option>
              </Select>
            </div>
          </Space>
        )
      
      case 'music':
        return (
          <Space direction="vertical" style={{ width: '100%' }}>
            <div>
              <Text strong>音乐上传:</Text>
              <Upload
                beforeUpload={file => {
                  const audioUrl = URL.createObjectURL(file)
                  handleUpdateContentBlock(block.id, {
                    content: { 
                      ...block.content, 
                      audio_url: audioUrl
                    },
                    file_url: audioUrl,
                    file_size: file.size,
                    title: file.name
                  })
                  return false
                }}
                showUploadList={false}
                accept="audio/*"
              >
                <Button icon={<UploadOutlined />}>选择音乐</Button>
              </Upload>
              {block.content.audio_url && (
                <div style={{ marginTop: 8 }}>
                  <audio 
                    src={block.content.audio_url}
                    style={{ width: '100%' }}
                    controls
                  />
                </div>
              )}
            </div>
            <div>
              <Text strong>音量: {Math.round((block.content.volume || 0.5) * 100)}%</Text>
              <Slider
                min={0}
                max={1}
                step={0.1}
                value={block.content.volume || 0.5}
                onChange={value => handleUpdateContentBlock(block.id, {
                  content: { ...block.content, volume: value }
                })}
              />
            </div>
            <div>
              <Text strong>循环播放:</Text>
              <div style={{ marginTop: 8 }}>
                <Switch
                  checked={block.content.loop}
                  onChange={checked => handleUpdateContentBlock(block.id, {
                    content: { ...block.content, loop: checked }
                  })}
                  checkedChildren="开启"
                  unCheckedChildren="关闭"
                />
              </div>
            </div>
            <div>
              <Text strong>淡入淡出:</Text>
              <div style={{ marginTop: 8 }}>
                <Switch
                  checked={block.content.fade}
                  onChange={checked => handleUpdateContentBlock(block.id, {
                    content: { ...block.content, fade: checked }
                  })}
                  checkedChildren="开启"
                  unCheckedChildren="关闭"
                />
              </div>
            </div>
          </Space>
        )
      
      default:
        return <Text type="secondary">选择内容块查看编辑选项</Text>
    }
  }

  const renderRenderingProgress = () => (
    <Card title="渲染进度" size="small">
      <Space direction="vertical" style={{ width: '100%' }}>
        {renderProgress && (
          <>
            <div style={{ textAlign: 'center', marginBottom: 24 }}>
              <LoadingOutlined style={{ fontSize: 48, color: '#1890ff' }} />
              <Title level={4} style={{ marginTop: 16 }}>
                正在渲染您的混合内容...
              </Title>
              <Text type="secondary">
                {renderProgress.current_step_name}
              </Text>
            </div>

            <Progress
              percent={Math.round(renderProgress.progress_percentage)}
              status="active"
              format={percent => `${percent}%`}
            />

            <Row gutter={16}>
              <Col span={8}>
                <Text strong>当前步骤:</Text>
                <br />
                <Text>{renderProgress.current_step}/{renderProgress.total_steps}</Text>
              </Col>
              <Col span={8}>
                <Text strong>预计剩余:</Text>
                <br />
                <Text>{Math.round(renderProgress.estimated_time_remaining)}秒</Text>
              </Col>
              <Col span={8}>
                <Text strong>总进度:</Text>
                <br />
                <Text>{Math.round(renderProgress.progress_percentage)}%</Text>
              </Col>
            </Row>

            <Timeline>
              {Array.from({ length: renderProgress.total_steps }, (_, i) => (
                <Timeline.Item
                  key={i}
                  color={
                    i < renderProgress.current_step - 1 ? 'green' :
                    i === renderProgress.current_step - 1 ? 'blue' : 'gray'
                  }
                  dot={
                    i < renderProgress.current_step - 1 ? <CheckOutlined /> :
                    i === renderProgress.current_step - 1 ? <LoadingOutlined /> : 
                    <ClockCircleOutlined />
                  }
                >
                  步骤 {i + 1}
                </Timeline.Item>
              ))}
            </Timeline>
          </>
        )}
      </Space>
    </Card>
  )

  const renderCompletedProject = () => (
    <Card title="渲染完成" size="small">
      <div style={{ textAlign: 'center', marginBottom: 24 }}>
        <CheckOutlined style={{ fontSize: 48, color: '#52c41a' }} />
        <Title level={4} style={{ marginTop: 16 }}>
          混合内容创作完成！
        </Title>
        <Text type="secondary">
          您的项目已成功渲染，可以预览或下载了。
        </Text>
      </div>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card size="small">
            <Text strong>项目名称</Text>
            <br />
            <Text>{project?.name}</Text>
          </Card>
        </Col>
        <Col span={8}>
          <Card size="small">
            <Text strong>输出格式</Text>
            <br />
            <Text>{project?.output_format}</Text>
          </Card>
        </Col>
        <Col span={8}>
          <Card size="small">
            <Text strong>文件大小</Text>
            <br />
            <Text>25.8 MB</Text>
          </Card>
        </Col>
      </Row>

      <Space style={{ width: '100%', justifyContent: 'center' }}>
        <Button type="primary" icon={<EyeOutlined />} size="large">
          预览结果
        </Button>
        <Button icon={<DownloadOutlined />} size="large">
          下载文件
        </Button>
        <Button icon={<StarOutlined />} size="large">
          保存到模板
        </Button>
      </Space>
    </Card>
  )

  // ================================
  // 主渲染
  // ================================

  return (
    <div className="mixall-content-create">
      <Card>
        <Title level={2}>
          <RobotOutlined /> 混合内容创作工坊
        </Title>
        <Paragraph>
          融合文本、语音、图像、视频等多种媒体，创造丰富的多模态内容体验。
        </Paragraph>

        <Steps 
          current={currentStep} 
          style={{ marginBottom: 24 }}
          onChange={setCurrentStep}
        >
          <Step title="项目设置" description="配置基本参数" />
          <Step title="内容编辑" description="添加和编辑内容" />
          <Step title="渲染处理" description="生成最终作品" />
          <Step title="完成发布" description="预览和下载" />
        </Steps>

        {renderStepContent()}
      </Card>
    </div>
  )
}

export default MixAllContentCreate