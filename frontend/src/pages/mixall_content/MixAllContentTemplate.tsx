/**
 * Mix All Content Template Component
 * 混合内容模板管理组件 - [MixAll][Content][Template]
 */

import React, { useState, useEffect } from 'react'
import {
  Card,
  Table,
  Button,
  Typography,
  Row,
  Col,
  Space,
  Tag,
  Modal,
  Form,
  Input,
  Select,
  Switch,
  Rate,
  message,
  Divider,
  Tooltip,
  Popconfirm,
  Avatar,
  Empty,
  Badge,
  Statistic
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  ShareAltOutlined,
  DownloadOutlined,
  CopyOutlined,
  StarOutlined,
  StarFilled,
  HeartOutlined,
  HeartFilled,
  FileTextOutlined,
  SoundOutlined,
  FileImageOutlined,
  VideoCameraOutlined,
  ThunderboltOutlined,
  FilterOutlined,
  SearchOutlined,
  TeamOutlined,
  CalendarOutlined,
  BulbOutlined,
  TagsOutlined
} from '@ant-design/icons'

const { Title, Paragraph, Text } = Typography
const { TextArea } = Input
const { Option } = Select
const { Search } = Input

// ================================
// 类型定义 - Types
// ================================

type TemplateCategory = 'business' | 'education' | 'entertainment' | 'marketing' | 'personal' | 'other'
type TemplateStatus = 'draft' | 'published' | 'archived'
type ContentType = 'text' | 'voice' | 'image' | 'video' | 'music'

interface TemplateContentBlock {
  id: string
  type: ContentType
  title: string
  content: any
  duration?: number
  position: number
  settings: Record<string, any>
}

interface ContentTemplate {
  id: string
  name: string
  description: string
  category: TemplateCategory
  status: TemplateStatus
  thumbnail_url?: string
  blocks: TemplateContentBlock[]
  settings: {
    output_format: string
    resolution: string
    frame_rate: number
    transitions: string
  }
  metadata: {
    author_id: string
    author_name: string
    created_at: string
    updated_at: string
    tags: string[]
    is_public: boolean
    is_featured: boolean
    difficulty_level: number
    estimated_time: number
  }
  stats: {
    view_count: number
    use_count: number
    like_count: number
    favorite_count: number
    rating: number
    rating_count: number
  }
}

interface TemplateFilter {
  category?: TemplateCategory
  status?: TemplateStatus
  author?: string
  tags?: string[]
  difficulty?: number
  is_public?: boolean
  is_featured?: boolean
}

// ================================
// 主组件
// ================================

