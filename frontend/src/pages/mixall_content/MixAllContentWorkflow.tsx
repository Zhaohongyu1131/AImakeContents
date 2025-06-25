/**
 * Mix All Content Workflow Editor Component
 * 混合内容工作流编辑器 - [MixAll][Content][Workflow]
 * 
 * 企业级可视化内容创作流程编辑器
 * 基于节点图的工作流设计，支持复杂的多媒体内容生产管道
 */

import React, { useState, useCallback, useRef, useEffect } from 'react'
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
  Switch,
  Slider,
  message,
  Drawer,
  Tabs,
  Collapse,
  Tag,
  Tooltip,
  Popconfirm,
  Alert,
  Progress,
  Timeline,
  Statistic,
  Badge,
  Divider
} from 'antd'
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  StopOutlined,
  SaveOutlined,
  DownloadOutlined,
  UploadOutlined,
  CopyOutlined,
  DeleteOutlined,
  SettingOutlined,
  EyeOutlined,
  BranchesOutlined,
  NodeIndexOutlined,
  ThunderboltOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined,
  PlusOutlined,
  MinusOutlined,
  ArrowRightOutlined,
  DragOutlined,
  FileTextOutlined,
  SoundOutlined,
  FileImageOutlined,
  VideoCameraOutlined,
  ApiOutlined,
  FunctionOutlined,
  FilterOutlined,
  MergeOutlined,
  SplitCellsOutlined,
  ShareAltOutlined
} from '@ant-design/icons'
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Connection,
  ConnectionMode,
  ReactFlowProvider,
  Panel,
  MarkerType,
  Position
} from 'reactflow'
import 'reactflow/dist/style.css'

const { Title, Paragraph, Text } = Typography
const { TextArea } = Input
const { Option } = Select
const { TabPane } = Tabs
const { Panel: CollapsePanel } = Collapse

// ================================
// 工作流节点类型定义 - Workflow Node Types
// ================================

export type WorkflowNodeType = 
  | 'input'           // 输入节点
  | 'text_process'    // 文本处理
  | 'voice_synthesis' // 语音合成
  | 'image_generate'  // 图像生成
  | 'video_compose'   // 视频合成
  | 'audio_mix'       // 音频混音
  | 'filter'          // 过滤器
  | 'transform'       // 变换处理
  | 'condition'       // 条件判断
  | 'loop'            // 循环控制
  | 'merge'           // 合并节点
  | 'split'           // 分割节点
  | 'output'          // 输出节点

export type WorkflowExecutionStatus = 'idle' | 'running' | 'paused' | 'completed' | 'failed'
export type NodeExecutionStatus = 'pending' | 'running' | 'completed' | 'failed' | 'skipped'

interface WorkflowNodeData {
  id: string
  type: WorkflowNodeType
  label: string
  description?: string
  parameters: Record<string, any>
  status: NodeExecutionStatus
  executionTime?: number
  errorMessage?: string
  inputPorts: string[]
  outputPorts: string[]
  position: { x: number; y: number }
}

interface WorkflowTemplate {
  id: string
  name: string
  description: string
  category: string
  nodes: WorkflowNodeData[]
  edges: Edge[]
  metadata: {
    author: string
    version: string
    created_at: string
    updated_at: string
    tags: string[]
    is_public: boolean
  }
  execution: {
    status: WorkflowExecutionStatus
    progress: number
    start_time?: string
    end_time?: string
    total_nodes: number
    completed_nodes: number
    failed_nodes: number
  }
}

// ================================
// 节点配置定义 - Node Configurations
// ================================

