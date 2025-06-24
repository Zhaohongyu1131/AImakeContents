/**
 * File Service Workspace Page
 * 文件服务工作台页面 - [pages][file_service][file_service_workspace]
 */

import React, { useState, useEffect } from 'react';
import {
  Layout,
  Menu,
  Card,
  Button,
  Space,
  Typography,
  Tabs,
  Row,
  Col,
  Statistic,
  Badge,
  Divider,
  Alert,
  Progress,
  Tag,
  Avatar,
  List,
  Empty,
  Table,
  Modal,
  Form,
  Input,
  message,
  Upload,
  Tooltip
} from 'antd';
import {
  FolderOutlined,
  FileOutlined,
  CloudUploadOutlined,
  DownloadOutlined,
  ShareAltOutlined,
  DeleteOutlined,
  BarChartOutlined,
  SettingOutlined,
  RecycleOutlined,
  SearchOutlined,
  PlusOutlined,
  StarOutlined,
  HistoryOutlined,
  SecurityScanOutlined,
  CopyOutlined,
  HddOutlined,
  TeamOutlined,
  SafetyOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

import { useFileServiceStore } from '../../stores/file_service/file_service_store';
import { useAuthStore } from '../../stores/auth/auth_store';
import {
  FileManagerExplorer
} from '../../components/file_service';
import type { 
  FileStorageBasic, 
  TrashFileBasic,
  FileShareResponse
} from '../../services/api/file_service_api';
import { AuthGuard, PermissionGuard } from '../../router/guards';

const { Sider, Content } = Layout;
const { Title, Text } = Typography;
const { TabPane } = Tabs;

type WorkspaceMode = 'explorer' | 'recent' | 'shared' | 'trash' | 'analytics' | 'settings';

interface FileServiceWorkspaceProps {
  className?: string;
}

export const FileServiceWorkspace: React.FC<FileServiceWorkspaceProps> = ({
  className
}) => {
  const [currentMode, setCurrentMode] = useState<WorkspaceMode>('explorer');
  const [siderCollapsed, setSiderCollapsed] = useState(false);
  const [sharePasswordModalVisible, setSharePasswordModalVisible] = useState(false);
  const [selectedShareId, setSelectedShareId] = useState<string>('');

  const [sharePasswordForm] = Form.useForm();

  const {
    storageStats,
    quotaInfo,
    trashList,
    shareList,
    duplicateFiles,
    file_service_store_load_storage_stats,
    file_service_store_load_quota_info,
    file_service_store_load_trash_list,
    file_service_store_load_share_list,
    file_service_store_restore_file,
    file_service_store_permanent_delete,
    file_service_store_empty_trash,
    file_service_store_cancel_share,
    file_service_store_detect_duplicates,
    file_service_store_get_share_detail
  } = useFileServiceStore();

  const { userInfo } = useAuthStore();

  // 初始化数据加载
  useEffect(() => {
    file_service_store_load_storage_stats('month');
    file_service_store_load_quota_info();
    
    if (currentMode === 'trash') {
      file_service_store_load_trash_list();
    } else if (currentMode === 'shared') {
      file_service_store_load_share_list();
    }
  }, [currentMode]);

  // 格式化文件大小
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleModeChange = (mode: WorkspaceMode) => {
    setCurrentMode(mode);
  };

  // 访问分享文件
  const handleAccessShare = async (shareId: string, requirePassword: boolean = false) => {
    if (requirePassword) {
      setSelectedShareId(shareId);
      setSharePasswordModalVisible(true);
    } else {
      try {
        const result = await file_service_store_get_share_detail(shareId);
        if (result) {
          message.success('分享文件加载成功');
          // 这里可以显示分享的文件列表
        }
      } catch (error) {
        message.error('访问分享失败');
      }
    }
  };

  // 输入密码访问分享
  const handleSharePasswordSubmit = async () => {
    try {
      const values = await sharePasswordForm.validateFields();
      const result = await file_service_store_get_share_detail(selectedShareId, values.password);
      if (result) {
        message.success('分享文件加载成功');
        setSharePasswordModalVisible(false);
        sharePasswordForm.resetFields();
      }
    } catch (error) {
      message.error('密码错误或分享已失效');
    }
  };

  const menuItems = [
    {
      key: 'explorer',
      icon: <FolderOutlined />,
      label: '文件管理',
      permission: 'file:read'
    },
    {
      key: 'recent',
      icon: <HistoryOutlined />,
      label: '最近使用',
      permission: 'file:read'
    },
    {
      key: 'shared',
      icon: <ShareAltOutlined />,
      label: '我的分享',
      permission: 'file:share'
    },
    {
      key: 'trash',
      icon: <RecycleOutlined />,
      label: '回收站',
      permission: 'file:delete'
    },
    {
      key: 'analytics',
      icon: <BarChartOutlined />,
      label: '存储分析',
      permission: 'file:analytics'
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '设置',
      permission: 'file:settings'
    }
  ];

  // 渲染侧边栏
  const renderSider = () => (
    <Sider
      collapsible
      collapsed={siderCollapsed}
      onCollapse={setSiderCollapsed}
      theme="light"
      width={220}
      style={{ 
        borderRight: '1px solid #f0f0f0',
        background: '#fafafa'
      }}
    >
      <div style={{ padding: '16px', textAlign: 'center' }}>
        <HddOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
        {!siderCollapsed && (
          <div style={{ marginTop: '8px' }}>
            <Text strong>文件中心</Text>
          </div>
        )}
      </div>
      
      <Menu
        mode="inline"
        selectedKeys={[currentMode]}
        style={{ border: 'none', background: 'transparent' }}
      >
        {menuItems.map(item => (
          <PermissionGuard key={item.key} permissions={[item.permission]} fallback={null}>
            <Menu.Item
              key={item.key}
              icon={item.icon}
              onClick={() => handleModeChange(item.key as WorkspaceMode)}
            >
              {item.label}
            </Menu.Item>
          </PermissionGuard>
        ))}
      </Menu>

      {/* 存储配额显示 */}
      {!siderCollapsed && quotaInfo && (
        <div style={{ padding: '16px', marginTop: '16px' }}>
          <Divider />
          <div style={{ textAlign: 'center' }}>
            <Statistic
              title="已用空间"
              value={quotaInfo.quota_percentage}
              suffix="%"
              valueStyle={{ fontSize: '16px' }}
            />
            <Progress
              percent={quotaInfo.quota_percentage}
              size="small"
              style={{ marginTop: '8px' }}
              strokeColor={quotaInfo.quota_percentage > 90 ? '#ff4d4f' : '#1890ff'}
            />
            <Text type="secondary" style={{ fontSize: '12px' }}>
              {formatFileSize(quotaInfo.used_quota)} / {formatFileSize(quotaInfo.total_quota)}
            </Text>
          </div>
        </div>
      )}
    </Sider>
  );

  // 回收站列表列定义
  const trashColumns: ColumnsType<TrashFileBasic> = [
    {
      title: '文件名',
      dataIndex: 'file_name',
      key: 'file_name',
      render: (name: string, record) => (
        <Space>
          <FileOutlined />
          <div>
            <div>{name}</div>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              原路径: {record.original_path}
            </Text>
          </div>
        </Space>
      )
    },
    {
      title: '文件大小',
      dataIndex: 'file_size',
      key: 'file_size',
      width: 120,
      render: (size: number) => formatFileSize(size)
    },
    {
      title: '删除时间',
      dataIndex: 'deleted_at',
      key: 'deleted_at',
      width: 180,
      render: (date: string) => new Date(date).toLocaleString()
    },
    {
      title: '自动删除时间',
      dataIndex: 'auto_delete_at',
      key: 'auto_delete_at',
      width: 180,
      render: (date: string) => new Date(date).toLocaleString()
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button
            size="small"
            onClick={() => file_service_store_restore_file(record.trash_id)}
          >
            恢复
          </Button>
          <Button
            size="small"
            danger
            onClick={() => {
              Modal.confirm({
                title: '确定永久删除此文件吗？',
                content: '永久删除后无法恢复',
                onOk: () => file_service_store_permanent_delete(record.trash_id)
              });
            }}
          >
            永久删除
          </Button>
        </Space>
      )
    }
  ];

  // 分享列表列定义
  const shareColumns: ColumnsType<FileShareResponse & { file_names: string[]; file_count: number }> = [
    {
      title: '分享内容',
      key: 'content',
      render: (_, record) => (
        <div>
          <div>{record.file_count > 1 ? `${record.file_count} 个文件` : record.file_names[0]}</div>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            分享码: {record.share_code}
          </Text>
        </div>
      )
    },
    {
      title: '访问次数',
      dataIndex: 'access_count',
      key: 'access_count',
      width: 100
    },
    {
      title: '下载次数',
      dataIndex: 'download_count',
      key: 'download_count',
      width: 100
    },
    {
      title: '到期时间',
      dataIndex: 'expire_time',
      key: 'expire_time',
      width: 180,
      render: (date: string) => date ? new Date(date).toLocaleString() : '永不过期'
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => new Date(date).toLocaleString()
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button
            size="small"
            onClick={() => {
              navigator.clipboard.writeText(record.share_url);
              message.success('分享链接已复制');
            }}
          >
            复制链接
          </Button>
          <Button
            size="small"
            danger
            onClick={() => {
              Modal.confirm({
                title: '确定取消此分享吗？',
                onOk: () => file_service_store_cancel_share(record.share_id)
              });
            }}
          >
            取消分享
          </Button>
        </Space>
      )
    }
  ];

  // 渲染主要内容区
  const renderContent = () => {
    switch (currentMode) {
      case 'explorer':
        return (
          <AuthGuard requirePermissions={['file:read']}>
            <div>
              <div style={{ marginBottom: '24px' }}>
                <Title level={3}>
                  <FolderOutlined /> 文件管理
                </Title>
                <Text type="secondary">
                  管理您的所有文件和文件夹
                </Text>
              </div>
              
              <FileManagerExplorer />
            </div>
          </AuthGuard>
        );

      case 'recent':
        return (
          <AuthGuard requirePermissions={['file:read']}>
            <div>
              <div style={{ marginBottom: '24px' }}>
                <Title level={3}>
                  <HistoryOutlined /> 最近使用
                </Title>
                <Text type="secondary">
                  查看最近访问和编辑的文件
                </Text>
              </div>
              
              <Card>
                <Empty description="最近使用功能开发中" />
              </Card>
            </div>
          </AuthGuard>
        );

      case 'shared':
        return (
          <AuthGuard requirePermissions={['file:share']}>
            <div>
              <div style={{ marginBottom: '24px' }}>
                <Title level={3}>
                  <ShareAltOutlined /> 我的分享
                </Title>
                <Text type="secondary">
                  管理您创建的文件分享
                </Text>
              </div>

              <Card>
                <Table
                  columns={shareColumns}
                  dataSource={shareList?.items || []}
                  rowKey="share_id"
                  pagination={{
                    current: shareList?.page || 1,
                    pageSize: shareList?.page_size || 20,
                    total: shareList?.total || 0,
                    showSizeChanger: true,
                    showTotal: (total) => `共 ${total} 个分享`
                  }}
                />
              </Card>
            </div>
          </AuthGuard>
        );

      case 'trash':
        return (
          <AuthGuard requirePermissions={['file:delete']}>
            <div>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                marginBottom: '24px'
              }}>
                <div>
                  <Title level={3}>
                    <RecycleOutlined /> 回收站
                  </Title>
                  <Text type="secondary">
                    已删除的文件将在30天后自动清理
                  </Text>
                </div>
                
                <Button
                  danger
                  onClick={() => {
                    Modal.confirm({
                      title: '确定清空回收站吗？',
                      content: '清空后所有文件将永久删除，无法恢复',
                      onOk: () => file_service_store_empty_trash()
                    });
                  }}
                >
                  清空回收站
                </Button>
              </div>

              <Card>
                <Table
                  columns={trashColumns}
                  dataSource={trashList?.items || []}
                  rowKey="trash_id"
                  pagination={{
                    current: trashList?.page || 1,
                    pageSize: trashList?.page_size || 20,
                    total: trashList?.total || 0,
                    showSizeChanger: true,
                    showTotal: (total) => `共 ${total} 个文件`
                  }}
                />
              </Card>
            </div>
          </AuthGuard>
        );

      case 'analytics':
        return (
          <AuthGuard requirePermissions={['file:analytics']}>
            <div>
              <div style={{ marginBottom: '24px' }}>
                <Title level={3}>
                  <BarChartOutlined /> 存储分析
                </Title>
                <Text type="secondary">
                  查看存储使用情况和统计数据
                </Text>
              </div>

              {storageStats && (
                <>
                  <Row gutter={24} style={{ marginBottom: 24 }}>
                    <Col span={6}>
                      <Card>
                        <Statistic
                          title="总文件数"
                          value={storageStats.total_files}
                          prefix={<FileOutlined />}
                        />
                      </Card>
                    </Col>
                    <Col span={6}>
                      <Card>
                        <Statistic
                          title="总存储量"
                          value={formatFileSize(storageStats.total_size)}
                          prefix={<HddOutlined />}
                        />
                      </Card>
                    </Col>
                    <Col span={6}>
                      <Card>
                        <Statistic
                          title="总下载次数"
                          value={storageStats.total_downloads}
                          prefix={<DownloadOutlined />}
                        />
                      </Card>
                    </Col>
                    <Col span={6}>
                      <Card>
                        <Statistic
                          title="总上传次数"
                          value={storageStats.total_uploads}
                          prefix={<CloudUploadOutlined />}
                        />
                      </Card>
                    </Col>
                  </Row>

                  {/* 文件类型分布 */}
                  <Card title="文件类型分布" style={{ marginBottom: 24 }}>
                    <Row gutter={16}>
                      {Object.entries(storageStats.type_distribution).map(([type, data]) => (
                        <Col span={4} key={type}>
                          <Card size="small">
                            <Statistic
                              title={
                                type === 'image' ? '图片' :
                                type === 'audio' ? '音频' :
                                type === 'video' ? '视频' :
                                type === 'document' ? '文档' :
                                type === 'archive' ? '压缩包' : '其他'
                              }
                              value={data.percentage.toFixed(1)}
                              suffix="%"
                              valueStyle={{ fontSize: '16px' }}
                            />
                            <div style={{ marginTop: 8 }}>
                              <Text type="secondary" style={{ fontSize: '12px' }}>
                                {data.file_count} 个文件
                              </Text>
                            </div>
                            <div>
                              <Text type="secondary" style={{ fontSize: '12px' }}>
                                {formatFileSize(data.total_size)}
                              </Text>
                            </div>
                          </Card>
                        </Col>
                      ))}
                    </Row>
                  </Card>

                  {/* 热门文件 */}
                  <Card title="热门文件" style={{ marginBottom: 24 }}>
                    <List
                      dataSource={storageStats.top_files}
                      renderItem={(item) => (
                        <List.Item>
                          <List.Item.Meta
                            avatar={<Avatar icon={<FileOutlined />} />}
                            title={item.file_name}
                            description={
                              <Space>
                                <Text type="secondary">下载 {item.download_count} 次</Text>
                                <Text type="secondary">{formatFileSize(item.file_size)}</Text>
                              </Space>
                            }
                          />
                        </List.Item>
                      )}
                    />
                  </Card>
                </>
              )}

              {/* 重复文件检测 */}
              <Card
                title="重复文件检测"
                extra={
                  <Button
                    icon={<SearchOutlined />}
                    onClick={() => file_service_store_detect_duplicates()}
                  >
                    开始检测
                  </Button>
                }
              >
                {duplicateFiles.length > 0 ? (
                  <List
                    dataSource={duplicateFiles}
                    renderItem={(group) => (
                      <List.Item>
                        <List.Item.Meta
                          title={`${group.duplicate_files.length} 个重复文件`}
                          description={
                            <div>
                              <div>文件大小: {formatFileSize(group.file_size)}</div>
                              <div>文件列表:</div>
                              {group.duplicate_files.map((file) => (
                                <div key={file.file_id} style={{ marginLeft: 16 }}>
                                  <Text type="secondary">{file.file_path}</Text>
                                </div>
                              ))}
                            </div>
                          }
                        />
                      </List.Item>
                    )}
                  />
                ) : (
                  <Empty description="暂无重复文件，点击开始检测" />
                )}
              </Card>
            </div>
          </AuthGuard>
        );

      case 'settings':
        return (
          <AuthGuard requirePermissions={['file:settings']}>
            <div>
              <div style={{ marginBottom: '24px' }}>
                <Title level={3}>
                  <SettingOutlined /> 文件设置
                </Title>
                <Text type="secondary">
                  配置文件管理相关设置
                </Text>
              </div>

              <Card title="存储设置" style={{ marginBottom: 24 }}>
                <div style={{ textAlign: 'center', padding: '60px 0' }}>
                  <SettingOutlined style={{ fontSize: '48px', color: '#d9d9d9' }} />
                  <div style={{ marginTop: '16px' }}>
                    <Title level={4} type="secondary">设置功能开发中</Title>
                    <Text type="secondary">敬请期待更多配置选项</Text>
                  </div>
                </div>
              </Card>
            </div>
          </AuthGuard>
        );

      default:
        return null;
    }
  };

  return (
    <AuthGuard requirePermissions={['file:read']}>
      <div className={`file-service-workspace ${className || ''}`}>
        <Layout style={{ minHeight: '100vh', background: '#fff' }}>
          {renderSider()}
          
          <Content style={{ padding: '24px', background: '#fff' }}>
            {renderContent()}
          </Content>
        </Layout>

        {/* 分享密码输入模态框 */}
        <Modal
          title="访问分享文件"
          open={sharePasswordModalVisible}
          onOk={handleSharePasswordSubmit}
          onCancel={() => setSharePasswordModalVisible(false)}
        >
          <Form form={sharePasswordForm} layout="vertical">
            <Form.Item
              name="password"
              label="访问密码"
              rules={[{ required: true, message: '请输入访问密码' }]}
            >
              <Input.Password placeholder="请输入分享密码" />
            </Form.Item>
          </Form>
        </Modal>
      </div>
    </AuthGuard>
  );
};

export default FileServiceWorkspace;