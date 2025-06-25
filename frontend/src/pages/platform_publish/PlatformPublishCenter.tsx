/**
 * Platform Publish Center Component
 * 平台发布中心组件 - [Platform][Publish][Center]
 * 
 * 统一的多平台内容发布管理中心
 * 支持抖音、微信、小红书、B站、微博等平台的内容发布和管理
 */

import React, { useState, useEffect, useCallback } from 'react'
import {
  Card,
  Button,
  Typography,
  Row,
  Col,
  Space,
  Modal,
  Form,
  Input,
  Select,
  Upload,
  Switch,
  DatePicker,
  TimePicker,
  Tag,
  message,
  Tabs,
  Table,
  Progress,
  Badge,
  Tooltip,
  Popconfirm,
  Alert,
  Divider,
  Steps,
  List,
  Avatar,
  Statistic,
  Empty,
  Drawer,
  Checkbox,
  Radio,
  Spin,
  notification
} from 'antd'
import {
  PlusOutlined,
  SendOutlined,
  ScheduleOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
  SettingOutlined,
  CloudUploadOutlined,
  VideoCameraOutlined,
  FileImageOutlined,
  FileTextOutlined,
  SoundOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  StopOutlined,
  PlayCircleOutlined,
  ShareAltOutlined,
  BarChartOutlined,
  LinkOutlined,
  BellOutlined,
  ThunderboltOutlined,
  GlobalOutlined,
  TeamOutlined,
  CalendarOutlined,
  TagsOutlined
} from '@ant-design/icons'
import type { UploadFile, UploadProps } from 'antd/es/upload/interface'
import type { ColumnsType } from 'antd/es/table'
import moment from 'moment'
import {
  PlatformPublishType,
  PublishContentInfo,
  PublishParams,
  PublishResult,
  PublishTaskStatus,
  platformPublishManager
} from '../../services/platform_publish/platform_publish_adapter'

const { Title, Paragraph, Text } = Typography
const { TextArea } = Input
const { Option } = Select
const { TabPane } = Tabs
const { Step } = Steps
const { RangePicker } = DatePicker

// ================================
// 类型定义 - Types
// ================================

interface PublishTask {
  id: string
  title: string
  description: string
  content_type: 'video' | 'image' | 'audio' | 'text' | 'article'
  target_platforms: PlatformPublishType[]
  status: 'draft' | 'scheduled' | 'publishing' | 'published' | 'failed' | 'cancelled'
  created_at: string
  scheduled_time?: string
  published_time?: string
  results: PublishResult[]
  engagement_summary: {
    total_views: number
    total_likes: number
    total_comments: number
    total_shares: number
  }
  file_urls: {
    video_url?: string
    audio_url?: string
    images: string[]
    cover_image?: string
  }
  tags: string[]
  author: string
}

interface PlatformAccount {
  platform_type: PlatformPublishType
  account_name: string
  account_id: string
  avatar_url: string
  followers_count: number
  connected: boolean
  access_token: string
  expires_at: string
  daily_quota: number
  used_quota: number
}

// ================================
// 主组件
// ================================

