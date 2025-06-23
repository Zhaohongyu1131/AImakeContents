# DataSay API设计规范

## 概述

DataSay API 是一个企业级多模态内容创作平台的RESTful API，支持文本、语音、图像/视频的智能生成与管理。API设计遵循RESTful规范，采用JSON格式进行数据交换。

## 基础信息

- **基础URL**: `https://api.datasay.com/v1`
- **协议**: HTTPS
- **数据格式**: JSON
- **字符编码**: UTF-8
- **API版本**: v1

## 认证机制

### JWT Bearer Token 认证
```http
Authorization: Bearer <jwt_token>
```

### 认证流程
1. 用户登录获取JWT Token
2. 在后续请求头中携带Token
3. Token有效期为24小时
4. 支持Token刷新机制

## 通用响应格式

### 成功响应格式
```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {
    // 具体数据内容
  },
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "req_123456789"
}
```

### 错误响应格式
```json
{
  "success": false,
  "code": 400,
  "message": "请求参数错误",
  "error": {
    "type": "ValidationError",
    "details": "用户名不能为空"
  },
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "req_123456789"
}
```

### HTTP状态码规范
- `200` - 成功
- `201` - 创建成功
- `400` - 请求参数错误
- `401` - 未授权
- `403` - 权限不足
- `404` - 资源不存在
- `409` - 资源冲突
- `422` - 数据验证失败
- `429` - 请求频率限制
- `500` - 服务器内部错误

## API模块设计

## 1. 用户认证模块 (/auth)

### 1.1 用户注册
```http
POST /auth/user/register
```

**请求参数**:
```json
{
  "user_name": "testuser",
  "user_email": "test@example.com",
  "user_password": "password123",
  "user_phone": "13800138000"
}
```

**响应数据**:
```json
{
  "success": true,
  "data": {
    "user_id": 1001,
    "user_name": "testuser",
    "user_email": "test@example.com",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_in": 86400
  }
}
```

### 1.2 用户登录
```http
POST /auth/user/login
```

**请求参数**:
```json
{
  "user_email": "test@example.com",
  "user_password": "password123"
}
```

### 1.3 刷新Token
```http
POST /auth/token/refresh
```

### 1.4 用户登出
```http
POST /auth/user/logout
```

## 2. 文件管理模块 (/files)

### 2.1 文件上传
```http
POST /files/storage/upload
Content-Type: multipart/form-data
```

**请求参数**:
```
file: <binary_file>
file_type: "audio" | "image" | "video" | "document"
```

**响应数据**:
```json
{
  "success": true,
  "data": {
    "file_id": 10001,
    "file_name": "generated_20240101_120000.wav",
    "file_original_name": "my_audio.wav",
    "file_path": "/storage/audio/2024/01/generated_20240101_120000.wav",
    "file_size": 1048576,
    "file_type": "audio",
    "file_url": "https://cdn.datasay.com/audio/2024/01/generated_20240101_120000.wav"
  }
}
```

### 2.2 文件下载
```http
GET /files/storage/download/{file_id}
```

### 2.3 文件删除
```http
DELETE /files/storage/delete/{file_id}
```

## 3. 文本内容模块 (/text)

### 3.1 创建文本内容
```http
POST /text/content/create
```

**请求参数**:
```json
{
  "text_title": "营销文案标题",
  "text_content": "这是一个营销文案的内容...",
  "text_content_type": "article",
  "text_language": "zh-CN",
  "text_tags": ["营销", "产品推广"],
  "text_template_id": 1001
}
```

**响应数据**:
```json
{
  "success": true,
  "data": {
    "text_id": 20001,
    "text_title": "营销文案标题",
    "text_content": "这是一个营销文案的内容...",
    "text_word_count": 256,
    "text_status": "published",
    "text_created_time": "2024-01-01T12:00:00Z"
  }
}
```

