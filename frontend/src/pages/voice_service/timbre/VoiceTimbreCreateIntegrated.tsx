/**
 * Voice Timbre Create Integrated Component
 * 音色创建集成组件 - [Voice][Timbre][Create][Integrated]
 * 
 * 展示如何集成统一语音服务的音色创建组件
 */

import React, { useState, useEffect } from 'react'
import {
  Card,
  Form,
  Input,
  Select,
  Button,
  Typography,
  Row,
  Col,
  Space,
  Alert,
  message,
  Progress,
  Switch
} from 'antd'
import {
  SoundOutlined,
  SaveOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  ThunderboltOutlined
} from '@ant-design/icons'
import { useVoiceService } from '../../../hooks/voice/useVoiceService'
import type { VoiceCloneParams } from '../../../services/voice/voice_platform_adapter'

const { Title, Paragraph, Text } = Typography
const { TextArea } = Input
const { Option } = Select

const VoiceTimbreCreateIntegrated: React.FC = () => {
  const [form] = Form.useForm()
  const [audioFiles, setAudioFiles] = useState<File[]>([])
  const [currentCloneId, setCurrentCloneId] = useState<string | null>(null)
  
  // 使用统一语音服务
  const {
    // 平台状态
    currentPlatform,
    availablePlatforms,
    platformConnected,
    
    // 功能状态
    cloning,
    cloneProgress,
    cloneResults,
    
    // 播放状态
    playing,
    
    // 方法
    switchPlatform,
    testPlatformConnection,
    startVoiceClone,
    getCloneStatus,
    playAudio,
    stopAudio
  } = useVoiceService()

  useEffect(() => {
    // 组件挂载时测试平台连接
    if (currentPlatform) {
      testPlatformConnection()
    }
  }, [currentPlatform, testPlatformConnection])

  const handleFileUpload = (file: File) => {
    setAudioFiles(prev => [...prev, file])
    return false // 阻止默认上传
  }

  const handleRemoveFile = (index: number) => {
    setAudioFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleSubmit = async (values: any) => {
    if (audioFiles.length === 0) {
      message.error('请至少上传一个音频文件')
      return
    }

    if (!currentPlatform) {
      message.error('请先选择语音平台')
      return
    }

    try {
      const cloneParams: VoiceCloneParams = {
        name: values.name,
        description: values.description,
        audio_files: audioFiles,
        gender: values.gender || 'auto',
        language: values.language,
        quality_level: values.quality_level || 'high',
        enhancement: values.enhancement !== false
      }

      const cloneId = await startVoiceClone(cloneParams)
      setCurrentCloneId(cloneId)
      
      message.success('音色克隆任务已启动，请等待处理完成')
    } catch (error) {
      console.error('Voice clone submission failed:', error)
      message.error('音色克隆失败，请重试')
    }
  }

  const handlePlaySample = async () => {
    // 这里可以播放样本音频
    if (playing) {
      stopAudio()
    } else {
      // 播放示例音频
      await playAudio('/audio/sample.mp3')
    }
  }

  const getCurrentCloneResult = () => {
    if (!currentCloneId) return null
    return cloneResults.get(currentCloneId)
  }

  const cloneResult = getCurrentCloneResult()

  return (
    <div className="voice-timbre-create-integrated">
      <Card>
        <Title level={2}>
          <SoundOutlined /> 智能音色创建
        </Title>
        <Paragraph>
          使用AI技术创建个性化音色，支持多平台自动选择和智能降级。
        </Paragraph>

        {/* 平台状态指示器 */}
        <Alert
          message={
            <Space>
              <Text>当前平台: {currentPlatform || '未选择'}</Text>
              <Text type={platformConnected ? 'success' : 'danger'}>
                {platformConnected ? '✓ 已连接' : '✗ 连接失败'}
              </Text>
            </Space>
          }
          type={platformConnected ? 'success' : 'warning'}
          showIcon
          style={{ marginBottom: 16 }}
          action={
            <Space>
              <Select
                value={currentPlatform}
                onChange={switchPlatform}
                style={{ width: 120 }}
                size="small"
              >
                {availablePlatforms.map(platform => (
                  <Option key={platform} value={platform}>
                    {platform}
                  </Option>
                ))}
              </Select>
              <Button 
                size="small" 
                onClick={() => testPlatformConnection()}
              >
                测试连接
              </Button>
            </Space>
          }
        />

        {/* 克隆进度显示 */}
        {cloning && (
          <Alert
            message={
              <div>
                <div style={{ marginBottom: 8 }}>
                  <Text strong>正在处理音色克隆...</Text>
                </div>
                <Progress 
                  percent={Math.round(cloneProgress)} 
                  status="active"
                  format={percent => `${percent}% ${cloneResult?.status === 'processing' ? '处理中' : '完成'}`}
                />
                {cloneResult?.estimated_time && (
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    预计完成时间: {cloneResult.estimated_time} 分钟
                  </Text>
                )}
              </div>
            }
            type="info"
            style={{ marginBottom: 16 }}
          />
        )}

        {/* 克隆完成提示 */}
        {cloneResult?.status === 'completed' && (
          <Alert
            message="音色克隆完成！"
            description={
              <Space direction="vertical">
                <Text>您的个性化音色已成功创建，现在可以使用了。</Text>
                <Space>
                  <Button 
                    type="primary" 
                    icon={playing ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
                    onClick={handlePlaySample}
                  >
                    {playing ? '停止试听' : '试听音色'}
                  </Button>
                  <Button icon={<SaveOutlined />}>
                    保存到音色库
                  </Button>
                </Space>
              </Space>
            }
            type="success"
            showIcon
            style={{ marginBottom: 16 }}
          />
        )}

        {/* 表单 */}
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          disabled={cloning}
        >
          <Row gutter={24}>
            <Col xs={24} lg={12}>
              <Card title="基本信息" size="small">
                <Form.Item
                  name="name"
                  label="音色名称"
                  rules={[{ required: true, message: '请输入音色名称' }]}
                >
                  <Input placeholder="为您的音色起一个独特的名字" />
                </Form.Item>

                <Form.Item
                  name="description"
                  label="音色描述"
                >
                  <TextArea
                    rows={3}
                    placeholder="描述这个音色的特点和用途..."
                  />
                </Form.Item>

                <Form.Item
                  name="language"
                  label="主要语言"
                  rules={[{ required: true, message: '请选择主要语言' }]}
                  initialValue="zh-CN"
                >
                  <Select>
                    <Option value="zh-CN">中文（普通话）</Option>
                    <Option value="zh-HK">中文（粤语）</Option>
                    <Option value="en-US">英语（美式）</Option>
                    <Option value="en-GB">英语（英式）</Option>
                    <Option value="ja-JP">日语</Option>
                    <Option value="ko-KR">韩语</Option>
                  </Select>
                </Form.Item>

                <Form.Item
                  name="gender"
                  label="性别识别"
                  initialValue="auto"
                >
                  <Select>
                    <Option value="auto">自动识别</Option>
                    <Option value="male">男性</Option>
                    <Option value="female">女性</Option>
                  </Select>
                </Form.Item>
              </Card>
            </Col>

            <Col xs={24} lg={12}>
              <Card title="高级设置" size="small">
                <Form.Item
                  name="quality_level"
                  label="克隆质量"
                  initialValue="high"
                >
                  <Select>
                    <Option value="standard">标准 (快速)</Option>
                    <Option value="high">高质量 (推荐)</Option>
                    <Option value="premium">超高质量 (较慢)</Option>
                  </Select>
                </Form.Item>

                <Form.Item
                  name="enhancement"
                  label="音频增强"
                  valuePropName="checked"
                  initialValue={true}
                >
                  <Switch 
                    checkedChildren="开启" 
                    unCheckedChildren="关闭"
                  />
                </Form.Item>

                <Alert
                  message="音频要求"
                  description={
                    <ul style={{ margin: 0, paddingLeft: 16 }}>
                      <li>上传3-10个音频文件</li>
                      <li>每个文件5-30秒</li>
                      <li>总时长2-5分钟</li>
                      <li>清晰无噪音</li>
                    </ul>
                  }
                  type="info"
                  showIcon
                />

                <div style={{ marginTop: 16 }}>
                  <Text strong>当前上传: {audioFiles.length} 个文件</Text>
                </div>
              </Card>
            </Col>
          </Row>

          <Card title="音频上传" size="small" style={{ marginTop: 16 }}>
            {/* 这里简化音频上传UI */}
            <input
              type="file"
              accept=".mp3,.wav,.m4a"
              multiple
              onChange={(e) => {
                const files = Array.from(e.target.files || [])
                files.forEach(handleFileUpload)
              }}
              style={{ marginBottom: 16 }}
            />

            {audioFiles.length > 0 && (
              <div>
                <Text strong>已上传文件:</Text>
                <ul>
                  {audioFiles.map((file, index) => (
                    <li key={index}>
                      <Space>
                        <Text>{file.name}</Text>
                        <Button 
                          type="link" 
                          danger 
                          size="small"
                          onClick={() => handleRemoveFile(index)}
                        >
                          删除
                        </Button>
                      </Space>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </Card>

          <div style={{ marginTop: 24, textAlign: 'center' }}>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                size="large"
                icon={<ThunderboltOutlined />}
                loading={cloning}
                disabled={!platformConnected || audioFiles.length === 0}
              >
                {cloning ? '正在克隆...' : '开始克隆音色'}
              </Button>
              <Button 
                size="large"
                disabled={cloning}
              >
                取消
              </Button>
            </Space>
          </div>
        </Form>
      </Card>
    </div>
  )
}

export default VoiceTimbreCreateIntegrated