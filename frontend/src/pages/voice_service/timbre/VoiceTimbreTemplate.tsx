/**
 * Voice Timbre Template Component
 * 音色模板组件 - [Voice][Timbre][Template]
 */

import React, { useState, useEffect } from 'react'
import {
  Card,
  Row,
  Col,
  Button,
  Input,
  Select,
  Tag,
  Typography,
  Space,
  Avatar,
  Rate,
  Divider,
  Modal,
  Form,
  message,
  Pagination,
  Empty,
  Spin,
  Badge,
  Tooltip,
  Dropdown,
  Menu
} from 'antd'
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  DownloadOutlined,
  StarOutlined,
  StarFilled,
  FilterOutlined,
  SortAscendingOutlined,
  SortDescendingOutlined,
  MenuOutlined,
  EyeOutlined,
  PlusOutlined,
  SearchOutlined,
  UserOutlined,
  SoundOutlined,
  GlobalOutlined,
  LockOutlined,
  ThunderboltOutlined
} from '@ant-design/icons'

const { Title, Text, Paragraph } = Typography
const { Search } = Input
const { Option } = Select

interface VoiceTimbreTemplate {
  id: string
  name: string
  description: string
  author: string
  avatar: string
  gender: 'male' | 'female' | 'neutral'
  age_range: string
  language: string
  style: string
  emotion: string
  category: string
  tags: string[]
  rating: number
  reviews_count: number
  usage_count: number
  is_premium: boolean
  is_public: boolean
  preview_url: string
  cover_image: string
  created_at: string
  updated_at: string
  price: number
  duration: number
  file_size: number
}

interface FilterState {
  search: string
  category: string
  gender: string
  language: string
  style: string
  rating: number
  is_premium: boolean | null
  sort_by: string
  sort_order: 'asc' | 'desc'
}