const MixAllContentTemplate: React.FC = () => {
  const [templates, setTemplates] = useState<ContentTemplate[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState<ContentTemplate | null>(null)
  const [editingTemplate, setEditingTemplate] = useState<ContentTemplate | null>(null)
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [filter, setFilter] = useState<TemplateFilter>({})
  const [searchText, setSearchText] = useState('')
  const [createModalVisible, setCreateModalVisible] = useState(false)
  const [editModalVisible, setEditModalVisible] = useState(false)
  const [previewModalVisible, setPreviewModalVisible] = useState(false)
  const [shareModalVisible, setShareModalVisible] = useState(false)
  const [form] = Form.useForm()

  const categoryOptions = [
    { label: '商业应用', value: 'business', color: 'blue', icon: <BulbOutlined /> },
    { label: '教育培训', value: 'education', color: 'green', icon: <FileTextOutlined /> },
    { label: '娱乐内容', value: 'entertainment', color: 'orange', icon: <VideoCameraOutlined /> },
    { label: '营销推广', value: 'marketing', color: 'red', icon: <ThunderboltOutlined /> },
    { label: '个人创作', value: 'personal', color: 'purple', icon: <HeartOutlined /> },
    { label: '其他分类', value: 'other', color: 'default', icon: <TagsOutlined /> }
  ]

  const contentTypeOptions = [
    { label: '文本内容', value: 'text', icon: <FileTextOutlined />, color: 'blue' },
    { label: '语音合成', value: 'voice', icon: <SoundOutlined />, color: 'green' },
    { label: '图像素材', value: 'image', icon: <FileImageOutlined />, color: 'orange' },
    { label: '视频片段', value: 'video', icon: <VideoCameraOutlined />, color: 'red' },
    { label: '背景音乐', value: 'music', icon: <SoundOutlined />, color: 'purple' }
  ]

  // ================================
  // 数据加载和管理 - Data Loading & Management
  // ================================

  useEffect(() => {
    loadTemplates()
  }, [filter, searchText])

  const loadTemplates = async () => {
    setLoading(true)
    try {
      // 模拟API调用
      // const response = await mixAllTemplateService.getTemplates({ filter, search: searchText })
      
      // 模拟数据
      const mockTemplates: ContentTemplate[] = [
        {
          id: 'template_001',
          name: '产品介绍视频模板',
          description: '专业的产品介绍视频模板，包含开场动画、产品展示、功能介绍和结尾Call-to-Action',
          category: 'business',
          status: 'published',
          thumbnail_url: '/images/template_001.jpg',
          blocks: [
            {
              id: 'block_001',
              type: 'text',
              title: '开场标题',
              content: { text: '{{产品名称}} - 革命性的解决方案' },
              duration: 3,
              position: 0,
              settings: { animation: 'fade', font_size: 48 }
            },
            {
              id: 'block_002',
              type: 'voice',
              title: '产品介绍旁白',
              content: { text: '欢迎了解{{产品名称}}，这是一款{{产品特点}}的创新产品...' },
              position: 1,
              settings: { voice_id: 'voice_001', speed: 1.0 }
            }
          ],
          settings: {
            output_format: 'video',
            resolution: '1920x1080',
            frame_rate: 30,
            transitions: 'fade'
          },
          metadata: {
            author_id: 'user_001',
            author_name: '专业创作者',
            created_at: '2024-06-20T10:00:00Z',
            updated_at: '2024-06-24T15:30:00Z',
            tags: ['产品介绍', '商业', '营销', '专业'],
            is_public: true,
            is_featured: true,
            difficulty_level: 3,
            estimated_time: 15
          },
          stats: {
            view_count: 1250,
            use_count: 89,
            like_count: 156,
            favorite_count: 67,
            rating: 4.6,
            rating_count: 23
          }
        },
        {
          id: 'template_002',
          name: '课程宣传短片',
          description: '教育培训课程宣传短片模板，适用于在线教育平台和培训机构',
          category: 'education',
          status: 'published',
          thumbnail_url: '/images/template_002.jpg',
          blocks: [],
          settings: {
            output_format: 'video',
            resolution: '1280x720',
            frame_rate: 24,
            transitions: 'slide'
          },
          metadata: {
            author_id: 'user_002',
            author_name: '教育专家',
            created_at: '2024-06-18T14:20:00Z',
            updated_at: '2024-06-22T09:15:00Z',
            tags: ['教育', '课程', '宣传', '培训'],
            is_public: true,
            is_featured: false,
            difficulty_level: 2,
            estimated_time: 10
          },
          stats: {
            view_count: 856,
            use_count: 45,
            like_count: 92,
            favorite_count: 31,
            rating: 4.3,
            rating_count: 18
          }
        },
        {
          id: 'template_003',
          name: '个人Vlog模板',
          description: '简洁清新的个人Vlog模板，包含标题动画、转场效果和背景音乐',
          category: 'personal',
          status: 'published',
          thumbnail_url: '/images/template_003.jpg',
          blocks: [],
          settings: {
            output_format: 'video',
            resolution: '1080x1920',
            frame_rate: 30,
            transitions: 'zoom'
          },
          metadata: {
            author_id: 'user_003',
            author_name: 'Vlog达人',
            created_at: '2024-06-15T20:45:00Z',
            updated_at: '2024-06-20T11:30:00Z',
            tags: ['Vlog', '个人', '生活', '竖屏'],
            is_public: true,
            is_featured: false,
            difficulty_level: 1,
            estimated_time: 8
          },
          stats: {
            view_count: 2134,
            use_count: 156,
            like_count: 234,
            favorite_count: 89,
            rating: 4.8,
            rating_count: 45
          }
        }
      ]

      setTemplates(mockTemplates)
    } catch (error) {
      console.error('Failed to load templates:', error)
      message.error('加载模板列表失败')
    } finally {
      setLoading(false)
    }
  }

  // ================================
  // 模板操作 - Template Operations
  // ================================

  const handleCreateTemplate = async (values: any) => {
    try {
      const newTemplate: Partial<ContentTemplate> = {
        name: values.name,
        description: values.description,
        category: values.category,
        status: 'draft',
        blocks: [],
        settings: {
          output_format: values.output_format || 'video',
          resolution: values.resolution || '1920x1080',
          frame_rate: values.frame_rate || 30,
          transitions: values.transitions || 'fade'
        },
        metadata: {
          author_id: 'current_user',
          author_name: '当前用户',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          tags: values.tags || [],
          is_public: values.is_public || false,
          is_featured: false,
          difficulty_level: values.difficulty_level || 1,
          estimated_time: values.estimated_time || 5
        },
        stats: {
          view_count: 0,
          use_count: 0,
          like_count: 0,
          favorite_count: 0,
          rating: 0,
          rating_count: 0
        }
      }

      // 这里应该调用API创建模板
      // await mixAllTemplateService.createTemplate(newTemplate)
      
      message.success('模板创建成功！')
      setCreateModalVisible(false)
      form.resetFields()
      loadTemplates()
    } catch (error) {
      console.error('Template creation failed:', error)
      message.error('模板创建失败')
    }
  }

  const handleEditTemplate = async (values: any) => {
    if (!editingTemplate) return

    try {
      const updatedTemplate = {
        ...editingTemplate,
        ...values,
        metadata: {
          ...editingTemplate.metadata,
          updated_at: new Date().toISOString(),
          tags: values.tags
        }
      }

      // 这里应该调用API更新模板
      // await mixAllTemplateService.updateTemplate(editingTemplate.id, updatedTemplate)
      
      message.success('模板更新成功！')
      setEditModalVisible(false)
      setEditingTemplate(null)
      form.resetFields()
      loadTemplates()
    } catch (error) {
      console.error('Template update failed:', error)
      message.error('模板更新失败')
    }
  }

  const handleDeleteTemplate = async (templateId: string) => {
    try {
      // 这里应该调用API删除模板
      // await mixAllTemplateService.deleteTemplate(templateId)
      
      message.success('模板删除成功！')
      loadTemplates()
    } catch (error) {
      console.error('Template deletion failed:', error)
      message.error('模板删除失败')
    }
  }

  const handleUseTemplate = (template: ContentTemplate) => {
    // 跳转到内容创作页面，并加载模板
    // router.push(`/mixall/create?template=${template.id}`)
    message.success(`正在使用模板：${template.name}`)
  }

  const handleToggleLike = async (template: ContentTemplate) => {
    try {
      // 这里应该调用API切换点赞状态
      // await mixAllTemplateService.toggleLike(template.id)
      
      message.success('操作成功！')
      loadTemplates()
    } catch (error) {
      console.error('Toggle like failed:', error)
      message.error('操作失败')
    }
  }

  const handleToggleFavorite = async (template: ContentTemplate) => {
    try {
      // 这里应该调用API切换收藏状态
      // await mixAllTemplateService.toggleFavorite(template.id)
      
      message.success('操作成功！')
      loadTemplates()
    } catch (error) {
      console.error('Toggle favorite failed:', error)
      message.error('操作失败')
    }
  }

  const handleShareTemplate = (template: ContentTemplate) => {
    setSelectedTemplate(template)
    setShareModalVisible(true)
  }

  // ================================
  // 渲染函数 - Render Functions
  // ================================

  const getCategoryInfo = (category: TemplateCategory) => {
    return categoryOptions.find(opt => opt.value === category) || categoryOptions[5]
  }

  const getContentTypeInfo = (type: ContentType) => {
    return contentTypeOptions.find(opt => opt.value === type) || contentTypeOptions[0]
  }

  const renderTemplateCard = (template: ContentTemplate) => (
    <Card
      key={template.id}
      hoverable
      cover={
        template.thumbnail_url ? (
          <img alt={template.name} src={template.thumbnail_url} style={{ height: 200, objectFit: 'cover' }} />
        ) : (
          <div style={{ height: 200, background: '#f0f0f0', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <FileTextOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />
          </div>
        )
      }
      actions={[
        <Tooltip title="预览">
          <EyeOutlined onClick={() => {
            setSelectedTemplate(template)
            setPreviewModalVisible(true)
          }} />
        </Tooltip>,
        <Tooltip title="使用模板">
          <ThunderboltOutlined onClick={() => handleUseTemplate(template)} />
        </Tooltip>,
        <Tooltip title="分享">
          <ShareAltOutlined onClick={() => handleShareTemplate(template)} />
        </Tooltip>,
        <Tooltip title="更多">
          <EditOutlined onClick={() => {
            setEditingTemplate(template)
            setEditModalVisible(true)
            form.setFieldsValue({
              name: template.name,
              description: template.description,
              category: template.category,
              tags: template.metadata.tags,
              is_public: template.metadata.is_public,
              difficulty_level: template.metadata.difficulty_level,
              estimated_time: template.metadata.estimated_time
            })
          }} />
        </Tooltip>
      ]
    >
      <Card.Meta
        title={
          <Space>
            <Text strong>{template.name}</Text>
            {template.metadata.is_featured && <StarFilled style={{ color: '#faad14' }} />}
          </Space>
        }
        description={
          <Space direction="vertical" style={{ width: '100%' }}>
            <Text ellipsis={{ tooltip: template.description }}>
              {template.description}
            </Text>
            <Space wrap>
              <Tag color={getCategoryInfo(template.category).color} icon={getCategoryInfo(template.category).icon}>
                {getCategoryInfo(template.category).label}
              </Tag>
              <Tag>难度: {template.metadata.difficulty_level}/5</Tag>
              <Tag>预计: {template.metadata.estimated_time}分钟</Tag>
            </Space>
            <Space>
              <Statistic
                title="使用"
                value={template.stats.use_count}
                prefix={<ThunderboltOutlined />}
                valueStyle={{ fontSize: 12 }}
              />
              <Statistic
                title="点赞"
                value={template.stats.like_count}
                prefix={<HeartOutlined />}
                valueStyle={{ fontSize: 12 }}
              />
              <Rate disabled defaultValue={template.stats.rating} style={{ fontSize: 12 }} />
            </Space>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Space>
                <Avatar size="small" />
                <Text type="secondary" style={{ fontSize: 12 }}>{template.metadata.author_name}</Text>
              </Space>
              <Text type="secondary" style={{ fontSize: 12 }}>
                {new Date(template.metadata.updated_at).toLocaleDateString()}
              </Text>
            </div>
          </Space>
        }
      />
    </Card>
  )

  const renderCreateModal = () => (
    <Modal
      title="创建新模板"
      open={createModalVisible}
      onCancel={() => {
        setCreateModalVisible(false)
        form.resetFields()
      }}
      onOk={() => form.submit()}
      width={600}
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleCreateTemplate}
      >
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="name"
              label="模板名称"
              rules={[{ required: true, message: '请输入模板名称' }]}
            >
              <Input placeholder="输入模板名称" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="category"
              label="模板分类"
              rules={[{ required: true, message: '请选择模板分类' }]}
            >
              <Select placeholder="选择分类">
                {categoryOptions.map(option => (
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
        </Row>

        <Form.Item
          name="description"
          label="模板描述"
          rules={[{ required: true, message: '请输入模板描述' }]}
        >
          <TextArea rows={3} placeholder="描述模板的用途和特点..." />
        </Form.Item>

        <Row gutter={16}>
          <Col span={8}>
            <Form.Item
              name="difficulty_level"
              label="难度等级"
              initialValue={1}
            >
              <Select>
                <Option value={1}>新手 (1星)</Option>
                <Option value={2}>初级 (2星)</Option>
                <Option value={3}>中级 (3星)</Option>
                <Option value={4}>高级 (4星)</Option>
                <Option value={5}>专家 (5星)</Option>
              </Select>
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item
              name="estimated_time"
              label="预计时长(分钟)"
              initialValue={5}
            >
              <Input type="number" min={1} max={120} />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item
              name="is_public"
              label="公开模板"
              valuePropName="checked"
              initialValue={false}
            >
              <Switch checkedChildren="公开" unCheckedChildren="私有" />
            </Form.Item>
          </Col>
        </Row>

        <Form.Item
          name="tags"
          label="标签"
        >
          <Select
            mode="tags"
            placeholder="添加标签..."
            tokenSeparators={[',']}
          />
        </Form.Item>
      </Form>
    </Modal>
  )

  const renderEditModal = () => (
    <Modal
      title="编辑模板"
      open={editModalVisible}
      onCancel={() => {
        setEditModalVisible(false)
        setEditingTemplate(null)
        form.resetFields()
      }}
      onOk={() => form.submit()}
      width={600}
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleEditTemplate}
      >
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="name"
              label="模板名称"
              rules={[{ required: true, message: '请输入模板名称' }]}
            >
              <Input placeholder="输入模板名称" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="category"
              label="模板分类"
              rules={[{ required: true, message: '请选择模板分类' }]}
            >
              <Select placeholder="选择分类">
                {categoryOptions.map(option => (
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
        </Row>

        <Form.Item
          name="description"
          label="模板描述"
          rules={[{ required: true, message: '请输入模板描述' }]}
        >
          <TextArea rows={3} placeholder="描述模板的用途和特点..." />
        </Form.Item>

        <Row gutter={16}>
          <Col span={8}>
            <Form.Item
              name="difficulty_level"
              label="难度等级"
            >
              <Select>
                <Option value={1}>新手 (1星)</Option>
                <Option value={2}>初级 (2星)</Option>
                <Option value={3}>中级 (3星)</Option>
                <Option value={4}>高级 (4星)</Option>
                <Option value={5}>专家 (5星)</Option>
              </Select>
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item
              name="estimated_time"
              label="预计时长(分钟)"
            >
              <Input type="number" min={1} max={120} />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item
              name="is_public"
              label="公开模板"
              valuePropName="checked"
            >
              <Switch checkedChildren="公开" unCheckedChildren="私有" />
            </Form.Item>
          </Col>
        </Row>

        <Form.Item
          name="tags"
          label="标签"
        >
          <Select
            mode="tags"
            placeholder="添加标签..."
            tokenSeparators={[',']}
          />
        </Form.Item>
      </Form>
    </Modal>
  )

  const renderPreviewModal = () => (
    <Modal
      title={selectedTemplate?.name}
      open={previewModalVisible}
      onCancel={() => {
        setPreviewModalVisible(false)
        setSelectedTemplate(null)
      }}
      footer={[
        <Button key="close" onClick={() => setPreviewModalVisible(false)}>
          关闭
        </Button>,
        <Button key="use" type="primary" onClick={() => {
          if (selectedTemplate) {
            handleUseTemplate(selectedTemplate)
            setPreviewModalVisible(false)
          }
        }}>
          使用模板
        </Button>
      ]}
      width={800}
    >
      {selectedTemplate && (
        <Space direction="vertical" style={{ width: '100%' }}>
          <Row gutter={16}>
            <Col span={16}>
              <div>
                <Title level={4}>模板描述</Title>
                <Paragraph>{selectedTemplate.description}</Paragraph>
                
                <Title level={4}>内容结构</Title>
                {selectedTemplate.blocks.length > 0 ? (
                  <div>
                    {selectedTemplate.blocks.map((block, index) => (
                      <Card key={block.id} size="small" style={{ marginBottom: 8 }}>
                        <Space>
                          <Badge count={index + 1} />
                          {getContentTypeInfo(block.type).icon}
                          <Text strong>{block.title}</Text>
                          <Tag color={getContentTypeInfo(block.type).color}>
                            {getContentTypeInfo(block.type).label}
                          </Tag>
                          {block.duration && <Text type="secondary">{block.duration}s</Text>}
                        </Space>
                      </Card>
                    ))}
                  </div>
                ) : (
                  <Empty description="暂无内容块" />
                )}

                <Title level={4}>使用标签</Title>
                <Space wrap>
                  {selectedTemplate.metadata.tags.map(tag => (
                    <Tag key={tag}>{tag}</Tag>
                  ))}
                </Space>
              </div>
            </Col>
            <Col span={8}>
              <Card size="small">
                <Statistic
                  title="模板统计"
                  value={selectedTemplate.stats.use_count}
                  prefix={<ThunderboltOutlined />}
                  suffix="次使用"
                />
                <Divider />
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Text>浏览次数:</Text>
                    <Text>{selectedTemplate.stats.view_count}</Text>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Text>点赞数:</Text>
                    <Text>{selectedTemplate.stats.like_count}</Text>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Text>收藏数:</Text>
                    <Text>{selectedTemplate.stats.favorite_count}</Text>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Text>平均评分:</Text>
                    <Space>
                      <Rate disabled defaultValue={selectedTemplate.stats.rating} style={{ fontSize: 14 }} />
                      <Text>({selectedTemplate.stats.rating_count})</Text>
                    </Space>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Text>难度等级:</Text>
                    <Rate disabled defaultValue={selectedTemplate.metadata.difficulty_level} style={{ fontSize: 14 }} />
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Text>预计时长:</Text>
                    <Text>{selectedTemplate.metadata.estimated_time} 分钟</Text>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Text>创建者:</Text>
                    <Text>{selectedTemplate.metadata.author_name}</Text>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Text>更新时间:</Text>
                    <Text>{new Date(selectedTemplate.metadata.updated_at).toLocaleDateString()}</Text>
                  </div>
                </Space>
              </Card>
            </Col>
          </Row>
        </Space>
      )}
    </Modal>
  )

  // ================================
  // 主渲染
  // ================================

  return (
    <div className="mixall-content-template">
      <Card>
        <div style={{ marginBottom: 24 }}>
          <Title level={2}>
            <TagsOutlined /> 内容模板库
          </Title>
          <Paragraph>
            浏览和管理混合内容模板，快速创建专业级的多媒体内容。
          </Paragraph>
        </div>

        {/* 工具栏 */}
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col xs={24} sm={12} md={8}>
            <Search
              placeholder="搜索模板..."
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              onSearch={loadTemplates}
              enterButton={<SearchOutlined />}
            />
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Select
              placeholder="选择分类"
              value={filter.category}
              onChange={(value) => setFilter({ ...filter, category: value })}
              allowClear
              style={{ width: '100%' }}
            >
              {categoryOptions.map(option => (
                <Option key={option.value} value={option.value}>
                  <Space>
                    {option.icon}
                    {option.label}
                  </Space>
                </Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={24} md={8}>
            <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
              <Button
                icon={<FilterOutlined />}
                onClick={() => {
                  // 显示高级筛选面板
                }}
              >
                高级筛选
              </Button>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => setCreateModalVisible(true)}
              >
                创建模板
              </Button>
            </Space>
          </Col>
        </Row>

        {/* 模板网格 */}
        <Row gutter={[16, 16]}>
          {templates.map(template => (
            <Col key={template.id} xs={24} sm={12} md={8} lg={6}>
              {renderTemplateCard(template)}
            </Col>
          ))}
        </Row>

        {templates.length === 0 && !loading && (
          <Empty
            description="暂无模板"
            style={{ margin: '40px 0' }}
          >
            <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateModalVisible(true)}>
              创建第一个模板
            </Button>
          </Empty>
        )}

        {/* 模态框 */}
        {renderCreateModal()}
        {renderEditModal()}
        {renderPreviewModal()}
      </Card>
    </div>
  )
}

export default MixAllContentTemplate