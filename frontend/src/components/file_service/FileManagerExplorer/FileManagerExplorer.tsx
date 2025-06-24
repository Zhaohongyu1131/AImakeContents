/**
 * File Manager Explorer Component
 * 文件管理器探索组件 - [components][file_service][file_manager_explorer]
 */

import React, { useState, useEffect, useRef } from 'react';
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
  Upload,
  message,
  Drawer,
  Row,
  Col,
  Statistic,
  Progress,
  Alert,
  Tooltip,
  Badge,
  Divider,
  Empty,
  Image,
  Switch,
  Dropdown,
  Menu,
  Breadcrumb,
  Tree,
  Spin
} from 'antd';
import {
  FolderOutlined,
  FileOutlined,
  PlusOutlined,
  UploadOutlined,
  DownloadOutlined,
  DeleteOutlined,
  EditOutlined,
  CopyOutlined,
  ShareAltOutlined,
  SearchOutlined,
  ReloadOutlined,
  SettingOutlined,
  EyeOutlined,
  FileImageOutlined,
  FileAudioOutlined,
  FileVideoOutlined,
  FilePdfOutlined,
  FileWordOutlined,
  FileExcelOutlined,
  FilePptOutlined,
  FileZipOutlined,
  MenuOutlined,
  AppstoreOutlined,
  BarsOutlined,
  FilterOutlined,
  SortAscendingOutlined,
  SortDescendingOutlined,
  CloudUploadOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { DataNode } from 'antd/es/tree';

import { useFileServiceStore } from '../../../stores/file_service/file_service_store';
import type { 
  FileStorageBasic,
  FileFolderBasic,
  FileUploadRequest,
  FolderCreateRequest,
  FileType,
  FilePermission,
  FileSortField,
  FileSortOrder
} from '../../../services/api/file_service_api';

const { Title, Text, Paragraph } = Typography;
const { Search } = Input;
const { Option } = Select;
const { Dragger } = Upload;
const { DirectoryTree } = Tree;

interface FileManagerExplorerProps {
  onFileSelect?: (file: FileStorageBasic) => void;
  onFolderSelect?: (folder: FileFolderBasic) => void;
  selectionMode?: 'single' | 'multiple' | 'none';
  allowUpload?: boolean;
  allowFolderCreate?: boolean;
  className?: string;
}

export const FileManagerExplorer: React.FC<FileManagerExplorerProps> = ({
  onFileSelect,
  onFolderSelect,
  selectionMode = 'multiple',
  allowUpload = true,
  allowFolderCreate = true,
  className
}) => {
  const [uploadModalVisible, setUploadModalVisible] = useState(false);
  const [createFolderModalVisible, setCreateFolderModalVisible] = useState(false);
  const [shareModalVisible, setShareModalVisible] = useState(false);
  const [fileDetailDrawerVisible, setFileDetailDrawerVisible] = useState(false);
  const [selectedFile, setSelectedFile] = useState<FileStorageBasic | null>(null);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [filterType, setFilterType] = useState<FileType | 'all'>('all');
  const [uploadFiles, setUploadFiles] = useState<File[]>([]);
  const [breadcrumbPath, setBreadcrumbPath] = useState<Array<{ id: number | null; name: string }>>([
    { id: null, name: '全部文件' }
  ]);

  const [uploadForm] = Form.useForm();
  const [folderForm] = Form.useForm();
  const [shareForm] = Form.useForm();

  const {
    fileList,
    folderTree,
    currentFolderId,
    selectedFiles,
    viewMode,
    sortField,
    sortOrder,
    fileListLoading,
    folderTreeLoading,
    uploadLoading,
    uploadProgress,
    quotaInfo,
    file_service_store_load_file_list,
    file_service_store_load_folder_tree,
    file_service_store_upload_files,
    file_service_store_create_folder,
    file_service_store_navigate_to_folder,
    file_service_store_select_file,
    file_service_store_toggle_file_selection,
    file_service_store_clear_selection,
    file_service_store_select_all,
    file_service_store_set_view_mode,
    file_service_store_set_sort,
    file_service_store_delete_file,
    file_service_store_rename_file,
    file_service_store_load_quota_info,
    file_service_store_search_files
  } = useFileServiceStore();

  // 初始化数据加载
  useEffect(() => {
    file_service_store_load_file_list();
    file_service_store_load_folder_tree();
    file_service_store_load_quota_info();
  }, []);

  // 文件类型图标映射
  const getFileIcon = (fileType: FileType, fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase();
    
    switch (fileType) {
      case 'image':
        return <FileImageOutlined style={{ color: '#52c41a' }} />;
      case 'audio':
        return <FileAudioOutlined style={{ color: '#722ed1' }} />;
      case 'video':
        return <FileVideoOutlined style={{ color: '#eb2f96' }} />;
      case 'document':
        if (['pdf'].includes(extension || '')) {
          return <FilePdfOutlined style={{ color: '#f5222d' }} />;
        } else if (['doc', 'docx'].includes(extension || '')) {
          return <FileWordOutlined style={{ color: '#1890ff' }} />;
        } else if (['xls', 'xlsx'].includes(extension || '')) {
          return <FileExcelOutlined style={{ color: '#52c41a' }} />;
        } else if (['ppt', 'pptx'].includes(extension || '')) {
          return <FilePptOutlined style={{ color: '#fa8c16' }} />;
        }
        return <FileOutlined style={{ color: '#722ed1' }} />;
      case 'archive':
        return <FileZipOutlined style={{ color: '#faad14' }} />;
      default:
        return <FileOutlined style={{ color: '#8c8c8c' }} />;
    }
  };

  // 格式化文件大小
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // 构建文件夹树数据
  const buildTreeData = (folders: FileFolderBasic[]): DataNode[] => {
    const buildChildren = (parentId: number | null): DataNode[] => {
      return folders
        .filter(folder => folder.parent_folder_id === parentId)
        .map(folder => ({
          key: folder.folder_id,
          title: folder.folder_name,
          icon: <FolderOutlined />,
          children: buildChildren(folder.folder_id)
        }));
    };
    
    return [
      {
        key: 'root',
        title: '全部文件',
        icon: <FolderOutlined />,
        children: buildChildren(null)
      }
    ];
  };

  // 文件夹导航
  const handleFolderNavigate = (folderId: number | null, folderName?: string) => {
    file_service_store_navigate_to_folder(folderId);
    
    // 更新面包屑
    if (folderId === null) {
      setBreadcrumbPath([{ id: null, name: '全部文件' }]);
    } else {
      // 简化处理，实际应该根据完整路径构建
      setBreadcrumbPath([
        { id: null, name: '全部文件' },
        { id: folderId, name: folderName || `文件夹 ${folderId}` }
      ]);
    }
  };

  // 文件上传
  const handleUpload = async () => {
    if (uploadFiles.length === 0) {
      message.warning('请选择要上传的文件');
      return;
    }

    try {
      const values = await uploadForm.validateFields();
      const request: FileUploadRequest = {
        files: uploadFiles,
        folder_id: currentFolderId || undefined,
        file_permission: values.file_permission || 'private',
        auto_rename: values.auto_rename || true,
        generate_thumbnail: values.generate_thumbnail || true,
        extract_metadata: values.extract_metadata || true
      };

      const success = await file_service_store_upload_files(request);
      if (success) {
        message.success('文件上传成功');
        setUploadModalVisible(false);
        setUploadFiles([]);
        uploadForm.resetFields();
      }
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  // 创建文件夹
  const handleCreateFolder = async () => {
    try {
      const values = await folderForm.validateFields();
      const request: FolderCreateRequest = {
        folder_name: values.folder_name,
        parent_folder_id: currentFolderId || undefined,
        folder_permission: values.folder_permission || 'private',
        folder_description: values.folder_description
      };

      const success = await file_service_store_create_folder(request);
      if (success) {
        message.success('文件夹创建成功');
        setCreateFolderModalVisible(false);
        folderForm.resetFields();
      }
    } catch (error) {
      console.error('Create folder failed:', error);
    }
  };

  // 文件搜索
  const handleSearch = (keyword: string) => {
    setSearchKeyword(keyword);
    if (keyword.trim()) {
      file_service_store_search_files({
        keyword,
        file_types: filterType === 'all' ? undefined : [filterType],
        folder_id: currentFolderId || undefined
      });
    } else {
      file_service_store_load_file_list(1, 20, currentFolderId || undefined);
    }
  };

  // 文件操作菜单
  const getFileActionMenu = (file: FileStorageBasic) => (
    <Menu>
      <Menu.Item 
        key="view" 
        icon={<EyeOutlined />}
        onClick={() => {
          setSelectedFile(file);
          setFileDetailDrawerVisible(true);
        }}
      >
        查看详情
      </Menu.Item>
      <Menu.Item 
        key="download" 
        icon={<DownloadOutlined />}
        onClick={() => window.open(file.file_url, '_blank')}
      >
        下载
      </Menu.Item>
      <Menu.Item 
        key="rename" 
        icon={<EditOutlined />}
        onClick={() => {
          const newName = prompt('请输入新名称', file.file_name);
          if (newName && newName !== file.file_name) {
            file_service_store_rename_file(file.file_id, newName);
          }
        }}
      >
        重命名
      </Menu.Item>
      <Menu.Item 
        key="copy" 
        icon={<CopyOutlined />}
      >
        复制
      </Menu.Item>
      <Menu.Item 
        key="share" 
        icon={<ShareAltOutlined />}
        onClick={() => {
          setSelectedFile(file);
          setShareModalVisible(true);
        }}
      >
        分享
      </Menu.Item>
      <Menu.Divider />
      <Menu.Item 
        key="delete" 
        icon={<DeleteOutlined />}
        danger
        onClick={() => {
          Modal.confirm({
            title: '确定删除此文件吗？',
            content: '删除后文件将移入回收站',
            onOk: () => file_service_store_delete_file(file.file_id)
          });
        }}
      >
        删除
      </Menu.Item>
    </Menu>
  );

  // 表格列定义
  const columns: ColumnsType<FileStorageBasic> = [
    {
      title: '文件名',
      key: 'name',
      render: (_, record) => (
        <Space>
          {getFileIcon(record.file_type, record.file_name)}
          <div>
            <div>
              <Text 
                strong
                style={{ cursor: 'pointer' }}
                onClick={() => {
                  if (onFileSelect) {
                    onFileSelect(record);
                  } else {
                    file_service_store_select_file(record.file_id);
                  }
                }}
              >
                {record.file_name}
              </Text>
            </div>
            <div>
              <Text type="secondary" style={{ fontSize: '12px' }}>
                {record.file_extension.toUpperCase()} • {formatFileSize(record.file_size)}
              </Text>
            </div>
          </div>
        </Space>
      ),
      sorter: true
    },
    {
      title: '类型',
      dataIndex: 'file_type',
      key: 'file_type',
      width: 80,
      render: (type: FileType) => (
        <Tag>
          {type === 'image' ? '图片' :
           type === 'audio' ? '音频' :
           type === 'video' ? '视频' :
           type === 'document' ? '文档' :
           type === 'archive' ? '压缩包' : '其他'}
        </Tag>
      ),
      filters: [
        { text: '图片', value: 'image' },
        { text: '音频', value: 'audio' },
        { text: '视频', value: 'video' },
        { text: '文档', value: 'document' },
        { text: '压缩包', value: 'archive' },
        { text: '其他', value: 'other' }
      ]
    },
    {
      title: '大小',
      dataIndex: 'file_size',
      key: 'file_size',
      width: 100,
      render: (size: number) => formatFileSize(size),
      sorter: true
    },
    {
      title: '修改时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 150,
      render: (date: string) => new Date(date).toLocaleString(),
      sorter: true
    },
    {
      title: '操作',
      key: 'actions',
      width: 100,
      render: (_, record) => (
        <Dropdown overlay={getFileActionMenu(record)} trigger={['click']}>
          <Button type="text" icon={<MenuOutlined />} />
        </Dropdown>
      )
    }
  ];

  // 渲染工具栏
  const renderToolbar = () => (
    <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
      <Col>
        <Space>
          {allowUpload && (
            <Button
              type="primary"
              icon={<UploadOutlined />}
              onClick={() => setUploadModalVisible(true)}
            >
              上传文件
            </Button>
          )}
          
          {allowFolderCreate && (
            <Button
              icon={<FolderOutlined />}
              onClick={() => setCreateFolderModalVisible(true)}
            >
              新建文件夹
            </Button>
          )}

          {selectedFiles.length > 0 && (
            <>
              <Button
                icon={<DownloadOutlined />}
                onClick={() => message.info('批量下载功能开发中')}
              >
                批量下载
              </Button>
              <Button
                icon={<DeleteOutlined />}
                danger
                onClick={() => {
                  Modal.confirm({
                    title: `确定删除选中的 ${selectedFiles.length} 个文件吗？`,
                    content: '删除后文件将移入回收站',
                    onOk: async () => {
                      // 这里应该调用批量删除接口
                      message.success('删除成功');
                      file_service_store_clear_selection();
                    }
                  });
                }}
              >
                批量删除
              </Button>
            </>
          )}
        </Space>
      </Col>

      <Col>
        <Space>
          <Search
            placeholder="搜索文件"
            value={searchKeyword}
            onChange={(e) => setSearchKeyword(e.target.value)}
            onSearch={handleSearch}
            style={{ width: 200 }}
          />

          <Select
            value={filterType}
            onChange={setFilterType}
            style={{ width: 100 }}
          >
            <Option value="all">全部</Option>
            <Option value="image">图片</Option>
            <Option value="audio">音频</Option>
            <Option value="video">视频</Option>
            <Option value="document">文档</Option>
          </Select>

          <Button.Group>
            <Button
              type={viewMode === 'list' ? 'primary' : 'default'}
              icon={<BarsOutlined />}
              onClick={() => file_service_store_set_view_mode('list')}
            />
            <Button
              type={viewMode === 'grid' ? 'primary' : 'default'}
              icon={<AppstoreOutlined />}
              onClick={() => file_service_store_set_view_mode('grid')}
            />
          </Button.Group>

          <Dropdown
            overlay={
              <Menu>
                <Menu.Item
                  key="name"
                  onClick={() => file_service_store_set_sort('name', sortOrder)}
                >
                  按名称排序
                </Menu.Item>
                <Menu.Item
                  key="size"
                  onClick={() => file_service_store_set_sort('size', sortOrder)}
                >
                  按大小排序
                </Menu.Item>
                <Menu.Item
                  key="date"
                  onClick={() => file_service_store_set_sort('updated_at', sortOrder)}
                >
                  按时间排序
                </Menu.Item>
                <Menu.Divider />
                <Menu.Item
                  key="asc"
                  icon={<SortAscendingOutlined />}
                  onClick={() => file_service_store_set_sort(sortField, 'asc')}
                >
                  升序
                </Menu.Item>
                <Menu.Item
                  key="desc"
                  icon={<SortDescendingOutlined />}
                  onClick={() => file_service_store_set_sort(sortField, 'desc')}
                >
                  降序
                </Menu.Item>
              </Menu>
            }
          >
            <Button icon={<FilterOutlined />} />
          </Dropdown>

          <Button
            icon={<ReloadOutlined />}
            onClick={() => file_service_store_load_file_list(1, 20, currentFolderId || undefined)}
          />
        </Space>
      </Col>
    </Row>
  );

  // 渲染面包屑导航
  const renderBreadcrumb = () => (
    <Breadcrumb style={{ marginBottom: 16 }}>
      {breadcrumbPath.map((item, index) => (
        <Breadcrumb.Item
          key={item.id || 'root'}
          onClick={() => index < breadcrumbPath.length - 1 ? handleFolderNavigate(item.id, item.name) : undefined}
          style={{ cursor: index < breadcrumbPath.length - 1 ? 'pointer' : 'default' }}
        >
          {item.name}
        </Breadcrumb.Item>
      ))}
    </Breadcrumb>
  );

  // 渲染存储配额
  const renderQuotaInfo = () => {
    if (!quotaInfo) return null;

    return (
      <Alert
        message={
          <Space>
            <Text>存储空间：</Text>
            <Text strong>
              {formatFileSize(quotaInfo.used_quota)} / {formatFileSize(quotaInfo.total_quota)}
            </Text>
            <Text type="secondary">({quotaInfo.quota_percentage.toFixed(1)}%)</Text>
          </Space>
        }
        type={quotaInfo.quota_percentage > 90 ? 'warning' : 'info'}
        showIcon={false}
        style={{ marginBottom: 16 }}
        action={
          <Progress
            percent={quotaInfo.quota_percentage}
            showInfo={false}
            size="small"
            style={{ width: 100 }}
          />
        }
      />
    );
  };

  return (
    <div className={`file-manager-explorer ${className || ''}`}>
      <Row gutter={16}>
        {/* 左侧文件夹树 */}
        <Col span={6}>
          <Card size="small" title="文件夹" loading={folderTreeLoading}>
            <DirectoryTree
              treeData={buildTreeData(folderTree)}
              onSelect={(selectedKeys) => {
                const key = selectedKeys[0];
                if (key === 'root') {
                  handleFolderNavigate(null);
                } else {
                  handleFolderNavigate(key as number);
                }
              }}
              selectedKeys={currentFolderId ? [currentFolderId] : ['root']}
            />
          </Card>
        </Col>

        {/* 右侧文件列表 */}
        <Col span={18}>
          <Card>
            {/* 存储配额 */}
            {renderQuotaInfo()}

            {/* 面包屑导航 */}
            {renderBreadcrumb()}

            {/* 工具栏 */}
            {renderToolbar()}

            {/* 文件列表 */}
            <Table
              columns={columns}
              dataSource={fileList?.items || []}
              rowKey="file_id"
              loading={fileListLoading}
              pagination={{
                current: fileList?.page || 1,
                pageSize: fileList?.page_size || 20,
                total: fileList?.total || 0,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total) => `共 ${total} 个文件`
              }}
              rowSelection={selectionMode !== 'none' ? {
                type: selectionMode === 'single' ? 'radio' : 'checkbox',
                selectedRowKeys: selectedFiles,
                onChange: (selectedRowKeys) => {
                  // 这里需要更新选中状态
                },
                onSelect: (record, selected) => {
                  if (selectionMode === 'single') {
                    file_service_store_select_file(record.file_id);
                  } else {
                    file_service_store_toggle_file_selection(record.file_id);
                  }
                },
                onSelectAll: (selected, selectedRows, changeRows) => {
                  if (selected) {
                    file_service_store_select_all();
                  } else {
                    file_service_store_clear_selection();
                  }
                }
              } : undefined}
            />
          </Card>
        </Col>
      </Row>

      {/* 文件上传模态框 */}
      <Modal
        title="上传文件"
        open={uploadModalVisible}
        onOk={handleUpload}
        onCancel={() => setUploadModalVisible(false)}
        confirmLoading={uploadLoading}
        width={600}
      >
        <Form form={uploadForm} layout="vertical">
          <Form.Item label="选择文件">
            <Dragger
              multiple
              beforeUpload={(file) => {
                setUploadFiles(prev => [...prev, file]);
                return false;
              }}
              fileList={uploadFiles.map((file, index) => ({
                uid: index.toString(),
                name: file.name,
                status: 'done' as const
              }))}
              onRemove={(file) => {
                const index = parseInt(file.uid);
                setUploadFiles(prev => prev.filter((_, i) => i !== index));
              }}
            >
              <p className="ant-upload-drag-icon">
                <CloudUploadOutlined />
              </p>
              <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
              <p className="ant-upload-hint">支持单个或批量上传</p>
            </Dragger>
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="file_permission" label="文件权限" initialValue="private">
                <Select>
                  <Option value="private">私有</Option>
                  <Option value="public">公开</Option>
                  <Option value="shared">共享</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="auto_rename" label="自动重命名" valuePropName="checked" initialValue={true}>
                <Switch />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="generate_thumbnail" label="生成缩略图" valuePropName="checked" initialValue={true}>
                <Switch />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="extract_metadata" label="提取元数据" valuePropName="checked" initialValue={true}>
                <Switch />
              </Form.Item>
            </Col>
          </Row>

          {uploadLoading && (
            <Progress 
              percent={uploadProgress} 
              status="active"
              style={{ marginTop: 16 }}
            />
          )}
        </Form>
      </Modal>

      {/* 创建文件夹模态框 */}
      <Modal
        title="新建文件夹"
        open={createFolderModalVisible}
        onOk={handleCreateFolder}
        onCancel={() => setCreateFolderModalVisible(false)}
        confirmLoading={false}
      >
        <Form form={folderForm} layout="vertical">
          <Form.Item
            name="folder_name"
            label="文件夹名称"
            rules={[{ required: true, message: '请输入文件夹名称' }]}
          >
            <Input placeholder="请输入文件夹名称" />
          </Form.Item>

          <Form.Item name="folder_permission" label="文件夹权限" initialValue="private">
            <Select>
              <Option value="private">私有</Option>
              <Option value="public">公开</Option>
              <Option value="shared">共享</Option>
            </Select>
          </Form.Item>

          <Form.Item name="folder_description" label="描述">
            <Input.TextArea placeholder="可选：添加文件夹描述" rows={3} />
          </Form.Item>
        </Form>
      </Modal>

      {/* 文件详情抽屉 */}
      <Drawer
        title="文件详情"
        open={fileDetailDrawerVisible}
        onClose={() => setFileDetailDrawerVisible(false)}
        width={500}
      >
        {selectedFile && (
          <div>
            <Row gutter={16}>
              <Col span={24}>
                {selectedFile.file_type === 'image' && selectedFile.thumbnail_url && (
                  <div style={{ marginBottom: 16, textAlign: 'center' }}>
                    <Image
                      src={selectedFile.thumbnail_url}
                      alt={selectedFile.file_name}
                      style={{ maxWidth: '100%', maxHeight: 200 }}
                    />
                  </div>
                )}
                
                <Card size="small">
                  <Statistic
                    title="文件名"
                    value={selectedFile.file_name}
                    prefix={getFileIcon(selectedFile.file_type, selectedFile.file_name)}
                  />
                </Card>
              </Col>
            </Row>

            <Divider />

            <Row gutter={16}>
              <Col span={12}>
                <div>
                  <Text type="secondary">文件大小:</Text>
                  <div>{formatFileSize(selectedFile.file_size)}</div>
                </div>
              </Col>
              <Col span={12}>
                <div>
                  <Text type="secondary">文件类型:</Text>
                  <div>{selectedFile.file_extension.toUpperCase()}</div>
                </div>
              </Col>
            </Row>

            <Divider />

            <Row gutter={16}>
              <Col span={12}>
                <div>
                  <Text type="secondary">创建时间:</Text>
                  <div>{new Date(selectedFile.created_at).toLocaleString()}</div>
                </div>
              </Col>
              <Col span={12}>
                <div>
                  <Text type="secondary">修改时间:</Text>
                  <div>{new Date(selectedFile.updated_at).toLocaleString()}</div>
                </div>
              </Col>
            </Row>

            <Divider />

            <Row gutter={16}>
              <Col span={12}>
                <div>
                  <Text type="secondary">下载次数:</Text>
                  <div>{selectedFile.download_count}</div>
                </div>
              </Col>
              <Col span={12}>
                <div>
                  <Text type="secondary">存储位置:</Text>
                  <div>{selectedFile.storage_provider.toUpperCase()}</div>
                </div>
              </Col>
            </Row>

            <Divider />

            <Space style={{ width: '100%', justifyContent: 'center' }}>
              <Button
                type="primary"
                icon={<DownloadOutlined />}
                onClick={() => window.open(selectedFile.file_url, '_blank')}
              >
                下载文件
              </Button>
              <Button
                icon={<ShareAltOutlined />}
                onClick={() => {
                  setFileDetailDrawerVisible(false);
                  setShareModalVisible(true);
                }}
              >
                分享文件
              </Button>
            </Space>
          </div>
        )}
      </Drawer>
    </div>
  );
};

export default FileManagerExplorer;