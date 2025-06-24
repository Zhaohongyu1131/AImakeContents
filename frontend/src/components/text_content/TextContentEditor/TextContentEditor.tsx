/**
 * Text Content Editor Component
 * 文本内容编辑器组件 - [components][text_content][text_content_editor]
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  Card,
  Form,
  Input,
  Select,
  Button,
  Space,
  Row,
  Col,
  Typography,
  Tag,
  Divider,
  Alert,
  Tooltip,
  Switch,
  Badge,
  message,
  Modal
} from 'antd';
import {
  SaveOutlined,
  EyeOutlined,
  UndoOutlined,
  RedoOutlined,
  FullscreenOutlined,
  FullscreenExitOutlined,
  FileTextOutlined,
  BulbOutlined,
  AnalyticsOutlined,
  TagsOutlined
} from '@ant-design/icons';

import { useTextContentStore } from '../../../stores/text_content/text_content_store';
import type { 
  TextContentBasic, 
  TextContentCreateRequest, 
  TextContentUpdateRequest,
  TextAnalyseResponse 
} from '../../../services/api/text_content_api';

const { TextArea } = Input;
const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

interface TextContentEditorProps {
  contentId?: number;
  initialData?: Partial<TextContentBasic>;
  mode?: 'create' | 'edit';
  onSave?: (content: TextContentBasic) => void;
  onCancel?: () => void;
  className?: string;
}

export const TextContentEditor: React.FC<TextContentEditorProps> = ({
  contentId,
  initialData,
  mode = 'create',
  onSave,
  onCancel,
  className
}) => {
  const [form] = Form.useForm();
  const [fullscreen, setFullscreen] = useState(false);
  const [previewMode, setPreviewMode] = useState(false);
  const [unsavedChanges, setUnsavedChanges] = useState(false);
  const [wordCount, setWordCount] = useState(0);
  const [analysisResult, setAnalysisResult] = useState<TextAnalyseResponse | null>(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [autoSaveEnabled, setAutoSaveEnabled] = useState(true);
  const autoSaveRef = useRef<NodeJS.Timeout>();

  const {
    currentContent,
    contentLoading,
    contentError,
    text_content_store_load_content_detail,
    text_content_store_create_content,
    text_content_store_update_content,
    text_content_store_analyse_text,
    text_content_store_clear_errors
  } = useTextContentStore();

  // 加载内容详情
  useEffect(() => {
    if (mode === 'edit' && contentId) {
      text_content_store_load_content_detail(contentId);
    }
  }, [mode, contentId]);

  // 初始化表单数据
  useEffect(() => {
    if (mode === 'edit' && currentContent) {
      form.setFieldsValue({
        content_title: currentContent.content_title,
        content_body: currentContent.content_body,
        content_type: currentContent.content_type,
        content_tags: currentContent.content_tags?.join(', ') || '',
        content_status: currentContent.content_status
      });
      setWordCount(currentContent.content_body?.length || 0);
    } else if (initialData) {
      form.setFieldsValue({
        content_title: initialData.content_title || '',
        content_body: initialData.content_body || '',
        content_type: initialData.content_type || 'article',
        content_tags: initialData.content_tags?.join(', ') || '',
        content_status: initialData.content_status || 'draft'
      });
      setWordCount(initialData.content_body?.length || 0);
    }
  }, [form, mode, currentContent, initialData]);

  // 监听表单变化
  const handleFormChange = () => {
    setUnsavedChanges(true);
    
    // 更新字数统计
    const content = form.getFieldValue('content_body') || '';
    setWordCount(content.length);

    // 自动保存
    if (autoSaveEnabled && mode === 'edit') {
      if (autoSaveRef.current) {
        clearTimeout(autoSaveRef.current);
      }
      autoSaveRef.current = setTimeout(() => {
        handleAutoSave();
      }, 3000); // 3秒后自动保存
    }
  };

  const handleAutoSave = async () => {
    if (!unsavedChanges || mode === 'create') return;
    
    try {
      const values = await form.validateFields();
      const updateData: TextContentUpdateRequest = {
        content_id: contentId!,
        content_title: values.content_title,
        content_body: values.content_body,
        content_type: values.content_type,
        content_tags: values.content_tags?.split(',').map((tag: string) => tag.trim()).filter(Boolean),
        content_status: values.content_status
      };

      const success = await text_content_store_update_content(updateData);
      if (success) {
        setUnsavedChanges(false);
        message.success('自动保存成功', 1);
      }
    } catch (error) {
      // 自动保存失败时不显示错误信息
      console.warn('Auto save failed:', error);
    }
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      
      if (mode === 'create') {
        const createData: TextContentCreateRequest = {
          content_title: values.content_title,
          content_body: values.content_body,
          content_type: values.content_type,
          content_tags: values.content_tags?.split(',').map((tag: string) => tag.trim()).filter(Boolean),
          content_status: values.content_status
        };

        const success = await text_content_store_create_content(createData);
        if (success && currentContent) {
          setUnsavedChanges(false);
          message.success('内容创建成功');
          onSave?.(currentContent);
        }
      } else if (mode === 'edit' && contentId) {
        const updateData: TextContentUpdateRequest = {
          content_id: contentId,
          content_title: values.content_title,
          content_body: values.content_body,
          content_type: values.content_type,
          content_tags: values.content_tags?.split(',').map((tag: string) => tag.trim()).filter(Boolean),
          content_status: values.content_status
        };

        const success = await text_content_store_update_content(updateData);
        if (success && currentContent) {
          setUnsavedChanges(false);
          message.success('内容更新成功');
          onSave?.(currentContent);
        }
      }
    } catch (error) {
      console.error('Save failed:', error);
    }
  };

  const handleAnalyse = async () => {
    const content = form.getFieldValue('content_body');
    if (!content || content.trim().length === 0) {
      message.warning('请先输入内容');
      return;
    }

    setAnalysisLoading(true);
    try {
      const result = await text_content_store_analyse_text({
        text: content,
        analysis_types: ['sentiment', 'keywords', 'summary', 'readability']
      });
      
      if (result) {
        setAnalysisResult(result);
        message.success('文本分析完成');
      }
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setAnalysisLoading(false);
    }
  };

  const handleCancel = () => {
    if (unsavedChanges) {
      Modal.confirm({
        title: '确定要离开吗？',
        content: '您有未保存的更改，离开将丢失这些更改。',
        okText: '确定离开',
        cancelText: '继续编辑',
        onOk: () => {
          onCancel?.();
        }
      });
    } else {
      onCancel?.();
    }
  };

  const renderToolbar = () => (
    <div style={{ marginBottom: 16 }}>
      <Row justify="space-between" align="middle">
        <Col>
          <Space>
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={handleSave}
              loading={contentLoading}
            >
              保存
            </Button>
            
            <Button
              icon={<EyeOutlined />}
              onClick={() => setPreviewMode(!previewMode)}
            >
              {previewMode ? '编辑' : '预览'}
            </Button>
            
            <Button
              icon={<AnalyticsOutlined />}
              onClick={handleAnalyse}
              loading={analysisLoading}
            >
              文本分析
            </Button>
            
            <Divider type="vertical" />
            
            <Button
              icon={fullscreen ? <FullscreenExitOutlined /> : <FullscreenOutlined />}
              onClick={() => setFullscreen(!fullscreen)}
            >
              {fullscreen ? '退出全屏' : '全屏'}
            </Button>
          </Space>
        </Col>
        
        <Col>
          <Space>
            <Badge
              count={wordCount}
              showZero
              style={{ backgroundColor: '#52c41a' }}
            >
              <Text type="secondary">字符数</Text>
            </Badge>
            
            {unsavedChanges && (
              <Badge dot>
                <Text type="secondary">未保存</Text>
              </Badge>
            )}
            
            <Switch
              checkedChildren="自动保存"
              unCheckedChildren="手动保存"
              checked={autoSaveEnabled}
              onChange={setAutoSaveEnabled}
              size="small"
            />
            
            {onCancel && (
              <Button onClick={handleCancel}>
                取消
              </Button>
            )}
          </Space>
        </Col>
      </Row>
    </div>
  );

  const renderEditor = () => {
    if (previewMode) {
      const content = form.getFieldValue('content_body') || '';
      return (
        <Card
          title="内容预览"
          style={{ minHeight: '500px' }}
        >
          <div style={{ 
            padding: '16px',
            background: '#fafafa',
            borderRadius: '6px',
            minHeight: '400px'
          }}>
            <Title level={3}>
              {form.getFieldValue('content_title') || '未命名内容'}
            </Title>
            <Paragraph style={{ whiteSpace: 'pre-wrap' }}>
              {content || '内容为空'}
            </Paragraph>
          </div>
        </Card>
      );
    }

    return (
      <Row gutter={24}>
        <Col xs={24} lg={analysisResult ? 16 : 24}>
          <Form
            form={form}
            layout="vertical"
            onValuesChange={handleFormChange}
          >
            <Form.Item
              name="content_title"
              label="标题"
              rules={[{ required: true, message: '请输入标题' }]}
            >
              <Input
                placeholder="请输入内容标题"
                size="large"
                maxLength={200}
                showCount
              />
            </Form.Item>

            <Row gutter={16}>
              <Col span={8}>
                <Form.Item
                  name="content_type"
                  label="内容类型"
                  rules={[{ required: true, message: '请选择内容类型' }]}
                >
                  <Select placeholder="选择内容类型">
                    <Option value="article">文章</Option>
                    <Option value="prompt">提示词</Option>
                    <Option value="script">脚本</Option>
                    <Option value="description">描述</Option>
                  </Select>
                </Form.Item>
              </Col>
              
              <Col span={8}>
                <Form.Item
                  name="content_status"
                  label="状态"
                  rules={[{ required: true, message: '请选择状态' }]}
                >
                  <Select placeholder="选择状态">
                    <Option value="draft">草稿</Option>
                    <Option value="published">已发布</Option>
                    <Option value="archived">已归档</Option>
                  </Select>
                </Form.Item>
              </Col>
              
              <Col span={8}>
                <Form.Item
                  name="content_tags"
                  label="标签"
                >
                  <Input
                    placeholder="多个标签用逗号分隔"
                    prefix={<TagsOutlined />}
                  />
                </Form.Item>
              </Col>
            </Row>

            <Form.Item
              name="content_body"
              label="内容"
              rules={[{ required: true, message: '请输入内容' }]}
            >
              <TextArea
                placeholder="请输入内容..."
                rows={fullscreen ? 25 : 15}
                showCount
                maxLength={50000}
                style={{ fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace' }}
              />
            </Form.Item>
          </Form>
        </Col>

        {/* 分析结果面板 */}
        {analysisResult && (
          <Col xs={24} lg={8}>
            <Card
              title="分析结果"
              size="small"
              extra={
                <Button
                  type="text"
                  size="small"
                  onClick={() => setAnalysisResult(null)}
                >
                  关闭
                </Button>
              }
            >
              {/* 情感分析 */}
              {analysisResult.analysis_results.sentiment && (
                <div style={{ marginBottom: 16 }}>
                  <Text strong>情感分析:</Text>
                  <div style={{ marginTop: 4 }}>
                    <Tag color={
                      analysisResult.analysis_results.sentiment.label === 'positive' ? 'green' :
                      analysisResult.analysis_results.sentiment.label === 'negative' ? 'red' : 'orange'
                    }>
                      {analysisResult.analysis_results.sentiment.label === 'positive' ? '积极' :
                       analysisResult.analysis_results.sentiment.label === 'negative' ? '消极' : '中性'}
                    </Tag>
                    <Text type="secondary">
                      (置信度: {(analysisResult.analysis_results.sentiment.confidence * 100).toFixed(1)}%)
                    </Text>
                  </div>
                </div>
              )}

              {/* 关键词 */}
              {analysisResult.analysis_results.keywords && (
                <div style={{ marginBottom: 16 }}>
                  <Text strong>关键词:</Text>
                  <div style={{ marginTop: 4 }}>
                    {analysisResult.analysis_results.keywords.slice(0, 10).map((keyword, index) => (
                      <Tag key={index} style={{ marginBottom: 4 }}>
                        {keyword.keyword}
                      </Tag>
                    ))}
                  </div>
                </div>
              )}

              {/* 摘要 */}
              {analysisResult.analysis_results.summary && (
                <div style={{ marginBottom: 16 }}>
                  <Text strong>智能摘要:</Text>
                  <Paragraph style={{ 
                    marginTop: 4,
                    fontSize: '12px',
                    background: '#f5f5f5',
                    padding: '8px',
                    borderRadius: '4px'
                  }}>
                    {analysisResult.analysis_results.summary.summary_text}
                  </Paragraph>
                </div>
              )}

              {/* 可读性 */}
              {analysisResult.analysis_results.readability && (
                <div>
                  <Text strong>可读性分析:</Text>
                  <div style={{ marginTop: 4 }}>
                    <div><Text type="secondary">阅读难度: </Text>{analysisResult.analysis_results.readability.reading_level}</div>
                    <div><Text type="secondary">平均句长: </Text>{analysisResult.analysis_results.readability.avg_sentence_length.toFixed(1)} 词</div>
                  </div>
                </div>
              )}
            </Card>
          </Col>
        )}
      </Row>
    );
  };

  if (contentError) {
    return (
      <Alert
        message="加载失败"
        description={contentError}
        type="error"
        showIcon
        action={
          <Button size="small" onClick={() => text_content_store_clear_errors()}>
            重试
          </Button>
        }
      />
    );
  }

  return (
    <div 
      className={`text-content-editor ${className || ''}`}
      style={{ 
        position: fullscreen ? 'fixed' : 'relative',
        top: fullscreen ? 0 : 'auto',
        left: fullscreen ? 0 : 'auto',
        right: fullscreen ? 0 : 'auto',
        bottom: fullscreen ? 0 : 'auto',
        zIndex: fullscreen ? 1000 : 'auto',
        background: fullscreen ? '#fff' : 'transparent',
        padding: fullscreen ? '24px' : '0'
      }}
    >
      <Card
        title={
          <Space>
            <FileTextOutlined />
            <span>{mode === 'create' ? '创建内容' : '编辑内容'}</span>
            {mode === 'edit' && currentContent && (
              <Text type="secondary">#{currentContent.content_id}</Text>
            )}
          </Space>
        }
        loading={contentLoading}
        bordered={!fullscreen}
      >
        {renderToolbar()}
        {renderEditor()}
      </Card>
    </div>
  );
};

export default TextContentEditor;