### 3.2 文本列表查询
```http
GET /text/content/list?page=1&size=20&content_type=article&status=published
```

### 3.3 文本详情查询
```http
GET /text/content/detail/{text_id}
```

### 3.4 文本内容更新
```http
PUT /text/content/update/{text_id}
```

### 3.5 文本内容删除
```http
DELETE /text/content/delete/{text_id}
```

### 3.6 文本分析
```http
POST /text/analyse/submit
```

**请求参数**:
```json
{
  "text_id": 20001,
  "analyse_type": "sentiment" // sentiment, keyword, summary, readability
}
```

**响应数据**:
```json
{
  "success": true,
  "data": {
    "analyse_id": 30001,
    "text_id": 20001,
    "analyse_type": "sentiment",
    "analyse_result": {
      "sentiment": "positive",
      "confidence": 0.85,
      "emotions": {
        "joy": 0.6,
        "trust": 0.4,
        "fear": 0.1
      }
    },
    "analyse_score": 85.5
  }
}
```

### 3.7 文本模板管理
```http
POST /text/template/create    # 创建模板
GET  /text/template/list      # 模板列表
GET  /text/template/detail/{template_id}  # 模板详情
PUT  /text/template/update/{template_id}  # 更新模板
DELETE /text/template/delete/{template_id} # 删除模板
```

## 4. 语音内容模块 (/voice)

### 4.1 音色管理子模块 (/voice/timbre)

#### 4.1.1 创建音色
```http
POST /voice/timbre/create
```

**请求参数**:
```json
{
  "timbre_name": "专业男声",
  "timbre_description": "成熟稳重的商务男声",
  "timbre_source_file_id": 10001,
  "timbre_language": "zh-CN",
  "timbre_gender": "male",
  "timbre_style": "professional"
}
```

**响应数据**:
```json
{
  "success": true,
  "data": {
    "timbre_id": 30001,
    "timbre_name": "专业男声",
    "timbre_status": "training",
    "clone_id": 30101,
    "estimated_completion_time": "2024-01-01T12:30:00Z",
    "timbre_created_time": "2024-01-01T12:00:00Z"
  }
}
```

#### 4.1.2 音色克隆状态查询
```http
GET /voice/timbre/clone/status/{clone_id}
```

#### 4.1.3 音色列表查询
```http
GET /voice/timbre/list?page=1&size=20&status=ready&gender=male
```

#### 4.1.4 音色管理
```http
GET /voice/timbre/detail/{timbre_id}      # 音色详情
PUT /voice/timbre/update/{timbre_id}      # 更新音色信息
DELETE /voice/timbre/delete/{timbre_id}   # 删除音色
```

#### 4.1.5 音色模板管理
```http
POST /voice/timbre/template/create    # 创建音色模板
GET  /voice/timbre/template/list      # 模板列表
GET  /voice/timbre/template/detail/{template_id}  # 模板详情
PUT  /voice/timbre/template/update/{template_id}  # 更新模板
DELETE /voice/timbre/template/delete/{template_id} # 删除模板
```

### 4.2 音频合成子模块 (/voice/audio)

#### 4.2.1 音频合成
```http
POST /voice/audio/create
```

**请求参数**:
```json
{
  "audio_title": "产品介绍音频",
  "audio_text_content": "欢迎使用我们的产品，这是一个创新的解决方案...",
  "audio_timbre_id": 30001,
  "audio_language": "zh-CN",
  "audio_speed": 1.0,
  "audio_pitch": 1.0,
  "audio_volume": 1.0,
  "audio_template_id": 40001
}
```

**响应数据**:
```json
{
  "success": true,
  "data": {
    "audio_id": 50001,
    "audio_title": "产品介绍音频",
    "audio_duration": 45.6,
    "audio_file_id": 10002,
    "audio_file_url": "https://cdn.datasay.com/audio/2024/01/audio_50001.wav",
    "audio_status": "completed",
    "audio_created_time": "2024-01-01T12:00:00Z"
  }
}
```

