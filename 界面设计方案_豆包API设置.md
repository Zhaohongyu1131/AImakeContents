# 界面设计方案 - 豆包API设置组件

## 概述

基于豆包API的参数要求，设计用户友好的设置界面，分为基础设置和高级设置两个层次，满足不同用户的使用需求。

## 1. 组件架构设计

### 1.1 组件层级结构

```
VoiceSettings (语音设置主组件)
├── VoiceCloneSettings (音色克隆设置)
│   ├── BasicCloneSettings (基础设置)
│   └── AdvancedCloneSettings (高级设置 - 可折叠)
├── TTSSettings (语音合成设置)
│   ├── BasicTTSSettings (基础设置)
│   └── AdvancedTTSSettings (高级设置 - 可折叠)
└── PresetManager (预设管理器)
```

### 1.2 通用设置组件

```
SettingsSection (设置区块组件)
├── SettingsGroup (设置分组)
├── SettingsField (设置字段)
├── ParameterSlider (参数滑块)
├── ParameterSelect (参数选择器)
├── ParameterSwitch (参数开关)
└── HelpTooltip (帮助提示)
```

## 2. 音色克隆设置界面

### 2.1 基础设置 (VoiceCloneBasicSettings.tsx)

```tsx
import React, { useState } from 'react';
import { Card, Form, Input, Select, Upload, Button, Space, Divider } from 'antd';
import { InboxOutlined, QuestionCircleOutlined } from '@ant-design/icons';

interface VoiceCloneBasicSettings {
  timbreName: string;
  timbreDescription: string;
  language: number;
  modelType: number;
  sourceAudioFile: File | null;
}

const VoiceCloneBasicSettings: React.FC = () => {
  const [form] = Form.useForm();
  const [settings, setSettings] = useState<VoiceCloneBasicSettings>({
    timbreName: '',
    timbreDescription: '',
    language: 0, // 默认中文
    modelType: 1, // 默认2.0效果
    sourceAudioFile: null
  });

  const languageOptions = [
    { value: 0, label: '中文', description: '支持中英混读' },
    { value: 1, label: '英文', description: '纯英文语音' },
    { value: 2, label: '日语', description: '日语语音' },
    { value: 3, label: '西班牙语', description: '西班牙语语音' },
    { value: 4, label: '印尼语', description: '印尼语语音' },
    { value: 5, label: '葡萄牙语', description: '葡萄牙语语音' }
  ];

  const modelTypeOptions = [
    { 
      value: 1, 
      label: '2.0效果(ICL)', 
      description: '推荐选择，音质自然，训练速度快',
      recommended: true 
    },
    { 
      value: 0, 
      label: '1.0效果', 
      description: '经典版本，稳定可靠' 
    },
    { 
      value: 2, 
      label: 'DiT标准版', 
      description: '还原音色，不保留个人风格' 
    },
    { 
      value: 3, 
      label: 'DiT还原版', 
      description: '还原音色和个人说话风格',
      advanced: true 
    }
  ];

  return (
    <Card 
      title="音色克隆 - 基础设置" 
      className="voice-clone-basic-settings"
      extra={
        <Button 
          type="link" 
          icon={<QuestionCircleOutlined />}
          href="/help/voice-clone"
          target="_blank"
        >
          使用帮助
        </Button>
      }
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={settings}
        onValuesChange={(changedValues, allValues) => {
          setSettings(allValues);
        }}
      >
        {/* 音频文件上传 */}
        <Form.Item
          name="sourceAudioFile"
          label={
            <Space>
              源音频文件
              <span className="required-mark">*</span>
            </Space>
          }
          rules={[{ required: true, message: '请上传音频文件' }]}
          extra="支持格式：WAV、MP3、OGG、M4A、AAC，建议时长10-60秒，文件大小不超过10MB"
        >
          <Upload.Dragger
            name="audioFile"
            accept=".wav,.mp3,.ogg,.m4a,.aac"
            beforeUpload={() => false} // 阻止自动上传
            showUploadList={{ showRemoveIcon: true }}
            className="audio-upload-dragger"
          >
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">点击或拖拽音频文件到此区域</p>
            <p className="ant-upload-hint">
              建议使用清晰、无背景噪音的音频文件，说话内容丰富的效果更好
            </p>
          </Upload.Dragger>
        </Form.Item>

        <Divider />

        {/* 基本信息 */}
        <div className="settings-group">
          <h4>基本信息</h4>
          
          <Form.Item
            name="timbreName"
            label="音色名称"
            rules={[
              { required: true, message: '请输入音色名称' },
              { max: 50, message: '音色名称不能超过50个字符' }
            ]}
          >
            <Input 
              placeholder="请输入一个易识别的音色名称"
              showCount
              maxLength={50}
            />
          </Form.Item>

          <Form.Item
            name="timbreDescription"
            label="音色描述"
            rules={[{ max: 200, message: '描述不能超过200个字符' }]}
          >
            <Input.TextArea 
              placeholder="可选：描述音色的特点、适用场景等"
              showCount
              maxLength={200}
              rows={3}
            />
          </Form.Item>
        </div>

        <Divider />

        {/* 语言设置 */}
        <div className="settings-group">
          <h4>语言设置</h4>
          
          <Form.Item
            name="language"
            label="主要语言"
            rules={[{ required: true, message: '请选择主要语言' }]}
          >
            <Select placeholder="选择音色主要支持的语言">
              {languageOptions.map(option => (
                <Select.Option key={option.value} value={option.value}>
                  <div>
                    <strong>{option.label}</strong>
                    <div className="option-description">{option.description}</div>
                  </div>
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
        </div>

        <Divider />

        {/* 模型设置 */}
        <div className="settings-group">
          <h4>模型版本</h4>
          
          <Form.Item
            name="modelType"
            label="训练模型"
            rules={[{ required: true, message: '请选择训练模型' }]}
            extra="不同模型版本在音质、训练时间和效果上有所不同"
          >
            <Select placeholder="选择训练使用的模型版本">
              {modelTypeOptions.map(option => (
                <Select.Option key={option.value} value={option.value}>
                  <div className="model-option">
                    <div className="model-label">
                      <strong>{option.label}</strong>
                      {option.recommended && (
                        <span className="recommended-badge">推荐</span>
                      )}
                      {option.advanced && (
                        <span className="advanced-badge">高级</span>
                      )}
                    </div>
                    <div className="model-description">{option.description}</div>
                  </div>
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
        </div>

        {/* 预估信息 */}
        <div className="estimation-info">
          <Card size="small" className="info-card">
            <div className="info-row">
              <span>预估训练时间：</span>
              <strong>15-30分钟</strong>
            </div>
            <div className="info-row">
              <span>预估可用次数：</span>
              <strong>10次训练机会</strong>
            </div>
            <div className="info-row">
              <span>有效期：</span>
              <strong>12个月</strong>
            </div>
          </Card>
        </div>
      </Form>
    </Card>
  );
};

export default VoiceCloneBasicSettings;
```