const workflowNodeConfigs: Record<WorkflowNodeType, {
  label: string
  icon: React.ReactNode
  color: string
  category: string
  description: string
  defaultParams: Record<string, any>
  inputPorts: string[]
  outputPorts: string[]
}> = {
  input: {
    label: '输入节点',
    icon: <UploadOutlined />,
    color: '#52c41a',
    category: '数据源',
    description: '工作流的起始节点，用于接收外部输入',
    defaultParams: { input_type: 'file', file_format: 'auto' },
    inputPorts: [],
    outputPorts: ['data']
  },
  text_process: {
    label: '文本处理',
    icon: <FileTextOutlined />,
    color: '#1890ff',
    category: '内容处理',
    description: '处理和转换文本内容',
    defaultParams: { operation: 'clean', language: 'zh-CN' },
    inputPorts: ['text_input'],
    outputPorts: ['text_output']
  },
  voice_synthesis: {
    label: '语音合成',
    icon: <SoundOutlined />,
    color: '#722ed1',
    category: '内容生成',
    description: '将文本转换为语音',
    defaultParams: { voice_id: '', speed: 1.0, pitch: 1.0, volume: 1.0 },
    inputPorts: ['text_input'],
    outputPorts: ['audio_output']
  },
  image_generate: {
    label: '图像生成',
    icon: <FileImageOutlined />,
    color: '#fa8c16',
    category: '内容生成',
    description: '基于文本描述生成图像',
    defaultParams: { style: 'realistic', resolution: '1024x1024', quality: 'high' },
    inputPorts: ['prompt_input'],
    outputPorts: ['image_output']
  },
  video_compose: {
    label: '视频合成',
    icon: <VideoCameraOutlined />,
    color: '#eb2f96',
    category: '内容合成',
    description: '合成多媒体内容为视频',
    defaultParams: { resolution: '1920x1080', fps: 30, format: 'mp4' },
    inputPorts: ['video_input', 'audio_input', 'image_input'],
    outputPorts: ['video_output']
  },
  audio_mix: {
    label: '音频混音',
    icon: <SoundOutlined />,
    color: '#13c2c2',
    category: '内容合成',
    description: '混合多个音频轨道',
    defaultParams: { mix_mode: 'overlay', volume_balance: 0.5 },
    inputPorts: ['audio_input_1', 'audio_input_2'],
    outputPorts: ['audio_output']
  },
  filter: {
    label: '过滤器',
    icon: <FilterOutlined />,
    color: '#faad14',
    category: '数据处理',
    description: '根据条件过滤数据',
    defaultParams: { filter_type: 'quality', threshold: 0.8 },
    inputPorts: ['data_input'],
    outputPorts: ['filtered_output', 'rejected_output']
  },
  transform: {
    label: '变换处理',
    icon: <FunctionOutlined />,
    color: '#a0d911',
    category: '数据处理',
    description: '对数据进行变换和处理',
    defaultParams: { transform_type: 'resize', parameters: {} },
    inputPorts: ['data_input'],
    outputPorts: ['data_output']
  },
  condition: {
    label: '条件判断',
    icon: <BranchesOutlined />,
    color: '#ff7a45',
    category: '流程控制',
    description: '根据条件控制执行流程',
    defaultParams: { condition_type: 'value_compare', operator: 'greater_than', threshold: 0 },
    inputPorts: ['condition_input'],
    outputPorts: ['true_output', 'false_output']
  },
  loop: {
    label: '循环控制',
    icon: <ApiOutlined />,
    color: '#f759ab',
    category: '流程控制',
    description: '循环执行指定的操作',
    defaultParams: { loop_type: 'count', max_iterations: 10, break_condition: '' },
    inputPorts: ['loop_input'],
    outputPorts: ['loop_output', 'final_output']
  },
  merge: {
    label: '合并节点',
    icon: <MergeOutlined />,
    color: '#40a9ff',
    category: '数据处理',
    description: '合并多个输入流',
    defaultParams: { merge_strategy: 'concat', sync_mode: 'wait_all' },
    inputPorts: ['input_1', 'input_2', 'input_3'],
    outputPorts: ['merged_output']
  },
  split: {
    label: '分割节点',
    icon: <SplitCellsOutlined />,
    color: '#95de64',
    category: '数据处理',
    description: '将输入分割为多个输出',
    defaultParams: { split_strategy: 'equal', output_count: 2 },
    inputPorts: ['data_input'],
    outputPorts: ['output_1', 'output_2', 'output_3']
  },
  output: {
    label: '输出节点',
    icon: <DownloadOutlined />,
    color: '#ff4d4f',
    category: '数据输出',
    description: '工作流的终止节点，输出最终结果',
    defaultParams: { output_format: 'file', storage_location: 'local' },
    inputPorts: ['final_input'],
    outputPorts: []
  }
}

// ================================
// 自定义节点组件 - Custom Node Components
// ================================