#### 4.2.2 音频合成状态查询
```http
GET /voice/audio/status/{audio_id}
```

#### 4.2.3 音频内容列表
```http
GET /voice/audio/list?page=1&size=20&timbre_id=30001&status=completed
```

#### 4.2.4 音频分析
```http
POST /voice/audio/analyse/submit
```

**请求参数**:
```json
{
  "audio_id": 50001,
  "analyse_type": "quality" // quality, emotion, clarity, noise, similarity
}
```

**响应数据**:
```json
{
  "success": true,
  "data": {
    "analyse_id": 60001,
    "audio_id": 50001,
    "analyse_type": "quality",
    "analyse_result": {
      "overall_quality": 8.5,
      "clarity_score": 9.2,
      "noise_level": 0.1,
      "naturalness": 8.8
    },
    "analyse_score": 85.0
  }
}
```

#### 4.2.5 音频管理
```http
GET /voice/audio/detail/{audio_id}        # 音频详情
PUT /voice/audio/update/{audio_id}        # 更新音频信息
DELETE /voice/audio/delete/{audio_id}     # 删除音频
```

#### 4.2.6 音频模板管理
```http
POST /voice/audio/template/create    # 创建音频模板
GET  /voice/audio/template/list      # 模板列表
GET  /voice/audio/template/detail/{template_id}  # 模板详情
PUT  /voice/audio/template/update/{template_id}  # 更新模板
DELETE /voice/audio/template/delete/{template_id} # 删除模板
```

## 5. 图像视频模块 (/image)

### 5.1 图像生成
```http
POST /image/content/create
```

**请求参数**:
```json
{
  "image_title": "产品宣传图",
  "image_prompt": "一个现代简约风格的产品展示图，白色背景，专业摄影",
  "image_type": "image",
  "image_width": 1024,
  "image_height": 1024,
  "image_template_id": 3001
}
```

**响应数据**:
```json
{
  "success": true,
  "data": {
    "image_id": 50001,
    "image_title": "产品宣传图",
    "image_file_id": 10003,
    "image_file_url": "https://cdn.datasay.com/image/2024/01/image_50001.jpg",
    "image_width": 1024,
    "image_height": 1024,
    "image_status": "completed",
    "image_created_time": "2024-01-01T12:00:00Z"
  }
}
```

### 5.2 视频生成
```http
POST /image/content/create
```

**请求参数**:
```json
{
  "image_title": "产品演示视频",
  "image_prompt": "展示产品使用过程的短视频，时长30秒",
  "image_type": "video",
  "image_duration": 30.0,
  "image_template_id": 3002
}
```

### 5.3 图像视频列表
```http
GET /image/content/list?page=1&size=20&type=image&status=completed
```

### 5.4 图像视频分析
```http
POST /image/analyse/submit
```

## 6. 混合内容模块 (/mixall)

### 6.1 创建混合作品
```http
POST /mixall/content/create
```

**请求参数**:
```json
{
  "mixall_title": "产品宣传视频",
  "mixall_description": "结合文案、语音和视频的完整宣传作品",
  "mixall_type": "video_with_voice",
  "mixall_text_id": 20001,
  "mixall_audio_id": 50001,
  "mixall_image_ids": [50001, 50002, 50003]
}
```

**响应数据**:
```json
{
  "success": true,
  "data": {
    "mixall_id": 60001,
    "mixall_title": "产品宣传视频",
    "mixall_status": "processing",
    "task_id": "task_uuid_123456",
    "mixall_created_time": "2024-01-01T12:00:00Z"
  }
}
```

### 6.2 混合作品状态查询
```http
GET /mixall/content/status/{mixall_id}
```

### 6.3 混合作品列表
```http
GET /mixall/content/list?page=1&size=20&type=video_with_voice&status=completed
```

## 7. 任务管理模块 (/task)

