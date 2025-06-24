/**
 * Platform Selector Component
 * 平台选择器组件 - [voice-workbench][platform-selector]
 */

import React, { useState } from 'react'
import {
  Card,
  Select,
  Space,
  Tag,
  Typography,
  Alert,
  Tooltip,
  Row,
  Col,
  Badge,
  Button,
  Modal,
  Descriptions,
  List,
  Progress,
  Statistic
} from 'antd'
import {
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  CloseCircleOutlined,
  SettingOutlined,
  InfoCircleOutlined,
  ApiOutlined,
  ThunderboltOutlined,
  DollarOutlined,
  ClockCircleOutlined
} from '@ant-design/icons'

const { Option } = Select
const { Text, Title } = Typography

// 平台健康状态类型
interface PlatformHealth {
  isHealthy: boolean
  responseTime: number
  errorRate: number
  lastCheck: string
  dailyRequestsUsed: number
  dailyRequestsLimit: number
}

// 平台类型定义
interface VoicePlatform {
  type: string
  name: string
  description: string
  isEnabled: boolean
  features: string[]
  priority: number
  costPerMinute: number
  health?: PlatformHealth
  limitations: {
    maxTextLength: number
    maxFileSize: number
    supportedFormats: string[]
  }
}

interface PlatformSelectorProps {
  platforms: VoicePlatform[]
  selectedPlatform: VoicePlatform | null
  onPlatformSelect: (platform: VoicePlatform) => void
  onPlatformSettings: (platform: VoicePlatform) => void
  loading?: boolean
  className?: string
}