const CustomWorkflowNode: React.FC<{
  data: WorkflowNodeData
  selected: boolean
}> = ({ data, selected }) => {
  const config = workflowNodeConfigs[data.type]
  
  const getStatusColor = (status: NodeExecutionStatus) => {
    switch (status) {
      case 'pending': return '#d9d9d9'
      case 'running': return '#1890ff'
      case 'completed': return '#52c41a'
      case 'failed': return '#ff4d4f'
      case 'skipped': return '#faad14'
      default: return '#d9d9d9'
    }
  }

  const getStatusIcon = (status: NodeExecutionStatus) => {
    switch (status) {
      case 'running': return <LoadingOutlined />
      case 'completed': return <CheckCircleOutlined />
      case 'failed': return <ExclamationCircleOutlined />
      case 'skipped': return <MinusOutlined />
      default: return <ClockCircleOutlined />
    }
  }

  return (
    <div
      style={{
        background: selected ? '#e6f7ff' : 'white',
        border: `2px solid ${selected ? config.color : '#d9d9d9'}`,
        borderRadius: 8,
        padding: '12px 16px',
        minWidth: 180,
        boxShadow: selected ? '0 4px 12px rgba(0,0,0,0.15)' : '0 2px 8px rgba(0,0,0,0.1)'
      }}
    >
      {/* 节点头部 */}
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
        <div
          style={{
            width: 24,
            height: 24,
            borderRadius: '50%',
            background: config.color,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            marginRight: 8
          }}
        >
          {config.icon}
        </div>
        <div style={{ flex: 1 }}>
          <Text strong style={{ fontSize: 12 }}>{data.label}</Text>
        </div>
        <div style={{ color: getStatusColor(data.status) }}>
          {getStatusIcon(data.status)}
        </div>
      </div>

      {/* 节点描述 */}
      {data.description && (
        <Text type="secondary" style={{ fontSize: 11, display: 'block', marginBottom: 8 }}>
          {data.description}
        </Text>
      )}

      {/* 执行信息 */}
      {data.status === 'running' && (
        <Progress size="small" percent={50} showInfo={false} />
      )}
      
      {data.status === 'failed' && data.errorMessage && (
        <Text type="danger" style={{ fontSize: 10 }}>
          错误: {data.errorMessage}
        </Text>
      )}

      {data.executionTime && (
        <Text type="secondary" style={{ fontSize: 10 }}>
          执行时间: {data.executionTime}ms
        </Text>
      )}

      {/* 连接点 */}
      {config.inputPorts.map((port, index) => (
        <div
          key={`input-${port}`}
          className="react-flow__handle react-flow__handle-left"
          style={{
            left: -8,
            top: 40 + index * 20,
            width: 12,
            height: 12,
            background: '#1890ff'
          }}
        />
      ))}

      {config.outputPorts.map((port, index) => (
        <div
          key={`output-${port}`}
          className="react-flow__handle react-flow__handle-right"
          style={{
            right: -8,
            top: 40 + index * 20,
            width: 12,
            height: 12,
            background: config.color
          }}
        />
      ))}
    </div>
  )
}

// ================================
// 主组件 - Main Component
// ================================