const PlatformPublishCenter: React.FC = () => {
  const [tasks, setTasks] = useState<PublishTask[]>([])
  const [accounts, setAccounts] = useState<PlatformAccount[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedTask, setSelectedTask] = useState<PublishTask | null>(null)
  const [createModalVisible, setCreateModalVisible] = useState(false)
  const [editModalVisible, setEditModalVisible] = useState(false)
  const [detailDrawerVisible, setDetailDrawerVisible] = useState(false)
  const [settingsDrawerVisible, setSettingsDrawerVisible] = useState(false)
  const [activeTab, setActiveTab] = useState('all')
  const [currentStep, setCurrentStep] = useState(0)
  const [uploadFiles, setUploadFiles] = useState<UploadFile[]>([])
  const [form] = Form.useForm()

  const platformOptions = [
    { 
      value: 'douyin', 
      label: '抖音', 
      icon: '🎵', 
      color: '#000000',
      supportedTypes: ['video'],
      description: '短视频平台，支持15秒-15分钟视频'
    },
    { 
      value: 'wechat', 
      label: '微信公众号', 
      icon: '💬', 
      color: '#07C160',
      supportedTypes: ['article', 'image', 'video'],
      description: '图文消息平台，支持文章、图片、视频'
    },
    { 
      value: 'xiaohongshu', 
      label: '小红书', 
      icon: '📔', 
      color: '#FF2442',
      supportedTypes: ['image', 'video'],
      description: '生活方式平台，支持图文笔记和视频笔记'
    },
    { 
      value: 'bilibili', 
      label: 'B站', 
      icon: '📺', 
      color: '#00A1D6',
      supportedTypes: ['video'],
      description: '视频平台，支持长视频投稿'
    },
    { 
      value: 'weibo', 
      label: '微博', 
      icon: '🔥', 
      color: '#E6162D',
      supportedTypes: ['text', 'image'],
      description: '社交媒体平台，支持文字和图片微博'
    }
  ]

  const contentTypeOptions = [
    { value: 'video', label: '视频内容', icon: <VideoCameraOutlined />, color: 'red' },
    { value: 'image', label: '图片内容', icon: <FileImageOutlined />, color: 'orange' },
    { value: 'article', label: '图文文章', icon: <FileTextOutlined />, color: 'blue' },
    { value: 'audio', label: '音频内容', icon: <SoundOutlined />, color: 'green' },
    { value: 'text', label: '纯文本', icon: <FileTextOutlined />, color: 'default' }
  ]

  // ================================
  // 数据加载和管理 - Data Loading & Management
  // ================================

  useEffect(() => {
    loadTasks()
    loadAccounts()
  }, [])

  const loadTasks = async () => {
    setLoading(true)
    try {
      // 模拟API调用
      // const response = await platformPublishService.getTasks()
      
      // 模拟数据
      const mockTasks: PublishTask[] = [
        {
          id: 'task_001',
          title: '产品宣传视频 - DataSay AI创作平台',
          description: '介绍DataSay平台的核心功能和优势，展示AI驱动的内容创作能力。包含产品演示、用户案例和技术亮点。',
          content_type: 'video',
          target_platforms: ['douyin', 'bilibili', 'xiaohongshu'],
          status: 'published',
          created_at: '2024-06-24T10:00:00Z',
          published_time: '2024-06-24T14:30:00Z',
          results: [
            {
              platform_type: 'douyin',
              success: true,
              post_id: 'dy_123456',
              post_url: 'https://www.douyin.com/video/dy_123456',
              published_at: '2024-06-24T14:30:00Z',
              status: 'published',
              engagement: { views: 15200, likes: 890, comments: 156, shares: 78 }
            },
            {
              platform_type: 'bilibili',
              success: true,
              post_id: 'bv_789012',
              post_url: 'https://www.bilibili.com/video/bv_789012',
              published_at: '2024-06-24T14:32:00Z',
              status: 'published',
              engagement: { views: 8650, likes: 425, comments: 89, shares: 34 }
            },
            {
              platform_type: 'xiaohongshu',
              success: false,
              error_message: '视频格式不支持',
              status: 'failed'
            }
          ],
          engagement_summary: {
            total_views: 23850,
            total_likes: 1315,
            total_comments: 245,
            total_shares: 112
          },
          file_urls: {
            video_url: '/uploads/product_demo.mp4',
            cover_image: '/uploads/product_demo_cover.jpg',
            images: []
          },
          tags: ['产品宣传', 'AI创作', '技术演示', 'DataSay'],
          author: '营销团队'
        },
        {
          id: 'task_002',
          title: '教程分享：如何使用AI生成专业配音',
          description: '详细教程，展示如何使用DataSay平台的语音合成功能创建专业级配音。包含实际操作演示和技巧分享。',
          content_type: 'video',
          target_platforms: ['douyin', 'bilibili'],
          status: 'scheduled',
          created_at: '2024-06-24T09:00:00Z',
          scheduled_time: '2024-06-25T20:00:00Z',
          results: [],
          engagement_summary: {
            total_views: 0,
            total_likes: 0,
            total_comments: 0,
            total_shares: 0
          },
          file_urls: {
            video_url: '/uploads/tutorial_voice.mp4',
            cover_image: '/uploads/tutorial_voice_cover.jpg',
            images: []
          },
          tags: ['教程', '语音合成', 'AI配音', '技术分享'],
          author: '技术团队'
        },
        {
          id: 'task_003',
          title: '用户案例展示 - 电商行业应用',
          description: '展示DataSay平台在电商行业的应用案例，包含产品介绍视频制作、营销文案生成等实际应用场景。',
          content_type: 'image',
          target_platforms: ['xiaohongshu', 'weibo'],
          status: 'publishing',
          created_at: '2024-06-24T11:30:00Z',
          results: [
            {
              platform_type: 'xiaohongshu',
              success: true,
              post_id: 'xhs_345678',
              status: 'published',
              engagement: { views: 2340, likes: 178, comments: 45, shares: 23 }
            }
          ],
          engagement_summary: {
            total_views: 2340,
            total_likes: 178,
            total_comments: 45,
            total_shares: 23
          },
          file_urls: {
            images: [
              '/uploads/case_ecommerce_1.jpg',
              '/uploads/case_ecommerce_2.jpg',
              '/uploads/case_ecommerce_3.jpg'
            ]
          },
          tags: ['用户案例', '电商应用', '营销', '成功案例'],
          author: '商务团队'
        }
      ]

      setTasks(mockTasks)
    } catch (error) {
      console.error('Failed to load tasks:', error)
      message.error('加载发布任务失败')
    } finally {
      setLoading(false)
    }
  }

  const loadAccounts = async () => {
    try {
      // 模拟API调用
      // const response = await platformPublishService.getAccounts()
      
      // 模拟数据
      const mockAccounts: PlatformAccount[] = [
        {
          platform_type: 'douyin',
          account_name: 'DataSay官方账号',
          account_id: 'datasay_official',
          avatar_url: '/avatars/douyin_avatar.jpg',
          followers_count: 15680,
          connected: true,
          access_token: 'dy_token_123',
          expires_at: '2024-12-24T00:00:00Z',
          daily_quota: 10,
          used_quota: 3
        },
        {
          platform_type: 'bilibili',
          account_name: 'DataSay技术频道',
          account_id: 'datasay_tech',
          avatar_url: '/avatars/bilibili_avatar.jpg',
          followers_count: 8920,
          connected: true,
          access_token: 'bili_token_456',
          expires_at: '2024-12-24T00:00:00Z',
          daily_quota: 5,
          used_quota: 1
        },
        {
          platform_type: 'xiaohongshu',
          account_name: 'DataSay创作分享',
          account_id: 'datasay_create',
          avatar_url: '/avatars/xiaohongshu_avatar.jpg',
          followers_count: 12450,
          connected: false,
          access_token: '',
          expires_at: '',
          daily_quota: 20,
          used_quota: 0
        }
      ]

      setAccounts(mockAccounts)
    } catch (error) {
      console.error('Failed to load accounts:', error)
    }
  }

  // ================================
  // 发布任务操作 - Publish Task Operations
  // ================================

  const createPublishTask = async (values: any) => {
    try {
      const contentInfo: PublishContentInfo = {
        content_id: `content_${Date.now()}`,
        title: values.title,
        description: values.description,
        tags: values.tags || [],
        content_type: values.content_type,
        cover_image_url: values.cover_image?.[0]?.response?.url,
        video_url: values.video_file?.[0]?.response?.url,
        audio_url: values.audio_file?.[0]?.response?.url,
        images: values.image_files?.map((file: any) => file.response?.url).filter(Boolean) || []
      }

      const publishParams: PublishParams = {
        content: contentInfo,
        schedule: {
          schedule_type: values.schedule_type,
          publish_time: values.publish_time?.toISOString(),
          timezone: 'Asia/Shanghai'
        },
        platform_params: {
          douyin: values.douyin_params,
          wechat: values.wechat_params,
          xiaohongshu: values.xiaohongshu_params,
          bilibili: values.bilibili_params
        },
        target_platforms: values.target_platforms
      }

      if (values.schedule_type === 'immediate') {
        // 立即发布
        const results = await platformPublishManager.publishToMultiplePlatforms(publishParams)
        
        const newTask: PublishTask = {
          id: `task_${Date.now()}`,
          title: values.title,
          description: values.description,
          content_type: values.content_type,
          target_platforms: values.target_platforms,
          status: results.every(r => r.success) ? 'published' : 'failed',
          created_at: new Date().toISOString(),
          published_time: new Date().toISOString(),
          results: results,
          engagement_summary: {
            total_views: 0,
            total_likes: 0,
            total_comments: 0,
            total_shares: 0
          },
          file_urls: {
            video_url: contentInfo.video_url,
            audio_url: contentInfo.audio_url,
            images: contentInfo.images,
            cover_image: contentInfo.cover_image_url
          },
          tags: contentInfo.tags,
          author: '当前用户'
        }

        setTasks(prev => [newTask, ...prev])
        message.success('内容发布成功！')
      } else {
        // 定时发布
        const newTask: PublishTask = {
          id: `task_${Date.now()}`,
          title: values.title,
          description: values.description,
          content_type: values.content_type,
          target_platforms: values.target_platforms,
          status: 'scheduled',
          created_at: new Date().toISOString(),
          scheduled_time: values.publish_time?.toISOString(),
          results: [],
          engagement_summary: {
            total_views: 0,
            total_likes: 0,
            total_comments: 0,
            total_shares: 0
          },
          file_urls: {
            video_url: contentInfo.video_url,
            audio_url: contentInfo.audio_url,
            images: contentInfo.images,
            cover_image: contentInfo.cover_image_url
          },
          tags: contentInfo.tags,
          author: '当前用户'
        }

        setTasks(prev => [newTask, ...prev])
        message.success('定时发布任务创建成功！')
      }

      setCreateModalVisible(false)
      form.resetFields()
      setUploadFiles([])
      setCurrentStep(0)
    } catch (error) {
      console.error('Create publish task failed:', error)
      message.error('创建发布任务失败')
    }
  }

  const cancelTask = async (taskId: string) => {
    try {
      // await platformPublishService.cancelTask(taskId)
      
      setTasks(prev =>
        prev.map(task =>
          task.id === taskId ? { ...task, status: 'cancelled' } : task
        )
      )
      
      message.success('任务已取消')
    } catch (error) {
      console.error('Cancel task failed:', error)
      message.error('取消任务失败')
    }
  }

  const retryTask = async (taskId: string) => {
    try {
      // await platformPublishService.retryTask(taskId)
      
      setTasks(prev =>
        prev.map(task =>
          task.id === taskId ? { ...task, status: 'publishing' } : task
        )
      )
      
      message.success('任务重试已启动')
    } catch (error) {
      console.error('Retry task failed:', error)
      message.error('重试任务失败')
    }
  }

  const deleteTask = async (taskId: string) => {
    try {
      // await platformPublishService.deleteTask(taskId)
      
      setTasks(prev => prev.filter(task => task.id !== taskId))
      message.success('任务已删除')
    } catch (error) {
      console.error('Delete task failed:', error)
      message.error('删除任务失败')
    }
  }

  // ================================
  // 渲染函数 - Render Functions
  // ================================

  const getPlatformInfo = (platform: PlatformPublishType) => {
    return platformOptions.find(p => p.value === platform) || platformOptions[0]
  }

  const getStatusInfo = (status: PublishTask['status']) => {
    const statusMap = {
      draft: { label: '草稿', color: 'default', icon: <EditOutlined /> },
      scheduled: { label: '已定时', color: 'blue', icon: <ClockCircleOutlined /> },
      publishing: { label: '发布中', color: 'processing', icon: <CloudUploadOutlined /> },
      published: { label: '已发布', color: 'success', icon: <CheckCircleOutlined /> },
      failed: { label: '失败', color: 'error', icon: <ExclamationCircleOutlined /> },
      cancelled: { label: '已取消', color: 'default', icon: <StopOutlined /> }
    }
    return statusMap[status] || statusMap.draft
  }

  const getContentTypeInfo = (type: PublishTask['content_type']) => {
    return contentTypeOptions.find(opt => opt.value === type) || contentTypeOptions[0]
  }

  const taskColumns: ColumnsType<PublishTask> = [
    {
      title: '任务信息',
      dataIndex: 'title',
      key: 'title',
      width: 250,
      render: (title, record) => (
        <div>
          <Text strong>{title}</Text>
          <br />
          <Text type="secondary" style={{ fontSize: 12 }}>
            {record.description.slice(0, 50)}...
          </Text>
          <br />
          <Space size="small" style={{ marginTop: 4 }}>
            {getContentTypeInfo(record.content_type).icon}
            <Text type="secondary" style={{ fontSize: 11 }}>
              {getContentTypeInfo(record.content_type).label}
            </Text>
            <Text type="secondary" style={{ fontSize: 11 }}>
              • {record.author}
            </Text>
          </Space>
        </div>
      )
    },
    {
      title: '目标平台',
      dataIndex: 'target_platforms',
      key: 'target_platforms',
      width: 150,
      render: (platforms: PlatformPublishType[]) => (
        <Space direction="vertical" size="small">
          {platforms.map(platform => {
            const info = getPlatformInfo(platform)
            return (
              <Tag key={platform} color={info.color}>
                {info.icon} {info.label}
              </Tag>
            )
          })}
        </Space>
      )
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => {
        const info = getStatusInfo(status)
        return (
          <Badge status={info.color as any} text={info.label} />
        )
      }
    },
    {
      title: '发布结果',
      dataIndex: 'results',
      key: 'results',
      width: 150,
      render: (results: PublishResult[], record) => {
        if (record.status === 'scheduled') {
          return (
            <Text type="secondary">
              定时：{moment(record.scheduled_time).format('MM-DD HH:mm')}
            </Text>
          )
        }
        
        const successCount = results.filter(r => r.success).length
        const totalCount = results.length
        
        if (totalCount === 0) return <Text type="secondary">-</Text>
        
        return (
          <div>
            <Progress
              percent={(successCount / totalCount) * 100}
              size="small"
              format={() => `${successCount}/${totalCount}`}
              status={successCount === totalCount ? 'success' : 'exception'}
            />
            <Text type="secondary" style={{ fontSize: 11 }}>
              成功 {successCount} / 总计 {totalCount}
            </Text>
          </div>
        )
      }
    },
    {
      title: '数据概览',
      dataIndex: 'engagement_summary',
      key: 'engagement',
      width: 120,
      render: (engagement) => (
        <div style={{ fontSize: 11 }}>
          <div>浏览: {engagement.total_views.toLocaleString()}</div>
          <div>点赞: {engagement.total_likes.toLocaleString()}</div>
          <div>评论: {engagement.total_comments.toLocaleString()}</div>
        </div>
      )
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 100,
      render: (time) => moment(time).format('MM-DD HH:mm')
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="primary"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => {
              setSelectedTask(record)
              setDetailDrawerVisible(true)
            }}
          >
            详情
          </Button>
          
          {record.status === 'scheduled' && (
            <Popconfirm
              title="确认取消定时发布吗？"
              onConfirm={() => cancelTask(record.id)}
            >
              <Button size="small" icon={<StopOutlined />}>
                取消
              </Button>
            </Popconfirm>
          )}
          
          {record.status === 'failed' && (
            <Button
              size="small"
              icon={<ReloadOutlined />}
              onClick={() => retryTask(record.id)}
            >
              重试
            </Button>
          )}
          
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => {
              setSelectedTask(record)
              setEditModalVisible(true)
            }}
          >
            编辑
          </Button>
          
          <Popconfirm
            title="确认删除任务吗？"
            onConfirm={() => deleteTask(record.id)}
          >
            <Button size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ]

  const renderAccountCards = () => (
    <Row gutter={16} style={{ marginBottom: 24 }}>
      {accounts.map(account => (
        <Col key={account.platform_type} xs={24} sm={12} md={8} lg={6}>
          <Card size="small" className="account-card">
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: 12 }}>
              <Avatar src={account.avatar_url} size={40} />
              <div style={{ marginLeft: 12, flex: 1 }}>
                <Text strong>{account.account_name}</Text>
                <br />
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {getPlatformInfo(account.platform_type).label}
                </Text>
              </div>
              <Badge 
                status={account.connected ? 'success' : 'error'} 
                text={account.connected ? '已连接' : '未连接'}
              />
            </div>
            
            <div style={{ marginBottom: 8 }}>
              <Text type="secondary" style={{ fontSize: 12 }}>
                粉丝: {account.followers_count.toLocaleString()}
              </Text>
            </div>
            
            <div style={{ marginBottom: 8 }}>
              <Text type="secondary" style={{ fontSize: 12 }}>
                今日配额: {account.used_quota}/{account.daily_quota}
              </Text>
              <Progress
                percent={(account.used_quota / account.daily_quota) * 100}
                size="small"
                showInfo={false}
                style={{ marginTop: 4 }}
              />
            </div>
            
            {!account.connected && (
              <Button size="small" type="primary" block>
                重新授权
              </Button>
            )}
          </Card>
        </Col>
      ))}
    </Row>
  )

  const renderCreateModal = () => (
    <Modal
      title="创建发布任务"
      open={createModalVisible}
      onCancel={() => {
        setCreateModalVisible(false)
        form.resetFields()
        setUploadFiles([])
        setCurrentStep(0)
      }}
      footer={null}
      width={900}
      style={{ top: 20 }}
    >
      <Steps current={currentStep} style={{ marginBottom: 24 }}>
        <Step title="基本信息" description="内容标题和描述" />
        <Step title="媒体文件" description="上传视频、图片等" />
        <Step title="平台配置" description="选择发布平台和参数" />
        <Step title="发布设置" description="定时发布或立即发布" />
      </Steps>

      <Form
        form={form}
        layout="vertical"
        onFinish={createPublishTask}
      >
        {currentStep === 0 && (
          <div>
            <Form.Item
              name="title"
              label="内容标题"
              rules={[{ required: true, message: '请输入内容标题' }]}
            >
              <Input placeholder="输入吸引人的标题..." maxLength={100} showCount />
            </Form.Item>

            <Form.Item
              name="description"
              label="内容描述"
              rules={[{ required: true, message: '请输入内容描述' }]}
            >
              <TextArea
                rows={4}
                placeholder="详细描述内容，将用作各平台的发布文案..."
                maxLength={2000}
                showCount
              />
            </Form.Item>

            <Form.Item
              name="content_type"
              label="内容类型"
              rules={[{ required: true, message: '请选择内容类型' }]}
            >
              <Radio.Group>
                {contentTypeOptions.map(option => (
                  <Radio key={option.value} value={option.value}>
                    <Space>
                      {option.icon}
                      {option.label}
                    </Space>
                  </Radio>
                ))}
              </Radio.Group>
            </Form.Item>

            <Form.Item
              name="tags"
              label="内容标签"
            >
              <Select
                mode="tags"
                placeholder="添加相关标签，有助于内容推荐..."
                maxTagCount={10}
              />
            </Form.Item>
          </div>
        )}

        {currentStep === 1 && (
          <div>
            <Form.Item
              name="cover_image"
              label="封面图片"
            >
              <Upload
                listType="picture-card"
                maxCount={1}
                beforeUpload={() => false}
              >
                <div>
                  <PlusOutlined />
                  <div style={{ marginTop: 8 }}>上传封面</div>
                </div>
              </Upload>
            </Form.Item>

            <Form.Item
              name="video_file"
              label="视频文件"
            >
              <Upload
                maxCount={1}
                beforeUpload={() => false}
                accept="video/*"
              >
                <Button icon={<CloudUploadOutlined />}>选择视频文件</Button>
              </Upload>
            </Form.Item>

            <Form.Item
              name="image_files"
              label="图片文件"
            >
              <Upload
                listType="picture-card"
                maxCount={9}
                beforeUpload={() => false}
                accept="image/*"
                multiple
              >
                <div>
                  <PlusOutlined />
                  <div style={{ marginTop: 8 }}>上传图片</div>
                </div>
              </Upload>
            </Form.Item>

            <Form.Item
              name="audio_file"
              label="音频文件"
            >
              <Upload
                maxCount={1}
                beforeUpload={() => false}
                accept="audio/*"
              >
                <Button icon={<SoundOutlined />}>选择音频文件</Button>
              </Upload>
            </Form.Item>
          </div>
        )}

        {currentStep === 2 && (
          <div>
            <Form.Item
              name="target_platforms"
              label="目标平台"
              rules={[{ required: true, message: '请选择至少一个发布平台' }]}
            >
              <Checkbox.Group>
                <Row gutter={16}>
                  {platformOptions.map(platform => (
                    <Col key={platform.value} span={12}>
                      <Card size="small" style={{ marginBottom: 8 }}>
                        <Checkbox value={platform.value}>
                          <Space>
                            <span style={{ fontSize: 16 }}>{platform.icon}</span>
                            <div>
                              <Text strong>{platform.label}</Text>
                              <br />
                              <Text type="secondary" style={{ fontSize: 11 }}>
                                {platform.description}
                              </Text>
                            </div>
                          </Space>
                        </Checkbox>
                      </Card>
                    </Col>
                  ))}
                </Row>
              </Checkbox.Group>
            </Form.Item>

            <Alert
              message="平台适配提醒"
              description="系统会根据不同平台的特点自动优化内容格式和参数，确保最佳发布效果。"
              type="info"
              showIcon
              style={{ marginTop: 16 }}
            />
          </div>
        )}

        {currentStep === 3 && (
          <div>
            <Form.Item
              name="schedule_type"
              label="发布方式"
              initialValue="immediate"
            >
              <Radio.Group>
                <Radio value="immediate">
                  <Space>
                    <SendOutlined />
                    立即发布
                  </Space>
                </Radio>
                <Radio value="scheduled">
                  <Space>
                    <ScheduleOutlined />
                    定时发布
                  </Space>
                </Radio>
              </Radio.Group>
            </Form.Item>

            <Form.Item
              name="publish_time"
              label="发布时间"
              dependencies={['schedule_type']}
              rules={[
                ({ getFieldValue }) => ({
                  required: getFieldValue('schedule_type') === 'scheduled',
                  message: '请选择发布时间'
                })
              ]}
            >
              <DatePicker
                showTime
                placeholder="选择发布时间"
                disabledDate={current => current && current < moment().startOf('day')}
                style={{ width: '100%' }}
              />
            </Form.Item>

            <Alert
              message="最佳发布时间建议"
              description="抖音: 19:00-21:00; B站: 20:00-22:00; 小红书: 11:00-13:00, 19:00-21:00; 微博: 12:00-14:00, 18:00-20:00"
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />
          </div>
        )}

        <div style={{ textAlign: 'right', marginTop: 24 }}>
          <Space>
            {currentStep > 0 && (
              <Button onClick={() => setCurrentStep(currentStep - 1)}>
                上一步
              </Button>
            )}
            
            {currentStep < 3 && (
              <Button type="primary" onClick={() => setCurrentStep(currentStep + 1)}>
                下一步
              </Button>
            )}
            
            {currentStep === 3 && (
              <Button type="primary" htmlType="submit">
                创建发布任务
              </Button>
            )}
          </Space>
        </div>
      </Form>
    </Modal>
  )

  const renderDetailDrawer = () => (
    <Drawer
      title={selectedTask?.title}
      placement="right"
      width={600}
      onClose={() => setDetailDrawerVisible(false)}
      open={detailDrawerVisible}
    >
      {selectedTask && (
        <div>
          <Card title="任务概览" size="small" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={12}>
                <Statistic
                  title="总浏览量"
                  value={selectedTask.engagement_summary.total_views}
                  prefix={<EyeOutlined />}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="总点赞数"
                  value={selectedTask.engagement_summary.total_likes}
                  prefix={<ThunderboltOutlined />}
                  valueStyle={{ color: '#cf1322' }}
                />
              </Col>
            </Row>
            <Row gutter={16} style={{ marginTop: 16 }}>
              <Col span={12}>
                <Statistic
                  title="总评论数"
                  value={selectedTask.engagement_summary.total_comments}
                  prefix={<TeamOutlined />}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="总分享数"
                  value={selectedTask.engagement_summary.total_shares}
                  prefix={<ShareAltOutlined />}
                />
              </Col>
            </Row>
          </Card>

          <Card title="发布结果" size="small" style={{ marginBottom: 16 }}>
            <List
              dataSource={selectedTask.results}
              renderItem={result => (
                <List.Item>
                  <List.Item.Meta
                    avatar={
                      <Avatar
                        style={{
                          backgroundColor: result.success ? '#52c41a' : '#ff4d4f'
                        }}
                        icon={result.success ? <CheckCircleOutlined /> : <ExclamationCircleOutlined />}
                      />
                    }
                    title={
                      <Space>
                        <Text strong>{getPlatformInfo(result.platform_type).label}</Text>
                        <Badge
                          status={result.success ? 'success' : 'error'}
                          text={result.success ? '发布成功' : '发布失败'}
                        />
                      </Space>
                    }
                    description={
                      <div>
                        {result.success ? (
                          <div>
                            <div>
                              <Text type="secondary">发布链接: </Text>
                              <a href={result.post_url} target="_blank" rel="noopener noreferrer">
                                {result.post_url}
                              </a>
                            </div>
                            {result.engagement && (
                              <div style={{ marginTop: 8 }}>
                                <Space split={<Divider type="vertical" />}>
                                  <Text type="secondary">
                                    浏览: {result.engagement.views?.toLocaleString() || 0}
                                  </Text>
                                  <Text type="secondary">
                                    点赞: {result.engagement.likes?.toLocaleString() || 0}
                                  </Text>
                                  <Text type="secondary">
                                    评论: {result.engagement.comments?.toLocaleString() || 0}
                                  </Text>
                                </Space>
                              </div>
                            )}
                          </div>
                        ) : (
                          <Text type="danger">{result.error_message}</Text>
                        )}
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>

          <Card title="内容信息" size="small">
            <div style={{ marginBottom: 12 }}>
              <Text strong>内容描述:</Text>
              <Paragraph style={{ marginTop: 8 }}>
                {selectedTask.description}
              </Paragraph>
            </div>

            <div style={{ marginBottom: 12 }}>
              <Text strong>内容标签:</Text>
              <div style={{ marginTop: 8 }}>
                {selectedTask.tags.map(tag => (
                  <Tag key={tag}>{tag}</Tag>
                ))}
              </div>
            </div>

            <div style={{ marginBottom: 12 }}>
              <Text strong>创建时间:</Text>
              <Text style={{ marginLeft: 8 }}>
                {moment(selectedTask.created_at).format('YYYY-MM-DD HH:mm:ss')}
              </Text>
            </div>

            {selectedTask.scheduled_time && (
              <div style={{ marginBottom: 12 }}>
                <Text strong>定时发布:</Text>
                <Text style={{ marginLeft: 8 }}>
                  {moment(selectedTask.scheduled_time).format('YYYY-MM-DD HH:mm:ss')}
                </Text>
              </div>
            )}

            <div>
              <Text strong>创建者:</Text>
              <Text style={{ marginLeft: 8 }}>{selectedTask.author}</Text>
            </div>
          </Card>
        </div>
      )}
    </Drawer>
  )

  const getFilteredTasks = () => {
    if (activeTab === 'all') return tasks
    return tasks.filter(task => task.status === activeTab)
  }

  // ================================
  // 主渲染
  // ================================

  return (
    <div className="platform-publish-center">
      <Card>
        <div style={{ marginBottom: 24 }}>
          <Title level={2}>
            <GlobalOutlined /> 平台发布中心
          </Title>
          <Paragraph>
            统一管理多平台内容发布，支持抖音、微信、小红书、B站、微博等主流平台。
          </Paragraph>
        </div>

        {/* 账号状态卡片 */}
        <Card title="平台账号状态" size="small" style={{ marginBottom: 24 }}>
          {renderAccountCards()}
        </Card>

        {/* 工具栏 */}
        <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
          <Col>
            <Space>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => setCreateModalVisible(true)}
              >
                创建发布任务
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={loadTasks}
                loading={loading}
              >
                刷新
              </Button>
              <Button
                icon={<SettingOutlined />}
                onClick={() => setSettingsDrawerVisible(true)}
              >
                平台设置
              </Button>
            </Space>
          </Col>
        </Row>

        {/* 任务标签页 */}
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane 
            tab={`全部 (${tasks.length})`} 
            key="all" 
          />
          <TabPane 
            tab={
              <Badge count={tasks.filter(t => t.status === 'scheduled').length} size="small">
                <span>定时发布</span>
              </Badge>
            } 
            key="scheduled" 
          />
          <TabPane 
            tab={
              <Badge count={tasks.filter(t => t.status === 'publishing').length} size="small">
                <span>发布中</span>
              </Badge>
            } 
            key="publishing" 
          />
          <TabPane 
            tab={
              <Badge count={tasks.filter(t => t.status === 'published').length} size="small">
                <span>已发布</span>
              </Badge>
            } 
            key="published" 
          />
          <TabPane 
            tab={
              <Badge count={tasks.filter(t => t.status === 'failed').length} size="small">
                <span>失败</span>
              </Badge>
            } 
            key="failed" 
          />
        </Tabs>

        {/* 任务列表 */}
        <Table
          columns={taskColumns}
          dataSource={getFilteredTasks()}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条记录`
          }}
          scroll={{ x: 'max-content' }}
        />

        {/* 模态框和抽屉 */}
        {renderCreateModal()}
        {renderDetailDrawer()}
      </Card>
    </div>
  )
}

export default PlatformPublishCenter