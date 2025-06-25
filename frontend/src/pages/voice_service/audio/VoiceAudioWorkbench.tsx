/**
 * Voice Audio Workbench Component
 * 音频合成工作台组件 - [Voice][Audio][Workbench]
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
  Upload,
  Table,
  Tag,
  Progress,
  Modal,
  Tabs,
  Switch,
  message,
  Timeline,
  Statistic,
  Alert,
  Drawer,
  Tooltip,
  Popconfirm,
  Badge,
  List,
  Avatar
} from 'antd'
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  SoundOutlined,
  UploadOutlined,
  DownloadOutlined,
  DeleteOutlined,
  EditOutlined,
  CopyOutlined,
  FolderOpenOutlined,
  ExportOutlined,
  ImportOutlined,
  ThunderboltOutlined,
  SettingOutlined,
  BulbOutlined,
  StarOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  LoadingOutlined,
  AudioOutlined,
  RobotOutlined,
  FileTextOutlined,
  TeamOutlined,
  CloudUploadOutlined
} from '@ant-design/icons'

const { Title, Paragraph, Text } = Typography
const { TextArea } = Input
const { Option } = Select
const { TabPane } = Tabs

interface BatchTask {
  id: string
  name: string
  texts: string[]
  speaker_id: string
  parameters: any
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'paused'
  progress: number
  current_index: number
  created_at: string
  estimated_completion: string
  results: BatchResult[]
  error_message?: string
}

interface BatchResult {
  id: string
  text: string
  audio_url: string
  duration: number
  file_size: number
  quality_score: number
  created_at: string
}

interface TextItem {
  id: string
  text: string
  priority: 'high' | 'normal' | 'low'
  tags: string[]
  notes: string
}

interface VoiceProject {
  id: string
  name: string
  description: string
  speaker_id: string
  text_count: number
  total_duration: number
  created_at: string
  updated_at: string
  status: 'draft' | 'processing' | 'completed'
  tasks: BatchTask[]
}

const VoiceAudioWorkbench: React.FC = () => {
  const [form] = Form.useForm()
  const [activeTab, setActiveTab] = useState('batch')
  const [textItems, setTextItems] = useState<TextItem[]>([])
  const [batchTasks, setBatchTasks] = useState<BatchTask[]>([])
  const [currentTask, setCurrentTask] = useState<BatchTask | null>(null)
  const [projects, setProjects] = useState<VoiceProject[]>([])
  const [selectedProject, setSelectedProject] = useState<string>('')
  const [textModalVisible, setTextModalVisible] = useState(false)
  const [taskModalVisible, setTaskModalVisible] = useState(false)
  const [projectModalVisible, setProjectModalVisible] = useState(false)
  const [settingsVisible, setSettingsVisible] = useState(false)
  const [playingAudio, setPlayingAudio] = useState<string | null>(null)
  const audioRef = useRef<HTMLAudioElement>(null)

  const speakerOptions = [
    { label: '温柔女声', value: 'gentle_female' },
    { label: '磁性男声', value: 'magnetic_male' },
    { label: '活泼童声', value: 'lively_child' },
    { label: '知性女声', value: 'intellectual_female' },
    { label: '稳重男声', value: 'stable_male' }
  ]

  const priorityOptions = [
    { label: '高优先级', value: 'high', color: 'red' },
    { label: '普通', value: 'normal', color: 'blue' },
    { label: '低优先级', value: 'low', color: 'default' }
  ]

  useEffect(() => {
    loadProjects()
    loadBatchTasks()
  }, [])

  useEffect(() => {
    // 模拟批处理任务进度更新
    const interval = setInterval(() => {
      setBatchTasks(prev => prev.map(task => {
        if (task.status === 'processing') {
          const newProgress = Math.min(task.progress + Math.random() * 3, 100)
          const newIndex = Math.floor((newProgress / 100) * task.texts.length)
          
          if (newProgress >= 100) {
            return {
              ...task,
              status: 'completed' as const,
              progress: 100,
              current_index: task.texts.length
            }
          }
          
          return {
            ...task,
            progress: newProgress,
            current_index: newIndex
          }
        }
        return task
      }))
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  const loadProjects = async () => {
    try {
      // 模拟加载项目
      const mockProjects: VoiceProject[] = [
        {
          id: '1',
          name: '企业宣传片配音',
          description: '为企业宣传片制作专业配音',
          speaker_id: 'professional_male',
          text_count: 25,
          total_duration: 180.5,
          created_at: '2024-06-20T10:00:00Z',
          updated_at: '2024-06-22T15:30:00Z',
          status: 'processing',
          tasks: []
        },
        {
          id: '2',
          name: '儿童故事配音',
          description: '儿童绘本故事配音制作',
          speaker_id: 'lively_child',
          text_count: 40,
          total_duration: 320.8,
          created_at: '2024-06-18T14:20:00Z',
          updated_at: '2024-06-21T09:15:00Z',
          status: 'completed',
          tasks: []
        }
      ]
      
      setProjects(mockProjects)
    } catch (error) {
      console.error('Load projects error:', error)
    }
  }

  const loadBatchTasks = async () => {
    try {
      // 模拟加载批处理任务
      const mockTasks: BatchTask[] = [
        {
          id: '1',
          name: '新闻播报批量合成',
          texts: [
            '今天是2024年6月24日，星期一。',
            '天气预报：今天多云，气温18-25度。',
            '交通提醒：早高峰期间请注意出行安全。'
          ],
          speaker_id: 'news_female',
          parameters: { speed: 0.9, pitch: 1.0, emotion: 'serious' },
          status: 'processing',
          progress: 67,
          current_index: 2,
          created_at: '2024-06-24T10:30:00Z',
          estimated_completion: '2024-06-24T10:45:00Z',
          results: []
        }
      ]
      
      setBatchTasks(mockTasks)
    } catch (error) {
      console.error('Load batch tasks error:', error)
    }
  }

  const handleAddText = (values: any) => {
    const newItem: TextItem = {
      id: Date.now().toString(),
      text: values.text,
      priority: values.priority || 'normal',
      tags: values.tags || [],
      notes: values.notes || ''
    }
    
    setTextItems(prev => [...prev, newItem])
    setTextModalVisible(false)
    form.resetFields()
    message.success('文本添加成功')
  }

  const handleBulkImport = (file: File) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const content = e.target?.result as string
        const lines = content.split('\n').filter(line => line.trim())
        
        const newItems: TextItem[] = lines.map((line, index) => ({
          id: `import_${Date.now()}_${index}`,
          text: line.trim(),
          priority: 'normal',
          tags: ['批量导入'],
          notes: ''
        }))
        
        setTextItems(prev => [...prev, ...newItems])
        message.success(`成功导入 ${newItems.length} 条文本`)
      } catch (error) {
        message.error('文件解析失败')
      }
    }
    reader.readAsText(file)
    return false
  }

  const handleStartBatch = async (values: any) => {
    if (textItems.length === 0) {
      message.error('请先添加要合成的文本')
      return
    }

    const newTask: BatchTask = {
      id: Date.now().toString(),
      name: values.task_name,
      texts: textItems.map(item => item.text),
      speaker_id: values.speaker_id,
      parameters: values.parameters || {},
      status: 'processing',
      progress: 0,
      current_index: 0,
      created_at: new Date().toISOString(),
      estimated_completion: new Date(Date.now() + textItems.length * 5000).toISOString(),
      results: []
    }

    setBatchTasks(prev => [newTask, ...prev])
    setCurrentTask(newTask)
    setTaskModalVisible(false)
    message.success('批处理任务已启动')
  }

  const handlePauseTask = (taskId: string) => {
    setBatchTasks(prev => prev.map(task => 
      task.id === taskId 
        ? { ...task, status: task.status === 'processing' ? 'paused' : 'processing' }
        : task
    ))
  }

  const handleStopTask = (taskId: string) => {
    setBatchTasks(prev => prev.map(task => 
      task.id === taskId 
        ? { ...task, status: 'failed', error_message: '用户手动停止' }
        : task
    ))
  }

  const handleDeleteTask = (taskId: string) => {
    setBatchTasks(prev => prev.filter(task => task.id !== taskId))
    message.success('任务已删除')
  }

  const handleExportResults = (task: BatchTask) => {
    // 导出批处理结果
    const data = {
      task_name: task.name,
      created_at: task.created_at,
      results: task.results
    }
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `batch_results_${task.id}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  const handlePlayAudio = (audioUrl: string) => {
    if (audioRef.current) {
      if (playingAudio === audioUrl) {
        audioRef.current.pause()
        setPlayingAudio(null)
      } else {
        audioRef.current.src = audioUrl
        audioRef.current.play()
        setPlayingAudio(audioUrl)
      }
    }
  }

  const textColumns = [
    {
      title: '文本内容',
      dataIndex: 'text',
      key: 'text',
      ellipsis: true
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      render: (priority: string) => {
        const option = priorityOptions.find(p => p.value === priority)
        return <Tag color={option?.color}>{option?.label}</Tag>
      }
    },
    {
      title: '标签',
      dataIndex: 'tags',
      key: 'tags',
      render: (tags: string[]) => (
        <Space>
          {tags.map(tag => (
            <Tag key={tag} size="small">{tag}</Tag>
          ))}
        </Space>
      )
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: any, record: TextItem) => (
        <Space>
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => {
              form.setFieldsValue(record)
              setTextModalVisible(true)
            }}
          />
          <Button
            type="text"
            icon={<CopyOutlined />}
            onClick={() => {
              const newItem = { ...record, id: Date.now().toString() }
              setTextItems(prev => [...prev, newItem])
              message.success('文本已复制')
            }}
          />
          <Popconfirm
            title="确认删除这条文本吗？"
            onConfirm={() => {
              setTextItems(prev => prev.filter(item => item.id !== record.id))
              message.success('文本已删除')
            }}
          >
            <Button type="text" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      )
    }
  ]

  const taskColumns = [
    {
      title: '任务名称',
      dataIndex: 'name',
      key: 'name'
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const statusConfig = {
          pending: { color: 'default', text: '等待中', icon: <ClockCircleOutlined /> },
          processing: { color: 'blue', text: '处理中', icon: <LoadingOutlined spin /> },
          completed: { color: 'green', text: '已完成', icon: <CheckCircleOutlined /> },
          failed: { color: 'red', text: '失败', icon: <ExclamationCircleOutlined /> },
          paused: { color: 'orange', text: '已暂停', icon: <PauseCircleOutlined /> }
        }[status] || { color: 'default', text: '未知', icon: null }
        
        return (
          <Tag color={statusConfig.color} icon={statusConfig.icon}>
            {statusConfig.text}
          </Tag>
        )
      }
    },
    {
      title: '进度',
      dataIndex: 'progress',
      key: 'progress',
      render: (progress: number, record: BatchTask) => (
        <div>
          <Progress percent={Math.round(progress)} size="small" />
          <Text type="secondary" style={{ fontSize: 12 }}>
            {record.current_index}/{record.texts.length}
          </Text>
        </div>
      )
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (time: string) => new Date(time).toLocaleString()
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: any, record: BatchTask) => (
        <Space>
          {record.status === 'processing' && (
            <Button
              type="text"
              icon={<PauseCircleOutlined />}
              onClick={() => handlePauseTask(record.id)}
            />
          )}
          {record.status === 'paused' && (
            <Button
              type="text"
              icon={<PlayCircleOutlined />}
              onClick={() => handlePauseTask(record.id)}
            />
          )}
          {(record.status === 'processing' || record.status === 'paused') && (
            <Popconfirm
              title="确认停止任务吗？"
              onConfirm={() => handleStopTask(record.id)}
            >
              <Button type="text" danger icon={<ExclamationCircleOutlined />} />
            </Popconfirm>
          )}
          {record.status === 'completed' && (
            <Button
              type="text"
              icon={<ExportOutlined />}
              onClick={() => handleExportResults(record)}
            />
          )}
          <Popconfirm
            title="确认删除任务吗？"
            onConfirm={() => handleDeleteTask(record.id)}
          >
            <Button type="text" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      )
    }
  ]

  const getTaskStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return <ClockCircleOutlined style={{ color: '#d9d9d9' }} />
      case 'processing': return <LoadingOutlined spin style={{ color: '#1890ff' }} />
      case 'completed': return <CheckCircleOutlined style={{ color: '#52c41a' }} />
      case 'failed': return <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />
      case 'paused': return <PauseCircleOutlined style={{ color: '#faad14' }} />
      default: return null
    }
  }

  return (
    <div className="voice-audio-workbench">
      <Card>
        <Title level={2}>
          <RobotOutlined /> 音频合成工作台
        </Title>
        <Paragraph>
          专业的批量语音合成工具，支持项目管理、批处理和高级音频处理功能。
        </Paragraph>

        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col>
            <Statistic
              title="活跃任务"
              value={batchTasks.filter(t => t.status === 'processing').length}
              prefix={<LoadingOutlined />}
            />
          </Col>
          <Col>
            <Statistic
              title="已完成"
              value={batchTasks.filter(t => t.status === 'completed').length}
              prefix={<CheckCircleOutlined />}
            />
          </Col>
          <Col>
            <Statistic
              title="文本队列"
              value={textItems.length}
              prefix={<FileTextOutlined />}
            />
          </Col>
          <Col>
            <Statistic
              title="总项目"
              value={projects.length}
              prefix={<FolderOpenOutlined />}
            />
          </Col>
        </Row>

        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane tab="批量合成" key="batch">
            <Row gutter={24}>
              <Col xs={24} lg={16}>
                <Card 
                  title="文本管理" 
                  size="small"
                  extra={
                    <Space>
                      <Upload
                        beforeUpload={handleBulkImport}
                        showUploadList={false}
                        accept=".txt,.csv"
                      >
                        <Button icon={<ImportOutlined />} size="small">
                          批量导入
                        </Button>
                      </Upload>
                      <Button
                        type="primary"
                        icon={<FileTextOutlined />}
                        size="small"
                        onClick={() => setTextModalVisible(true)}
                      >
                        添加文本
                      </Button>
                    </Space>
                  }
                >
                  <Table
                    dataSource={textItems}
                    columns={textColumns}
                    pagination={{ pageSize: 10 }}
                    size="small"
                    rowKey="id"
                  />
                </Card>
              </Col>

              <Col xs={24} lg={8}>
                <Card title="批处理控制" size="small">
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Button
                      type="primary"
                      icon={<ThunderboltOutlined />}
                      onClick={() => setTaskModalVisible(true)}
                      disabled={textItems.length === 0}
                      block
                    >
                      开始批量合成
                    </Button>

                    <Button
                      icon={<SettingOutlined />}
                      onClick={() => setSettingsVisible(true)}
                      block
                    >
                      合成设置
                    </Button>

                    <Divider />

                    <div>
                      <Text strong>快速统计</Text>
                      <div style={{ marginTop: 8 }}>
                        <Text type="secondary">
                          总文本数: {textItems.length} 条
                        </Text>
                        <br />
                        <Text type="secondary">
                          预计时长: {(textItems.length * 8).toFixed(1)} 分钟
                        </Text>
                        <br />
                        <Text type="secondary">
                          预计文件大小: {(textItems.length * 2.5).toFixed(1)} MB
                        </Text>
                      </div>
                    </div>

                    <Alert
                      message="提示"
                      description="批量合成将按照文本顺序依次处理，请确保网络连接稳定。"
                      type="info"
                      showIcon
                      style={{ fontSize: 12 }}
                    />
                  </Space>
                </Card>
              </Col>
            </Row>
          </TabPane>

          <TabPane tab="任务监控" key="tasks">
            <Card title="批处理任务" size="small">
              {batchTasks.length === 0 ? (
                <div style={{ textAlign: 'center', padding: 40 }}>
                  <RobotOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />
                  <div style={{ marginTop: 16 }}>
                    <Text type="secondary">暂无批处理任务</Text>
                  </div>
                </div>
              ) : (
                <List
                  dataSource={batchTasks}
                  renderItem={task => (
                    <List.Item>
                      <Card size="small" style={{ width: '100%' }}>
                        <Row align="middle" gutter={16}>
                          <Col span={1}>
                            {getTaskStatusIcon(task.status)}
                          </Col>
                          <Col flex="auto">
                            <div>
                              <Text strong>{task.name}</Text>
                              <Tag style={{ marginLeft: 8 }}>
                                {task.texts.length} 条文本
                              </Tag>
                            </div>
                            <div style={{ marginTop: 4 }}>
                              <Progress
                                percent={Math.round(task.progress)}
                                size="small"
                                status={task.status === 'failed' ? 'exception' : 'active'}
                              />
                            </div>
                            <div style={{ marginTop: 4 }}>
                              <Text type="secondary" style={{ fontSize: 12 }}>
                                {task.status === 'processing' && `进行中: ${task.current_index}/${task.texts.length}`}
                                {task.status === 'completed' && `已完成于 ${new Date(task.created_at).toLocaleTimeString()}`}
                                {task.status === 'failed' && `失败: ${task.error_message}`}
                                {task.status === 'paused' && '已暂停'}
                              </Text>
                            </div>
                          </Col>
                          <Col>
                            <Space>
                              {task.status === 'processing' && (
                                <Button
                                  type="text"
                                  icon={<PauseCircleOutlined />}
                                  onClick={() => handlePauseTask(task.id)}
                                />
                              )}
                              {task.status === 'paused' && (
                                <Button
                                  type="text"
                                  icon={<PlayCircleOutlined />}
                                  onClick={() => handlePauseTask(task.id)}
                                />
                              )}
                              {task.status === 'completed' && (
                                <Button
                                  type="text"
                                  icon={<ExportOutlined />}
                                  onClick={() => handleExportResults(task)}
                                />
                              )}
                              <Popconfirm
                                title="确认删除任务吗？"
                                onConfirm={() => handleDeleteTask(task.id)}
                              >
                                <Button type="text" danger icon={<DeleteOutlined />} />
                              </Popconfirm>
                            </Space>
                          </Col>
                        </Row>
                      </Card>
                    </List.Item>
                  )}
                />
              )}
            </Card>
          </TabPane>

          <TabPane tab="项目管理" key="projects">
            <Card 
              title="项目列表" 
              size="small"
              extra={
                <Button
                  type="primary"
                  icon={<FolderOpenOutlined />}
                  onClick={() => setProjectModalVisible(true)}
                >
                  新建项目
                </Button>
              }
            >
              <Row gutter={16}>
                {projects.map(project => (
                  <Col key={project.id} xs={24} sm={12} lg={8}>
                    <Card
                      size="small"
                      hoverable
                      title={project.name}
                      extra={
                        <Badge
                          status={
                            project.status === 'completed' ? 'success' :
                            project.status === 'processing' ? 'processing' : 'default'
                          }
                          text={
                            project.status === 'completed' ? '已完成' :
                            project.status === 'processing' ? '进行中' : '草稿'
                          }
                        />
                      }
                    >
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <Text type="secondary" ellipsis>
                          {project.description}
                        </Text>
                        
                        <Row gutter={8}>
                          <Col span={12}>
                            <Statistic
                              title="文本数"
                              value={project.text_count}
                              valueStyle={{ fontSize: 14 }}
                            />
                          </Col>
                          <Col span={12}>
                            <Statistic
                              title="总时长"
                              value={`${(project.total_duration / 60).toFixed(1)}分`}
                              valueStyle={{ fontSize: 14 }}
                            />
                          </Col>
                        </Row>

                        <div style={{ textAlign: 'right' }}>
                          <Space>
                            <Button
                              type="text"
                              size="small"
                              icon={<EditOutlined />}
                            >
                              编辑
                            </Button>
                            <Button
                              type="text"
                              size="small"
                              icon={<ExportOutlined />}
                            >
                              导出
                            </Button>
                          </Space>
                        </div>
                      </Space>
                    </Card>
                  </Col>
                ))}
              </Row>
            </Card>
          </TabPane>
        </Tabs>
      </Card>

      <audio ref={audioRef} />

      {/* 添加文本模态框 */}
      <Modal
        title="添加文本"
        open={textModalVisible}
        onCancel={() => setTextModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleAddText}>
          <Form.Item
            name="text"
            label="文本内容"
            rules={[{ required: true, message: '请输入文本内容' }]}
          >
            <TextArea
              rows={4}
              placeholder="请输入要合成的文本内容..."
              showCount
              maxLength={500}
            />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="priority"
                label="优先级"
                initialValue="normal"
              >
                <Select>
                  {priorityOptions.map(option => (
                    <Option key={option.value} value={option.value}>
                      {option.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="tags"
                label="标签"
              >
                <Select
                  mode="tags"
                  placeholder="添加标签"
                  tokenSeparators={[',']}
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="notes"
            label="备注"
          >
            <TextArea rows={2} placeholder="添加备注信息..." />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                添加文本
              </Button>
              <Button onClick={() => setTextModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 启动批处理模态框 */}
      <Modal
        title="启动批量合成"
        open={taskModalVisible}
        onCancel={() => setTaskModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form layout="vertical" onFinish={handleStartBatch}>
          <Form.Item
            name="task_name"
            label="任务名称"
            rules={[{ required: true, message: '请输入任务名称' }]}
          >
            <Input placeholder="为您的批处理任务起一个名字" />
          </Form.Item>

          <Form.Item
            name="speaker_id"
            label="说话人"
            rules={[{ required: true, message: '请选择说话人' }]}
          >
            <Select placeholder="选择说话人">
              {speakerOptions.map(option => (
                <Option key={option.value} value={option.value}>
                  {option.label}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Alert
            message="批处理信息"
            description={`将处理 ${textItems.length} 条文本，预计需要 ${(textItems.length * 5 / 60).toFixed(1)} 分钟完成。`}
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
          />

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                启动批处理
              </Button>
              <Button onClick={() => setTaskModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 合成设置抽屉 */}
      <Drawer
        title="批量合成设置"
        open={settingsVisible}
        onClose={() => setSettingsVisible(false)}
        width={400}
      >
        <Form layout="vertical">
          <Title level={4}>音质设置</Title>
          <Form.Item label="音频格式">
            <Select defaultValue="mp3">
              <Option value="mp3">MP3 (推荐)</Option>
              <Option value="wav">WAV (无损)</Option>
              <Option value="m4a">M4A (高质量)</Option>
            </Select>
          </Form.Item>

          <Form.Item label="采样率">
            <Select defaultValue="22050">
              <Option value="16000">16kHz (标准)</Option>
              <Option value="22050">22kHz (推荐)</Option>
              <Option value="44100">44kHz (高质量)</Option>
            </Select>
          </Form.Item>

          <Form.Item label="比特率">
            <Select defaultValue="128">
              <Option value="96">96kbps</Option>
              <Option value="128">128kbps (推荐)</Option>
              <Option value="192">192kbps</Option>
              <Option value="320">320kbps (最高)</Option>
            </Select>
          </Form.Item>

          <Divider />

          <Title level={4}>处理选项</Title>
          <Form.Item>
            <Space direction="vertical">
              <Switch defaultChecked /> 自动标准化音量
              <Switch defaultChecked /> 移除长时间静音
              <Switch /> 添加淡入淡出效果
              <Switch /> 启用噪音抑制
            </Space>
          </Form.Item>

          <Divider />

          <Title level={4}>输出选项</Title>
          <Form.Item label="文件命名">
            <Select defaultValue="index">
              <Option value="index">序号命名 (001, 002...)</Option>
              <Option value="text">文本摘要命名</Option>
              <Option value="timestamp">时间戳命名</Option>
            </Select>
          </Form.Item>

          <Form.Item>
            <Space direction="vertical">
              <Switch defaultChecked /> 自动打包下载
              <Switch /> 生成播放列表
              <Switch /> 导出批处理报告
            </Space>
          </Form.Item>
        </Form>
      </Drawer>
    </div>
  )
}

export default VoiceAudioWorkbench