const MixAllContentWorkflow: React.FC = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [selectedNode, setSelectedNode] = useState<WorkflowNodeData | null>(null)
  const [workflow, setWorkflow] = useState<WorkflowTemplate | null>(null)
  const [drawerVisible, setDrawerVisible] = useState(false)
  const [executionStatus, setExecutionStatus] = useState<WorkflowExecutionStatus>('idle')
  const [executionProgress, setExecutionProgress] = useState(0)
  const [saveModalVisible, setSaveModalVisible] = useState(false)
  const [loadModalVisible, setLoadModalVisible] = useState(false)
  const [form] = Form.useForm()
  const reactFlowWrapper = useRef<HTMLDivElement>(null)
  const [reactFlowInstance, setReactFlowInstance] = useState<any>(null)

  // ================================
  // 节点操作 - Node Operations
  // ================================

  const onConnect = useCallback(
    (params: Connection) => {
      const newEdge = {
        ...params,
        animated: true,
        style: { stroke: '#1890ff' },
        markerEnd: { type: MarkerType.ArrowClosed, color: '#1890ff' }
      }
      setEdges((eds) => addEdge(newEdge, eds))
    },
    [setEdges]
  )

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
  }, [])

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault()

      const reactFlowBounds = reactFlowWrapper.current?.getBoundingClientRect()
      if (!reactFlowBounds || !reactFlowInstance) return

      const nodeType = event.dataTransfer.getData('application/reactflow')
      if (!nodeType || !workflowNodeConfigs[nodeType as WorkflowNodeType]) return

      const position = reactFlowInstance.project({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top
      })

      addNode(nodeType as WorkflowNodeType, position)
    },
    [reactFlowInstance]
  )

  const addNode = (nodeType: WorkflowNodeType, position: { x: number; y: number }) => {
    const config = workflowNodeConfigs[nodeType]
    const nodeId = `${nodeType}_${Date.now()}`
    
    const newNodeData: WorkflowNodeData = {
      id: nodeId,
      type: nodeType,
      label: config.label,
      description: config.description,
      parameters: { ...config.defaultParams },
      status: 'pending',
      inputPorts: config.inputPorts,
      outputPorts: config.outputPorts,
      position
    }

    const newNode: Node = {
      id: nodeId,
      type: 'custom',
      position,
      data: newNodeData
    }

    setNodes((nds) => nds.concat(newNode))
  }

  const deleteNode = (nodeId: string) => {
    setNodes((nds) => nds.filter((node) => node.id !== nodeId))
    setEdges((eds) => eds.filter((edge) => edge.source !== nodeId && edge.target !== nodeId))
  }

  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node.data as WorkflowNodeData)
    setDrawerVisible(true)
  }, [])

  // ================================
  // 工作流执行 - Workflow Execution
  // ================================

  const executeWorkflow = async () => {
    if (nodes.length === 0) {
      message.warning('工作流为空，请添加节点')
      return
    }

    setExecutionStatus('running')
    setExecutionProgress(0)
    
    try {
      // 拓扑排序确定执行顺序
      const executionOrder = topologicalSort(nodes, edges)
      
      for (let i = 0; i < executionOrder.length; i++) {
        const nodeId = executionOrder[i]
        
        // 更新节点状态为运行中
        setNodes((nds) =>
          nds.map((node) =>
            node.id === nodeId
              ? { ...node, data: { ...node.data, status: 'running' } }
              : node
          )
        )

        // 模拟节点执行
        await simulateNodeExecution(nodeId)
        
        // 更新节点状态为完成
        setNodes((nds) =>
          nds.map((node) =>
            node.id === nodeId
              ? {
                  ...node,
                  data: {
                    ...node.data,
                    status: 'completed',
                    executionTime: Math.random() * 2000 + 500
                  }
                }
              : node
          )
        )

        // 更新执行进度
        const progress = ((i + 1) / executionOrder.length) * 100
        setExecutionProgress(progress)
      }

      setExecutionStatus('completed')
      message.success('工作流执行完成！')
    } catch (error) {
      setExecutionStatus('failed')
      message.error('工作流执行失败')
      console.error('Workflow execution failed:', error)
    }
  }

  const pauseWorkflow = () => {
    setExecutionStatus('paused')
    message.info('工作流已暂停')
  }

  const stopWorkflow = () => {
    setExecutionStatus('idle')
    setExecutionProgress(0)
    
    // 重置所有节点状态
    setNodes((nds) =>
      nds.map((node) => ({
        ...node,
        data: { ...node.data, status: 'pending', executionTime: undefined, errorMessage: undefined }
      }))
    )
    
    message.info('工作流已停止')
  }

  const simulateNodeExecution = (nodeId: string): Promise<void> => {
    return new Promise((resolve) => {
      // 模拟不同类型节点的执行时间
      const executionTime = Math.random() * 2000 + 1000
      setTimeout(resolve, executionTime)
    })
  }

  const topologicalSort = (nodes: Node[], edges: Edge[]): string[] => {
    // 简化的拓扑排序实现
    const inDegree: Record<string, number> = {}
    const graph: Record<string, string[]> = {}

    // 初始化
    nodes.forEach((node) => {
      inDegree[node.id] = 0
      graph[node.id] = []
    })

    // 构建图和计算入度
    edges.forEach((edge) => {
      if (edge.source && edge.target) {
        graph[edge.source].push(edge.target)
        inDegree[edge.target] = (inDegree[edge.target] || 0) + 1
      }
    })

    // 拓扑排序
    const queue: string[] = []
    const result: string[] = []

    Object.keys(inDegree).forEach((nodeId) => {
      if (inDegree[nodeId] === 0) {
        queue.push(nodeId)
      }
    })

    while (queue.length > 0) {
      const current = queue.shift()!
      result.push(current)

      graph[current].forEach((neighbor) => {
        inDegree[neighbor]--
        if (inDegree[neighbor] === 0) {
          queue.push(neighbor)
        }
      })
    }

    return result
  }

  // ================================
  // 工作流保存和加载 - Workflow Save & Load
  // ================================

  const saveWorkflow = async (values: any) => {
    try {
      const workflowTemplate: WorkflowTemplate = {
        id: `workflow_${Date.now()}`,
        name: values.name,
        description: values.description,
        category: values.category,
        nodes: nodes.map((node) => node.data as WorkflowNodeData),
        edges: edges,
        metadata: {
          author: 'current_user',
          version: '1.0.0',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          tags: values.tags || [],
          is_public: values.is_public || false
        },
        execution: {
          status: 'idle',
          progress: 0,
          total_nodes: nodes.length,
          completed_nodes: 0,
          failed_nodes: 0
        }
      }

      // 这里应该调用API保存工作流
      // await workflowService.saveWorkflow(workflowTemplate)
      
      setWorkflow(workflowTemplate)
      message.success('工作流保存成功！')
      setSaveModalVisible(false)
      form.resetFields()
    } catch (error) {
      console.error('Failed to save workflow:', error)
      message.error('工作流保存失败')
    }
  }

  const loadWorkflow = (workflowTemplate: WorkflowTemplate) => {
    try {
      // 重建节点
      const loadedNodes: Node[] = workflowTemplate.nodes.map((nodeData) => ({
        id: nodeData.id,
        type: 'custom',
        position: nodeData.position,
        data: nodeData
      }))

      setNodes(loadedNodes)
      setEdges(workflowTemplate.edges)
      setWorkflow(workflowTemplate)
      
      message.success(`工作流 "${workflowTemplate.name}" 加载成功！`)
      setLoadModalVisible(false)
    } catch (error) {
      console.error('Failed to load workflow:', error)
      message.error('工作流加载失败')
    }
  }

  // ================================
  // 节点面板渲染 - Node Panel Rendering
  // ================================

  const renderNodePanel = () => (
    <Card title="节点库" size="small" style={{ marginBottom: 16 }}>
      <Collapse size="small" defaultActiveKey={['content', 'process', 'control']}>
        <CollapsePanel header="内容生成" key="content">
          <Space direction="vertical" style={{ width: '100%' }}>
            {Object.entries(workflowNodeConfigs)
              .filter(([, config]) => config.category === '内容生成' || config.category === '数据源')
              .map(([nodeType, config]) => (
                <Button
                  key={nodeType}
                  size="small"
                  block
                  icon={config.icon}
                  draggable
                  onDragStart={(event) => {
                    event.dataTransfer.setData('application/reactflow', nodeType)
                    event.dataTransfer.effectAllowed = 'move'
                  }}
                  style={{
                    textAlign: 'left',
                    borderColor: config.color,
                    color: config.color
                  }}
                >
                  {config.label}
                </Button>
              ))}
          </Space>
        </CollapsePanel>

        <CollapsePanel header="数据处理" key="process">
          <Space direction="vertical" style={{ width: '100%' }}>
            {Object.entries(workflowNodeConfigs)
              .filter(([, config]) => config.category === '数据处理' || config.category === '内容处理' || config.category === '内容合成')
              .map(([nodeType, config]) => (
                <Button
                  key={nodeType}
                  size="small"
                  block
                  icon={config.icon}
                  draggable
                  onDragStart={(event) => {
                    event.dataTransfer.setData('application/reactflow', nodeType)
                    event.dataTransfer.effectAllowed = 'move'
                  }}
                  style={{
                    textAlign: 'left',
                    borderColor: config.color,
                    color: config.color
                  }}
                >
                  {config.label}
                </Button>
              ))}
          </Space>
        </CollapsePanel>

        <CollapsePanel header="流程控制" key="control">
          <Space direction="vertical" style={{ width: '100%' }}>
            {Object.entries(workflowNodeConfigs)
              .filter(([, config]) => config.category === '流程控制' || config.category === '数据输出')
              .map(([nodeType, config]) => (
                <Button
                  key={nodeType}
                  size="small"
                  block
                  icon={config.icon}
                  draggable
                  onDragStart={(event) => {
                    event.dataTransfer.setData('application/reactflow', nodeType)
                    event.dataTransfer.effectAllowed = 'move'
                  }}
                  style={{
                    textAlign: 'left',
                    borderColor: config.color,
                    color: config.color
                  }}
                >
                  {config.label}
                </Button>
              ))}
          </Space>
        </CollapsePanel>
      </Collapse>
    </Card>
  )

  const renderExecutionPanel = () => (
    <Card title="执行控制" size="small">
      <Space direction="vertical" style={{ width: '100%' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <Space>
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={executeWorkflow}
              disabled={executionStatus === 'running' || nodes.length === 0}
              size="small"
            >
              执行
            </Button>
            <Button
              icon={<PauseCircleOutlined />}
              onClick={pauseWorkflow}
              disabled={executionStatus !== 'running'}
              size="small"
            >
              暂停
            </Button>
            <Button
              icon={<StopOutlined />}
              onClick={stopWorkflow}
              disabled={executionStatus === 'idle'}
              size="small"
            >
              停止
            </Button>
          </Space>
        </div>

        {executionStatus !== 'idle' && (
          <div>
            <div style={{ marginBottom: 8 }}>
              <Text strong>执行状态: </Text>
              <Badge
                status={
                  executionStatus === 'running' ? 'processing' :
                  executionStatus === 'completed' ? 'success' :
                  executionStatus === 'failed' ? 'error' : 'default'
                }
                text={
                  executionStatus === 'running' ? '运行中' :
                  executionStatus === 'completed' ? '已完成' :
                  executionStatus === 'failed' ? '失败' : '暂停'
                }
              />
            </div>
            <Progress percent={Math.round(executionProgress)} size="small" />
          </div>
        )}

        <Divider style={{ margin: '12px 0' }} />

        <div>
          <Text strong>工作流统计</Text>
          <Row gutter={8} style={{ marginTop: 8 }}>
            <Col span={12}>
              <Statistic
                title="节点总数"
                value={nodes.length}
                valueStyle={{ fontSize: 14 }}
              />
            </Col>
            <Col span={12}>
              <Statistic
                title="连接数"
                value={edges.length}
                valueStyle={{ fontSize: 14 }}
              />
            </Col>
          </Row>
        </div>
      </Space>
    </Card>
  )

  const renderNodeDrawer = () => (
    <Drawer
      title={selectedNode ? `${selectedNode.label} - 节点设置` : '节点设置'}
      placement="right"
      width={400}
      onClose={() => setDrawerVisible(false)}
      open={drawerVisible}
    >
      {selectedNode && (
        <div>
          <Tabs defaultActiveKey="properties">
            <TabPane tab="属性" key="properties">
              <Form layout="vertical">
                <Form.Item label="节点名称">
                  <Input
                    value={selectedNode.label}
                    onChange={(e) => {
                      const updatedNode = { ...selectedNode, label: e.target.value }
                      setSelectedNode(updatedNode)
                      setNodes((nds) =>
                        nds.map((node) =>
                          node.id === selectedNode.id
                            ? { ...node, data: updatedNode }
                            : node
                        )
                      )
                    }}
                  />
                </Form.Item>

                <Form.Item label="描述">
                  <TextArea
                    rows={3}
                    value={selectedNode.description}
                    onChange={(e) => {
                      const updatedNode = { ...selectedNode, description: e.target.value }
                      setSelectedNode(updatedNode)
                      setNodes((nds) =>
                        nds.map((node) =>
                          node.id === selectedNode.id
                            ? { ...node, data: updatedNode }
                            : node
                        )
                      )
                    }}
                  />
                </Form.Item>

                <Divider>参数配置</Divider>

                {/* 根据节点类型渲染不同的参数配置 */}
                {selectedNode.type === 'voice_synthesis' && (
                  <>
                    <Form.Item label="音色ID">
                      <Select
                        value={selectedNode.parameters.voice_id}
                        onChange={(value) => {
                          const updatedParams = { ...selectedNode.parameters, voice_id: value }
                          const updatedNode = { ...selectedNode, parameters: updatedParams }
                          setSelectedNode(updatedNode)
                          setNodes((nds) =>
                            nds.map((node) =>
                              node.id === selectedNode.id
                                ? { ...node, data: updatedNode }
                                : node
                            )
                          )
                        }}
                      >
                        <Option value="voice_001">标准女声</Option>
                        <Option value="voice_002">标准男声</Option>
                        <Option value="voice_003">甜美女声</Option>
                      </Select>
                    </Form.Item>

                    <Form.Item label={`语速: ${selectedNode.parameters.speed}x`}>
                      <Slider
                        min={0.5}
                        max={2.0}
                        step={0.1}
                        value={selectedNode.parameters.speed}
                        onChange={(value) => {
                          const updatedParams = { ...selectedNode.parameters, speed: value }
                          const updatedNode = { ...selectedNode, parameters: updatedParams }
                          setSelectedNode(updatedNode)
                        }}
                      />
                    </Form.Item>

                    <Form.Item label={`音调: ${selectedNode.parameters.pitch}x`}>
                      <Slider
                        min={0.5}
                        max={2.0}
                        step={0.1}
                        value={selectedNode.parameters.pitch}
                        onChange={(value) => {
                          const updatedParams = { ...selectedNode.parameters, pitch: value }
                          const updatedNode = { ...selectedNode, parameters: updatedParams }
                          setSelectedNode(updatedNode)
                        }}
                      />
                    </Form.Item>
                  </>
                )}

                {selectedNode.type === 'image_generate' && (
                  <>
                    <Form.Item label="生成风格">
                      <Select
                        value={selectedNode.parameters.style}
                        onChange={(value) => {
                          const updatedParams = { ...selectedNode.parameters, style: value }
                          const updatedNode = { ...selectedNode, parameters: updatedParams }
                          setSelectedNode(updatedNode)
                        }}
                      >
                        <Option value="realistic">写实风格</Option>
                        <Option value="anime">动漫风格</Option>
                        <Option value="artistic">艺术风格</Option>
                        <Option value="abstract">抽象风格</Option>
                      </Select>
                    </Form.Item>

                    <Form.Item label="分辨率">
                      <Select
                        value={selectedNode.parameters.resolution}
                        onChange={(value) => {
                          const updatedParams = { ...selectedNode.parameters, resolution: value }
                          const updatedNode = { ...selectedNode, parameters: updatedParams }
                          setSelectedNode(updatedNode)
                        }}
                      >
                        <Option value="512x512">512x512</Option>
                        <Option value="1024x1024">1024x1024</Option>
                        <Option value="1920x1080">1920x1080</Option>
                      </Select>
                    </Form.Item>
                  </>
                )}
              </Form>
            </TabPane>

            <TabPane tab="连接" key="connections">
              <div>
                <Title level={5}>输入端口</Title>
                {selectedNode.inputPorts.map((port) => (
                  <Tag key={port} style={{ margin: '4px 0' }}>{port}</Tag>
                ))}

                <Title level={5} style={{ marginTop: 16 }}>输出端口</Title>
                {selectedNode.outputPorts.map((port) => (
                  <Tag key={port} style={{ margin: '4px 0' }}>{port}</Tag>
                ))}
              </div>
            </TabPane>

            <TabPane tab="操作" key="actions">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Button
                  icon={<CopyOutlined />}
                  onClick={() => {
                    // 复制节点逻辑
                    message.success('节点已复制')
                  }}
                  block
                >
                  复制节点
                </Button>
                
                <Popconfirm
                  title="确认删除此节点吗？"
                  onConfirm={() => {
                    deleteNode(selectedNode.id)
                    setDrawerVisible(false)
                  }}
                  okText="确认"
                  cancelText="取消"
                >
                  <Button icon={<DeleteOutlined />} danger block>
                    删除节点
                  </Button>
                </Popconfirm>
              </Space>
            </TabPane>
          </Tabs>
        </div>
      )}
    </Drawer>
  )

  const renderSaveModal = () => (
    <Modal
      title="保存工作流"
      open={saveModalVisible}
      onCancel={() => setSaveModalVisible(false)}
      onOk={() => form.submit()}
    >
      <Form form={form} layout="vertical" onFinish={saveWorkflow}>
        <Form.Item
          name="name"
          label="工作流名称"
          rules={[{ required: true, message: '请输入工作流名称' }]}
        >
          <Input placeholder="输入工作流名称" />
        </Form.Item>

        <Form.Item
          name="description"
          label="工作流描述"
          rules={[{ required: true, message: '请输入工作流描述' }]}
        >
          <TextArea rows={3} placeholder="描述工作流的用途和特点..." />
        </Form.Item>

        <Form.Item
          name="category"
          label="分类"
          rules={[{ required: true, message: '请选择分类' }]}
        >
          <Select placeholder="选择分类">
            <Option value="business">商业应用</Option>
            <Option value="education">教育培训</Option>
            <Option value="entertainment">娱乐内容</Option>
            <Option value="marketing">营销推广</Option>
          </Select>
        </Form.Item>

        <Form.Item
          name="tags"
          label="标签"
        >
          <Select mode="tags" placeholder="添加标签..." />
        </Form.Item>

        <Form.Item
          name="is_public"
          label="公开工作流"
          valuePropName="checked"
        >
          <Switch />
        </Form.Item>
      </Form>
    </Modal>
  )

  // ================================
  // 主渲染
  // ================================

  return (
    <div className="mixall-content-workflow" style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* 顶部工具栏 */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Space>
              <Title level={4} style={{ margin: 0 }}>
                <NodeIndexOutlined /> 工作流编辑器
              </Title>
              {workflow && (
                <Tag color="blue">{workflow.name}</Tag>
              )}
            </Space>
          </Col>
          <Col>
            <Space>
              <Button
                icon={<SaveOutlined />}
                onClick={() => setSaveModalVisible(true)}
                disabled={nodes.length === 0}
              >
                保存
              </Button>
              <Button
                icon={<UploadOutlined />}
                onClick={() => setLoadModalVisible(true)}
              >
                加载
              </Button>
              <Button
                icon={<DownloadOutlined />}
                onClick={() => {
                  // 导出工作流
                  message.info('工作流导出功能开发中...')
                }}
              >
                导出
              </Button>
              <Button
                icon={<ShareAltOutlined />}
                onClick={() => {
                  // 分享工作流
                  message.info('工作流分享功能开发中...')
                }}
              >
                分享
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 主要编辑区域 */}
      <div style={{ flex: 1, display: 'flex', gap: 16 }}>
        {/* 左侧面板 */}
        <div style={{ width: 280, display: 'flex', flexDirection: 'column', gap: 16 }}>
          {renderNodePanel()}
          {renderExecutionPanel()}
        </div>

        {/* 中间工作流画布 */}
        <div style={{ flex: 1 }}>
          <div ref={reactFlowWrapper} style={{ height: '100%' }}>
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              onInit={setReactFlowInstance}
              onDrop={onDrop}
              onDragOver={onDragOver}
              onNodeClick={onNodeClick}
              nodeTypes={{
                custom: CustomWorkflowNode
              }}
              connectionMode={ConnectionMode.Loose}
              defaultEdgeOptions={{
                animated: true,
                style: { stroke: '#1890ff' },
                markerEnd: { type: MarkerType.ArrowClosed, color: '#1890ff' }
              }}
              fitView
            >
              <Background />
              <Controls />
              <MiniMap 
                style={{
                  height: 120,
                  backgroundColor: '#f5f5f5'
                }}
                zoomable
                pannable
              />
              <Panel position="top-left">
                <Alert
                  message="拖拽节点到画布开始创建工作流"
                  type="info"
                  showIcon
                  style={{ marginBottom: 8 }}
                />
              </Panel>
            </ReactFlow>
          </div>
        </div>
      </div>

      {/* 侧边抽屉和模态框 */}
      {renderNodeDrawer()}
      {renderSaveModal()}
    </div>
  )
}

// 包装组件以提供ReactFlow上下文
const MixAllContentWorkflowWrapper: React.FC = () => (
  <ReactFlowProvider>
    <MixAllContentWorkflow />
  </ReactFlowProvider>
)

export default MixAllContentWorkflowWrapper