/**
 * Platform Publish Monitor Component
 * 平台发布监控组件 - [Platform][Publish][Monitor]
 * 
 * 实时监控和追踪多平台发布状态
 * 提供数据分析、趋势洞察和性能优化建议
 */

import React, { useState, useEffect, useRef } from 'react'
import {
  Card,
  Row,
  Col,
  Typography,
  Statistic,
  Progress,
  Table,
  Tag,
  Space,
  Button,
  Select,
  DatePicker,
  Alert,
  Timeline,
  Badge,
  Tooltip,
  Empty,
  Spin,
  Tabs,
  List,
  Avatar,
  Divider,
  message
} from 'antd'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Legend
} from 'recharts'
import {
  EyeOutlined,
  ThunderboltOutlined,
  MessageOutlined,
  ShareAltOutlined,
  TrendingUpOutlined,
  TrendingDownOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ReloadOutlined,
  DownloadOutlined,
  FilterOutlined,
  BarChartOutlined,
  DashboardOutlined,
  RiseOutlined,
  FallOutlined,
  GlobalOutlined,
  FireOutlined,
  TeamOutlined
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import moment from 'moment'
import {
  PlatformPublishType,
  PublishResult,
  platformPublishManager
} from '../../services/platform_publish/platform_publish_adapter'

const { Title, Paragraph, Text } = Typography
const { Option } = Select
const { RangePicker } = DatePicker
const { TabPane } = Tabs

// ================================
// 类型定义 - Types
// ================================

interface PublishAnalytics {
  total_posts: number
  successful_posts: number
  failed_posts: number
  success_rate: number
  total_engagement: {
    views: number
    likes: number
    comments: number
    shares: number
  }
  platform_breakdown: Array<{
    platform: PlatformPublishType
    posts_count: number
    success_rate: number
    avg_engagement: number
    total_views: number
  }>
  time_series: Array<{
    date: string
    posts: number
    views: number
    likes: number
    comments: number
    shares: number
  }>
  top_performing_content: Array<{
    id: string
    title: string
    platform: PlatformPublishType
    views: number
    engagement_rate: number
    published_at: string
  }>
}

interface RealtimeMetrics {
  active_tasks: number
  pending_tasks: number
  completed_today: number
  failed_today: number
  current_engagement_velocity: number
  platform_health: Record<PlatformPublishType, {
    status: 'healthy' | 'warning' | 'error'
    response_time: number
    success_rate: number
    last_check: string
  }>
  trending_topics: Array<{
    topic: string
    mentions: number
    growth_rate: number
  }>
}

interface ContentPerformanceItem {
  id: string
  title: string
  platform: PlatformPublishType
  published_at: string
  status: 'published' | 'failed' | 'pending'
  metrics: {
    views: number
    likes: number
    comments: number
    shares: number
    engagement_rate: number
    ctr: number
  }
  trending_score: number
}

// ================================
// 主组件
// ================================

const PlatformPublishMonitor: React.FC = () => {
  const [analytics, setAnalytics] = useState<PublishAnalytics | null>(null)
  const [realtimeMetrics, setRealtimeMetrics] = useState<RealtimeMetrics | null>(null)
  const [contentPerformance, setContentPerformance] = useState<ContentPerformanceItem[]>([])
  const [loading, setLoading] = useState(false)
  const [timeRange, setTimeRange] = useState<[moment.Moment, moment.Moment]>([
    moment().subtract(7, 'days'),
    moment()
  ])
  const [selectedPlatforms, setSelectedPlatforms] = useState<PlatformPublishType[]>(['douyin', 'bilibili', 'xiaohongshu', 'wechat'])
  const [activeTab, setActiveTab] = useState('overview')
  const wsRef = useRef<WebSocket | null>(null)

  const platformOptions = [
    { value: 'douyin', label: '抖音', color: '#000000' },
    { value: 'bilibili', label: 'B站', color: '#00A1D6' },
    { value: 'xiaohongshu', label: '小红书', color: '#FF2442' },
    { value: 'wechat', label: '微信公众号', color: '#07C160' },
    { value: 'weibo', label: '微博', color: '#E6162D' }
  ]

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D']

  // ================================
  // 数据加载和实时更新 - Data Loading & Real-time Updates
  // ================================

  useEffect(() => {
    loadAnalytics()
    loadRealtimeMetrics()
    loadContentPerformance()
    connectRealtimeUpdates()

    const interval = setInterval(() => {
      loadRealtimeMetrics()
    }, 30000) // 每30秒更新实时数据

    return () => {
      clearInterval(interval)
      disconnectRealtimeUpdates()
    }
  }, [timeRange, selectedPlatforms])

  const loadAnalytics = async () => {
    setLoading(true)
    try {
      // 模拟API调用
      // const response = await publishAnalyticsService.getAnalytics({
      //   start_date: timeRange[0].toISOString(),
      //   end_date: timeRange[1].toISOString(),
      //   platforms: selectedPlatforms
      // })

      // 模拟数据
      const mockAnalytics: PublishAnalytics = {
        total_posts: 156,
        successful_posts: 142,
        failed_posts: 14,
        success_rate: 91.0,
        total_engagement: {
          views: 2456780,
          likes: 89650,
          comments: 12340,
          shares: 5670
        },
        platform_breakdown: [
          {
            platform: 'douyin',
            posts_count: 65,
            success_rate: 93.8,
            avg_engagement: 15.2,
            total_views: 1250000
          },
          {
            platform: 'bilibili',
            posts_count: 28,
            success_rate: 96.4,
            avg_engagement: 12.8,
            total_views: 680000
          },
          {
            platform: 'xiaohongshu',
            posts_count: 38,
            success_rate: 89.5,
            avg_engagement: 18.6,
            total_views: 420000
          },
          {
            platform: 'wechat',
            posts_count: 25,
            success_rate: 84.0,
            avg_engagement: 8.4,
            total_views: 106780
          }
        ],
        time_series: Array.from({ length: 7 }, (_, i) => ({
          date: moment().subtract(6 - i, 'days').format('MM-DD'),
          posts: Math.floor(Math.random() * 25) + 15,
          views: Math.floor(Math.random() * 50000) + 30000,
          likes: Math.floor(Math.random() * 2000) + 1000,
          comments: Math.floor(Math.random() * 300) + 150,
          shares: Math.floor(Math.random() * 150) + 75
        })),
        top_performing_content: [
          {
            id: 'content_001',
            title: 'DataSay AI创作平台功能演示',
            platform: 'douyin',
            views: 85600,
            engagement_rate: 24.5,
            published_at: '2024-06-23T14:30:00Z'
          },
          {
            id: 'content_002',
            title: '5分钟学会AI配音技巧',
            platform: 'bilibili',
            views: 42300,
            engagement_rate: 18.7,
            published_at: '2024-06-22T20:15:00Z'
          },
          {
            id: 'content_003',
            title: '创作者必备：智能内容生成工具',
            platform: 'xiaohongshu',
            views: 28900,
            engagement_rate: 31.2,
            published_at: '2024-06-21T16:45:00Z'
          }
        ]
      }

      setAnalytics(mockAnalytics)
    } catch (error) {
      console.error('Failed to load analytics:', error)
      message.error('加载分析数据失败')
    } finally {
      setLoading(false)
    }
  }

  const loadRealtimeMetrics = async () => {
    try {
      // 模拟API调用
      // const response = await publishAnalyticsService.getRealtimeMetrics()

      // 模拟数据
      const mockRealtime: RealtimeMetrics = {
        active_tasks: 5,
        pending_tasks: 12,
        completed_today: 28,
        failed_today: 3,
        current_engagement_velocity: 145.6,
        platform_health: {
          douyin: {
            status: 'healthy',
            response_time: 245,
            success_rate: 98.5,
            last_check: new Date().toISOString()
          },
          bilibili: {
            status: 'healthy',
            response_time: 380,
            success_rate: 96.2,
            last_check: new Date().toISOString()
          },
          xiaohongshu: {
            status: 'warning',
            response_time: 890,
            success_rate: 89.1,
            last_check: new Date().toISOString()
          },
          wechat: {
            status: 'healthy',
            response_time: 320,
            success_rate: 94.8,
            last_check: new Date().toISOString()
          },
          weibo: {
            status: 'error',
            response_time: 1200,
            success_rate: 76.3,
            last_check: new Date().toISOString()
          }
        },
        trending_topics: [
          { topic: 'AI创作', mentions: 1250, growth_rate: 45.6 },
          { topic: '内容营销', mentions: 890, growth_rate: 23.4 },
          { topic: '数字化转型', mentions: 670, growth_rate: 67.8 }
        ]
      }

      setRealtimeMetrics(mockRealtime)
    } catch (error) {
      console.error('Failed to load realtime metrics:', error)
    }
  }

  const loadContentPerformance = async () => {
    try {
      // 模拟数据
      const mockPerformance: ContentPerformanceItem[] = Array.from({ length: 20 }, (_, i) => ({
        id: `content_${i + 1}`,
        title: `内容标题 ${i + 1}`,
        platform: (['douyin', 'bilibili', 'xiaohongshu', 'wechat'] as PlatformPublishType[])[i % 4],
        published_at: moment().subtract(Math.floor(Math.random() * 30), 'days').toISOString(),
        status: (['published', 'published', 'published', 'failed'][Math.floor(Math.random() * 4)] as any),
        metrics: {
          views: Math.floor(Math.random() * 100000) + 5000,
          likes: Math.floor(Math.random() * 5000) + 200,
          comments: Math.floor(Math.random() * 500) + 20,
          shares: Math.floor(Math.random() * 200) + 10,
          engagement_rate: Math.round((Math.random() * 20 + 5) * 10) / 10,
          ctr: Math.round((Math.random() * 5 + 1) * 10) / 10
        },
        trending_score: Math.round((Math.random() * 100) * 10) / 10
      }))

      setContentPerformance(mockPerformance)
    } catch (error) {
      console.error('Failed to load content performance:', error)
    }
  }

  const connectRealtimeUpdates = () => {
    try {
      // const ws = new WebSocket('ws://localhost:8000/ws/publish-analytics')
      // wsRef.current = ws

      // ws.onmessage = (event) => {
      //   const data = JSON.parse(event.data)
      //   handleRealtimeUpdate(data)
      // }

      // 模拟实时更新
      const interval = setInterval(() => {
        if (realtimeMetrics) {
          setRealtimeMetrics(prev => prev ? {
            ...prev,
            current_engagement_velocity: prev.current_engagement_velocity + (Math.random() - 0.5) * 10,
            active_tasks: Math.max(0, prev.active_tasks + (Math.random() > 0.7 ? 1 : -1))
          } : null)
        }
      }, 10000)

      return () => clearInterval(interval)
    } catch (error) {
      console.error('Failed to connect realtime updates:', error)
    }
  }

  const disconnectRealtimeUpdates = () => {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
  }

  // ================================
  // 渲染函数 - Render Functions
  // ================================

  const getPlatformInfo = (platform: PlatformPublishType) => {
    return platformOptions.find(p => p.value === platform) || platformOptions[0]
  }

  const getHealthStatusInfo = (status: 'healthy' | 'warning' | 'error') => {
    const statusMap = {
      healthy: { color: 'success', text: '健康', icon: <CheckCircleOutlined /> },
      warning: { color: 'warning', text: '警告', icon: <ExclamationCircleOutlined /> },
      error: { color: 'error', text: '异常', icon: <ExclamationCircleOutlined /> }
    }
    return statusMap[status]
  }

  const renderOverviewCards = () => (
    <Row gutter={16} style={{ marginBottom: 24 }}>
      <Col xs={24} sm={12} md={6}>
        <Card size="small">
          <Statistic
            title="总发布数"
            value={analytics?.total_posts || 0}
            prefix={<GlobalOutlined />}
            valueStyle={{ color: '#1890ff' }}
          />
        </Card>
      </Col>
      <Col xs={24} sm={12} md={6}>
        <Card size="small">
          <Statistic
            title="成功率"
            value={analytics?.success_rate || 0}
            precision={1}
            suffix="%"
            prefix={<CheckCircleOutlined />}
            valueStyle={{ color: '#52c41a' }}
          />
        </Card>
      </Col>
      <Col xs={24} sm={12} md={6}>
        <Card size="small">
          <Statistic
            title="总浏览量"
            value={analytics?.total_engagement.views || 0}
            formatter={value => value.toLocaleString()}
            prefix={<EyeOutlined />}
            valueStyle={{ color: '#722ed1' }}
          />
        </Card>
      </Col>
      <Col xs={24} sm={12} md={6}>
        <Card size="small">
          <Statistic
            title="互动率"
            value={analytics ? 
              ((analytics.total_engagement.likes + analytics.total_engagement.comments + analytics.total_engagement.shares) / analytics.total_engagement.views * 100)
              : 0
            }
            precision={2}
            suffix="%"
            prefix={<ThunderboltOutlined />}
            valueStyle={{ color: '#fa8c16' }}
          />
        </Card>
      </Col>
    </Row>
  )

  const renderRealtimeMetrics = () => (
    <Row gutter={16} style={{ marginBottom: 24 }}>
      <Col xs={24} lg={16}>
        <Card title="实时任务状态" size="small">
          <Row gutter={16}>
            <Col span={6}>
              <Statistic
                title="进行中"
                value={realtimeMetrics?.active_tasks || 0}
                prefix={<ClockCircleOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="等待中"
                value={realtimeMetrics?.pending_tasks || 0}
                prefix={<ClockCircleOutlined />}
                valueStyle={{ color: '#faad14' }}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="今日完成"
                value={realtimeMetrics?.completed_today || 0}
                prefix={<CheckCircleOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="今日失败"
                value={realtimeMetrics?.failed_today || 0}
                prefix={<ExclamationCircleOutlined />}
                valueStyle={{ color: '#ff4d4f' }}
              />
            </Col>
          </Row>
        </Card>
      </Col>
      <Col xs={24} lg={8}>
        <Card title="互动速度" size="small">
          <div style={{ textAlign: 'center' }}>
            <Statistic
              title="当前互动速度"
              value={realtimeMetrics?.current_engagement_velocity || 0}
              precision={1}
              suffix="次/分钟"
              prefix={<TrendingUpOutlined />}
              valueStyle={{ color: '#13c2c2' }}
            />
            <Progress
              type="circle"
              percent={Math.min(((realtimeMetrics?.current_engagement_velocity || 0) / 200) * 100, 100)}
              size={80}
              strokeColor="#13c2c2"
            />
          </div>
        </Card>
      </Col>
    </Row>
  )

  const renderPlatformHealth = () => (
    <Card title="平台健康状态" size="small" style={{ marginBottom: 24 }}>
      <Row gutter={16}>
        {realtimeMetrics && Object.entries(realtimeMetrics.platform_health).map(([platform, health]) => (
          <Col key={platform} xs={24} sm={12} md={8} lg={4.8}>
            <Card size="small" style={{ textAlign: 'center' }}>
              <div style={{ marginBottom: 8 }}>
                <Text strong>{getPlatformInfo(platform as PlatformPublishType).label}</Text>
              </div>
              <div style={{ marginBottom: 8 }}>
                <Badge
                  status={health.status === 'healthy' ? 'success' : health.status === 'warning' ? 'warning' : 'error'}
                  text={getHealthStatusInfo(health.status).text}
                />
              </div>
              <div style={{ fontSize: 12, color: '#666' }}>
                <div>响应时间: {health.response_time}ms</div>
                <div>成功率: {health.success_rate}%</div>
              </div>
            </Card>
          </Col>
        ))}
      </Row>
    </Card>
  )

  const renderTrendingTopics = () => (
    <Card title="热门话题" size="small" style={{ marginBottom: 24 }}>
      <List
        dataSource={realtimeMetrics?.trending_topics || []}
        renderItem={topic => (
          <List.Item>
            <List.Item.Meta
              avatar={<Avatar icon={<FireOutlined />} style={{ backgroundColor: '#fa541c' }} />}
              title={
                <Space>
                  <Text strong>#{topic.topic}</Text>
                  <Tag color={topic.growth_rate > 50 ? 'red' : topic.growth_rate > 20 ? 'orange' : 'blue'}>
                    {topic.growth_rate > 0 ? <RiseOutlined /> : <FallOutlined />}
                    {Math.abs(topic.growth_rate)}%
                  </Tag>
                </Space>
              }
              description={`${topic.mentions.toLocaleString()} 次提及`}
            />
          </List.Item>
        )}
      />
    </Card>
  )

  const renderCharts = () => (
    <Row gutter={16} style={{ marginBottom: 24 }}>
      <Col xs={24} lg={12}>
        <Card title="发布趋势" size="small">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={analytics?.time_series || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Legend />
              <Bar yAxisId="left" dataKey="posts" fill="#8884d8" name="发布数量" />
              <Line yAxisId="right" type="monotone" dataKey="views" stroke="#82ca9d" name="浏览量" />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      </Col>
      <Col xs={24} lg={12}>
        <Card title="平台分布" size="small">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={analytics?.platform_breakdown.map(item => ({
                  name: getPlatformInfo(item.platform).label,
                  value: item.posts_count,
                  color: getPlatformInfo(item.platform).color
                })) || []}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={120}
                paddingAngle={5}
                dataKey="value"
                label={(entry) => `${entry.name}: ${entry.value}`}
              >
                {analytics?.platform_breakdown.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </Col>
    </Row>
  )

  const performanceColumns: ColumnsType<ContentPerformanceItem> = [
    {
      title: '内容标题',
      dataIndex: 'title',
      key: 'title',
      width: 200,
      render: (title, record) => (
        <div>
          <Text strong>{title}</Text>
          <br />
          <Space size="small">
            <Tag color={getPlatformInfo(record.platform).color}>
              {getPlatformInfo(record.platform).label}
            </Tag>
            <Text type="secondary" style={{ fontSize: 11 }}>
              {moment(record.published_at).fromNow()}
            </Text>
          </Space>
        </div>
      )
    },
    {
      title: '浏览量',
      dataIndex: ['metrics', 'views'],
      key: 'views',
      width: 100,
      render: (views) => views.toLocaleString(),
      sorter: (a, b) => a.metrics.views - b.metrics.views
    },
    {
      title: '互动率',
      dataIndex: ['metrics', 'engagement_rate'],
      key: 'engagement_rate',
      width: 100,
      render: (rate) => `${rate}%`,
      sorter: (a, b) => a.metrics.engagement_rate - b.metrics.engagement_rate
    },
    {
      title: '热度分数',
      dataIndex: 'trending_score',
      key: 'trending_score',
      width: 100,
      render: (score) => (
        <div>
          <Progress
            percent={score}
            size="small"
            strokeColor={score > 80 ? '#f5222d' : score > 60 ? '#fa8c16' : '#52c41a'}
          />
          <Text style={{ fontSize: 11 }}>{score}</Text>
        </div>
      ),
      sorter: (a, b) => a.trending_score - b.trending_score
    },
    {
      title: '互动数据',
      key: 'engagement',
      width: 150,
      render: (_, record) => (
        <div style={{ fontSize: 11 }}>
          <div>👍 {record.metrics.likes.toLocaleString()}</div>
          <div>💬 {record.metrics.comments.toLocaleString()}</div>
          <div>📤 {record.metrics.shares.toLocaleString()}</div>
        </div>
      )
    }
  ]

  const renderTopPerformingContent = () => (
    <Card title="内容表现排行" size="small">
      <Table
        columns={performanceColumns}
        dataSource={contentPerformance}
        rowKey="id"
        pagination={{ pageSize: 10 }}
        size="small"
        scroll={{ x: 'max-content' }}
      />
    </Card>
  )

  // ================================
  // 主渲染
  // ================================

  return (
    <div className="platform-publish-monitor">
      <Card>
        <div style={{ marginBottom: 24 }}>
          <Title level={2}>
            <DashboardOutlined /> 发布监控中心
          </Title>
          <Paragraph>
            实时监控多平台发布状态，分析内容表现，优化发布策略。
          </Paragraph>
        </div>

        {/* 控制面板 */}
        <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
          <Col>
            <Space>
              <Select
                mode="multiple"
                placeholder="选择平台"
                value={selectedPlatforms}
                onChange={setSelectedPlatforms}
                style={{ width: 200 }}
              >
                {platformOptions.map(platform => (
                  <Option key={platform.value} value={platform.value}>
                    {platform.label}
                  </Option>
                ))}
              </Select>
              <RangePicker
                value={timeRange}
                onChange={(dates) => dates && setTimeRange(dates)}
                format="YYYY-MM-DD"
              />
            </Space>
          </Col>
          <Col>
            <Space>
              <Button
                icon={<ReloadOutlined />}
                onClick={() => {
                  loadAnalytics()
                  loadRealtimeMetrics()
                  loadContentPerformance()
                }}
                loading={loading}
              >
                刷新数据
              </Button>
              <Button
                icon={<DownloadOutlined />}
                onClick={() => {
                  message.info('数据导出功能开发中...')
                }}
              >
                导出报告
              </Button>
            </Space>
          </Col>
        </Row>

        {loading ? (
          <div style={{ textAlign: 'center', padding: 60 }}>
            <Spin size="large" />
          </div>
        ) : (
          <Tabs activeKey={activeTab} onChange={setActiveTab}>
            <TabPane tab="概览仪表板" key="overview">
              {renderOverviewCards()}
              {renderRealtimeMetrics()}
              {renderPlatformHealth()}
              {renderCharts()}
            </TabPane>

            <TabPane tab="内容表现" key="performance">
              {renderTopPerformingContent()}
            </TabPane>

            <TabPane tab="趋势分析" key="trends">
              <Row gutter={16}>
                <Col xs={24} lg={16}>
                  <Card title="互动趋势" size="small">
                    <ResponsiveContainer width="100%" height={400}>
                      <AreaChart data={analytics?.time_series || []}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Legend />
                        <Area type="monotone" dataKey="likes" stackId="1" stroke="#8884d8" fill="#8884d8" name="点赞" />
                        <Area type="monotone" dataKey="comments" stackId="1" stroke="#82ca9d" fill="#82ca9d" name="评论" />
                        <Area type="monotone" dataKey="shares" stackId="1" stroke="#ffc658" fill="#ffc658" name="分享" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </Card>
                </Col>
                <Col xs={24} lg={8}>
                  {renderTrendingTopics()}
                </Col>
              </Row>
            </TabPane>

            <TabPane tab="平台对比" key="comparison">
              <Card title="平台表现对比" size="small">
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={analytics?.platform_breakdown || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey={(item) => getPlatformInfo(item.platform).label} />
                    <YAxis yAxisId="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Legend />
                    <Bar yAxisId="left" dataKey="posts_count" fill="#8884d8" name="发布数量" />
                    <Bar yAxisId="left" dataKey="success_rate" fill="#82ca9d" name="成功率(%)" />
                    <Bar yAxisId="right" dataKey="avg_engagement" fill="#ffc658" name="平均互动率(%)" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </TabPane>
          </Tabs>
        )}
      </Card>
    </div>
  )
}

export default PlatformPublishMonitor