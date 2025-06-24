/**
 * Image Template Manage Component
 * 图像模板管理组件 - [components][image_service][image_template_manage]
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Typography,
  Tag,
  Avatar,
  Popconfirm,
  Modal,
  Form,
  Input,
  Select,
  message,
  Drawer,
  Row,
  Col,
  Statistic,
  Alert,
  Tooltip,
  Badge,
  Divider,
  Empty,
  Image,
  Switch
} from 'antd';
import {
  PictureOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  CopyOutlined,
  StarOutlined,
  ThunderboltOutlined,
  ReloadOutlined,
  SearchOutlined,
  FilterOutlined,
  SettingOutlined,
  BulbOutlined,
  ShareAltOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

import { useImageServiceStore } from '../../../stores/image_service/image_service_store';
import type { 
  ImageTemplateBasic,
  ImageTemplateCreateRequest,
  ImageTemplateUpdateRequest,
  ImagePlatformType,
  ImageGenerationResponse
} from '../../../services/api/image_service_api';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { Search } = Input;
const { TextArea } = Input;

interface ImageTemplateManageProps {
  onTemplateSelect?: (template: ImageTemplateBasic) => void;
  onTemplateGenerate?: (result: ImageGenerationResponse) => void;
  selectedTemplateId?: number;
  showSelector?: boolean;
  className?: string;
}

interface TemplateFilters {
  template_type?: 'style' | 'prompt' | 'composition';
  platform_type?: ImagePlatformType;
  is_public?: boolean;
  search?: string;
}

export const ImageTemplateManage: React.FC<ImageTemplateManageProps> = ({
  onTemplateSelect,
  onTemplateGenerate,
  selectedTemplateId,
  showSelector = false,
  className
}) => {
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [detailDrawerVisible, setDetailDrawerVisible] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<ImageTemplateBasic | null>(null);
  const [filters, setFilters] = useState<TemplateFilters>({});
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  const [createForm] = Form.useForm();
  const [editForm] = Form.useForm();

  const {
    templateList,
    currentTemplate,
    templateListLoading,
    templateCreateLoading,
    templateUpdateLoading,
    generationLoading,
    image_service_store_load_template_list,
    image_service_store_load_template_detail,
    image_service_store_create_template,
    image_service_store_update_template,
    image_service_store_delete_template,
    image_service_store_generate_from_template
  } = useImageServiceStore();

  // 初始化数据加载
  useEffect(() => {
    loadTemplateList();
  }, []);

  // 监听过滤条件变化
  useEffect(() => {
    loadTemplateList();
  }, [filters, currentPage, pageSize]);

  const loadTemplateList = () => {
    image_service_store_load_template_list(currentPage, pageSize, filters);
  };

  // 查看详情
  const handleViewDetail = (template: ImageTemplateBasic) => {
    setSelectedTemplate(template);
    image_service_store_load_template_detail(template.template_id);
    setDetailDrawerVisible(true);
  };

  // 使用模板生成
  const handleGenerateFromTemplate = async (template: ImageTemplateBasic) => {
    try {
      const result = await image_service_store_generate_from_template(template.template_id);
      if (result) {
        message.success('模板生成成功');
        onTemplateGenerate?.(result);
      }
    } catch (error) {
      console.error('Template generation failed:', error);
    }
  };

  // 编辑模板
  const handleEdit = (template: ImageTemplateBasic) => {
    setSelectedTemplate(template);
    editForm.setFieldsValue({
      template_id: template.template_id,
      template_name: template.template_name,
      template_description: template.template_description,
      template_prompt: template.template_prompt,
      is_public: template.is_public
    });
    setEditModalVisible(true);
  };

  // 删除模板
  const handleDelete = async (templateId: number) => {
    const success = await image_service_store_delete_template(templateId);
    if (success) {
      message.success('模板删除成功');
      loadTemplateList();
    }
  };

  // 复制模板提示词
  const handleCopyPrompt = (prompt: string) => {
    navigator.clipboard.writeText(prompt);
    message.success('提示词已复制到剪贴板');
  };

  // 创建模板
  const handleCreate = async () => {
    try {
      const values = await createForm.validateFields();
      const request: ImageTemplateCreateRequest = {
        template_name: values.template_name,
        template_type: values.template_type,
        template_description: values.template_description,
        template_prompt: values.template_prompt,
        template_params: values.template_params,
        platform_type: values.platform_type,
        is_public: values.is_public
      };

      const success = await image_service_store_create_template(request);
      if (success) {
        message.success('模板创建成功');
        setCreateModalVisible(false);
        createForm.resetFields();
        loadTemplateList();
      }
    } catch (error) {
      console.error('Create template failed:', error);
    }
  };

  // 更新模板
  const handleUpdate = async () => {
    try {
      const values = await editForm.validateFields();
      const request: ImageTemplateUpdateRequest = {
        template_id: values.template_id,
        template_name: values.template_name,
        template_description: values.template_description,
        template_prompt: values.template_prompt,
        is_public: values.is_public
      };

      const success = await image_service_store_update_template(request);
      if (success) {
        message.success('模板更新成功');
        setEditModalVisible(false);
        editForm.resetFields();
        loadTemplateList();
      }
    } catch (error) {
      console.error('Update template failed:', error);
    }
  };

  // 表格列定义
  const columns: ColumnsType<ImageTemplateBasic> = [
    {
      title: '模板信息',
      key: 'info',
      width: 280,
      render: (_, record) => (
        <Space>
          {record.preview_image_url ? (
            <Avatar 
              size={50}
              src={record.preview_image_url}
              style={{ borderRadius: 6 }}
            />
          ) : (
            <Avatar 
              size={50}
              icon={<PictureOutlined />} 
              style={{ backgroundColor: '#f0f0f0', color: '#999' }}
            />
          )}
          <div>
            <div>
              <Text strong>{record.template_name}</Text>
              {record.is_public && (
                <Tag color="green" size="small" style={{ marginLeft: 8 }}>
                  公开
                </Tag>
              )}
            </div>
            <div>
              <Text type="secondary" style={{ fontSize: '12px' }}>
                #{record.template_id} · {record.template_type}
              </Text>
            </div>
          </div>
        </Space>
      )
    },
    {
      title: '平台/类型',
      key: 'platform_type',
      width: 120,
      render: (_, record) => (
        <Space direction="vertical" size="small">
          <Tag color="blue">{record.platform_type.toUpperCase()}</Tag>
          <Tag color="orange">
            {record.template_type === 'style' ? '风格' :
             record.template_type === 'prompt' ? '提示词' : '构图'}
          </Tag>
        </Space>
      ),
      filters: [
        { text: 'Doubao', value: 'doubao' },
        { text: 'DALL-E', value: 'dalle' },
        { text: 'Stable Diffusion', value: 'stable_diffusion' },
        { text: 'Midjourney', value: 'midjourney' }
      ]
    },
    {
      title: '提示词预览',
      dataIndex: 'template_prompt',
      key: 'template_prompt',
      ellipsis: true,
      render: (prompt: string) => (
        <Tooltip title={prompt}>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            {prompt.length > 50 ? `${prompt.substring(0, 50)}...` : prompt}
          </Text>
        </Tooltip>
      )
    },
    {
      title: '使用次数',
      dataIndex: 'usage_count',
      key: 'usage_count',
      width: 100,
      render: (count: number) => (
        <Badge count={count} showZero style={{ backgroundColor: '#52c41a' }} />
      ),
      sorter: (a, b) => a.usage_count - b.usage_count
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 120,
      render: (date: string) => (
        <Text type="secondary">
          {new Date(date).toLocaleDateString()}
        </Text>
      ),
      sorter: (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_, record) => (
        <Space>
          <Tooltip title="使用模板生成">
            <Button
              type="primary"
              size="small"
              icon={<ThunderboltOutlined />}
              onClick={() => handleGenerateFromTemplate(record)}
              loading={generationLoading}
            >
              生成
            </Button>
          </Tooltip>
          
          <Tooltip title="查看详情">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => handleViewDetail(record)}
            />
          </Tooltip>

          <Tooltip title="复制提示词">
            <Button
              type="text"
              icon={<CopyOutlined />}
              onClick={() => handleCopyPrompt(record.template_prompt)}
            />
          </Tooltip>

          {showSelector && (
            <Button
              type={selectedTemplateId === record.template_id ? 'primary' : 'default'}
              size="small"
              onClick={() => onTemplateSelect?.(record)}
            >
              {selectedTemplateId === record.template_id ? '已选择' : '选择'}
            </Button>
          )}

          {!showSelector && (
            <>
              <Tooltip title="编辑">
                <Button
                  type="text"
                  icon={<EditOutlined />}
                  onClick={() => handleEdit(record)}
                />
              </Tooltip>

              <Popconfirm
                title="确定要删除这个模板吗？"
                onConfirm={() => handleDelete(record.template_id)}
                okText="确定"
                cancelText="取消"
              >
                <Tooltip title="删除">
                  <Button
                    type="text"
                    icon={<DeleteOutlined />}
                    danger
                  />
                </Tooltip>
              </Popconfirm>
            </>
          )}
        </Space>
      )
    }
  ];

  // 渲染过滤器
  const renderFilters = () => (
    <Row gutter={16} style={{ marginBottom: 16 }}>
      <Col span={6}>
        <Search
          placeholder="搜索模板名称"
          onSearch={(value) => setFilters({ ...filters, search: value })}
          allowClear
        />
      </Col>
      <Col span={4}>
        <Select
          placeholder="平台"
          allowClear
          onChange={(value) => setFilters({ ...filters, platform_type: value })}
          style={{ width: '100%' }}
        >
          <Option value="doubao">Doubao</Option>
          <Option value="dalle">DALL-E</Option>
          <Option value="stable_diffusion">Stable Diffusion</Option>
          <Option value="midjourney">Midjourney</Option>
        </Select>
      </Col>
      <Col span={4}>
        <Select
          placeholder="类型"
          allowClear
          onChange={(value) => setFilters({ ...filters, template_type: value })}
          style={{ width: '100%' }}
        >
          <Option value="style">风格模板</Option>
          <Option value="prompt">提示词模板</Option>
          <Option value="composition">构图模板</Option>
        </Select>
      </Col>
      <Col span={4}>
        <Select
          placeholder="可见性"
          allowClear
          onChange={(value) => setFilters({ ...filters, is_public: value })}
          style={{ width: '100%' }}
        >
          <Option value={true}>公开</Option>
          <Option value={false}>私有</Option>
        </Select>
      </Col>
      <Col span={6}>
        <Space>
          <Button
            icon={<ReloadOutlined />}
            onClick={() => {
              setFilters({});
              loadTemplateList();
            }}
          >
            重置
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
  );

  return (
    <div className={`image-template-manage ${className || ''}`}>
      <Card
        title={
          <Space>
            <BulbOutlined />
            <span>图像模板</span>
            <Badge count={templateList?.total || 0} style={{ backgroundColor: '#52c41a' }} />
          </Space>
        }
        extra={
          !showSelector && (
            <Space>
              <Text type="secondary">智能模板，一键生成</Text>
            </Space>
          )
        }
      >
        {/* 过滤器 */}
        {renderFilters()}

        {/* 模板列表 */}
        <Table
          columns={columns}
          dataSource={templateList?.items || []}
          rowKey="template_id"
          loading={templateListLoading}
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: templateList?.total || 0,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 个模板`,
            onChange: (page, size) => {
              setCurrentPage(page);
              setPageSize(size || 20);
            }
          }}
          rowSelection={showSelector ? {
            type: 'radio',
            selectedRowKeys: selectedTemplateId ? [selectedTemplateId] : [],
            onSelect: (record) => onTemplateSelect?.(record)
          } : undefined}
        />
      </Card>

      {/* 创建模板模态框 */}
      <Modal
        title="创建图像模板"
        open={createModalVisible}
        onOk={handleCreate}
        onCancel={() => setCreateModalVisible(false)}
        confirmLoading={templateCreateLoading}
        width={700}
      >
        <Form form={createForm} layout="vertical">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="template_name"
                label="模板名称"
                rules={[{ required: true, message: '请输入模板名称' }]}
              >
                <Input placeholder="请输入模板名称" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="template_type"
                label="模板类型"
                rules={[{ required: true, message: '请选择模板类型' }]}
              >
                <Select placeholder="选择模板类型">
                  <Option value="style">风格模板</Option>
                  <Option value="prompt">提示词模板</Option>
                  <Option value="composition">构图模板</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="platform_type"
                label="适用平台"
                rules={[{ required: true, message: '请选择适用平台' }]}
              >
                <Select placeholder="选择适用平台">
                  <Option value="doubao">Doubao</Option>
                  <Option value="dalle">DALL-E</Option>
                  <Option value="stable_diffusion">Stable Diffusion</Option>
                  <Option value="midjourney">Midjourney</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="is_public"
                label="公开模板"
                valuePropName="checked"
                initialValue={false}
              >
                <Switch checkedChildren="公开" unCheckedChildren="私有" />
              </Form.Item>
            </Col>
            <Col span={24}>
              <Form.Item
                name="template_prompt"
                label="模板提示词"
                rules={[{ required: true, message: '请输入模板提示词' }]}
              >
                <TextArea
                  placeholder="输入详细的图像生成提示词..."
                  rows={6}
                  showCount
                  maxLength={2000}
                />
              </Form.Item>
            </Col>
            <Col span={24}>
              <Form.Item
                name="template_description"
                label="模板描述"
              >
                <TextArea
                  placeholder="描述模板的用途和特点..."
                  rows={3}
                  maxLength={500}
                />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* 编辑模板模态框 */}
      <Modal
        title="编辑图像模板"
        open={editModalVisible}
        onOk={handleUpdate}
        onCancel={() => setEditModalVisible(false)}
        confirmLoading={templateUpdateLoading}
        width={700}
      >
        <Form form={editForm} layout="vertical">
          <Form.Item name="template_id" hidden>
            <Input />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="template_name"
                label="模板名称"
                rules={[{ required: true, message: '请输入模板名称' }]}
              >
                <Input placeholder="请输入模板名称" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="is_public"
                label="公开模板"
                valuePropName="checked"
              >
                <Switch checkedChildren="公开" unCheckedChildren="私有" />
              </Form.Item>
            </Col>
            <Col span={24}>
              <Form.Item
                name="template_prompt"
                label="模板提示词"
                rules={[{ required: true, message: '请输入模板提示词' }]}
              >
                <TextArea
                  placeholder="输入详细的图像生成提示词..."
                  rows={6}
                  showCount
                  maxLength={2000}
                />
              </Form.Item>
            </Col>
            <Col span={24}>
              <Form.Item
                name="template_description"
                label="模板描述"
              >
                <TextArea
                  placeholder="描述模板的用途和特点..."
                  rows={3}
                  maxLength={500}
                />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* 模板详情抽屉 */}
      <Drawer
        title="模板详情"
        open={detailDrawerVisible}
        onClose={() => setDetailDrawerVisible(false)}
        width={500}
      >
        {currentTemplate && (
          <div>
            <Row gutter={16}>
              <Col span={24}>
                <Card size="small">
                  <Statistic
                    title="模板名称"
                    value={currentTemplate.template_name}
                    prefix={<BulbOutlined />}
                  />
                </Card>
              </Col>
            </Row>

            <Divider />

            <Row gutter={16}>
              <Col span={12}>
                <div>
                  <Text type="secondary">模板类型:</Text>
                  <div>
                    <Tag color="orange">
                      {currentTemplate.template_type === 'style' ? '风格模板' :
                       currentTemplate.template_type === 'prompt' ? '提示词模板' : '构图模板'}
                    </Tag>
                  </div>
                </div>
              </Col>
              <Col span={12}>
                <div>
                  <Text type="secondary">适用平台:</Text>
                  <div><Tag color="blue">{currentTemplate.platform_type.toUpperCase()}</Tag></div>
                </div>
              </Col>
            </Row>

            <Divider />

            <Row gutter={16}>
              <Col span={12}>
                <div>
                  <Text type="secondary">使用次数:</Text>
                  <div><Badge count={currentTemplate.usage_count} style={{ backgroundColor: '#52c41a' }} /></div>
                </div>
              </Col>
              <Col span={12}>
                <div>
                  <Text type="secondary">可见性:</Text>
                  <div>
                    <Badge 
                      status={currentTemplate.is_public ? 'success' : 'default'}
                      text={currentTemplate.is_public ? '公开' : '私有'}
                    />
                  </div>
                </div>
              </Col>
            </Row>

            {currentTemplate.template_description && (
              <>
                <Divider />
                <div>
                  <Text type="secondary">模板描述:</Text>
                  <Paragraph>{currentTemplate.template_description}</Paragraph>
                </div>
              </>
            )}

            <Divider />
            <div>
              <Text type="secondary">模板提示词:</Text>
              <div style={{ 
                marginTop: 8,
                padding: 12,
                background: '#f5f5f5',
                borderRadius: 6,
                fontFamily: 'Monaco, Menlo, monospace',
                fontSize: '12px'
              }}>
                {currentTemplate.template_prompt}
              </div>
              <div style={{ marginTop: 8 }}>
                <Button
                  size="small"
                  icon={<CopyOutlined />}
                  onClick={() => handleCopyPrompt(currentTemplate.template_prompt)}
                >
                  复制提示词
                </Button>
              </div>
            </div>

            {currentTemplate.preview_image_url && (
              <>
                <Divider />
                <div>
                  <Text type="secondary">预览图像:</Text>
                  <div style={{ marginTop: 8 }}>
                    <Image
                      width="100%"
                      src={currentTemplate.preview_image_url}
                      style={{ borderRadius: 6 }}
                    />
                  </div>
                </div>
              </>
            )}

            <Divider />

            <Row gutter={16}>
              <Col span={24}>
                <div>
                  <Text type="secondary">创建时间:</Text>
                  <div>{new Date(currentTemplate.created_at).toLocaleString()}</div>
                </div>
              </Col>
            </Row>

            <Divider />

            <Space style={{ width: '100%', justifyContent: 'center' }}>
              <Button
                type="primary"
                icon={<ThunderboltOutlined />}
                onClick={() => handleGenerateFromTemplate(currentTemplate)}
                loading={generationLoading}
              >
                使用模板生成
              </Button>
              <Button
                icon={<EditOutlined />}
                onClick={() => {
                  setDetailDrawerVisible(false);
                  handleEdit(currentTemplate);
                }}
              >
                编辑模板
              </Button>
            </Space>
          </div>
        )}
      </Drawer>
    </div>
  );
};

export default ImageTemplateManage;