const PlatformSelector: React.FC<PlatformSelectorProps> = ({
  platforms,
  selectedPlatform,
  onPlatformSelect,
  onPlatformSettings,
  loading = false,
  className
}) => {
  const [detailModalVisible, setDetailModalVisible] = useState(false)
  const [selectedDetailPlatform, setSelectedDetailPlatform] = useState<VoicePlatform | null>(null)

  // 获取平台状态颜色
  const getPlatformStatusColor = (platform: VoicePlatform): string => {
    if (!platform.isEnabled) return 'default'
    if (!platform.health) return 'orange'
    return platform.health.isHealthy ? 'green' : 'red'
  }

  // 获取平台状态文本
  const getPlatformStatusText = (platform: VoicePlatform): string => {
    if (!platform.isEnabled) return '未启用'
    if (!platform.health) return '未知'
    return platform.health.isHealthy ? '健康' : '异常'
  }

  // 获取平台状态图标
  const getPlatformStatusIcon = (platform: VoicePlatform) => {
    if (!platform.isEnabled) return <CloseCircleOutlined />
    if (!platform.health) return <ExclamationCircleOutlined />
    return platform.health.isHealthy ? <CheckCircleOutlined /> : <CloseCircleOutlined />
  }

  // 获取可用平台（已启用且健康）
  const getAvailablePlatforms = (): VoicePlatform[] => {
    return platforms.filter(p => p.isEnabled && p.health?.isHealthy)
  }

  // 获取推荐平台
  const getRecommendedPlatform = (): VoicePlatform | null => {
    const available = getAvailablePlatforms()
    if (available.length === 0) return null
    
    // 按优先级和健康状态排序
    return available.sort((a, b) => {
      if (a.priority !== b.priority) return a.priority - b.priority
      if (a.health && b.health) {
        return a.health.responseTime - b.health.responseTime
      }
      return 0
    })[0]
  }

  // 显示平台详情
  const showPlatformDetail = (platform: VoicePlatform) => {
    setSelectedDetailPlatform(platform)
    setDetailModalVisible(true)
  }

  // 渲染平台选项
  const renderPlatformOption = (platform: VoicePlatform) => {
    const statusColor = getPlatformStatusColor(platform)
    const statusText = getPlatformStatusText(platform)
    const statusIcon = getPlatformStatusIcon(platform)

    return (
      <Option key={platform.type} value={platform.type} disabled={!platform.isEnabled}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Space>
            <Badge status={statusColor as any} />
            <span>{platform.name}</span>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              {platform.description}
            </Text>
          </Space>
          <Space>
            {platform.health && (
              <Text type="secondary" style={{ fontSize: '11px' }}>
                {platform.health.responseTime}ms
              </Text>
            )}
            {statusIcon}
          </Space>
        </div>
      </Option>
    )
  }

  // 渲染平台卡片
  const renderPlatformCard = (platform: VoicePlatform) => {
    const statusColor = getPlatformStatusColor(platform)
    const isSelected = selectedPlatform?.type === platform.type
    const usagePercent = platform.health ? 
      (platform.health.dailyRequestsUsed / platform.health.dailyRequestsLimit) * 100 : 0

    return (
      <Card
        key={platform.type}
        size="small"
        className={`platform-card ${isSelected ? 'selected' : ''}`}
        style={{
          border: isSelected ? '2px solid #1890ff' : '1px solid #d9d9d9',
          cursor: platform.isEnabled ? 'pointer' : 'not-allowed',
          opacity: platform.isEnabled ? 1 : 0.6
        }}
        onClick={() => platform.isEnabled && onPlatformSelect(platform)}
        extra={
          <Space>
            <Tooltip title="查看详情">
              <Button 
                type="text" 
                size="small" 
                icon={<InfoCircleOutlined />}
                onClick={(e) => {
                  e.stopPropagation()
                  showPlatformDetail(platform)
                }}
              />
            </Tooltip>
            <Tooltip title="平台设置">
              <Button 
                type="text" 
                size="small" 
                icon={<SettingOutlined />}
                onClick={(e) => {
                  e.stopPropagation()
                  onPlatformSettings(platform)
                }}
              />
            </Tooltip>
          </Space>
        }
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <Space>
            <Tag color={statusColor}>{getPlatformStatusText(platform)}</Tag>
            <Text strong>{platform.name}</Text>
            {platform.priority === 1 && <Tag color="gold">推荐</Tag>}
          </Space>
          
          <Text type="secondary" style={{ fontSize: '12px' }}>
            {platform.description}
          </Text>
          
          {platform.health && (
            <Row gutter={8}>
              <Col span={8}>
                <Statistic
                  title="响应时间"
                  value={platform.health.responseTime}
                  suffix="ms"
                  valueStyle={{ fontSize: '14px' }}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="错误率"
                  value={platform.health.errorRate}
                  suffix="%"
                  valueStyle={{ fontSize: '14px' }}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="费用"
                  value={platform.costPerMinute}
                  prefix="¥"
                  suffix="/分钟"
                  valueStyle={{ fontSize: '14px' }}
                />
              </Col>
            </Row>
          )}
          
          {platform.health && (
            <div>
              <Text type="secondary" style={{ fontSize: '11px' }}>
                今日使用: {platform.health.dailyRequestsUsed}/{platform.health.dailyRequestsLimit}
              </Text>
              <Progress
                percent={usagePercent}
                size="small"
                showInfo={false}
                strokeColor={usagePercent > 80 ? '#ff4d4f' : '#52c41a'}
              />
            </div>
          )}
          
          <Space wrap>
            {platform.features.slice(0, 3).map(feature => (
              <Tag key={feature} size="small">
                {feature}
              </Tag>
            ))}
            {platform.features.length > 3 && (
              <Tag size="small">+{platform.features.length - 3}</Tag>
            )}
          </Space>
        </Space>
      </Card>
    )
  }

  const availablePlatforms = getAvailablePlatforms()
  const recommendedPlatform = getRecommendedPlatform()

  return (
    <div className={className}>
      {/* 平台状态概览 */}
      <Card title="平台选择" size="small" style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          {/* 快速选择 */}
          <div>
            <Text strong>当前平台: </Text>
            <Select
              value={selectedPlatform?.type}
              placeholder="选择语音平台"
              style={{ width: 300 }}
              loading={loading}
              onChange={(value) => {
                const platform = platforms.find(p => p.type === value)
                if (platform) onPlatformSelect(platform)
              }}
            >
              {platforms.map(renderPlatformOption)}
            </Select>
          </div>

          {/* 推荐提示 */}
          {recommendedPlatform && recommendedPlatform !== selectedPlatform && (
            <Alert
              message={`推荐使用 ${recommendedPlatform.name}`}
              description={`基于当前性能和可用性，推荐使用 ${recommendedPlatform.name} 平台`}
              type="info"
              showIcon
              action={
                <Button
                  size="small"
                  type="primary"
                  onClick={() => onPlatformSelect(recommendedPlatform)}
                >
                  切换
                </Button>
              }
              closable
            />
          )}

          {/* 平台统计 */}
          <Row gutter={16}>
            <Col span={6}>
              <Statistic
                title="总平台数"
                value={platforms.length}
                prefix={<ApiOutlined />}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="可用平台"
                value={availablePlatforms.length}
                prefix={<CheckCircleOutlined />}
                valueStyle={{ color: '#3f8600' }}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="平均响应"
                value={
                  availablePlatforms.length > 0
                    ? Math.round(
                        availablePlatforms.reduce((sum, p) => sum + (p.health?.responseTime || 0), 0) /
                        availablePlatforms.length
                      )
                    : 0
                }
                suffix="ms"
                prefix={<ThunderboltOutlined />}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="平均费用"
                value={
                  platforms.length > 0
                    ? (platforms.reduce((sum, p) => sum + p.costPerMinute, 0) / platforms.length).toFixed(3)
                    : 0
                }
                prefix={<DollarOutlined />}
                suffix="/分钟"
              />
            </Col>
          </Row>
        </Space>
      </Card>

      {/* 平台卡片列表 */}
      <Row gutter={[16, 16]}>
        {platforms.map(platform => (
          <Col span={8} key={platform.type}>
            {renderPlatformCard(platform)}
          </Col>
        ))}
      </Row>

      {/* 平台详情模态框 */}
      <Modal
        title={selectedDetailPlatform?.name}
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>,
          <Button
            key="settings"
            type="primary"
            icon={<SettingOutlined />}
            onClick={() => {
              if (selectedDetailPlatform) {
                onPlatformSettings(selectedDetailPlatform)
                setDetailModalVisible(false)
              }
            }}
          >
            配置
          </Button>
        ]}
        width={800}
      >
        {selectedDetailPlatform && (
          <Space direction="vertical" style={{ width: '100%' }}>
            <Descriptions bordered column={2}>
              <Descriptions.Item label="平台类型">
                {selectedDetailPlatform.type}
              </Descriptions.Item>
              <Descriptions.Item label="启用状态">
                <Tag color={selectedDetailPlatform.isEnabled ? 'green' : 'red'}>
                  {selectedDetailPlatform.isEnabled ? '已启用' : '未启用'}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="优先级">
                {selectedDetailPlatform.priority}
              </Descriptions.Item>
              <Descriptions.Item label="费用">
                ¥{selectedDetailPlatform.costPerMinute}/分钟
              </Descriptions.Item>
              <Descriptions.Item label="最大文本长度">
                {selectedDetailPlatform.limitations.maxTextLength} 字符
              </Descriptions.Item>
              <Descriptions.Item label="最大文件大小">
                {selectedDetailPlatform.limitations.maxFileSize / 1024 / 1024} MB
              </Descriptions.Item>
            </Descriptions>

            {selectedDetailPlatform.health && (
              <Card title="健康状态" size="small">
                <Row gutter={16}>
                  <Col span={8}>
                    <Statistic
                      title="健康状态"
                      value={selectedDetailPlatform.health.isHealthy ? '健康' : '异常'}
                      valueStyle={{
                        color: selectedDetailPlatform.health.isHealthy ? '#3f8600' : '#cf1322'
                      }}
                    />
                  </Col>
                  <Col span={8}>
                    <Statistic
                      title="响应时间"
                      value={selectedDetailPlatform.health.responseTime}
                      suffix="ms"
                    />
                  </Col>
                  <Col span={8}>
                    <Statistic
                      title="错误率"
                      value={selectedDetailPlatform.health.errorRate}
                      suffix="%"
                    />
                  </Col>
                </Row>
                
                <div style={{ marginTop: 16 }}>
                  <Text>今日请求量: </Text>
                  <Progress
                    percent={
                      (selectedDetailPlatform.health.dailyRequestsUsed /
                        selectedDetailPlatform.health.dailyRequestsLimit) * 100
                    }
                    format={() => 
                      `${selectedDetailPlatform.health?.dailyRequestsUsed}/${selectedDetailPlatform.health?.dailyRequestsLimit}`
                    }
                  />
                </div>
                
                <div style={{ marginTop: 8 }}>
                  <Text type="secondary">
                    <ClockCircleOutlined /> 最后检查: {selectedDetailPlatform.health.lastCheck}
                  </Text>
                </div>
              </Card>
            )}

            <Card title="支持功能" size="small">
              <List
                dataSource={selectedDetailPlatform.features}
                renderItem={feature => (
                  <List.Item>
                    <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
                    {feature}
                  </List.Item>
                )}
              />
            </Card>

            <Card title="支持格式" size="small">
              <Space wrap>
                {selectedDetailPlatform.limitations.supportedFormats.map(format => (
                  <Tag key={format}>{format.toUpperCase()}</Tag>
                ))}
              </Space>
            </Card>
          </Space>
        )}
      </Modal>
    </div>
  )
}

export default PlatformSelector