### 2.2 高级设置 (VoiceCloneAdvancedSettings.tsx)

```tsx
import React, { useState } from 'react';
import { Collapse, Form, Input, Select, Switch, Slider, Alert, Space } from 'antd';
import { SettingOutlined, ExperimentOutlined } from '@ant-design/icons';

const { Panel } = Collapse;

interface VoiceCloneAdvancedSettings {
  referenceText: string;
  audioFormat: string;
  qualityPriority: string;
  noiseReduction: boolean;
  customParameters: Record<string, any>;
}

const VoiceCloneAdvancedSettings: React.FC = () => {
  const [form] = Form.useForm();
  const [activeKey, setActiveKey] = useState<string[]>([]);

  const audioFormatOptions = [
    { value: 'wav', label: 'WAV', description: '无损音质，文件较大' },
    { value: 'mp3', label: 'MP3', description: '压缩格式，文件较小' },
    { value: 'ogg', label: 'OGG', description: '开源格式，平衡音质和大小' },
    { value: 'm4a', label: 'M4A', description: 'Apple格式，兼容性好' },
    { value: 'aac', label: 'AAC', description: '高效压缩，音质优秀' }
  ];

  return (
    <Collapse
      activeKey={activeKey}
      onChange={setActiveKey}
      className="voice-clone-advanced-settings"
      ghost
    >
      <Panel
        header={
          <Space>
            <ExperimentOutlined />
            高级设置
            <span className="panel-description">专业用户选项，通常使用默认值即可</span>
          </Space>
        }
        key="advanced"
        className="advanced-panel"
      >
        <Alert
          message="高级设置说明"
          description="这些设置适用于对音色克隆有特殊要求的专业用户。修改前请确保您了解各参数的作用。"
          type="info"
          showIcon
          className="advanced-warning"
        />

        <Form form={form} layout="vertical">
          {/* 质量优化 */}
          <div className="settings-group">
            <h4>质量优化</h4>
            
            <Form.Item
              name="referenceText"
              label="参考文本"
              extra="提供与音频内容匹配的文本，可提高训练质量和准确性"
            >
              <Input.TextArea
                placeholder="可选：输入音频中说话的内容文本"
                rows={4}
                showCount
                maxLength={1000}
              />
            </Form.Item>

            <Form.Item
              name="qualityPriority"
              label="质量优先级"
              initialValue="balanced"
            >
              <Select>
                <Select.Option value="speed">速度优先 - 快速训练，标准质量</Select.Option>
                <Select.Option value="balanced">平衡模式 - 速度和质量平衡</Select.Option>
                <Select.Option value="quality">质量优先 - 最佳音质，训练时间较长</Select.Option>
              </Select>
            </Form.Item>

            <Form.Item
              name="noiseReduction"
              label="智能降噪"
              valuePropName="checked"
              initialValue={true}
            >
              <Switch 
                checkedChildren="开启" 
                unCheckedChildren="关闭"
                className="setting-switch"
              />
            </Form.Item>
          </div>

          {/* 音频处理 */}
          <div className="settings-group">
            <h4>音频处理</h4>
            
            <Form.Item
              name="audioFormat"
              label="音频格式要求"
              initialValue="wav"
              extra="指定源音频文件的格式要求，影响处理精度"
            >
              <Select>
                {audioFormatOptions.map(option => (
                  <Select.Option key={option.value} value={option.value}>
                    <div>
                      <strong>{option.label}</strong>
                      <div className="option-description">{option.description}</div>
                    </div>
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item
              name="volumeNormalization"
              label="音量标准化"
              valuePropName="checked"
              initialValue={true}
            >
              <Switch 
                checkedChildren="启用" 
                unCheckedChildren="禁用"
                className="setting-switch"
              />
            </Form.Item>
          </div>

          {/* 训练参数 */}
          <div className="settings-group">
            <h4>训练参数</h4>
            
            <Form.Item
              name="trainingIterations"
              label="训练轮数"
              initialValue={100}
              extra="更多轮数可能提高质量但增加训练时间"
            >
              <Slider
                min={50}
                max={200}
                step={10}
                marks={{
                  50: '快速',
                  100: '标准',
                  150: '精细',
                  200: '极致'
                }}
                tipFormatter={(value) => `${value}轮`}
              />
            </Form.Item>

            <Form.Item
              name="learningRate"
              label="学习率"
              initialValue={0.001}
            >
              <Slider
                min={0.0001}
                max={0.01}
                step={0.0001}
                marks={{
                  0.0001: '保守',
                  0.001: '标准',
                  0.005: '激进',
                  0.01: '极速'
                }}
                tipFormatter={(value) => value?.toFixed(4)}
              />
            </Form.Item>
          </div>

          {/* 实验性功能 */}
          <div className="settings-group experimental">
            <h4>
              <Space>
                <ExperimentOutlined />
                实验性功能
              </Space>
            </h4>
            
            <Alert
              message="实验性功能警告"
              description="以下功能仍在测试阶段，可能影响训练结果的稳定性"
              type="warning"
              showIcon
              className="experimental-warning"
            />

            <Form.Item
              name="voiceConversion"
              label="声音转换增强"
              valuePropName="checked"
              initialValue={false}
            >
              <Switch 
                checkedChildren="启用" 
                unCheckedChildren="禁用"
                className="setting-switch"
              />
            </Form.Item>

            <Form.Item
              name="emotionPreservation"
              label="情感保持"
              valuePropName="checked"
              initialValue={false}
            >
              <Switch 
                checkedChildren="启用" 
                unCheckedChildren="禁用"
                className="setting-switch"
              />
            </Form.Item>
          </div>
        </Form>
      </Panel>
    </Collapse>
  );
};

export default VoiceCloneAdvancedSettings;
```

