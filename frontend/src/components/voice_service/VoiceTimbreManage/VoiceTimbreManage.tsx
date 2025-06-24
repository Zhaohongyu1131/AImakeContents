/**
 * Voice Timbre Manage Component
 * 语音音色管理组件 - [components][voice_service][voice_timbre_manage]
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
  Empty
} from 'antd';
import {
  SoundOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  PlayCircleOutlined,
  UploadOutlined,
  ExperimentOutlined,
  UserOutlined,
  GlobalOutlined,
  ThunderboltOutlined,
  ReloadOutlined,
  SearchOutlined,
  FilterOutlined,
  SettingOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

import { useVoiceServiceStore } from '../../../stores/voice_service/voice_service_store';
import type { 
  VoiceTimbreBasic,
  VoiceTimbreCreateRequest,
  VoiceTimbreUpdateRequest,
  VoiceTimbreCloneRequest,
  VoicePlatformType,
  VoiceGender,
  VoiceLanguage,
  TimbreType
} from '../../../services/api/voice_service_api';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { Search } = Input;
const { Dragger } = Upload;

interface VoiceTimbreManageProps {
  onTimbreSelect?: (timbre: VoiceTimbreBasic) => void;
  selectedTimbreId?: number;
  showSelector?: boolean;
  className?: string;
}

interface TimbreFilters {
  platform_type?: VoicePlatformType;
  timbre_type?: TimbreType;
  voice_gender?: VoiceGender;
  voice_language?: VoiceLanguage;
  is_available?: boolean;
  search?: string;
}

export const VoiceTimbreManage: React.FC<VoiceTimbreManageProps> = ({
  onTimbreSelect,
  selectedTimbreId,
  showSelector = false,
  className
}) => {
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [cloneModalVisible, setCloneModalVisible] = useState(false);
  const [detailDrawerVisible, setDetailDrawerVisible] = useState(false);
  const [selectedTimbre, setSelectedTimbre] = useState<VoiceTimbreBasic | null>(null);
  const [filters, setFilters] = useState<TimbreFilters>({});
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [audioPlayer, setAudioPlayer] = useState<HTMLAudioElement | null>(null);
  const [playingTimbreId, setPlayingTimbreId] = useState<number | null>(null);

  const [createForm] = Form.useForm();
  const [editForm] = Form.useForm();
  const [cloneForm] = Form.useForm();

  const {
    timbreList,
    currentTimbre,
    timbreListLoading,
    timbreCreateLoading,
    timbreUpdateLoading,
    cloneLoading,
    currentCloneTask,
    platformVoices,
    voice_service_store_load_timbre_list,
    voice_service_store_load_timbre_detail,
    voice_service_store_create_timbre,
    voice_service_store_update_timbre,
    voice_service_store_delete_timbre,
    voice_service_store_clone_timbre,
    voice_service_store_check_clone_status,
    voice_service_store_load_platform_voices
  } = useVoiceServiceStore();

  // 初始化数据加载
  useEffect(() => {
    loadTimbreList();
    loadPlatformVoices();
  }, []);

  // 监听过滤条件变化
  useEffect(() => {
    loadTimbreList();
  }, [filters, currentPage, pageSize]);

  // 监听克隆任务状态
  useEffect(() => {
    if (currentCloneTask?.clone_task_id && currentCloneTask.status === 'processing') {
      const interval = setInterval(() => {
        voice_service_store_check_clone_status(currentCloneTask.clone_task_id);
      }, 3000);

      return () => clearInterval(interval);
    }
  }, [currentCloneTask]);

  const loadTimbreList = () => {
    voice_service_store_load_timbre_list(currentPage, pageSize, filters);
  };

  const loadPlatformVoices = () => {
    voice_service_store_load_platform_voices('doubao', 'zh-CN');
    voice_service_store_load_platform_voices('azure', 'zh-CN');
    voice_service_store_load_platform_voices('openai', 'zh-CN');
  };

  // 播放样本音频
  const handlePlaySample = (timbre: VoiceTimbreBasic) => {
    if (!timbre.sample_audio_url) {
      message.warning('该音色没有样本音频');
      return;
    }

    if (playingTimbreId === timbre.timbre_id) {
      // 停止播放
      audioPlayer?.pause();
      setPlayingTimbreId(null);
      setAudioPlayer(null);
    } else {
      // 开始播放
      if (audioPlayer) {
        audioPlayer.pause();
      }

      const audio = new Audio(timbre.sample_audio_url);
      audio.addEventListener('ended', () => {
        setPlayingTimbreId(null);
        setAudioPlayer(null);
      });
      
      audio.play().then(() => {
        setAudioPlayer(audio);
        setPlayingTimbreId(timbre.timbre_id);
      }).catch(() => {
        message.error('音频播放失败');
      });
    }
  };

  // 查看详情
  const handleViewDetail = (timbre: VoiceTimbreBasic) => {
    setSelectedTimbre(timbre);
    voice_service_store_load_timbre_detail(timbre.timbre_id);
    setDetailDrawerVisible(true);
  };

  // 编辑音色
  const handleEdit = (timbre: VoiceTimbreBasic) => {
    setSelectedTimbre(timbre);
    editForm.setFieldsValue({
      timbre_id: timbre.timbre_id,
      timbre_name: timbre.timbre_name,
      voice_description: timbre.voice_description,
      is_available: timbre.is_available
    });
    setEditModalVisible(true);
  };

  // 删除音色
  const handleDelete = async (timbreId: number) => {
    const success = await voice_service_store_delete_timbre(timbreId);
    if (success) {
      message.success('音色删除成功');
      loadTimbreList();
    }
  };

  // 创建音色
  const handleCreate = async () => {
    try {
      const values = await createForm.validateFields();
      const request: VoiceTimbreCreateRequest = {
        timbre_name: values.timbre_name,
        timbre_type: values.timbre_type,
        platform_type: values.platform_type,
        platform_voice_id: values.platform_voice_id,
        voice_gender: values.voice_gender,
        voice_language: values.voice_language,
        voice_description: values.voice_description,
        timbre_params: values.timbre_params
      };

      const success = await voice_service_store_create_timbre(request);
      if (success) {
        message.success('音色创建成功');
        setCreateModalVisible(false);
        createForm.resetFields();
        loadTimbreList();
      }
    } catch (error) {
      console.error('Create timbre failed:', error);
    }
  };

  // 更新音色
  const handleUpdate = async () => {
    try {
      const values = await editForm.validateFields();
      const request: VoiceTimbreUpdateRequest = {
        timbre_id: values.timbre_id,
        timbre_name: values.timbre_name,
        voice_description: values.voice_description,
        is_available: values.is_available
      };

      const success = await voice_service_store_update_timbre(request);
      if (success) {
        message.success('音色更新成功');
        setEditModalVisible(false);
        editForm.resetFields();
        loadTimbreList();
      }
    } catch (error) {
      console.error('Update timbre failed:', error);
    }
  };

  // 克隆音色
  const handleClone = async () => {
    try {
      const values = await cloneForm.validateFields();
      
      if (!values.source_audio_files || values.source_audio_files.length === 0) {
        message.error('请上传音频文件');
        return;
      }

      const request: VoiceTimbreCloneRequest = {
        timbre_name: values.timbre_name,
        platform_type: values.platform_type,
        source_audio_files: values.source_audio_files.map((file: any) => file.originFileObj),
        voice_description: values.voice_description,
        voice_gender: values.voice_gender,
        voice_language: values.voice_language,
        clone_params: {
          quality_level: values.quality_level,
          enhancement: values.enhancement
        }
      };

      const success = await voice_service_store_clone_timbre(request);
      if (success) {
        message.success('音色克隆任务已启动');
        setCloneModalVisible(false);
        cloneForm.resetFields();
      }
    } catch (error) {
      console.error('Clone timbre failed:', error);
    }
  };

  // 表格列定义
  const columns: ColumnsType<VoiceTimbreBasic> = [
    {
      title: '音色信息',
      key: 'info',
      width: 280,
      render: (_, record) => (
        <Space>
          <Avatar 
            icon={<SoundOutlined />} 
            style={{ 
              backgroundColor: record.is_available ? '#52c41a' : '#d9d9d9'
            }}
          />
          <div>
            <div>
              <Text strong>{record.timbre_name}</Text>
              {!record.is_available && (
                <Tag color="red" size="small" style={{ marginLeft: 8 }}>
                  不可用
                </Tag>
              )}
            </div>
            <div>
              <Text type="secondary" style={{ fontSize: '12px' }}>
                #{record.timbre_id} · {record.timbre_type}
              </Text>
            </div>
          </div>
        </Space>
      )
    },
    {
      title: '平台',
      dataIndex: 'platform_type',
      key: 'platform_type',
      width: 100,
      render: (platform: VoicePlatformType) => (
        <Tag color="blue">{platform.toUpperCase()}</Tag>
      ),
      filters: [
        { text: 'Doubao', value: 'doubao' },
        { text: 'Azure', value: 'azure' },
        { text: 'OpenAI', value: 'openai' },
        { text: 'ElevenLabs', value: 'elevenlabs' }
      ]
    },
    {
      title: '语言/性别',
      key: 'voice_info',
      width: 120,
      render: (_, record) => (
        <Space direction="vertical" size="small">
          <Tag icon={<GlobalOutlined />}>{record.voice_language}</Tag>
          <Tag 
            color={record.voice_gender === 'male' ? 'blue' : 
                   record.voice_gender === 'female' ? 'pink' : 'green'}
            icon={<UserOutlined />}
          >
            {record.voice_gender === 'male' ? '男声' : 
             record.voice_gender === 'female' ? '女声' : '中性'}
          </Tag>
        </Space>
      )
    },
    {
      title: '描述',
      dataIndex: 'voice_description',
      key: 'voice_description',
      ellipsis: true,
      render: (text: string) => (
        <Tooltip title={text}>
          <Text type="secondary">{text || '暂无描述'}</Text>
        </Tooltip>
      )
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
      )
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_, record) => (
        <Space>
          {record.sample_audio_url && (
            <Tooltip title="播放样本">
              <Button
                type="text"
                icon={<PlayCircleOutlined />}
                onClick={() => handlePlaySample(record)}
                style={{ 
                  color: playingTimbreId === record.timbre_id ? '#ff4d4f' : '#1890ff'
                }}
              />
            </Tooltip>
          )}
          
          <Tooltip title="查看详情">
            <Button
              type="text"
              icon={<SearchOutlined />}
              onClick={() => handleViewDetail(record)}
            />
          </Tooltip>

          {showSelector && (
            <Button
              type={selectedTimbreId === record.timbre_id ? 'primary' : 'default'}
              size="small"
              onClick={() => onTimbreSelect?.(record)}
            >
              {selectedTimbreId === record.timbre_id ? '已选择' : '选择'}
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
                title="确定要删除这个音色吗？"
                onConfirm={() => handleDelete(record.timbre_id)}
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
          placeholder="搜索音色名称"
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
          <Option value="azure">Azure</Option>
          <Option value="openai">OpenAI</Option>
          <Option value="elevenlabs">ElevenLabs</Option>
        </Select>
      </Col>
      <Col span={4}>
        <Select
          placeholder="类型"
          allowClear
          onChange={(value) => setFilters({ ...filters, timbre_type: value })}
          style={{ width: '100%' }}
        >
          <Option value="default">默认</Option>
          <Option value="cloned">克隆</Option>
          <Option value="custom">自定义</Option>
        </Select>
      </Col>
      <Col span={4}>
        <Select
          placeholder="性别"
          allowClear
          onChange={(value) => setFilters({ ...filters, voice_gender: value })}
          style={{ width: '100%' }}
        >
          <Option value="male">男声</Option>
          <Option value="female">女声</Option>
          <Option value="neutral">中性</Option>
        </Select>
      </Col>
      <Col span={4}>
        <Select
          placeholder="状态"
          allowClear
          onChange={(value) => setFilters({ ...filters, is_available: value })}
          style={{ width: '100%' }}
        >
          <Option value={true}>可用</Option>
          <Option value={false}>不可用</Option>
        </Select>
      </Col>
      <Col span={2}>
        <Button
          icon={<ReloadOutlined />}
          onClick={() => {
            setFilters({});
            loadTimbreList();
          }}
        >
          重置
        </Button>
      </Col>
    </Row>
  );

  // 渲染克隆进度
  const renderCloneProgress = () => {
    if (!currentCloneTask) return null;

    return (
      <Alert
        message="音色克隆进行中"
        description={
          <div>
            <div>任务ID: {currentCloneTask.clone_task_id}</div>
            <div>状态: {currentCloneTask.status}</div>
            {currentCloneTask.status === 'processing' && (
              <Progress percent={50} status="active" showInfo={false} />
            )}
          </div>
        }
        type={currentCloneTask.status === 'completed' ? 'success' : 'info'}
        showIcon
        style={{ marginBottom: 16 }}
      />
    );
  };

  return (
    <div className={`voice-timbre-manage ${className || ''}`}>
      <Card
        title={
          <Space>
            <SoundOutlined />
            <span>音色管理</span>
            <Badge count={timbreList?.total || 0} style={{ backgroundColor: '#52c41a' }} />
          </Space>
        }
        extra={
          !showSelector && (
            <Space>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => setCreateModalVisible(true)}
              >
                添加音色
              </Button>
              <Button
                icon={<ExperimentOutlined />}
                onClick={() => setCloneModalVisible(true)}
              >
                克隆音色
              </Button>
            </Space>
          )
        }
      >
        {/* 克隆进度提示 */}
        {renderCloneProgress()}

        {/* 过滤器 */}
        {renderFilters()}

        {/* 音色列表 */}
        <Table
          columns={columns}
          dataSource={timbreList?.items || []}
          rowKey="timbre_id"
          loading={timbreListLoading}
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: timbreList?.total || 0,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 个音色`,
            onChange: (page, size) => {
              setCurrentPage(page);
              setPageSize(size || 20);
            }
          }}
          rowSelection={showSelector ? {
            type: 'radio',
            selectedRowKeys: selectedTimbreId ? [selectedTimbreId] : [],
            onSelect: (record) => onTimbreSelect?.(record)
          } : undefined}
        />
      </Card>

      {/* 创建音色模态框 */}
      <Modal
        title="添加音色"
        open={createModalVisible}
        onOk={handleCreate}
        onCancel={() => setCreateModalVisible(false)}
        confirmLoading={timbreCreateLoading}
        width={600}
      >
        <Form form={createForm} layout="vertical">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="timbre_name"
                label="音色名称"
                rules={[{ required: true, message: '请输入音色名称' }]}
              >
                <Input placeholder="请输入音色名称" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="platform_type"
                label="平台"
                rules={[{ required: true, message: '请选择平台' }]}
              >
                <Select placeholder="选择平台">
                  <Option value="doubao">Doubao</Option>
                  <Option value="azure">Azure</Option>
                  <Option value="openai">OpenAI</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="voice_gender"
                label="声音性别"
                rules={[{ required: true, message: '请选择声音性别' }]}
              >
                <Select placeholder="选择声音性别">
                  <Option value="male">男声</Option>
                  <Option value="female">女声</Option>
                  <Option value="neutral">中性</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="voice_language"
                label="语言"
                rules={[{ required: true, message: '请选择语言' }]}
              >
                <Select placeholder="选择语言">
                  <Option value="zh-CN">中文</Option>
                  <Option value="en-US">英语</Option>
                  <Option value="ja-JP">日语</Option>
                  <Option value="ko-KR">韩语</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={24}>
              <Form.Item
                name="voice_description"
                label="描述"
              >
                <Input.TextArea placeholder="请输入音色描述" rows={3} />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* 编辑音色模态框 */}
      <Modal
        title="编辑音色"
        open={editModalVisible}
        onOk={handleUpdate}
        onCancel={() => setEditModalVisible(false)}
        confirmLoading={timbreUpdateLoading}
      >
        <Form form={editForm} layout="vertical">
          <Form.Item name="timbre_id" hidden>
            <Input />
          </Form.Item>
          <Form.Item
            name="timbre_name"
            label="音色名称"
            rules={[{ required: true, message: '请输入音色名称' }]}
          >
            <Input placeholder="请输入音色名称" />
          </Form.Item>
          <Form.Item
            name="voice_description"
            label="描述"
          >
            <Input.TextArea placeholder="请输入音色描述" rows={3} />
          </Form.Item>
          <Form.Item
            name="is_available"
            label="状态"
            valuePropName="checked"
          >
            <Switch checkedChildren="可用" unCheckedChildren="禁用" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 克隆音色模态框 */}
      <Modal
        title="克隆音色"
        open={cloneModalVisible}
        onOk={handleClone}
        onCancel={() => setCloneModalVisible(false)}
        confirmLoading={cloneLoading}
        width={700}
      >
        <Form form={cloneForm} layout="vertical">
          <Alert
            message="音色克隆说明"
            description="上传高质量的音频文件(建议10-30秒,WAV或MP3格式),AI将学习音色特征并生成可用于合成的音色模型。"
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
          />

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="timbre_name"
                label="音色名称"
                rules={[{ required: true, message: '请输入音色名称' }]}
              >
                <Input placeholder="为克隆的音色命名" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="platform_type"
                label="克隆平台"
                rules={[{ required: true, message: '请选择克隆平台' }]}
              >
                <Select placeholder="选择克隆平台">
                  <Option value="doubao">Doubao</Option>
                  <Option value="azure">Azure</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="voice_gender"
                label="声音性别"
                rules={[{ required: true, message: '请选择声音性别' }]}
              >
                <Select placeholder="选择声音性别">
                  <Option value="male">男声</Option>
                  <Option value="female">女声</Option>
                  <Option value="neutral">中性</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="voice_language"
                label="语言"
                rules={[{ required: true, message: '请选择语言' }]}
              >
                <Select placeholder="选择语言">
                  <Option value="zh-CN">中文</Option>
                  <Option value="en-US">英语</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={24}>
              <Form.Item
                name="source_audio_files"
                label="音频文件"
                rules={[{ required: true, message: '请上传音频文件' }]}
              >
                <Dragger
                  multiple
                  accept=".wav,.mp3,.m4a"
                  beforeUpload={() => false}
                  maxCount={5}
                >
                  <p className="ant-upload-drag-icon">
                    <UploadOutlined />
                  </p>
                  <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
                  <p className="ant-upload-hint">
                    支持WAV、MP3格式，建议上传10-30秒的高质量音频
                  </p>
                </Dragger>
              </Form.Item>
            </Col>
            <Col span={24}>
              <Form.Item
                name="voice_description"
                label="描述"
              >
                <Input.TextArea placeholder="描述音色特点，有助于AI更好地学习" rows={2} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="quality_level"
                label="质量等级"
                initialValue="standard"
              >
                <Select>
                  <Option value="standard">标准</Option>
                  <Option value="high">高质量</Option>
                  <Option value="premium">专业级</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="enhancement"
                label="音频增强"
                valuePropName="checked"
                initialValue={true}
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* 音色详情抽屉 */}
      <Drawer
        title="音色详情"
        open={detailDrawerVisible}
        onClose={() => setDetailDrawerVisible(false)}
        width={500}
      >
        {currentTimbre && (
          <div>
            <Row gutter={16}>
              <Col span={24}>
                <Card size="small">
                  <Statistic
                    title="音色名称"
                    value={currentTimbre.timbre_name}
                    prefix={<SoundOutlined />}
                  />
                </Card>
              </Col>
            </Row>

            <Divider />

            <Row gutter={16}>
              <Col span={12}>
                <div>
                  <Text type="secondary">平台类型:</Text>
                  <div><Tag color="blue">{currentTimbre.platform_type.toUpperCase()}</Tag></div>
                </div>
              </Col>
              <Col span={12}>
                <div>
                  <Text type="secondary">音色类型:</Text>
                  <div><Tag>{currentTimbre.timbre_type}</Tag></div>
                </div>
              </Col>
            </Row>

            <Divider />

            <Row gutter={16}>
              <Col span={12}>
                <div>
                  <Text type="secondary">性别:</Text>
                  <div>
                    <Tag color={currentTimbre.voice_gender === 'male' ? 'blue' : 'pink'}>
                      {currentTimbre.voice_gender === 'male' ? '男声' : 
                       currentTimbre.voice_gender === 'female' ? '女声' : '中性'}
                    </Tag>
                  </div>
                </div>
              </Col>
              <Col span={12}>
                <div>
                  <Text type="secondary">语言:</Text>
                  <div><Tag icon={<GlobalOutlined />}>{currentTimbre.voice_language}</Tag></div>
                </div>
              </Col>
            </Row>

            {currentTimbre.voice_description && (
              <>
                <Divider />
                <div>
                  <Text type="secondary">描述:</Text>
                  <Paragraph>{currentTimbre.voice_description}</Paragraph>
                </div>
              </>
            )}

            {currentTimbre.sample_audio_url && (
              <>
                <Divider />
                <div>
                  <Text type="secondary">样本音频:</Text>
                  <div style={{ marginTop: 8 }}>
                    <Button
                      icon={<PlayCircleOutlined />}
                      onClick={() => handlePlaySample(currentTimbre)}
                    >
                      播放样本
                    </Button>
                  </div>
                </div>
              </>
            )}

            <Divider />

            <Row gutter={16}>
              <Col span={12}>
                <div>
                  <Text type="secondary">创建时间:</Text>
                  <div>{new Date(currentTimbre.created_at).toLocaleString()}</div>
                </div>
              </Col>
              <Col span={12}>
                <div>
                  <Text type="secondary">状态:</Text>
                  <div>
                    <Badge 
                      status={currentTimbre.is_available ? 'success' : 'error'}
                      text={currentTimbre.is_available ? '可用' : '不可用'}
                    />
                  </div>
                </div>
              </Col>
            </Row>
          </div>
        )}
      </Drawer>
    </div>
  );
};

export default VoiceTimbreManage;