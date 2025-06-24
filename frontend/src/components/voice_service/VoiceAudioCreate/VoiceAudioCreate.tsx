/**
 * Voice Audio Create Component
 * 语音音频创建组件 - [components][voice_service][voice_audio_create]
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
  Slider,
  Switch,
  Alert,
  Progress,
  Divider,
  message,
  Upload,
  Tag,
  Tooltip,
  Badge,
  Collapse
} from 'antd';
import {
  SoundOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  DownloadOutlined,
  SettingOutlined,
  FileTextOutlined,
  CloudUploadOutlined,
  ExperimentOutlined,
  ThunderboltOutlined,
  SaveOutlined,
  ReloadOutlined
} from '@ant-design/icons';

import { useVoiceServiceStore } from '../../../stores/voice_service/voice_service_store';
import type { 
  VoiceSynthesisRequest,
  VoiceSynthesisResponse,
  VoiceTimbreBasic,
  VoicePlatformType 
} from '../../../services/api/voice_service_api';

const { TextArea } = Input;
const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { Panel } = Collapse;

interface VoiceAudioCreateProps {
  initialText?: string;
  initialTimbreId?: number;
  onCreated?: (result: VoiceSynthesisResponse) => void;
  onSaved?: (audioId: number) => void;
  className?: string;
}

export const VoiceAudioCreate: React.FC<VoiceAudioCreateProps> = ({
  initialText = '',
  initialTimbreId,
  onCreated,
  onSaved,
  className
}) => {
  const [form] = Form.useForm();
  const [audioPlayer, setAudioPlayer] = useState<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackTime, setPlaybackTime] = useState(0);
  const [audioDuration, setAudioDuration] = useState(0);
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);
  const [previewMode, setPreviewMode] = useState(false);
  const [wordCount, setWordCount] = useState(0);
  const [estimatedDuration, setEstimatedDuration] = useState(0);
  const audioRef = useRef<HTMLAudioElement>(null);

  const {
    timbreList,
    synthesisLoading,
    synthesisProgress,
    lastSynthesisResult,
    platformVoices,
    platformConnectionStatus,
    voice_service_store_load_timbre_list,
    voice_service_store_synthesize_text,
    voice_service_store_load_platform_voices,
    voice_service_store_test_platform_connection,
    voice_service_store_clear_errors
  } = useVoiceServiceStore();

  // 初始化数据加载
  useEffect(() => {
    voice_service_store_load_timbre_list(1, 50, { is_available: true });
    voice_service_store_load_platform_voices('doubao', 'zh-CN');
    voice_service_store_load_platform_voices('azure', 'zh-CN');
  }, []);

  // 初始化表单
  useEffect(() => {
    form.setFieldsValue({
      text: initialText,
      voice_timbre_id: initialTimbreId,
      synthesis_params: {
        speed: 1.0,
        pitch: 0,
        volume: 80,
        emotion: 'neutral',
        style: 'general'
      },
      audio_format: 'mp3',
      save_to_library: true
    });
    
    if (initialText) {
      setWordCount(initialText.length);
      setEstimatedDuration(Math.ceil(initialText.length / 3)); // 简单估算：3字符/秒
    }
  }, [form, initialText, initialTimbreId]);

  // 监听文本变化
  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const text = e.target.value;
    setWordCount(text.length);
    setEstimatedDuration(Math.ceil(text.length / 3));
  };

  // 播放/暂停音频
  const handlePlayPause = () => {
    if (!lastSynthesisResult?.audio_url) return;

    if (audioPlayer) {
      if (isPlaying) {
        audioPlayer.pause();
      } else {
        audioPlayer.play();
      }
      setIsPlaying(!isPlaying);
    } else {
      const audio = new Audio(lastSynthesisResult.audio_url);
      setAudioPlayer(audio);
      
      audio.addEventListener('loadedmetadata', () => {
        setAudioDuration(audio.duration);
      });
      
      audio.addEventListener('timeupdate', () => {
        setPlaybackTime(audio.currentTime);
      });
      
      audio.addEventListener('ended', () => {
        setIsPlaying(false);
        setPlaybackTime(0);
      });
      
      audio.play();
      setIsPlaying(true);
    }
  };

  // 下载音频
  const handleDownload = () => {
    if (!lastSynthesisResult?.audio_url) return;
    
    const link = document.createElement('a');
    link.href = lastSynthesisResult.audio_url;
    link.download = `voice_${lastSynthesisResult.audio_id}.${form.getFieldValue('audio_format')}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // 语音合成
  const handleSynthesize = async () => {
    try {
      const values = await form.validateFields();
      
      const request: VoiceSynthesisRequest = {
        text: values.text,
        voice_timbre_id: values.voice_timbre_id,
        synthesis_params: values.synthesis_params,
        audio_format: values.audio_format,
        save_to_library: values.save_to_library,
        audio_title: values.audio_title || `语音合成_${new Date().getTime()}`
      };

      const result = await voice_service_store_synthesize_text(request);
      if (result) {
        message.success('语音合成成功');
        onCreated?.(result);
        
        // 自动播放新生成的音频
        if (audioPlayer) {
          audioPlayer.pause();
          setAudioPlayer(null);
        }
        setIsPlaying(false);
        setPlaybackTime(0);
      }
    } catch (error) {
      console.error('Synthesis failed:', error);
    }
  };

  // 测试平台连接
  const handleTestConnection = async (platform: VoicePlatformType) => {
    const success = await voice_service_store_test_platform_connection(platform);
    if (success) {
      message.success(`${platform} 平台连接正常`);
    } else {
      message.error(`${platform} 平台连接失败`);
    }
  };

  // 获取可用音色列表
  const getAvailableTimbresByPlatform = (platform: VoicePlatformType) => {
    if (!timbreList) return [];
    return timbreList.items.filter(timbre => 
      timbre.platform_type === platform && timbre.is_available
    );
  };

  // 渲染平台状态
  const renderPlatformStatus = (platform: VoicePlatformType) => {
    const status = platformConnectionStatus[platform];
    const isConnected = status?.is_connected;
    
    return (
      <Badge
        status={isConnected ? 'success' : 'error'}
        text={
          <Space>
            <Text>{platform.toUpperCase()}</Text>
            {status?.response_time && (
              <Text type="secondary">({status.response_time}ms)</Text>
            )}
            <Button
              type="link"
              size="small"
              onClick={() => handleTestConnection(platform)}
            >
              测试
            </Button>
          </Space>
        }
      />
    );
  };

  // 渲染基础设置
  const renderBasicSettings = () => (
    <Row gutter={24}>
      <Col span={24}>
        <Form.Item
          name="text"
          label="合成文本"
          rules={[
            { required: true, message: '请输入要合成的文本' },
            { max: 10000, message: '文本长度不能超过10000字符' }
          ]}
        >
          <TextArea
            placeholder="请输入要合成的文本内容..."
            rows={8}
            showCount
            maxLength={10000}
            onChange={handleTextChange}
            style={{ fontFamily: 'PingFang SC, Microsoft YaHei, sans-serif' }}
          />
        </Form.Item>
      </Col>

      <Col span={12}>
        <Form.Item
          name="voice_timbre_id"
          label="选择音色"
          rules={[{ required: true, message: '请选择音色' }]}
        >
          <Select
            placeholder="选择音色"
            showSearch
            filterOption={(input, option) =>
              option?.children?.toString().toLowerCase().includes(input.toLowerCase())
            }
          >
            {['doubao', 'azure', 'openai', 'elevenlabs'].map(platform => {
              const timbres = getAvailableTimbresByPlatform(platform as VoicePlatformType);
              if (timbres.length === 0) return null;
              
              return (
                <Select.OptGroup key={platform} label={platform.toUpperCase()}>
                  {timbres.map(timbre => (
                    <Option key={timbre.timbre_id} value={timbre.timbre_id}>
                      <Space>
                        <span>{timbre.timbre_name}</span>
                        <Tag size="small">{timbre.voice_gender}</Tag>
                        <Tag size="small">{timbre.voice_language}</Tag>
                      </Space>
                    </Option>
                  ))}
                </Select.OptGroup>
              );
            })}
          </Select>
        </Form.Item>
      </Col>

      <Col span={12}>
        <Form.Item
          name="audio_format"
          label="音频格式"
          rules={[{ required: true, message: '请选择音频格式' }]}
        >
          <Select placeholder="选择音频格式">
            <Option value="mp3">MP3 (推荐)</Option>
            <Option value="wav">WAV (高质量)</Option>
            <Option value="ogg">OGG (小文件)</Option>
          </Select>
        </Form.Item>
      </Col>

      <Col span={12}>
        <Form.Item
          name="audio_title"
          label="音频标题"
        >
          <Input placeholder="为生成的音频命名" />
        </Form.Item>
      </Col>

      <Col span={12}>
        <Form.Item
          name="save_to_library"
          label="保存到音频库"
          valuePropName="checked"
        >
          <Switch checkedChildren="保存" unCheckedChildren="不保存" />
        </Form.Item>
      </Col>
    </Row>
  );

  // 渲染高级参数设置
  const renderAdvancedSettings = () => (
    <Collapse
      ghost
      expandIconPosition="end"
      onChange={(keys) => setShowAdvancedSettings(keys.length > 0)}
    >
      <Panel header="高级参数设置" key="advanced">
        <Row gutter={24}>
          <Col span={8}>
            <Form.Item
              name={['synthesis_params', 'speed']}
              label="语速"
              tooltip="调整语音播放速度，1.0为正常速度"
            >
              <Slider
                min={0.5}
                max={2.0}
                step={0.1}
                marks={{
                  0.5: '0.5x',
                  1.0: '正常',
                  2.0: '2.0x'
                }}
              />
            </Form.Item>
          </Col>

          <Col span={8}>
            <Form.Item
              name={['synthesis_params', 'pitch']}
              label="音调"
              tooltip="调整语音音调，0为默认音调"
            >
              <Slider
                min={-20}
                max={20}
                marks={{
                  '-20': '低',
                  0: '默认',
                  20: '高'
                }}
              />
            </Form.Item>
          </Col>

          <Col span={8}>
            <Form.Item
              name={['synthesis_params', 'volume']}
              label="音量"
              tooltip="调整语音音量大小"
            >
              <Slider
                min={0}
                max={100}
                marks={{
                  0: '静音',
                  50: '50%',
                  100: '100%'
                }}
              />
            </Form.Item>
          </Col>

          <Col span={12}>
            <Form.Item
              name={['synthesis_params', 'emotion']}
              label="情感风格"
            >
              <Select placeholder="选择情感风格">
                <Option value="neutral">中性</Option>
                <Option value="happy">愉快</Option>
                <Option value="sad">悲伤</Option>
                <Option value="angry">愤怒</Option>
                <Option value="excited">兴奋</Option>
                <Option value="calm">平静</Option>
              </Select>
            </Form.Item>
          </Col>

          <Col span={12}>
            <Form.Item
              name={['synthesis_params', 'style']}
              label="说话风格"
            >
              <Select placeholder="选择说话风格">
                <Option value="general">通用</Option>
                <Option value="news">新闻播报</Option>
                <Option value="story">故事讲述</Option>
                <Option value="conversation">对话</Option>
                <Option value="advertisement">广告</Option>
              </Select>
            </Form.Item>
          </Col>
        </Row>
      </Panel>
    </Collapse>
  );

  // 渲染操作区
  const renderActionArea = () => (
    <Row justify="space-between" align="middle">
      <Col>
        <Space>
          <Badge count={wordCount} showZero style={{ backgroundColor: '#52c41a' }}>
            <Text type="secondary">字符数</Text>
          </Badge>
          <Badge count={`${estimatedDuration}s`} style={{ backgroundColor: '#1890ff' }}>
            <Text type="secondary">预计时长</Text>
          </Badge>
        </Space>
      </Col>
      
      <Col>
        <Space>
          <Button
            type="primary"
            icon={<SoundOutlined />}
            onClick={handleSynthesize}
            loading={synthesisLoading}
            size="large"
          >
            {synthesisLoading ? '合成中...' : '开始合成'}
          </Button>
          
          <Button
            icon={<ReloadOutlined />}
            onClick={() => {
              form.resetFields();
              voice_service_store_clear_errors();
              setWordCount(0);
              setEstimatedDuration(0);
            }}
          >
            重置
          </Button>
        </Space>
      </Col>
    </Row>
  );

  // 渲染结果预览
  const renderResultPreview = () => {
    if (!lastSynthesisResult) return null;

    return (
      <Card
        title="合成结果"
        size="small"
        extra={
          <Space>
            <Button
              type="primary"
              icon={isPlaying ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
              onClick={handlePlayPause}
              size="small"
            >
              {isPlaying ? '暂停' : '播放'}
            </Button>
            <Button
              icon={<DownloadOutlined />}
              onClick={handleDownload}
              size="small"
            >
              下载
            </Button>
          </Space>
        }
        style={{ marginTop: 24 }}
      >
        <Row gutter={16}>
          <Col span={12}>
            <div>
              <Text type="secondary">音频时长: </Text>
              <Text>{lastSynthesisResult.audio_duration}秒</Text>
            </div>
            <div>
              <Text type="secondary">文件大小: </Text>
              <Text>{(lastSynthesisResult.audio_size / 1024).toFixed(1)}KB</Text>
            </div>
          </Col>
          <Col span={12}>
            <div>
              <Text type="secondary">合成平台: </Text>
              <Tag>{lastSynthesisResult.platform_used.toUpperCase()}</Tag>
            </div>
            <div>
              <Text type="secondary">合成耗时: </Text>
              <Text>{lastSynthesisResult.synthesis_time}ms</Text>
            </div>
          </Col>
        </Row>

        {/* 播放进度条 */}
        {isPlaying && audioDuration > 0 && (
          <div style={{ marginTop: 16 }}>
            <Progress 
              percent={(playbackTime / audioDuration) * 100}
              showInfo={false}
              strokeColor="#1890ff"
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#999' }}>
              <span>{Math.floor(playbackTime)}s</span>
              <span>{Math.floor(audioDuration)}s</span>
            </div>
          </div>
        )}

        {/* 成本信息 */}
        {lastSynthesisResult.cost_info && (
          <Alert
            message={
              <Space>
                <Text>本次合成消耗: </Text>
                <Text strong>{lastSynthesisResult.cost_info.tokens_used} tokens</Text>
                <Text>费用: </Text>
                <Text strong>
                  {lastSynthesisResult.cost_info.cost_amount} {lastSynthesisResult.cost_info.currency}
                </Text>
              </Space>
            }
            type="info"
            showIcon={false}
            style={{ marginTop: 8 }}
          />
        )}
      </Card>
    );
  };

  // 渲染合成进度
  const renderSynthesisProgress = () => {
    if (!synthesisLoading) return null;

    return (
      <Card size="small" style={{ marginTop: 16 }}>
        <div style={{ textAlign: 'center' }}>
          <Progress 
            type="circle" 
            percent={synthesisProgress} 
            status="active"
            width={80}
          />
          <div style={{ marginTop: 8 }}>
            <Text>正在合成语音...</Text>
          </div>
        </div>
      </Card>
    );
  };

  return (
    <div className={`voice-audio-create ${className || ''}`}>
      <Card
        title={
          <Space>
            <SoundOutlined />
            <span>语音合成</span>
            <Badge status="processing" text="AI驱动" />
          </Space>
        }
        extra={
          <Space>
            {/* 平台状态显示 */}
            {renderPlatformStatus('doubao')}
            {renderPlatformStatus('azure')}
          </Space>
        }
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            synthesis_params: {
              speed: 1.0,
              pitch: 0,
              volume: 80,
              emotion: 'neutral',
              style: 'general'
            },
            audio_format: 'mp3',
            save_to_library: true
          }}
        >
          {/* 基础设置 */}
          {renderBasicSettings()}
          
          <Divider />
          
          {/* 高级设置 */}
          {renderAdvancedSettings()}
          
          <Divider />
          
          {/* 操作区 */}
          {renderActionArea()}
        </Form>

        {/* 合成进度 */}
        {renderSynthesisProgress()}
        
        {/* 结果预览 */}
        {renderResultPreview()}
      </Card>
    </div>
  );
};

export default VoiceAudioCreate;