## 3. 语音合成设置界面

### 3.1 基础设置 (TTSBasicSettings.tsx)

```tsx
import React, { useState } from 'react';
import { Card, Form, Select, Slider, Radio, Space, Divider, Button } from 'antd';
import { PlayCircleOutlined, PauseCircleOutlined } from '@ant-design/icons';

interface TTSBasicSettings {
  voiceType: string;
  speedRatio: number;
  volumeRatio: number;
  pitchRatio: number;
  encoding: string;
  sampleRate: number;
  language: string;
}

const TTSBasicSettings: React.FC = () => {
  const [form] = Form.useForm();
  const [isPlaying, setIsPlaying] = useState(false);
  const [settings, setSettings] = useState<TTSBasicSettings>({
    voiceType: '',
    speedRatio: 1.0,
    volumeRatio: 1.0,
    pitchRatio: 1.0,
    encoding: 'mp3',
    sampleRate: 24000,
    language: 'zh-CN'
  });

  const encodingOptions = [
    { 
      value: 'mp3', 
      label: 'MP3', 
      description: '推荐格式，兼容性好，文件小',
      recommended: true 
    },
    { 
      value: 'wav', 
      label: 'WAV', 
      description: '无损音质，文件较大' 
    },
    { 
      value: 'ogg_opus', 
      label: 'OGG Opus', 
      description: '高压缩比，音质优秀' 
    },
    { 
      value: 'pcm', 
      label: 'PCM', 
      description: '原始格式，专业用途' 
    }
  ];

  const sampleRateOptions = [
    { value: 8000, label: '8kHz', description: '电话质量' },
    { value: 16000, label: '16kHz', description: '标准质量' },
    { value: 24000, label: '24kHz', description: '高质量（推荐）' }
  ];

  const testAudio = () => {
    setIsPlaying(!isPlaying);
    // TODO: 实现音频预览功能
  };

  return (
    <Card 
      title="语音合成 - 基础设置"
      className="tts-basic-settings"
      extra={
        <Button 
          type="primary" 
          icon={isPlaying ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
          onClick={testAudio}
        >
          {isPlaying ? '停止试听' : '试听效果'}
        </Button>
      }
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={settings}
        onValuesChange={(changedValues, allValues) => {
          setSettings(allValues);
        }}
      >
        {/* 音色选择 */}
        <div className="settings-group">
          <h4>音色选择</h4>
          
          <Form.Item
            name="voiceType"
            label="选择音色"
            rules={[{ required: true, message: '请选择音色' }]}
          >
            <Select 
              placeholder="选择要使用的音色"
              showSearch
              filterOption={(input, option) =>
                option?.children?.toString().toLowerCase().includes(input.toLowerCase())
              }
            >
              <Select.OptGroup label="我的音色">
                <Select.Option value="S_custom_001">我的音色1 - 专业男声</Select.Option>
                <Select.Option value="S_custom_002">我的音色2 - 温柔女声</Select.Option>
              </Select.OptGroup>
              <Select.OptGroup label="系统音色">
                <Select.Option value="S_system_001">标准男声</Select.Option>
                <Select.Option value="S_system_002">标准女声</Select.Option>
                <Select.Option value="S_system_003">儿童声音</Select.Option>
              </Select.OptGroup>
            </Select>
          </Form.Item>
        </div>

        <Divider />

        {/* 语音控制 */}
        <div className="settings-group">
          <h4>语音控制</h4>
          
          <Form.Item
            name="speedRatio"
            label={`语速：${settings.speedRatio}x`}
          >
            <Slider
              min={0.2}
              max={3.0}
              step={0.1}
              marks={{
                0.2: '很慢',
                0.5: '慢',
                1.0: '正常',
                1.5: '快',
                2.0: '很快',
                3.0: '极快'
              }}
              tipFormatter={(value) => `${value}x`}
              className="speed-slider"
            />
          </Form.Item>

          <Form.Item
            name="volumeRatio"
            label={`音量：${Math.round(settings.volumeRatio * 100)}%`}
          >
            <Slider
              min={0.1}
              max={2.0}
              step={0.1}
              marks={{
                0.1: '很小',
                0.5: '小',
                1.0: '正常',
                1.5: '大',
                2.0: '很大'
              }}
              tipFormatter={(value) => `${Math.round((value || 0) * 100)}%`}
              className="volume-slider"
            />
          </Form.Item>

          <Form.Item
            name="pitchRatio"
            label={`音调：${settings.pitchRatio}x`}
          >
            <Slider
              min={0.5}
              max={2.0}
              step={0.1}
              marks={{
                0.5: '很低',
                0.8: '低',
                1.0: '正常',
                1.2: '高',
                2.0: '很高'
              }}
              tipFormatter={(value) => `${value}x`}
              className="pitch-slider"
            />
          </Form.Item>
        </div>

        <Divider />

        {/* 输出设置 */}
        <div className="settings-group">
          <h4>输出设置</h4>
          
          <Form.Item
            name="encoding"
            label="音频格式"
          >
            <Radio.Group className="encoding-radio-group">
              {encodingOptions.map(option => (
                <Radio.Button key={option.value} value={option.value} className="encoding-option">
                  <div>
                    <strong>{option.label}</strong>
                    {option.recommended && (
                      <span className="recommended-badge">推荐</span>
                    )}
                    <div className="option-description">{option.description}</div>
                  </div>
                </Radio.Button>
              ))}
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="sampleRate"
            label="音频质量"
          >
            <Select>
              {sampleRateOptions.map(option => (
                <Select.Option key={option.value} value={option.value}>
                  <div>
                    <strong>{option.label}</strong>
                    <span className="option-description"> - {option.description}</span>
                  </div>
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
        </div>

        {/* 快速预设 */}
        <div className="settings-group">
          <h4>快速预设</h4>
          <Space wrap>
            <Button onClick={() => form.setFieldsValue({ speedRatio: 0.8, pitchRatio: 0.9 })}>
              新闻播报
            </Button>
            <Button onClick={() => form.setFieldsValue({ speedRatio: 1.2, pitchRatio: 1.1 })}>
              活力讲解
            </Button>
            <Button onClick={() => form.setFieldsValue({ speedRatio: 0.9, pitchRatio: 0.95 })}>
              温和叙述
            </Button>
            <Button onClick={() => form.setFieldsValue({ speedRatio: 1.0, pitchRatio: 1.0, volumeRatio: 1.0 })}>
              重置默认
            </Button>
          </Space>
        </div>
      </Form>
    </Card>
  );
};

export default TTSBasicSettings;
```

