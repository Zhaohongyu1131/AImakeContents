# DataSay - 企业级语音克隆与合成平台

DataSay是一个基于现代技术栈构建的企业级语音克隆与合成平台，提供高质量的语音生成服务。

## 🏗️ 技术架构

### 核心技术栈
- **后端**: Python 3.8+ FastAPI + SQLAlchemy 2.0 + PostgreSQL
- **前端**: React 18 + TypeScript + Vite + Ant Design
- **AI处理**: PyTorch + 火山引擎语音服务
- **容器化**: Docker + Docker Compose
- **缓存**: Redis
- **任务队列**: Celery

### 系统特性
- 🎯 **多平台音色支持** - 支持火山引擎、Azure等多个TTS平台
- 🔊 **高质量语音克隆** - 基于先进的AI模型进行语音克隆
- 📊 **实时监控** - 完整的系统监控和性能指标
- 🔒 **企业级安全** - 多租户架构，完善的权限控制
- 🚀 **高性能** - 异步处理，支持高并发
- 📱 **多端支持** - Web端、移动端、API接口

## 🚀 快速开始

### 环境要求
- Docker & Docker Compose
- Python 3.8+
- Node.js 16+

### 数据库配置

#### 统一PostgreSQL配置

本项目使用统一的PostgreSQL数据库配置：

- **数据库服务器**: PostgreSQL 15
- **用户名**: DataSayai
- **密码**: DataSayai123
- **默认数据库**: DataSay
- **端口**: 5433
