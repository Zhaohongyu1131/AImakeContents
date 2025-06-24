/**
 * Text Content List Component
 * 文本内容列表组件 - [components][text_content][text_content_list]
 */

import React, { useEffect, useState } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Input,
  Select,
  DatePicker,
  Tag,
  Popconfirm,
  Tooltip,
  Modal,
  Typography,
  Row,
  Col,
  Statistic,
  message
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  SearchOutlined,
  FilterOutlined,
  ExportOutlined,
  ReloadOutlined,
  FileTextOutlined,
  BulbOutlined
} from '@ant-design/icons';
import { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';

import { useTextContentStore } from '../../../stores/text_content/text_content_store';
import { textContentApiService } from '../../../services/api/text_content_api';
import type { TextContentBasic } from '../../../services/api/text_content_api';
import { AuthGuard, PermissionGuard } from '../../../router/guards';

const { Search } = Input;
const { RangePicker } = DatePicker;
const { Text, Title, Paragraph } = Typography;
const { Option } = Select;

interface TextContentListProps {
  className?: string;
  onItemClick?: (content: TextContentBasic) => void;
  onItemEdit?: (content: TextContentBasic) => void;
  selectionMode?: boolean;
  onSelectionChange?: (selectedItems: TextContentBasic[]) => void;
}

export const TextContentList: React.FC<TextContentListProps> = ({
  className,
  onItemClick,
  onItemEdit,
  selectionMode = false,
  onSelectionChange
}) => {
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [previewModal, setPreviewModal] = useState<{
    visible: boolean;
    content: TextContentBasic | null;
  }>({ visible: false, content: null });
  const [usageStats, setUsageStats] = useState<any>(null);

  const {
    contentList,
    contentLoading,
    contentError,
    filters,
    pagination,
    text_content_store_load_content_list,
    text_content_store_delete_content,
    text_content_store_batch_delete_content,
    text_content_store_set_filters,
    text_content_store_set_pagination,
    text_content_store_clear_errors
  } = useTextContentStore();

  // 加载数据
  useEffect(() => {
    text_content_store_load_content_list();
    loadUsageStats();
  }, []);

  const loadUsageStats = async () => {
    try {
      const response = await textContentApiService.text_content_api_get_usage_stats('month');
      if (response.success && response.data) {
        setUsageStats(response.data);
      }
    } catch (error) {
      console.error('Failed to load usage stats:', error);
    }
  };

  const handleTableChange = (pagination: any, tableFilters: any, sorter: any) => {
    text_content_store_set_pagination({
      page: pagination.current,
      page_size: pagination.pageSize
    });
    text_content_store_load_content_list();
  };

  const handleSearch = (value: string) => {
    text_content_store_set_filters({ search: value });
    text_content_store_set_pagination({ page: 1 });
    text_content_store_load_content_list();
  };

  const handleFilterChange = (key: string, value: any) => {
    text_content_store_set_filters({ [key]: value });
    text_content_store_set_pagination({ page: 1 });
    text_content_store_load_content_list();
  };

  const handleDateRangeChange = (dates: any) => {
    if (dates && dates.length === 2) {
      text_content_store_set_filters({
        date_from: dates[0].format('YYYY-MM-DD'),
        date_to: dates[1].format('YYYY-MM-DD')
      });
    } else {
      text_content_store_set_filters({
        date_from: undefined,
        date_to: undefined
      });
    }
    text_content_store_set_pagination({ page: 1 });
    text_content_store_load_content_list();
  };

  const handleDelete = async (contentId: number) => {
    const success = await text_content_store_delete_content(contentId);
    if (success) {
      message.success('内容删除成功');
    }
  };

  const handleBatchDelete = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请选择要删除的内容');
      return;
    }

    const success = await text_content_store_batch_delete_content(
      selectedRowKeys as number[]
    );
    
    if (success) {
      setSelectedRowKeys([]);
      message.success(`成功删除 ${selectedRowKeys.length} 个内容`);
    }
  };

  const handlePreview = (content: TextContentBasic) => {
    setPreviewModal({ visible: true, content });
  };

  const handleRowSelection = {
    selectedRowKeys,
    onChange: (keys: React.Key[], selectedRows: TextContentBasic[]) => {
      setSelectedRowKeys(keys);
      if (onSelectionChange) {
        onSelectionChange(selectedRows);
      }
    },
  };

  const getStatusColor = (status: TextContentBasic['content_status']) => {
    switch (status) {
      case 'published': return 'green';
      case 'draft': return 'orange';
      case 'archived': return 'default';
      default: return 'default';
    }
  };

  const getStatusText = (status: TextContentBasic['content_status']) => {
    switch (status) {
      case 'published': return '已发布';
      case 'draft': return '草稿';
      case 'archived': return '已归档';
      default: return status;
    }
  };

  const getContentTypeText = (type: TextContentBasic['content_type']) => {
    switch (type) {
      case 'article': return '文章';
      case 'prompt': return '提示词';
      case 'script': return '脚本';
      case 'description': return '描述';
      default: return type;
    }
  };

  const columns: ColumnsType<TextContentBasic> = [
    {
      title: '标题',
      dataIndex: 'content_title',
      key: 'content_title',
      ellipsis: true,
      render: (title: string, record: TextContentBasic) => (
        <div>
          <Button
            type="link"
            onClick={() => onItemClick?.(record)}
            style={{ padding: 0, height: 'auto' }}
          >
            {title}
          </Button>
          <div style={{ fontSize: '12px', color: '#999', marginTop: '2px' }}>
            {record.content_length} 字符
          </div>
        </div>
      ),
    },
    {
      title: '类型',
      dataIndex: 'content_type',
      key: 'content_type',
      width: 100,
      render: (type: TextContentBasic['content_type']) => (
        <Tag color="blue">{getContentTypeText(type)}</Tag>
      ),
      filters: [
        { text: '文章', value: 'article' },
        { text: '提示词', value: 'prompt' },
        { text: '脚本', value: 'script' },
        { text: '描述', value: 'description' },
      ],
    },
    {
      title: '状态',
      dataIndex: 'content_status',
      key: 'content_status',
      width: 100,
      render: (status: TextContentBasic['content_status']) => (
        <Tag color={getStatusColor(status)}>{getStatusText(status)}</Tag>
      ),
      filters: [
        { text: '已发布', value: 'published' },
        { text: '草稿', value: 'draft' },
        { text: '已归档', value: 'archived' },
      ],
    },
    {
      title: '标签',
      dataIndex: 'content_tags',
      key: 'content_tags',
      width: 200,
      render: (tags: string[]) => (
        <div>
          {tags?.slice(0, 3).map(tag => (
            <Tag key={tag} size="small">{tag}</Tag>
          ))}
          {tags && tags.length > 3 && (
            <Tooltip title={tags.slice(3).join(', ')}>
              <Tag size="small">+{tags.length - 3}</Tag>
            </Tooltip>
          )}
        </div>
      ),
    },
    {
      title: '生成模型',
      dataIndex: 'generation_provider',
      key: 'generation_provider',
      width: 120,
      render: (provider: string, record: TextContentBasic) => {
        if (!provider) return <Text type="secondary">手动创建</Text>;
        
        return (
          <Tooltip title={`模型: ${record.generation_model || 'default'}`}>
            <Tag color={provider === 'doubao' ? 'blue' : provider === 'openai' ? 'green' : 'orange'}>
              {provider.toUpperCase()}
            </Tag>
          </Tooltip>
        );
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (date: string) => (
        <div>
          <div>{dayjs(date).format('MM-DD HH:mm')}</div>
          <Text type="secondary" style={{ fontSize: '11px' }}>
            {dayjs(date).fromNow()}
          </Text>
        </div>
      ),
      sorter: true,
    },
    {
      title: '操作',
      key: 'actions',
      width: 120,
      fixed: 'right',
      render: (_, record: TextContentBasic) => (
        <Space size="small">
          <Tooltip title="预览">
            <Button
              type="text"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => handlePreview(record)}
            />
          </Tooltip>
          
          <PermissionGuard permissions={['text:edit']}>
            <Tooltip title="编辑">
              <Button
                type="text"
                size="small"
                icon={<EditOutlined />}
                onClick={() => onItemEdit?.(record)}
              />
            </Tooltip>
          </PermissionGuard>
          
          <PermissionGuard permissions={['text:delete']}>
            <Popconfirm
              title="确定要删除这个内容吗？"
              onConfirm={() => handleDelete(record.content_id)}
              okText="确定"
              cancelText="取消"
            >
              <Tooltip title="删除">
                <Button
                  type="text"
                  size="small"
                  danger
                  icon={<DeleteOutlined />}
                />
              </Tooltip>
            </Popconfirm>
          </PermissionGuard>
        </Space>
      ),
    },
  ];

  const renderToolbar = () => (
    <div style={{ marginBottom: 16 }}>
      <Row gutter={[16, 16]} align="middle">
        <Col xs={24} sm={12} md={8}>
          <Search
            placeholder="搜索标题或内容..."
            allowClear
            onSearch={handleSearch}
            style={{ width: '100%' }}
          />
        </Col>
        
        <Col xs={24} sm={12} md={8}>
          <Space>
            <Button
              icon={<FilterOutlined />}
              onClick={() => setShowFilters(!showFilters)}
            >
              筛选
            </Button>
            <Button
              icon={<ReloadOutlined />}
              onClick={() => text_content_store_load_content_list()}
              loading={contentLoading}
            >
              刷新
            </Button>
          </Space>
        </Col>
        
        <Col xs={24} sm={24} md={8} style={{ textAlign: 'right' }}>
          <Space>
            {selectedRowKeys.length > 0 && (
              <Popconfirm
                title={`确定要删除选中的 ${selectedRowKeys.length} 个内容吗？`}
                onConfirm={handleBatchDelete}
              >
                <Button danger>
                  删除选中 ({selectedRowKeys.length})
                </Button>
              </Popconfirm>
            )}
            
            <Button icon={<ExportOutlined />}>
              导出
            </Button>
            
            <PermissionGuard permissions={['text:create']}>
              <Button type="primary" icon={<PlusOutlined />}>
                新建内容
              </Button>
            </PermissionGuard>
          </Space>
        </Col>
      </Row>

      {/* 筛选器 */}
      {showFilters && (
        <Card size="small" style={{ marginTop: 16 }}>
          <Row gutter={16}>
            <Col span={6}>
              <Select
                placeholder="内容类型"
                allowClear
                style={{ width: '100%' }}
                value={filters.content_type}
                onChange={(value) => handleFilterChange('content_type', value)}
              >
                <Option value="article">文章</Option>
                <Option value="prompt">提示词</Option>
                <Option value="script">脚本</Option>
                <Option value="description">描述</Option>
              </Select>
            </Col>
            
            <Col span={6}>
              <Select
                placeholder="状态"
                allowClear
                style={{ width: '100%' }}
                value={filters.content_status}
                onChange={(value) => handleFilterChange('content_status', value)}
              >
                <Option value="published">已发布</Option>
                <Option value="draft">草稿</Option>
                <Option value="archived">已归档</Option>
              </Select>
            </Col>
            
            <Col span={12}>
              <RangePicker
                placeholder={['开始日期', '结束日期']}
                style={{ width: '100%' }}
                onChange={handleDateRangeChange}
                value={filters.date_from && filters.date_to ? [
                  dayjs(filters.date_from),
                  dayjs(filters.date_to)
                ] : null}
              />
            </Col>
          </Row>
        </Card>
      )}
    </div>
  );

  const renderStats = () => {
    if (!usageStats) return null;

    return (
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="本月内容总数"
              value={usageStats.total_content_count}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="AI生成次数"
              value={usageStats.total_generation_count}
              prefix={<BulbOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Token使用量"
              value={usageStats.total_tokens_used}
              suffix="tokens"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="主要模型"
              value={Object.keys(usageStats.generation_by_provider || {})[0] || 'N/A'}
              valueStyle={{ fontSize: '16px' }}
            />
          </Card>
        </Col>
      </Row>
    );
  };

  return (
    <div className={`text-content-list ${className || ''}`}>
      {renderStats()}
      
      <Card>
        {renderToolbar()}
        
        <Table
          columns={columns}
          dataSource={contentList?.items || []}
          loading={contentLoading}
          rowKey="content_id"
          rowSelection={selectionMode ? handleRowSelection : undefined}
          pagination={{
            current: contentList?.pagination.page || 1,
            pageSize: contentList?.pagination.page_size || 20,
            total: contentList?.pagination.total || 0,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
          }}
          onChange={handleTableChange}
          scroll={{ x: 1200 }}
        />
      </Card>

      {/* 预览模态框 */}
      <Modal
        title={previewModal.content?.content_title}
        open={previewModal.visible}
        onCancel={() => setPreviewModal({ visible: false, content: null })}
        footer={null}
        width={800}
      >
        {previewModal.content && (
          <div>
            <div style={{ marginBottom: 16 }}>
              <Space>
                <Tag color="blue">
                  {getContentTypeText(previewModal.content.content_type)}
                </Tag>
                <Tag color={getStatusColor(previewModal.content.content_status)}>
                  {getStatusText(previewModal.content.content_status)}
                </Tag>
                <Text type="secondary">
                  {previewModal.content.content_length} 字符
                </Text>
              </Space>
            </div>
            
            <Paragraph style={{ 
              whiteSpace: 'pre-wrap',
              minHeight: '300px',
              maxHeight: '500px',
              overflow: 'auto',
              padding: '16px',
              background: '#f5f5f5',
              borderRadius: '6px'
            }}>
              {previewModal.content.content_body}
            </Paragraph>
            
            {previewModal.content.content_tags && previewModal.content.content_tags.length > 0 && (
              <div style={{ marginTop: 16 }}>
                <Text strong>标签：</Text>
                {previewModal.content.content_tags.map(tag => (
                  <Tag key={tag}>{tag}</Tag>
                ))}
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default TextContentList;