### 3.2 高级设置 (TTSAdvancedSettings.tsx)

```tsx
import React, { useState } from 'react';
import { Collapse, Form, Select, Switch, Input, Alert, Space, Tooltip } from 'antd';
import { SettingOutlined, QuestionCircleOutlined, ExperimentOutlined } from '@ant-design/icons';

const { Panel } = Collapse;

const TTSAdvancedSettings: React.FC = () => {
  const [form] = Form.useForm();
  const [activeKey, setActiveKey] = useState<string[]>([]);

  return (
    <Collapse
      activeKey={activeKey}
      onChange={setActiveKey}
      className="tts-advanced-settings"
      ghost
    >
      <Panel
        header={
          <Space>
            <SettingOutlined />
            高级设置
            <span className="panel-description">专业控制选项，可精确调节合成效果</span>
          </Space>
        }
        key="advanced"
        className="advanced-panel"
      >
        <Form form={form} layout="vertical">
          {/* 语言设置 */}
          <div className="settings-group">
            <h4>语言设置</h4>
            
            <Form.Item
              name="explicitLanguage"
              label={
                <Space>
                  语种控制
                  <Tooltip title="精确控制文本语种识别方式，影响多语言混合的处理效果">
                    <QuestionCircleOutlined />
                  </Tooltip>
                </Space>
              }
              initialValue="zh"
            >
              <Select>
                <Select.Option value="">自动检测 - 智能识别语种</Select.Option>
                <Select.Option value="crosslingual">多语种混合 - 支持中英日等混读</Select.Option>
                <Select.Option value="zh">中文为主 - 支持中英混读</Select.Option>
                <Select.Option value="en">仅英文 - 纯英文处理</Select.Option>
                <Select.Option value="ja">仅日文 - 纯日文处理</Select.Option>
                <Select.Option value="es-mx">仅墨西哥语 - 纯墨西哥语处理</Select.Option>
                <Select.Option value="id">仅印尼语 - 纯印尼语处理</Select.Option>
                <Select.Option value="pt-br">仅巴西葡语 - 纯巴西葡萄牙语处理</Select.Option>
              </Select>
            </Form.Item>

            <Form.Item
              name="contextLanguage"
              label={
                <Space>
                  参考语种
                  <Tooltip title="为西欧语种提供参考语言，影响发音准确性">
                    <QuestionCircleOutlined />
                  </Tooltip>
                </Space>
              }
              initialValue=""
            >
              <Select>
                <Select.Option value="">默认(英语参考)</Select.Option>
                <Select.Option value="id">印尼语参考</Select.Option>
                <Select.Option value="es">西班牙语参考</Select.Option>
                <Select.Option value="pt">葡萄牙语参考</Select.Option>
              </Select>
            </Form.Item>
          </div>

          {/* 文本处理 */}
          <div className="settings-group">
            <h4>文本处理</h4>
            
            <Form.Item
              name="textType"
              label="文本类型"
              initialValue="plain"
            >
              <Select>
                <Select.Option value="plain">
                  <div>
                    <strong>纯文本</strong>
                    <div className="option-description">普通文本，自动处理标点和停顿</div>
                  </div>
                </Select.Option>
                <Select.Option value="ssml">
                  <div>
                    <strong>SSML标记语言</strong>
                    <div className="option-description">支持精确的语音控制标记</div>
                  </div>
                </Select.Option>
              </Select>
            </Form.Item>

            <Form.Item
              name="splitSentence"
              label={
                <Space>
                  分句处理
                  <Tooltip title="专门针对1.0音色的语速优化，解决语速过快问题">
                    <QuestionCircleOutlined />
                  </Tooltip>
                </Space>
              }
              valuePropName="checked"
              initialValue={false}
            >
              <Switch 
                checkedChildren="启用" 
                unCheckedChildren="禁用"
                className="setting-switch"
              />
            </Form.Item>
          </div>

          {/* 输出选项 */}
          <div className="settings-group">
            <h4>输出选项</h4>
            
            <Form.Item
              name="withTimestamp"
              label={
                <Space>
                  时间戳信息
                  <Tooltip title="返回文本的时间戳信息，用于字幕同步等高级功能">
                    <QuestionCircleOutlined />
                  </Tooltip>
                </Space>
              }
              valuePropName="checked"
              initialValue={false}
            >
              <Switch 
                checkedChildren="启用" 
                unCheckedChildren="禁用"
                className="setting-switch"
              />
            </Form.Item>

            <Form.Item
              name="audioOnly"
              label="仅返回音频"
              valuePropName="checked"
              initialValue={true}
            >
              <Switch 
                checkedChildren="仅音频" 
                unCheckedChildren="音频+元数据"
                className="setting-switch"
              />
            </Form.Item>
          </div>

          {/* 性能优化 */}
          <div className="settings-group">
            <h4>性能优化</h4>
            
            <Form.Item
              name="cacheEnabled"
              label={
                <Space>
                  智能缓存
                  <Tooltip title="缓存相同文本的合成结果，大幅提高重复内容的响应速度">
                    <QuestionCircleOutlined />
                  </Tooltip>
                </Space>
              }
              valuePropName="checked"
              initialValue={false}
              extra="启用后，相同文本的合成请求将直接返回缓存结果"
            >
              <Switch 
                checkedChildren="启用" 
                unCheckedChildren="禁用"
                className="setting-switch"
              />
            </Form.Item>

            <Form.Item
              name="cluster"
              label="处理集群"
              initialValue="volcano_icl"
            >
              <Select>
                <Select.Option value="volcano_icl">
                  <div>
                    <strong>标准集群</strong>
                    <div className="option-description">平衡性能和质量，适合大多数场景</div>
                  </div>
                </Select.Option>
                <Select.Option value="volcano_icl_concurr">
                  <div>
                    <strong>并发集群</strong>
                    <div className="option-description">高并发处理，适合大量请求场景</div>
                  </div>
                </Select.Option>
              </Select>
            </Form.Item>
          </div>

          {/* 实验性功能 */}
          <div className="settings-group experimental">
            <h4>
              <Space>
                <ExperimentOutlined />
                实验性功能
              </Space>
            </h4>
            
            <Alert
              message="实验性功能"
              description="以下功能可能不稳定，建议在测试环境中使用"
              type="warning"
              showIcon
              className="experimental-warning"
            />

            <Form.Item
              name="voiceOptimization"
              label="音质增强"
              valuePropName="checked"
              initialValue={false}
            >
              <Switch 
                checkedChildren="启用" 
                unCheckedChildren="禁用"
                className="setting-switch"
              />
            </Form.Item>

            <Form.Item
              name="adaptiveSpeed"
              label="自适应语速"
              valuePropName="checked"
              initialValue={false}
            >
              <Switch 
                checkedChildren="启用" 
                unCheckedChildren="禁用"
                className="setting-switch"
              />
            </Form.Item>
          </div>

          {/* 自定义参数 */}
          <div className="settings-group">
            <h4>自定义参数</h4>
            
            <Form.Item
              name="customParameters"
              label="额外参数"
              extra="高级用户可输入JSON格式的额外参数"
            >
              <Input.TextArea
                placeholder='例如: {"custom_param": "value"}'
                rows={3}
              />
            </Form.Item>
          </div>
        </Form>
      </Panel>
    </Collapse>
  );
};

export default TTSAdvancedSettings;
```