### 7.1 任务状态查询
```http
GET /task/management/status/{task_uuid}
```

**响应数据**:
```json
{
  "success": true,
  "data": {
    "task_id": 70001,
    "task_uuid": "task_uuid_123456",
    "task_name": "混合内容生成",
    "task_type": "mixall_generate",
    "task_status": "running",
    "task_progress": 65,
    "task_created_time": "2024-01-01T12:00:00Z",
    "task_started_time": "2024-01-01T12:01:00Z",
    "estimated_completion_time": "2024-01-01T12:05:00Z"
  }
}
```

### 7.2 用户任务列表
```http
GET /task/management/list?page=1&size=20&status=running&type=voice_synthesize
```

### 7.3 取消任务
```http
POST /task/management/cancel/{task_uuid}
```

## 8. 豆包API封装模块 (/doubao)

### 8.1 音色相关接口

#### 8.1.1 平台音色列表
```http
GET /doubao/voice/timbre/list
```

**响应数据**:
```json
{
  "success": true,
  "data": {
    "speakers": [
      {
        "speaker_id": "volcano_speaker_001",
        "speaker_name": "温和女声",
        "language": "zh-CN",
        "gender": "female",
        "style": "gentle"
      }
    ]
  }
}
```

#### 8.1.2 音色克隆
```http
POST /doubao/voice/timbre/clone/submit
```

**请求参数**:
```json
{
  "timbre_name": "自定义音色名称",
  "timbre_source_file_id": 10004,
  "timbre_description": "温和的男声",
  "clone_params": {
    "quality": "high",
    "training_duration": 30
  }
}
```

**响应数据**:
```json
{
  "success": true,
  "data": {
    "clone_task_id": "clone_task_123456",
    "estimated_time": 1800,
    "status": "submitted"
  }
}
```

#### 8.1.3 音色克隆状态查询
```http
GET /doubao/voice/timbre/clone/status/{task_id}
```

### 8.2 音频合成接口

#### 8.2.1 音频合成
```http
POST /doubao/voice/audio/synthesize
```

**请求参数**:
```json
{
  "text": "要合成的文本内容",
  "timbre_id": "volcano_speaker_001",
  "speed": 1.0,
  "pitch": 1.0,
  "volume": 1.0,
  "audio_format": "wav"
}
```

**响应数据**:
```json
{
  "success": true,
  "data": {
    "synthesis_task_id": "tts_task_123456",
    "estimated_time": 30,
    "status": "processing"
  }
}
```

### 8.3 文本相关接口

#### 8.3.1 文本生成
```http
POST /doubao/text/generate
```

**请求参数**:
```json
{
  "prompt": "写一个关于人工智能的文章",
  "max_tokens": 1000,
  "temperature": 0.7,
  "content_type": "article"
}
```

### 8.4 图像相关接口

#### 8.4.1 图像生成
```http
POST /doubao/image/generate
```

**请求参数**:
```json
{
  "prompt": "一个美丽的日落景色",
  "image_size": "1024x1024",
  "style": "realistic"
}
```

## 9. 平台集成模块 (/platform)

### 9.1 抖音平台集成

#### 9.1.1 授权配置
```http
POST /platform/douyin/auth/config
```

#### 9.1.2 内容发布
```http
POST /platform/douyin/publish/content
```

**请求参数**:
```json
{
  "content_type": "mixall",
  "content_id": 60001,
  "publish_title": "我的新作品",
  "publish_description": "这是一个很棒的内容",
  "publish_tags": ["AI", "创作", "视频"]
}
```

### 9.2 微信平台集成

#### 9.2.1 授权配置
```http
POST /platform/weixin/auth/config
```

#### 9.2.2 内容发布
```http
POST /platform/weixin/publish/content
```

## API调用示例

### 完整的内容创作流程示例

