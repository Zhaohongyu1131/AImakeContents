# DataSay Frontend

DataSay 前端应用 - 企业级多模态内容创作平台用户端

## 🚀 技术栈

- **React 18** - 用户界面库
- **TypeScript** - 类型安全的JavaScript
- **Vite** - 快速构建工具
- **Ant Design 5** - 企业级UI组件库
- **React Router DOM** - 客户端路由
- **Zustand** - 轻量级状态管理
- **Axios** - HTTP客户端

## 📁 项目结构

```
frontend/
├── src/
│   ├── components/          # 组件目录
│   │   └── layout/         # 布局组件
│   ├── pages/              # 页面目录
│   │   ├── auth/          # 认证页面
│   │   ├── text/          # 文本相关页面
│   │   ├── voice/         # 语音相关页面
│   │   │   ├── timbre/    # 音色管理
│   │   │   └── audio/     # 音频管理
│   │   ├── image/         # 图像视频页面
│   │   ├── mixall/        # 混合内容页面
│   │   ├── settings/      # 设置页面
│   │   └── error/         # 错误页面
│   ├── services/          # 服务层
│   │   └── http/          # HTTP客户端
│   ├── stores/            # 状态管理
│   │   └── app/           # 应用状态
│   ├── types/             # 类型定义
│   ├── utils/             # 工具函数
│   ├── hooks/             # 自定义hooks
│   └── assets/            # 静态资源
├── public/                # 公共资源
└── package.json
```

## 🏗️ 开发规范

### 命名约定

严格遵循 `[业务模块][数据对象][操作][属性/修饰符]` 命名规范：

**组件命名**:
- `TextContentCreate.tsx` - [Text][Content][Create]
- `VoiceTimbreList.tsx` - [Voice][Timbre][List]
- `VoiceAudioManage.tsx` - [Voice][Audio][Manage]

**函数命名**:
- `textContentCreateSubmit()` - [text][content][create][submit]
- `voiceTimbreListLoad()` - [voice][timbre][list][load]
- `appThemeToggle()` - [app][theme][toggle]

**状态管理**:
- `useTextStore()` - [text][store]
- `useVoiceTimbreStore()` - [voice][timbre][store]
- `useAppStore()` - [app][store]

## 🛠️ 开发指南

### 环境设置

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

### 代码质量

```bash
# 代码检查
npm run lint

# 代码格式化
npm run format

# 类型检查
npm run type-check

# 运行测试
npm run test
```

### 环境配置

复制 `.env.example` 为 `.env` 并配置相应环境变量：

```bash
cp .env.example .env
```

## 🔗 API集成

前端通过统一的HTTP客户端与后端API通信：

```typescript
import { httpClient } from '@/services/http/httpClient'

// GET请求
const response = await httpClient.get('/text/content/list')

// POST请求
const result = await httpClient.post('/text/content/create', {
  text_title: '标题',
  text_content: '内容'
})
```

## 🎨 样式规范

- 使用Ant Design组件库统一视觉风格
- 自定义样式遵循BEM命名规范
- 支持浅色/深色主题切换
- 响应式设计适配移动端

## 📱 路由结构

```
/ - 首页
/auth/login - 登录
/auth/register - 注册
/text/content - 文本内容列表
/text/content/create - 创建文本
/voice/timbre - 音色管理
/voice/audio - 音频管理  
/image/content - 图像内容
/mixall/content - 混合内容
/settings - 系统设置
```

## 🔧 构建配置

项目使用Vite作为构建工具，配置文件为 `vite.config.ts`：

- 支持TypeScript
- 路径别名配置
- 开发代理配置
- 生产构建优化

## 📦 部署

### 开发环境部署

```bash
# 启动开发服务器
npm run dev
```

### 生产环境部署

```bash
# 构建生产版本
npm run build

# 部署dist目录到静态服务器
```

## 🤝 开发协作

- 提交代码前运行 `npm run lint` 和 `npm run type-check`
- 遵循组件开发规范和命名约定
- 保持代码简洁和注释完整
- 及时更新类型定义