## 4. 样式设计 (CSS)

### 4.1 组件样式 (VoiceSettings.css)

```css
/* 语音设置主样式 */
.voice-settings-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.voice-clone-basic-settings,
.tts-basic-settings {
  margin-bottom: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 设置分组样式 */
.settings-group {
  margin-bottom: 24px;
}

.settings-group h4 {
  color: #1f2937;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  border-left: 4px solid #3b82f6;
  padding-left: 12px;
}

/* 必填标记 */
.required-mark {
  color: #ef4444;
  font-weight: bold;
}

/* 推荐标记 */
.recommended-badge {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 12px;
  margin-left: 8px;
  font-weight: 500;
}

.advanced-badge {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  color: white;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 12px;
  margin-left: 8px;
  font-weight: 500;
}

/* 选项描述 */
.option-description {
  color: #6b7280;
  font-size: 12px;
  margin-top: 2px;
}

.model-option {
  padding: 4px 0;
}

.model-label {
  display: flex;
  align-items: center;
}

.model-description {
  color: #6b7280;
  font-size: 12px;
  margin-top: 2px;
}

/* 音频上传区域 */
.audio-upload-dragger {
  border: 2px dashed #d1d5db !important;
  border-radius: 8px !important;
  background: #fafafa !important;
  transition: all 0.3s ease;
}

.audio-upload-dragger:hover {
  border-color: #3b82f6 !important;
  background: #f0f9ff !important;
}

.audio-upload-dragger.ant-upload-drag-hover {
  border-color: #3b82f6 !important;
}

/* 滑块样式 */
.speed-slider .ant-slider-track {
  background: linear-gradient(to right, #ef4444, #f59e0b, #10b981);
}

.volume-slider .ant-slider-track {
  background: linear-gradient(to right, #6b7280, #3b82f6);
}

.pitch-slider .ant-slider-track {
  background: linear-gradient(to right, #8b5cf6, #ec4899);
}

/* 编码选项样式 */
.encoding-radio-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.encoding-option {
  height: auto !important;
  padding: 12px !important;
  text-align: left;
  border-radius: 8px !important;
}

.encoding-option > div {
  width: 100%;
}

/* 预估信息卡片 */
.estimation-info {
  margin-top: 24px;
}

.info-card {
  background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
  border: 1px solid #bae6fd;
  border-radius: 8px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.info-row:last-child {
  margin-bottom: 0;
}

/* 高级设置面板 */
.voice-clone-advanced-settings,
.tts-advanced-settings {
  margin-top: 16px;
}

.advanced-panel .ant-collapse-header {
  padding: 16px 24px !important;
  background: #f8fafc;
  border-radius: 8px;
  margin-bottom: 16px;
}

.panel-description {
  color: #6b7280;
  font-size: 13px;
  font-weight: normal;
}

.advanced-warning,
.experimental-warning {
  margin-bottom: 24px;
}

/* 实验性功能样式 */
.settings-group.experimental {
  padding: 16px;
  background: #fef3c7;
  border: 1px solid #f59e0b;
  border-radius: 8px;
  margin-top: 24px;
}

.settings-group.experimental h4 {
  color: #92400e;
  border-left-color: #f59e0b;
}

/* 开关样式 */
.setting-switch {
  min-width: 60px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .voice-settings-container {
    padding: 16px;
  }
  
  .encoding-radio-group {
    grid-template-columns: 1fr;
  }
  
  .info-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .settings-group h4 {
    color: #f9fafb;
  }
  
  .option-description,
  .model-description,
  .panel-description {
    color: #9ca3af;
  }
  
  .info-card {
    background: linear-gradient(135deg, #1e293b, #334155);
    border-color: #475569;
  }
  
  .audio-upload-dragger {
    background: #374151 !important;
    border-color: #6b7280 !important;
  }
  
  .audio-upload-dragger:hover {
    background: #4b5563 !important;
    border-color: #3b82f6 !important;
  }
}
```

