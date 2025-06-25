/**
 * Mix All Content Batch Processing Component
 * 混合内容批量处理组件 - [MixAll][Content][Batch]
 * 
 * 企业级批量内容处理和任务管理系统
 * 支持大规模批量处理、任务队列管理、进度监控和错误恢复
 */

import React, { useState, useEffect, useCallback, useRef } from 'react'
import {
  Card,
  Table,
  Button,
  Typography,
  Row,
  Col,
  Space,
  Upload,
  Progress,
  Tag,
  Modal,
  Form,
  Input,
  Select,
  Switch,
  message,
  Tabs,
  Statistic,
  Timeline,
  Alert,
  Divider,
  Tooltip,
  Popconfirm,
  Badge,
  Drawer,
  Steps,
  Radio,
  Checkbox,
  Slider,
  List,
  Avatar,
  Empty,
  Spin,
  notification
} from 'antd'
import {
  UploadOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  StopOutlined,
  ReloadOutlined,
  DeleteOutlined,
  DownloadOutlined,
  EyeOutlined,
  SettingOutlined,
  FileTextOutlined,
  SoundOutlined,
  FileImageOutlined,
  VideoCameraOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  CloseCircleOutlined,
  ThunderboltOutlined,
  FilterOutlined,
  SearchOutlined,
  CloudUploadOutlined,
  BranchesOutlined,
  BarChartOutlined,
  TeamOutlined,
  CalendarOutlined,
  WarningOutlined,
  InfoCircleOutlined,
  RobotOutlined,
  ApiOutlined,
  MonitorOutlined,
  DashboardOutlined
} from '@ant-design/icons'
import type { UploadFile, UploadProps } from 'antd/es/upload/interface'
import type { ColumnsType } from 'antd/es/table'

const { Title, Paragraph, Text } = Typography
const { TextArea } = Input
const { Option } = Select
const { TabPane } = Tabs
const { Step } = Steps
const { Search } = Input

// ================================
// 类型定义 - Types
// ================================

export type BatchTaskType = 'text_generation' | 'voice_synthesis' | 'image_generation' | 'video_composition' | 'workflow_execution'
export type BatchTaskStatus = 'pending' | 'queued' | 'running' | 'paused' | 'completed' | 'failed' | 'cancelled'
export type BatchTaskPriority = 'low' | 'normal' | 'high' | 'urgent'

interface BatchTaskFile {
  id: string
  name: string
  size: number
  type: string
  url: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  result_url?: string
  error_message?: string
  processing_time?: number
}

interface BatchTask {
  id: string
  name: string
  type: BatchTaskType
  status: BatchTaskStatus
  priority: BatchTaskPriority
  created_at: string
  started_at?: string
  completed_at?: string
  created_by: string
  description: string
  
  // 文件相关
  input_files: BatchTaskFile[]
  output_files: BatchTaskFile[]
  total_files: number
  processed_files: number
  failed_files: number
  
  // 进度相关
  progress: number
  estimated_time_remaining?: number
  
  // 配置相关
  processing_config: Record<string, any>
  template_id?: string
  workflow_id?: string
  
  // 资源使用
  resource_usage: {
    cpu_time: number
    memory_peak: number
    storage_used: number
    cost_estimate: number
  }
  
  // 错误处理
  error_count: number
  last_error?: string
  retry_count: number
  max_retries: number
  
  // 统计信息
  stats: {
    success_rate: number
    average_processing_time: number
    throughput: number // 文件/分钟
  }
}

interface BatchProcessingConfig {
  concurrent_tasks: number
  max_queue_size: number
  retry_strategy: 'immediate' | 'exponential_backoff' | 'fixed_delay'
  retry_delay: number
  auto_resume: boolean
  notification_settings: {
    on_completion: boolean
    on_failure: boolean
    on_queue_full: boolean
  }
  resource_limits: {
    max_cpu_usage: number
    max_memory_usage: number
    max_storage_usage: number
  }
}

interface QueueStatistics {
  total_tasks: number
  pending_tasks: number
  running_tasks: number
  completed_tasks: number
  failed_tasks: number
  average_wait_time: number
  average_processing_time: number
  queue_throughput: number
  resource_utilization: {
    cpu: number
    memory: number
    storage: number
  }
}

// ================================
// 主组件
// ================================