```javascript
// 1. 用户登录
const loginResponse = await fetch('/auth/user/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_email: 'user@example.com',
    user_password: 'password123'
  })
});
const { access_token } = loginResponse.data;

// 2. 创建文本内容
const textResponse = await fetch('/text/content/create', {
  method: 'POST',
  headers: { 
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json' 
  },
  body: JSON.stringify({
    text_title: '产品介绍文案',
    text_content: '我们的产品具有创新的功能...',
    text_content_type: 'script'
  })
});
const { text_id } = textResponse.data;

// 3. 创建或选择音色
const timbreResponse = await fetch('/voice/timbre/list', {
  method: 'GET',
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const timbre_id = timbreResponse.data.timbres[0].timbre_id; // 选择一个音色

// 4. 基于文本和音色生成音频
const audioResponse = await fetch('/voice/audio/create', {
  method: 'POST',
  headers: { 
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json' 
  },
  body: JSON.stringify({
    audio_title: '产品介绍音频',
    audio_text_content: textResponse.data.text_content,
    audio_timbre_id: timbre_id
  })
});
const { audio_id } = audioResponse.data;

// 5. 生成配套图像
const imageResponse = await fetch('/image/content/create', {
  method: 'POST',
  headers: { 
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json' 
  },
  body: JSON.stringify({
    image_title: '产品宣传图',
    image_prompt: '现代简约的产品展示图',
    image_type: 'image'
  })
});
const { image_id } = imageResponse.data;

// 6. 创建混合作品
const mixallResponse = await fetch('/mixall/content/create', {
  method: 'POST',
  headers: { 
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json' 
  },
  body: JSON.stringify({
    mixall_title: '完整产品宣传作品',
    mixall_type: 'video_with_voice',
    mixall_text_id: text_id,
    mixall_audio_id: audio_id,
    mixall_image_ids: [image_id]
  })
});

// 7. 查询任务状态
const taskStatus = await fetch(`/task/management/status/${mixallResponse.data.task_id}`, {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
```

## 错误处理指南

### 常见错误码说明

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 40001 | 参数验证失败 | 检查请求参数格式和必填字段 |
| 40002 | 认证失效 | 重新登录获取新Token |
| 40003 | 权限不足 | 联系管理员开通相应权限 |
| 40004 | 资源不存在 | 确认资源ID是否正确 |
| 40005 | 资源已存在 | 使用不同的资源名称 |
| 50001 | 第三方API调用失败 | 检查网络连接和API配置 |
| 50002 | 文件处理失败 | 检查文件格式和大小限制 |
| 50003 | 任务队列满 | 稍后重试或联系技术支持 |

### 重试机制建议
- 对于5xx错误，建议实现指数退避重试
- 对于任务相关API，建议轮询查询状态
- 对于文件上传，建议实现断点续传

## API限流规则

### 限流策略
- **用户级别限流**: 每用户每分钟最多100次请求
- **IP级别限流**: 每IP每分钟最多500次请求
- **API级别限流**: 生成类API每用户每小时最多50次

### 限流响应头
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1609459200
```

## API版本控制

### 版本策略
- URL路径版本控制: `/v1/`, `/v2/`
- 向后兼容至少支持2个版本
- 新版本发布前30天通知客户端升级

### 版本迁移指南
- 提供版本对比文档
- 提供迁移工具和示例代码
- 设置过渡期和废弃时间表

## 安全规范

### 数据安全
- 所有敏感数据传输使用HTTPS
- API密钥定期轮换
- 请求参数验证和SQL注入防护

### 访问控制
- 基于JWT的身份认证
- 基于角色的访问控制(RBAC)
- API调用审计日志记录

## 监控和日志

### 监控指标
- API响应时间
- 错误率统计
- 调用量统计
- 用户活跃度

### 日志格式
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "req_123456789",
  "user_id": 1001,
  "api_path": "/text/content/create",
  "method": "POST",
  "status_code": 200,
  "response_time": 234,
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0..."
}
```