const VoiceTimbreTemplate: React.FC = () => {
  const [templates, setTemplates] = useState<VoiceTimbreTemplate[]>([])
  const [loading, setLoading] = useState(true)
  const [favorites, setFavorites] = useState<Set<string>>(new Set())
  const [playingId, setPlayingId] = useState<string | null>(null)
  const [previewVisible, setPreviewVisible] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState<VoiceTimbreTemplate | null>(null)
  const [applyModalVisible, setApplyModalVisible] = useState(false)
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 12,
    total: 0
  })
  
  const [filters, setFilters] = useState<FilterState>({
    search: '',
    category: '',
    gender: '',
    language: '',
    style: '',
    rating: 0,
    is_premium: null,
    sort_by: 'usage_count',
    sort_order: 'desc'
  })

  const [form] = Form.useForm()

  const categoryOptions = [
    { label: '全部', value: '' },
    { label: '原创音色', value: 'original' },
    { label: '名人音色', value: 'celebrity' },
    { label: '角色音色', value: 'character' },
    { label: '专业配音', value: 'professional' }
  ]

  const genderOptions = [
    { label: '全部', value: '' },
    { label: '男性', value: 'male' },
    { label: '女性', value: 'female' },
    { label: '中性', value: 'neutral' }
  ]

  const languageOptions = [
    { label: '全部', value: '' },
    { label: '中文', value: 'zh-CN' },
    { label: '英语', value: 'en-US' },
    { label: '日语', value: 'ja-JP' },
    { label: '韩语', value: 'ko-KR' }
  ]

  const styleOptions = [
    { label: '全部', value: '' },
    { label: '正式', value: 'formal' },
    { label: '随意', value: 'casual' },
    { label: '新闻播报', value: 'news' },
    { label: '故事讲述', value: 'storytelling' },
    { label: '广告配音', value: 'commercial' },
    { label: '客服', value: 'customer_service' }
  ]

  const sortOptions = [
    { label: '使用量', value: 'usage_count' },
    { label: '评分', value: 'rating' },
    { label: '创建时间', value: 'created_at' },
    { label: '价格', value: 'price' }
  ]

  useEffect(() => {
    loadTemplates()
  }, [filters, pagination.current, pagination.pageSize])

  const loadTemplates = async () => {
    setLoading(true)
    try {
      // 模拟API调用
      // const response = await voiceTimbreService.getTemplates({
      //   ...filters,
      //   page: pagination.current,
      //   page_size: pagination.pageSize
      // })

      // 模拟数据
      const mockTemplates: VoiceTimbreTemplate[] = [
        {
          id: '1',
          name: '甜美女声',
          description: '温柔甜美的女性声音，适合故事讲述和客服场景',
          author: '音色大师',
          avatar: '/avatars/author1.jpg',
          gender: 'female',
          age_range: 'young_adult',
          language: 'zh-CN',
          style: 'storytelling',
          emotion: 'happy',
          category: 'original',
          tags: ['温柔', '甜美', '故事'],
          rating: 4.8,
          reviews_count: 245,
          usage_count: 1520,
          is_premium: false,
          is_public: true,
          preview_url: '/audio/preview1.mp3',
          cover_image: '/images/voice1.jpg',
          created_at: '2024-06-20T10:00:00Z',
          updated_at: '2024-06-22T15:30:00Z',
          price: 0,
          duration: 23.5,
          file_size: 385024
        },
        {
          id: '2',
          name: '磁性男声',
          description: '低沉磁性的男性声音，适合广告配音和新闻播报',
          author: '声音工匠',
          avatar: '/avatars/author2.jpg',
          gender: 'male',
          age_range: 'middle_aged',
          language: 'zh-CN',
          style: 'commercial',
          emotion: 'serious',
          category: 'professional',
          tags: ['磁性', '低沉', '广告'],
          rating: 4.9,
          reviews_count: 189,
          usage_count: 2340,
          is_premium: true,
          is_public: true,
          preview_url: '/audio/preview2.mp3',
          cover_image: '/images/voice2.jpg',
          created_at: '2024-06-18T14:20:00Z',
          updated_at: '2024-06-21T09:15:00Z',
          price: 99,
          duration: 18.2,
          file_size: 298345
        },
        {
          id: '3',
          name: '活泼童声',
          description: '充满活力的儿童声音，适合儿童故事和教育内容',
          author: '儿童配音师',
          avatar: '/avatars/author3.jpg',
          gender: 'neutral',
          age_range: 'child',
          language: 'zh-CN',
          style: 'storytelling',
          emotion: 'excited',
          category: 'character',
          tags: ['活泼', '童声', '教育'],
          rating: 4.7,
          reviews_count: 156,
          usage_count: 890,
          is_premium: false,
          is_public: true,
          preview_url: '/audio/preview3.mp3',
          cover_image: '/images/voice3.jpg',
          created_at: '2024-06-15T16:45:00Z',
          updated_at: '2024-06-20T11:30:00Z',
          price: 0,
          duration: 25.8,
          file_size: 420156
        }
      ]

      setTemplates(mockTemplates)
      setPagination(prev => ({
        ...prev,
        total: 50 // 模拟总数
      }))

    } catch (error) {
      message.error('加载音色模板失败')
      console.error('Load templates error:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFilterChange = (key: string, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }))
    setPagination(prev => ({
      ...prev,
      current: 1
    }))
  }

  const handleSearch = (value: string) => {
    handleFilterChange('search', value)
  }

  const handlePlay = (templateId: string) => {
    if (playingId === templateId) {
      setPlayingId(null)
    } else {
      setPlayingId(templateId)
      // 这里实现实际的音频播放逻辑
    }
  }

  const handleFavorite = (templateId: string) => {
    setFavorites(prev => {
      const newFavorites = new Set(prev)
      if (newFavorites.has(templateId)) {
        newFavorites.delete(templateId)
        message.success('已从收藏夹移除')
      } else {
        newFavorites.add(templateId)
        message.success('已添加到收藏夹')
      }
      return newFavorites
    })
  }

  const handlePreview = (template: VoiceTimbreTemplate) => {
    setSelectedTemplate(template)
    setPreviewVisible(true)
  }

  const handleApplyTemplate = (template: VoiceTimbreTemplate) => {
    setSelectedTemplate(template)
    setApplyModalVisible(true)
    form.setFieldsValue({
      template_id: template.id,
      use_original_settings: true,
      customize_name: template.name + ' - 副本',
      modify_parameters: false
    })
  }

  const handleApplySubmit = async (values: any) => {
    try {
      // 这里应该调用API应用模板
      // await voiceTimbreService.applyTemplate(values)
      
      message.success('模板应用成功，正在创建您的音色...')
      setApplyModalVisible(false)
      form.resetFields()
      
    } catch (error) {
      message.error('应用模板失败')
      console.error('Apply template error:', error)
    }
  }

  const handlePaginationChange = (page: number, pageSize: number) => {
    setPagination(prev => ({
      ...prev,
      current: page,
      pageSize
    }))
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

  const getGenderIcon = (gender: string) => {
    switch (gender) {
      case 'male': return '👨'
      case 'female': return '👩'
      case 'neutral': return '🧑'
      default: return '👤'
    }
  }

  const sortMenu = (
    <Menu
      onClick={({ key }) => {
        const [sortBy, sortOrder] = key.split('_')
        handleFilterChange('sort_by', sortBy)
        handleFilterChange('sort_order', sortOrder)
      }}
    >
      {sortOptions.map(option => (
        <Menu.SubMenu key={option.value} title={option.label}>
          <Menu.Item key={`${option.value}_desc`}>
            <SortDescendingOutlined /> 降序
          </Menu.Item>
          <Menu.Item key={`${option.value}_asc`}>
            <SortAscendingOutlined /> 升序
          </Menu.Item>
        </Menu.SubMenu>
      ))}
    </Menu>
  )

  return (
    <div className="voice-timbre-template">
      <Card>
        <Title level={2}>
          <SoundOutlined /> 音色模板库
        </Title>
        <Paragraph>
          从丰富的音色模板库中选择适合的音色，快速创建专业的语音内容。
        </Paragraph>

        {/* 搜索和筛选 */}
        <Card size="small" style={{ marginBottom: 16 }}>
          <Row gutter={16} align="middle">
            <Col xs={24} sm={8} md={6}>
              <Search
                placeholder="搜索音色模板..."
                onSearch={handleSearch}
                prefix={<SearchOutlined />}
                allowClear
              />
            </Col>
            <Col xs={12} sm={4} md={3}>
              <Select
                placeholder="类型"
                value={filters.category}
                onChange={value => handleFilterChange('category', value)}
                style={{ width: '100%' }}
              >
                {categoryOptions.map(option => (
                  <Option key={option.value} value={option.value}>
                    {option.label}
                  </Option>
                ))}
              </Select>
            </Col>
            <Col xs={12} sm={4} md={3}>
              <Select
                placeholder="性别"
                value={filters.gender}
                onChange={value => handleFilterChange('gender', value)}
                style={{ width: '100%' }}
              >
                {genderOptions.map(option => (
                  <Option key={option.value} value={option.value}>
                    {option.label}
                  </Option>
                ))}
              </Select>
            </Col>
            <Col xs={12} sm={4} md={3}>
              <Select
                placeholder="语言"
                value={filters.language}
                onChange={value => handleFilterChange('language', value)}
                style={{ width: '100%' }}
              >
                {languageOptions.map(option => (
                  <Option key={option.value} value={option.value}>
                    {option.label}
                  </Option>
                ))}
              </Select>
            </Col>
            <Col xs={12} sm={4} md={3}>
              <Select
                placeholder="风格"
                value={filters.style}
                onChange={value => handleFilterChange('style', value)}
                style={{ width: '100%' }}
              >
                {styleOptions.map(option => (
                  <Option key={option.value} value={option.value}>
                    {option.label}
                  </Option>
                ))}
              </Select>
            </Col>
            <Col>
              <Space>
                <Dropdown overlay={sortMenu} trigger={['click']}>
                  <Button icon={<MenuOutlined />}>
                    排序
                  </Button>
                </Dropdown>
                <Button
                  icon={<FilterOutlined />}
                  onClick={() => {
                    setFilters({
                      search: '',
                      category: '',
                      gender: '',
                      language: '',
                      style: '',
                      rating: 0,
                      is_premium: null,
                      sort_by: 'usage_count',
                      sort_order: 'desc'
                    })
                  }}
                >
                  清除筛选
                </Button>
              </Space>
            </Col>
          </Row>
        </Card>

        {/* 模板列表 */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: 50 }}>
            <Spin size="large" />
          </div>
        ) : templates.length === 0 ? (
          <Empty
            description="没有找到匹配的音色模板"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          >
            <Button type="primary" icon={<PlusOutlined />}>
              创建新模板
            </Button>
          </Empty>
        ) : (
          <>
            <Row gutter={[16, 16]}>
              {templates.map(template => (
                <Col key={template.id} xs={24} sm={12} md={8} lg={6}>
                  <Badge.Ribbon
                    text={template.is_premium ? '付费' : '免费'}
                    color={template.is_premium ? 'gold' : 'green'}
                  >
                    <Card
                      hoverable
                      cover={
                        <div style={{ height: 120, background: '#f5f5f5', position: 'relative' }}>
                          <div
                            style={{
                              position: 'absolute',
                              top: 0,
                              left: 0,
                              right: 0,
                              bottom: 0,
                              background: `linear-gradient(45deg, #667eea 0%, #764ba2 100%)`,
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              color: 'white',
                              fontSize: 24
                            }}
                          >
                            {getGenderIcon(template.gender)}
                          </div>
                          <div style={{ position: 'absolute', top: 8, right: 8 }}>
                            <Button
                              type="text"
                              shape="circle"
                              icon={
                                favorites.has(template.id) ? 
                                <StarFilled style={{ color: '#faad14' }} /> : 
                                <StarOutlined style={{ color: 'white' }} />
                              }
                              onClick={() => handleFavorite(template.id)}
                            />
                          </div>
                          <div style={{ position: 'absolute', bottom: 8, left: 8 }}>
                            <Button
                              type="primary"
                              shape="circle"
                              icon={
                                playingId === template.id ? 
                                <PauseCircleOutlined /> : 
                                <PlayCircleOutlined />
                              }
                              onClick={() => handlePlay(template.id)}
                            />
                          </div>
                        </div>
                      }
                      actions={[
                        <Tooltip title="预览详情">
                          <Button
                            type="text"
                            icon={<EyeOutlined />}
                            onClick={() => handlePreview(template)}
                          />
                        </Tooltip>,
                        <Tooltip title="应用模板">
                          <Button
                            type="text"
                            icon={<DownloadOutlined />}
                            onClick={() => handleApplyTemplate(template)}
                          />
                        </Tooltip>
                      ]}
                    >
                      <Card.Meta
                        title={
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                            <Text strong ellipsis style={{ flex: 1 }}>
                              {template.name}
                            </Text>
                            {template.is_premium && (
                              <ThunderboltOutlined style={{ color: '#faad14' }} />
                            )}
                          </div>
                        }
                        description={
                          <Space direction="vertical" size="small" style={{ width: '100%' }}>
                            <Text ellipsis type="secondary" style={{ fontSize: 12 }}>
                              {template.description}
                            </Text>
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                              <Space size="small">
                                <Avatar size="small" icon={<UserOutlined />} />
                                <Text style={{ fontSize: 12 }}>{template.author}</Text>
                              </Space>
                              <Space size="small">
                                {template.is_public ? (
                                  <GlobalOutlined style={{ color: '#52c41a' }} />
                                ) : (
                                  <LockOutlined style={{ color: '#faad14' }} />
                                )}
                              </Space>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                              <Rate disabled defaultValue={template.rating} style={{ fontSize: 12 }} />
                              <Text style={{ fontSize: 12 }} type="secondary">
                                {template.usage_count} 次使用
                              </Text>
                            </div>
                            <div style={{ marginTop: 8 }}>
                              {template.tags.slice(0, 2).map(tag => (
                                <Tag key={tag} size="small" style={{ marginBottom: 2 }}>
                                  {tag}
                                </Tag>
                              ))}
                              {template.tags.length > 2 && (
                                <Tag size="small" style={{ marginBottom: 2 }}>
                                  +{template.tags.length - 2}
                                </Tag>
                              )}
                            </div>
                            {template.is_premium && (
                              <div style={{ textAlign: 'right' }}>
                                <Text strong style={{ color: '#faad14' }}>
                                  ¥{template.price}
                                </Text>
                              </div>
                            )}
                          </Space>
                        }
                      />
                    </Card>
                  </Badge.Ribbon>
                </Col>
              ))}
            </Row>

            <div style={{ textAlign: 'center', marginTop: 24 }}>
              <Pagination
                current={pagination.current}
                pageSize={pagination.pageSize}
                total={pagination.total}
                onChange={handlePaginationChange}
                showSizeChanger
                showQuickJumper
                showTotal={(total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`}
              />
            </div>
          </>
        )}
      </Card>

      {/* 预览模态框 */}
      <Modal
        title="音色模板预览"
        open={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        footer={[
          <Button key="cancel" onClick={() => setPreviewVisible(false)}>
            关闭
          </Button>,
          <Button
            key="apply"
            type="primary"
            onClick={() => {
              setPreviewVisible(false)
              if (selectedTemplate) {
                handleApplyTemplate(selectedTemplate)
              }
            }}
          >
            应用模板
          </Button>
        ]}
        width={800}
      >
        {selectedTemplate && (
          <div>
            <Row gutter={24}>
              <Col span={8}>
                <div
                  style={{
                    height: 200,
                    background: `linear-gradient(45deg, #667eea 0%, #764ba2 100%)`,
                    borderRadius: 8,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    fontSize: 48
                  }}
                >
                  {getGenderIcon(selectedTemplate.gender)}
                </div>
              </Col>
              <Col span={16}>
                <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                  <div>
                    <Title level={3}>{selectedTemplate.name}</Title>
                    <Text type="secondary">{selectedTemplate.description}</Text>
                  </div>
                  
                  <Row gutter={16}>
                    <Col span={12}>
                      <Text strong>作者:</Text> {selectedTemplate.author}
                    </Col>
                    <Col span={12}>
                      <Text strong>类型:</Text> {selectedTemplate.category}
                    </Col>
                    <Col span={12}>
                      <Text strong>性别:</Text> {selectedTemplate.gender}
                    </Col>
                    <Col span={12}>
                      <Text strong>语言:</Text> {selectedTemplate.language}
                    </Col>
                    <Col span={12}>
                      <Text strong>风格:</Text> {selectedTemplate.style}
                    </Col>
                    <Col span={12}>
                      <Text strong>时长:</Text> {formatDuration(selectedTemplate.duration)}
                    </Col>
                  </Row>

                  <div>
                    <Rate disabled value={selectedTemplate.rating} />
                    <Text style={{ marginLeft: 8 }}>
                      {selectedTemplate.rating} ({selectedTemplate.reviews_count} 评价)
                    </Text>
                  </div>

                  <div>
                    <Text strong>标签: </Text>
                    {selectedTemplate.tags.map(tag => (
                      <Tag key={tag}>{tag}</Tag>
                    ))}
                  </div>

                  <audio controls style={{ width: '100%' }} src={selectedTemplate.preview_url} />
                </Space>
              </Col>
            </Row>
          </div>
        )}
      </Modal>

      {/* 应用模板模态框 */}
      <Modal
        title="应用音色模板"
        open={applyModalVisible}
        onCancel={() => setApplyModalVisible(false)}
        onOk={() => form.submit()}
        okText="确认应用"
        cancelText="取消"
      >
        {selectedTemplate && (
          <Form form={form} layout="vertical" onFinish={handleApplySubmit}>
            <Form.Item name="template_id" hidden>
              <Input />
            </Form.Item>

            <Alert
              message={`即将应用模板: ${selectedTemplate.name}`}
              description="应用模板后，将会基于该模板创建一个新的音色配置。"
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />

            <Form.Item
              name="customize_name"
              label="自定义名称"
              rules={[{ required: true, message: '请输入自定义名称' }]}
            >
              <Input placeholder="为您的音色起一个名字" />
            </Form.Item>

            <Form.Item
              name="use_original_settings"
              label="使用原始设置"
              valuePropName="checked"
            >
              <Switch
                checkedChildren="是"
                unCheckedChildren="否"
                defaultChecked
              />
            </Form.Item>

            <Form.Item
              name="modify_parameters"
              label="允许修改参数"
              valuePropName="checked"
            >
              <Switch
                checkedChildren="是"
                unCheckedChildren="否"
              />
            </Form.Item>

            {selectedTemplate.is_premium && (
              <Alert
                message="付费模板"
                description={`使用此模板需要支付 ¥${selectedTemplate.price}，费用将在确认后扣除。`}
                type="warning"
                showIcon
              />
            )}
          </Form>
        )}
      </Modal>
    </div>
  )
}

export default VoiceTimbreTemplate