const MixAllContentBatch: React.FC = () => {
  const [tasks, setTasks] = useState<BatchTask[]>([])
  const [selectedTask, setSelectedTask] = useState<BatchTask | null>(null)
  const [loading, setLoading] = useState(false)
  const [queueStats, setQueueStats] = useState<QueueStatistics | null>(null)
  const [config, setConfig] = useState<BatchProcessingConfig>({
    concurrent_tasks: 3,
    max_queue_size: 100,
    retry_strategy: 'exponential_backoff',
    retry_delay: 5000,
    auto_resume: true,
    notification_settings: {
      on_completion: true,
      on_failure: true,
      on_queue_full: false
    },
    resource_limits: {
      max_cpu_usage: 80,
      max_memory_usage: 16384,
      max_storage_usage: 10240
    }
  })
  
  const [createModalVisible, setCreateModalVisible] = useState(false)
  const [configDrawerVisible, setConfigDrawerVisible] = useState(false)
  const [detailDrawerVisible, setDetailDrawerVisible] = useState(false)
  const [uploadFiles, setUploadFiles] = useState<UploadFile[]>([])
  const [activeTab, setActiveTab] = useState('running')
  const [form] = Form.useForm()
  const wsRef = useRef<WebSocket | null>(null)

  // ================================
  // 数据加载和实时更新 - Data Loading & Real-time Updates
  // ================================

  useEffect(() => {
    loadTasks()
    loadQueueStatistics()
    connectWebSocket()

    // 定期刷新数据
    const interval = setInterval(() => {
      loadQueueStatistics()
    }, 5000)

    return () => {
      clearInterval(interval)
      disconnectWebSocket()
    }
  }, [])

  const loadTasks = async () => {
    setLoading(true)
    try {
      // 模拟API调用
      // const response = await batchProcessingService.getTasks()
      
      // 模拟数据
      const mockTasks: BatchTask[] = [
        {
          id: 'task_001',
          name: '产品宣传视频批量生成',
          type: 'video_composition',
          status: 'running',
          priority: 'high',
          created_at: '2024-06-24T10:00:00Z',
          started_at: '2024-06-24T10:05:00Z',
          created_by: 'user_001',
          description: '为100个产品生成宣传视频，包含产品图片、语音介绍和品牌元素',
          input_files: Array.from({ length: 100 }, (_, i) => ({
            id: `file_${i + 1}`,
            name: `product_${i + 1}.json`,
            size: 2048 + Math.random() * 1024,
            type: 'application/json',
            url: `/uploads/product_${i + 1}.json`,
            status: i < 45 ? 'completed' : i < 48 ? 'processing' : 'pending',
            progress: i < 45 ? 100 : i < 48 ? Math.random() * 100 : 0,
            result_url: i < 45 ? `/output/video_${i + 1}.mp4` : undefined,
            processing_time: i < 45 ? 15000 + Math.random() * 10000 : undefined
          })),
          output_files: [],
          total_files: 100,
          processed_files: 45,
          failed_files: 2,
          progress: 47,
          estimated_time_remaining: 1800,
          processing_config: {
            template_id: 'template_001',
            output_format: 'mp4',
            resolution: '1920x1080',
            quality: 'high'
          },
          template_id: 'template_001',
          resource_usage: {
            cpu_time: 3600,
            memory_peak: 8192,
            storage_used: 2560,
            cost_estimate: 12.50
          },
          error_count: 2,
          retry_count: 0,
          max_retries: 3,
          stats: {
            success_rate: 95.7,
            average_processing_time: 18500,
            throughput: 2.4
          }
        },
        {
          id: 'task_002',
          name: '课程语音批量合成',
          type: 'voice_synthesis',
          status: 'completed',
          priority: 'normal',
          created_at: '2024-06-24T09:00:00Z',
          started_at: '2024-06-24T09:02:00Z',
          completed_at: '2024-06-24T09:45:00Z',
          created_by: 'user_002',
          description: '为在线课程生成200个音频文件，使用标准女声，语速适中',
          input_files: Array.from({ length: 200 }, (_, i) => ({
            id: `audio_file_${i + 1}`,
            name: `lesson_${i + 1}.txt`,
            size: 512 + Math.random() * 256,
            type: 'text/plain',
            url: `/uploads/lesson_${i + 1}.txt`,
            status: 'completed',
            progress: 100,
            result_url: `/output/audio_${i + 1}.mp3`,
            processing_time: 3000 + Math.random() * 2000
          })),
          output_files: [],
          total_files: 200,
          processed_files: 200,
          failed_files: 0,
          progress: 100,
          processing_config: {
            voice_id: 'voice_002',
            speed: 1.0,
            pitch: 1.0,
            volume: 1.0,
            format: 'mp3'
          },
          resource_usage: {
            cpu_time: 2400,
            memory_peak: 4096,
            storage_used: 1280,
            cost_estimate: 8.00
          },
          error_count: 0,
          retry_count: 0,
          max_retries: 3,
          stats: {
            success_rate: 100,
            average_processing_time: 4200,
            throughput: 4.6
          }
        },
        {
          id: 'task_003',
          name: '营销文案批量生成',
          type: 'text_generation',
          status: 'failed',
          priority: 'low',
          created_at: '2024-06-24T08:00:00Z',
          started_at: '2024-06-24T08:05:00Z',
          created_by: 'user_003',
          description: '为50个产品生成营销文案和产品描述',
          input_files: Array.from({ length: 50 }, (_, i) => ({
            id: `text_file_${i + 1}`,
            name: `product_info_${i + 1}.json`,
            size: 1024 + Math.random() * 512,
            type: 'application/json',
            url: `/uploads/product_info_${i + 1}.json`,
            status: i < 25 ? 'completed' : i < 30 ? 'failed' : 'pending',
            progress: i < 25 ? 100 : 0,
            result_url: i < 25 ? `/output/copy_${i + 1}.txt` : undefined,
            error_message: i >= 25 && i < 30 ? 'API调用限制' : undefined,
            processing_time: i < 25 ? 5000 + Math.random() * 3000 : undefined
          })),
          output_files: [],
          total_files: 50,
          processed_files: 25,
          failed_files: 5,
          progress: 50,
          processing_config: {
            model: 'gpt-4',
            max_tokens: 500,
            temperature: 0.7,
            language: 'zh-CN'
          },
          resource_usage: {
            cpu_time: 600,
            memory_peak: 2048,
            storage_used: 256,
            cost_estimate: 15.30
          },
          error_count: 5,
          last_error: 'API调用限制，请稍后重试',
          retry_count: 2,
          max_retries: 3,
          stats: {
            success_rate: 83.3,
            average_processing_time: 6800,
            throughput: 3.1
          }
        }
      ]

      setTasks(mockTasks)
    } catch (error) {
      console.error('Failed to load tasks:', error)
      message.error('加载任务列表失败')
    } finally {
      setLoading(false)
    }
  }

  const loadQueueStatistics = async () => {
    try {
      // 模拟API调用
      // const response = await batchProcessingService.getQueueStatistics()
      
      // 模拟数据
      const mockStats: QueueStatistics = {
        total_tasks: tasks.length,
        pending_tasks: tasks.filter(t => t.status === 'pending').length,
        running_tasks: tasks.filter(t => t.status === 'running').length,
        completed_tasks: tasks.filter(t => t.status === 'completed').length,
        failed_tasks: tasks.filter(t => t.status === 'failed').length,
        average_wait_time: 120,
        average_processing_time: 1800,
        queue_throughput: 3.2,
        resource_utilization: {
          cpu: 45,
          memory: 62,
          storage: 38
        }
      }

      setQueueStats(mockStats)
    } catch (error) {
      console.error('Failed to load queue statistics:', error)
    }
  }

  const connectWebSocket = () => {
    try {
      // const ws = new WebSocket('ws://localhost:8000/ws/batch-processing')
      // wsRef.current = ws

      // ws.onmessage = (event) => {
      //   const data = JSON.parse(event.data)
      //   handleWebSocketMessage(data)
      // }

      // ws.onerror = (error) => {
      //   console.error('WebSocket error:', error)
      // }

      // 模拟实时更新
      const interval = setInterval(() => {
        updateRunningTasks()
      }, 2000)

      return () => clearInterval(interval)
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
    }
  }

  const disconnectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
  }

  const updateRunningTasks = () => {
    setTasks(prevTasks => 
      prevTasks.map(task => {
        if (task.status === 'running') {
          const newProgress = Math.min(task.progress + Math.random() * 2, 100)
          const newProcessedFiles = Math.floor((newProgress / 100) * task.total_files)
          
          return {
            ...task,
            progress: newProgress,
            processed_files: newProcessedFiles,
            estimated_time_remaining: Math.max(0, task.estimated_time_remaining! - 2)
          }
        }
        return task
      })
    )
  }

  // ================================
  // 任务操作 - Task Operations
  // ================================

  const createBatchTask = async (values: any) => {
    try {
      const taskConfig = {
        name: values.name,
        type: values.type,
        description: values.description,
        priority: values.priority,
        processing_config: values.processing_config,
        template_id: values.template_id,
        workflow_id: values.workflow_id,
        max_retries: values.max_retries || 3,
        input_files: uploadFiles.map(file => ({
          id: file.uid!,
          name: file.name,
          size: file.size || 0,
          type: file.type || 'application/octet-stream',
          url: file.response?.url || '',
          status: 'pending' as const,
          progress: 0
        }))
      }

      // 这里应该调用API创建任务
      // await batchProcessingService.createTask(taskConfig)
      
      message.success('批量任务创建成功！')
      setCreateModalVisible(false)
      form.resetFields()
      setUploadFiles([])
      loadTasks()
    } catch (error) {
      console.error('Failed to create batch task:', error)
      message.error('批量任务创建失败')
    }
  }

  const startTask = async (taskId: string) => {
    try {
      // await batchProcessingService.startTask(taskId)
      
      setTasks(prevTasks =>
        prevTasks.map(task =>
          task.id === taskId
            ? { ...task, status: 'running', started_at: new Date().toISOString() }
            : task
        )
      )
      
      message.success('任务已启动')
    } catch (error) {
      console.error('Failed to start task:', error)
      message.error('启动任务失败')
    }
  }

  const pauseTask = async (taskId: string) => {
    try {
      // await batchProcessingService.pauseTask(taskId)
      
      setTasks(prevTasks =>
        prevTasks.map(task =>
          task.id === taskId ? { ...task, status: 'paused' } : task
        )
      )
      
      message.success('任务已暂停')
    } catch (error) {
      console.error('Failed to pause task:', error)
      message.error('暂停任务失败')
    }
  }

  const stopTask = async (taskId: string) => {
    try {
      // await batchProcessingService.stopTask(taskId)
      
      setTasks(prevTasks =>
        prevTasks.map(task =>
          task.id === taskId ? { ...task, status: 'cancelled' } : task
        )
      )
      
      message.success('任务已停止')
    } catch (error) {
      console.error('Failed to stop task:', error)
      message.error('停止任务失败')
    }
  }

  const retryTask = async (taskId: string) => {
    try {
      // await batchProcessingService.retryTask(taskId)
      
      setTasks(prevTasks =>
        prevTasks.map(task =>
          task.id === taskId
            ? { 
                ...task, 
                status: 'running',
                retry_count: task.retry_count + 1,
                started_at: new Date().toISOString()
              }
            : task
        )
      )
      
      message.success('任务重试已启动')
    } catch (error) {
      console.error('Failed to retry task:', error)
      message.error('重试任务失败')
    }
  }

  const deleteTask = async (taskId: string) => {
    try {
      // await batchProcessingService.deleteTask(taskId)
      
      setTasks(prevTasks => prevTasks.filter(task => task.id !== taskId))
      message.success('任务已删除')
    } catch (error) {
      console.error('Failed to delete task:', error)
      message.error('删除任务失败')
    }
  }

  // ================================
  // 渲染函数 - Render Functions
  // ================================

  const getTaskTypeInfo = (type: BatchTaskType) => {
    const typeMap = {
      text_generation: { label: '文本生成', icon: <FileTextOutlined />, color: 'blue' },
      voice_synthesis: { label: '语音合成', icon: <SoundOutlined />, color: 'green' },
      image_generation: { label: '图像生成', icon: <FileImageOutlined />, color: 'orange' },
      video_composition: { label: '视频合成', icon: <VideoCameraOutlined />, color: 'red' },
      workflow_execution: { label: '工作流执行', icon: <BranchesOutlined />, color: 'purple' }
    }
    return typeMap[type] || typeMap.text_generation
  }

  const getStatusInfo = (status: BatchTaskStatus) => {
    const statusMap = {
      pending: { label: '等待中', color: 'default', icon: <ClockCircleOutlined /> },
      queued: { label: '已排队', color: 'blue', icon: <ClockCircleOutlined /> },
      running: { label: '运行中', color: 'processing', icon: <PlayCircleOutlined /> },
      paused: { label: '已暂停', color: 'warning', icon: <PauseCircleOutlined /> },
      completed: { label: '已完成', color: 'success', icon: <CheckCircleOutlined /> },
      failed: { label: '失败', color: 'error', icon: <ExclamationCircleOutlined /> },
      cancelled: { label: '已取消', color: 'default', icon: <CloseCircleOutlined /> }
    }
    return statusMap[status] || statusMap.pending
  }

  const getPriorityInfo = (priority: BatchTaskPriority) => {
    const priorityMap = {
      low: { label: '低', color: 'default' },
      normal: { label: '普通', color: 'blue' },
      high: { label: '高', color: 'orange' },
      urgent: { label: '紧急', color: 'red' }
    }
    return priorityMap[priority] || priorityMap.normal
  }

  const taskColumns: ColumnsType<BatchTask> = [
    {
      title: '任务名称',
      dataIndex: 'name',
      key: 'name',
      width: 200,
      render: (name, record) => (
        <div>
          <Text strong>{name}</Text>
          <br />
          <Text type="secondary" style={{ fontSize: 12 }}>
            {record.description}
          </Text>
        </div>
      )
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 120,
      render: (type) => {
        const info = getTaskTypeInfo(type)
        return (
          <Tag icon={info.icon} color={info.color}>
            {info.label}
          </Tag>
        )
      }
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
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 80,
      render: (priority) => {
        const info = getPriorityInfo(priority)
        return (
          <Tag color={info.color}>{info.label}</Tag>
        )
      }
    },
    {
      title: '进度',
      dataIndex: 'progress',
      key: 'progress',
      width: 150,
      render: (progress, record) => (
        <div>
          <Progress 
            percent={Math.round(progress)} 
            size="small"
            status={record.status === 'failed' ? 'exception' : undefined}
          />
          <Text type="secondary" style={{ fontSize: 11 }}>
            {record.processed_files}/{record.total_files} 文件
          </Text>
        </div>
      )
    },
    {
      title: '预计剩余',
      dataIndex: 'estimated_time_remaining',
      key: 'estimated_time_remaining',
      width: 100,
      render: (time) => {
        if (!time) return '-'
        const minutes = Math.floor(time / 60)
        const seconds = time % 60
        return (
          <Text type="secondary">
            {minutes > 0 ? `${minutes}分` : ''}{seconds}秒
          </Text>
        )
      }
    },
    {
      title: '成本',
      dataIndex: ['resource_usage', 'cost_estimate'],
      key: 'cost',
      width: 80,
      render: (cost) => (
        <Text>${cost?.toFixed(2) || '0.00'}</Text>
      )
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_, record) => (
        <Space size="small">
          {record.status === 'pending' && (
            <Button
              type="primary"
              size="small"
              icon={<PlayCircleOutlined />}
              onClick={() => startTask(record.id)}
            >
              开始
            </Button>
          )}
          
          {record.status === 'running' && (
            <Button
              size="small"
              icon={<PauseCircleOutlined />}
              onClick={() => pauseTask(record.id)}
            >
              暂停
            </Button>
          )}
          
          {(record.status === 'running' || record.status === 'paused') && (
            <Popconfirm
              title="确认停止任务吗？"
              onConfirm={() => stopTask(record.id)}
            >
              <Button size="small" icon={<StopOutlined />} danger>
                停止
              </Button>
            </Popconfirm>
          )}
          
          {record.status === 'failed' && record.retry_count < record.max_retries && (
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
            icon={<EyeOutlined />}
            onClick={() => {
              setSelectedTask(record)
              setDetailDrawerVisible(true)
            }}
          >
            详情
          </Button>
          
          {record.status === 'completed' && (
            <Button
              size="small"
              icon={<DownloadOutlined />}
              onClick={() => {
                // 下载结果
                message.info('开始下载结果文件...')
              }}
            >
              下载
            </Button>
          )}
          
          {['completed', 'failed', 'cancelled'].includes(record.status) && (
            <Popconfirm
              title="确认删除任务吗？"
              onConfirm={() => deleteTask(record.id)}
            >
              <Button size="small" icon={<DeleteOutlined />} danger type="text">
                删除
              </Button>
            </Popconfirm>
          )}
        </Space>
      )
    }
  ]

  const renderQueueStatistics = () => (
    <Row gutter={16} style={{ marginBottom: 24 }}>
      <Col span={6}>
        <Card size="small">
          <Statistic
            title="总任务数"
            value={queueStats?.total_tasks || 0}
            prefix={<DashboardOutlined />}
          />
        </Card>
      </Col>
      <Col span={6}>
        <Card size="small">
          <Statistic
            title="运行中"
            value={queueStats?.running_tasks || 0}
            prefix={<PlayCircleOutlined />}
            valueStyle={{ color: '#1890ff' }}
          />
        </Card>
      </Col>
      <Col span={6}>
        <Card size="small">
          <Statistic
            title="等待中"
            value={queueStats?.pending_tasks || 0}
            prefix={<ClockCircleOutlined />}
            valueStyle={{ color: '#faad14' }}
          />
        </Card>
      </Col>
      <Col span={6}>
        <Card size="small">
          <Statistic
            title="吞吐量"
            value={queueStats?.queue_throughput || 0}
            precision={1}
            suffix="任务/分钟"
            prefix={<ThunderboltOutlined />}
            valueStyle={{ color: '#52c41a' }}
          />
        </Card>
      </Col>
    </Row>
  )

  const renderResourceUsage = () => (
    <Card title="资源使用情况" size="small" style={{ marginBottom: 16 }}>
      <Row gutter={16}>
        <Col span={8}>
          <div style={{ textAlign: 'center' }}>
            <Progress
              type="circle"
              percent={queueStats?.resource_utilization.cpu || 0}
              size={80}
              format={percent => `CPU\n${percent}%`}
            />
          </div>
        </Col>
        <Col span={8}>
          <div style={{ textAlign: 'center' }}>
            <Progress
              type="circle"
              percent={queueStats?.resource_utilization.memory || 0}
              size={80}
              strokeColor="#722ed1"
              format={percent => `内存\n${percent}%`}
            />
          </div>
        </Col>
        <Col span={8}>
          <div style={{ textAlign: 'center' }}>
            <Progress
              type="circle"
              percent={queueStats?.resource_utilization.storage || 0}
              size={80}
              strokeColor="#13c2c2"
              format={percent => `存储\n${percent}%`}
            />
          </div>
        </Col>
      </Row>
    </Card>
  )

  const renderCreateModal = () => (
    <Modal
      title="创建批量任务"
      open={createModalVisible}
      onCancel={() => {
        setCreateModalVisible(false)
        form.resetFields()
        setUploadFiles([])
      }}
      onOk={() => form.submit()}
      width={800}
    >
      <Form form={form} layout="vertical" onFinish={createBatchTask}>
        <Steps current={0} style={{ marginBottom: 24 }}>
          <Step title="基本信息" description="任务名称和描述" />
          <Step title="处理配置" description="选择处理类型和参数" />
          <Step title="文件上传" description="上传待处理文件" />
        </Steps>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="name"
              label="任务名称"
              rules={[{ required: true, message: '请输入任务名称' }]}
            >
              <Input placeholder="输入任务名称" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="priority"
              label="优先级"
              rules={[{ required: true, message: '请选择优先级' }]}
              initialValue="normal"
            >
              <Select>
                <Option value="low">低优先级</Option>
                <Option value="normal">普通优先级</Option>
                <Option value="high">高优先级</Option>
                <Option value="urgent">紧急</Option>
              </Select>
            </Form.Item>
          </Col>
        </Row>

        <Form.Item
          name="description"
          label="任务描述"
        >
          <TextArea rows={3} placeholder="描述批量处理任务的目标和要求..." />
        </Form.Item>

        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="type"
              label="处理类型"
              rules={[{ required: true, message: '请选择处理类型' }]}
            >
              <Select placeholder="选择处理类型">
                <Option value="text_generation">文本生成</Option>
                <Option value="voice_synthesis">语音合成</Option>
                <Option value="image_generation">图像生成</Option>
                <Option value="video_composition">视频合成</Option>
                <Option value="workflow_execution">工作流执行</Option>
              </Select>
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="template_id"
              label="使用模板"
            >
              <Select placeholder="选择模板（可选）">
                <Option value="template_001">产品宣传视频模板</Option>
                <Option value="template_002">课程介绍模板</Option>
                <Option value="template_003">营销文案模板</Option>
              </Select>
            </Form.Item>
          </Col>
        </Row>

        <Form.Item label="文件上传">
          <Upload
            multiple
            fileList={uploadFiles}
            onChange={({ fileList }) => setUploadFiles(fileList)}
            beforeUpload={() => false}
            listType="text"
          >
            <Button icon={<UploadOutlined />}>选择文件</Button>
          </Upload>
          <Text type="secondary" style={{ marginTop: 8, display: 'block' }}>
            支持拖拽上传，可批量选择多个文件
          </Text>
        </Form.Item>

        <Alert
          message="批量处理说明"
          description="系统将根据选择的处理类型和配置，自动处理上传的所有文件。处理过程中可以暂停、停止或重试失败的任务。"
          type="info"
          showIcon
          style={{ marginTop: 16 }}
        />
      </Form>
    </Modal>
  )

  const renderConfigDrawer = () => (
    <Drawer
      title="批量处理配置"
      placement="right"
      width={500}
      onClose={() => setConfigDrawerVisible(false)}
      open={configDrawerVisible}
    >
      <Form layout="vertical" initialValues={config}>
        <Card title="队列设置" size="small" style={{ marginBottom: 16 }}>
          <Form.Item label="并发任务数">
            <Slider
              min={1}
              max={10}
              value={config.concurrent_tasks}
              onChange={(value) => setConfig(prev => ({ ...prev, concurrent_tasks: value }))}
              marks={{ 1: '1', 5: '5', 10: '10' }}
            />
          </Form.Item>

          <Form.Item label="最大队列大小">
            <Slider
              min={10}
              max={500}
              value={config.max_queue_size}
              onChange={(value) => setConfig(prev => ({ ...prev, max_queue_size: value }))}
              marks={{ 10: '10', 100: '100', 500: '500' }}
            />
          </Form.Item>

          <Form.Item label="重试策略">
            <Radio.Group
              value={config.retry_strategy}
              onChange={(e) => setConfig(prev => ({ ...prev, retry_strategy: e.target.value }))}
            >
              <Radio value="immediate">立即重试</Radio>
              <Radio value="exponential_backoff">指数退避</Radio>
              <Radio value="fixed_delay">固定延迟</Radio>
            </Radio.Group>
          </Form.Item>
        </Card>

        <Card title="通知设置" size="small" style={{ marginBottom: 16 }}>
          <Form.Item>
            <Checkbox
              checked={config.notification_settings.on_completion}
              onChange={(e) => setConfig(prev => ({
                ...prev,
                notification_settings: {
                  ...prev.notification_settings,
                  on_completion: e.target.checked
                }
              }))}
            >
              任务完成时通知
            </Checkbox>
          </Form.Item>
          
          <Form.Item>
            <Checkbox
              checked={config.notification_settings.on_failure}
              onChange={(e) => setConfig(prev => ({
                ...prev,
                notification_settings: {
                  ...prev.notification_settings,
                  on_failure: e.target.checked
                }
              }))}
            >
              任务失败时通知
            </Checkbox>
          </Form.Item>
        </Card>

        <Card title="资源限制" size="small">
          <Form.Item label={`CPU使用限制: ${config.resource_limits.max_cpu_usage}%`}>
            <Slider
              min={20}
              max={100}
              value={config.resource_limits.max_cpu_usage}
              onChange={(value) => setConfig(prev => ({
                ...prev,
                resource_limits: { ...prev.resource_limits, max_cpu_usage: value }
              }))}
            />
          </Form.Item>

          <Form.Item label={`内存使用限制: ${config.resource_limits.max_memory_usage}MB`}>
            <Slider
              min={1024}
              max={32768}
              value={config.resource_limits.max_memory_usage}
              onChange={(value) => setConfig(prev => ({
                ...prev,
                resource_limits: { ...prev.resource_limits, max_memory_usage: value }
              }))}
            />
          </Form.Item>
        </Card>

        <div style={{ marginTop: 24 }}>
          <Button type="primary" block onClick={() => {
            message.success('配置已保存')
            setConfigDrawerVisible(false)
          }}>
            保存配置
          </Button>
        </div>
      </Form>
    </Drawer>
  )

  const renderDetailDrawer = () => (
    <Drawer
      title={selectedTask?.name}
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
                  title="总文件数"
                  value={selectedTask.total_files}
                  prefix={<FileTextOutlined />}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="已处理"
                  value={selectedTask.processed_files}
                  prefix={<CheckCircleOutlined />}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Col>
            </Row>
            <Row gutter={16} style={{ marginTop: 16 }}>
              <Col span={12}>
                <Statistic
                  title="失败"
                  value={selectedTask.failed_files}
                  prefix={<ExclamationCircleOutlined />}
                  valueStyle={{ color: '#ff4d4f' }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="成功率"
                  value={selectedTask.stats.success_rate}
                  precision={1}
                  suffix="%"
                  prefix={<BarChartOutlined />}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Col>
            </Row>
          </Card>

          <Card title="执行进度" size="small" style={{ marginBottom: 16 }}>
            <Progress
              percent={Math.round(selectedTask.progress)}
              status={selectedTask.status === 'failed' ? 'exception' : undefined}
            />
            <Timeline style={{ marginTop: 16 }}>
              <Timeline.Item
                color="green"
                dot={<CheckCircleOutlined />}
              >
                <Text strong>任务创建</Text>
                <br />
                <Text type="secondary">{new Date(selectedTask.created_at).toLocaleString()}</Text>
              </Timeline.Item>
              
              {selectedTask.started_at && (
                <Timeline.Item
                  color="blue"
                  dot={<PlayCircleOutlined />}
                >
                  <Text strong>开始执行</Text>
                  <br />
                  <Text type="secondary">{new Date(selectedTask.started_at).toLocaleString()}</Text>
                </Timeline.Item>
              )}
              
              {selectedTask.completed_at && (
                <Timeline.Item
                  color="green"
                  dot={<CheckCircleOutlined />}
                >
                  <Text strong>执行完成</Text>
                  <br />
                  <Text type="secondary">{new Date(selectedTask.completed_at).toLocaleString()}</Text>
                </Timeline.Item>
              )}
            </Timeline>
          </Card>

          <Card title="文件处理详情" size="small" style={{ marginBottom: 16 }}>
            <List
              size="small"
              dataSource={selectedTask.input_files.slice(0, 10)} // 只显示前10个文件
              renderItem={(file) => (
                <List.Item
                  extra={
                    <Space>
                      <Progress 
                        percent={file.progress} 
                        size="small" 
                        style={{ width: 100 }}
                        status={file.status === 'failed' ? 'exception' : undefined}
                      />
                      <Badge 
                        status={
                          file.status === 'completed' ? 'success' :
                          file.status === 'processing' ? 'processing' :
                          file.status === 'failed' ? 'error' : 'default'
                        }
                      />
                    </Space>
                  }
                >
                  <List.Item.Meta
                    avatar={<Avatar icon={<FileTextOutlined />} size="small" />}
                    title={file.name}
                    description={
                      <Space>
                        <Text type="secondary">{(file.size / 1024).toFixed(1)} KB</Text>
                        {file.processing_time && (
                          <Text type="secondary">{(file.processing_time / 1000).toFixed(1)}s</Text>
                        )}
                        {file.error_message && (
                          <Text type="danger">{file.error_message}</Text>
                        )}
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
            {selectedTask.input_files.length > 10 && (
              <div style={{ textAlign: 'center', marginTop: 8 }}>
                <Text type="secondary">还有 {selectedTask.input_files.length - 10} 个文件...</Text>
              </div>
            )}
          </Card>

          <Card title="资源使用" size="small">
            <Row gutter={16}>
              <Col span={12}>
                <Statistic
                  title="CPU时间"
                  value={selectedTask.resource_usage.cpu_time}
                  suffix="秒"
                  prefix={<MonitorOutlined />}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="内存峰值"
                  value={selectedTask.resource_usage.memory_peak}
                  suffix="MB"
                  prefix={<DashboardOutlined />}
                />
              </Col>
            </Row>
            <Row gutter={16} style={{ marginTop: 16 }}>
              <Col span={12}>
                <Statistic
                  title="存储使用"
                  value={selectedTask.resource_usage.storage_used}
                  suffix="MB"
                  prefix={<CloudUploadOutlined />}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="预估成本"
                  value={selectedTask.resource_usage.cost_estimate}
                  prefix="$"
                  precision={2}
                  valueStyle={{ color: '#faad14' }}
                />
              </Col>
            </Row>
          </Card>
        </div>
      )}
    </Drawer>
  )

  const getFilteredTasks = () => {
    return tasks.filter(task => {
      switch (activeTab) {
        case 'running':
          return ['running', 'paused'].includes(task.status)
        case 'pending':
          return ['pending', 'queued'].includes(task.status)
        case 'completed':
          return task.status === 'completed'
        case 'failed':
          return task.status === 'failed'
        default:
          return true
      }
    })
  }

  // ================================
  // 主渲染
  // ================================

  return (
    <div className="mixall-content-batch">
      <Card>
        <div style={{ marginBottom: 24 }}>
          <Title level={2}>
            <RobotOutlined /> 批量处理中心
          </Title>
          <Paragraph>
            企业级批量内容处理和任务管理系统，支持大规模并发处理和智能资源调度。
          </Paragraph>
        </div>

        {/* 统计面板 */}
        {renderQueueStatistics()}

        {/* 工具栏 */}
        <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
          <Col>
            <Space>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => setCreateModalVisible(true)}
              >
                创建批量任务
              </Button>
              <Button
                icon={<SettingOutlined />}
                onClick={() => setConfigDrawerVisible(true)}
              >
                处理配置
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={loadTasks}
                loading={loading}
              >
                刷新
              </Button>
            </Space>
          </Col>
          <Col>
            {renderResourceUsage()}
          </Col>
        </Row>

        {/* 任务标签页 */}
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane 
            tab={
              <Badge count={tasks.filter(t => ['running', 'paused'].includes(t.status)).length}>
                <span>运行中</span>
              </Badge>
            } 
            key="running" 
          />
          <TabPane 
            tab={
              <Badge count={tasks.filter(t => ['pending', 'queued'].includes(t.status)).length}>
                <span>等待中</span>
              </Badge>
            } 
            key="pending" 
          />
          <TabPane 
            tab={
              <Badge count={tasks.filter(t => t.status === 'completed').length}>
                <span>已完成</span>
              </Badge>
            } 
            key="completed" 
          />
          <TabPane 
            tab={
              <Badge count={tasks.filter(t => t.status === 'failed').length}>
                <span>失败</span>
              </Badge>
            } 
            key="failed" 
          />
          <TabPane tab="全部" key="all" />
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
        {renderConfigDrawer()}
        {renderDetailDrawer()}
      </Card>
    </div>
  )
}

export default MixAllContentBatch