## 5. 使用示例

### 5.1 主组件集成 (VoiceSettingsPage.tsx)

```tsx
import React, { useState } from 'react';
import { Layout, Steps, Button, Space, message } from 'antd';
import VoiceCloneBasicSettings from './components/VoiceCloneBasicSettings';
import VoiceCloneAdvancedSettings from './components/VoiceCloneAdvancedSettings';
import TTSBasicSettings from './components/TTSBasicSettings';
import TTSAdvancedSettings from './components/TTSAdvancedSettings';
import './VoiceSettings.css';

const { Content } = Layout;

const VoiceSettingsPage: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const steps = [
    {
      title: '音色克隆',
      description: '创建或选择音色',
      content: (
        <>
          <VoiceCloneBasicSettings />
          <VoiceCloneAdvancedSettings />
        </>
      )
    },
    {
      title: '语音合成',
      description: '配置合成参数',
      content: (
        <>
          <TTSBasicSettings />
          <TTSAdvancedSettings />
        </>
      )
    },
    {
      title: '预览确认',
      description: '检查设置并测试',
      content: <div>预览和确认组件</div>
    }
  ];

  const handleNext = () => {
    setCurrentStep(currentStep + 1);
  };

  const handlePrev = () => {
    setCurrentStep(currentStep - 1);
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      // 提交设置逻辑
      message.success('设置保存成功！');
    } catch (error) {
      message.error('设置保存失败，请重试');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Layout className="voice-settings-container">
      <Content>
        <Steps current={currentStep} className="settings-steps">
          {steps.map(item => (
            <Steps.Step 
              key={item.title} 
              title={item.title} 
              description={item.description} 
            />
          ))}
        </Steps>

        <div className="settings-content">
          {steps[currentStep].content}
        </div>

        <div className="settings-actions">
          <Space>
            {currentStep > 0 && (
              <Button onClick={handlePrev}>上一步</Button>
            )}
            {currentStep < steps.length - 1 && (
              <Button type="primary" onClick={handleNext}>下一步</Button>
            )}
            {currentStep === steps.length - 1 && (
              <Button 
                type="primary" 
                loading={isSubmitting}
                onClick={handleSubmit}
              >
                完成设置
              </Button>
            )}
          </Space>
        </div>
      </Content>
    </Layout>
  );
};

export default VoiceSettingsPage;
```

## 总结

这套界面设计方案具有以下特点：

1. **分层设计** - 基础设置简单易用，高级设置专业可控
2. **用户友好** - 清晰的标签、描述和视觉反馈
3. **响应式** - 适配不同屏幕尺寸和设备
4. **可扩展** - 易于添加新参数和功能
5. **类型安全** - 完整的TypeScript类型定义

通过这样的设计，既能满足普通用户的简单需求，也为专业用户提供了精细控制的能力。