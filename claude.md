# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DataSay is an enterprise-grade voice cloning and synthesis platform built with modern technology stack. The platform provides high-quality voice generation services, supporting multiple TTS platforms including Volcano Engine (ByteDance), Azure, and others.

**Current Status**: The project is in early planning/design phase. Backend and frontend directories exist but are mostly empty - only documentation and configuration files are present.

## Architecture & Technology Stack

### Backend (Not Yet Implemented)
- **Framework**: FastAPI 0.115.6 + Uvicorn 0.30.0
- **Database**: PostgreSQL 15 (async with SQLAlchemy 2.0 + AsyncPG)
- **Authentication**: JWT (Python-JOSE + Passlib/bcrypt)
- **Task Queue**: Celery 5.3.4 + Redis
- **AI/Audio**: PyTorch 2.3.1, Torchaudio, Librosa
- **Monitoring**: Prometheus + custom instrumentator

### Frontend (Not Yet Implemented)
Two separate React applications planned:
1. **User Frontend** (`frontend/`): React 18 + TypeScript + Vite + Ant Design
2. **Admin UI** (`admin-ui/`): React 18 + TypeScript + Vite + Ant Design

### Database Configuration
```bash
# PostgreSQL connection (from .env)
Host: localhost:5433
Database: datasay
Username: datasayai  
Password: datasayai123
URL: postgresql+asyncpg://datasayai:datasayai123@localhost:5433/datasay
```

## Service Ports
- Backend API: 8000
- Frontend: 3000
- Admin UI: 3001
- PostgreSQL: 5433
- Redis: 6379

## Business Domain Structure

Follow business-driven directory organization (not technical/architectural):

### Core API Modules
- **Volcano Engine Integration** (`/doubao/`):
  - Voice services: `/doubao/voice/`, `/doubao/voice/manage`, `/doubao/voice/clone`, `/doubao/voice/tts`
  - Text services: `/doubao/text/`
  - Image/Video: `/doubao/image/`

- **Business Logic**:
  - Text: `/text/`, `/text/analyse`, `/text/create`, `/text/manage`, `/text/template`
  - Voice: `/voice/`, `/voice/analyse`, `/voice/create`, `/voice/manage`, `/voice/template`
  - Image/Video: `/image/`, `/image/analyse`, `/image/create`, `/image/manage`, `/image/template`
  - Mixed content: `/mixall/`

- **Foundation Services**:
  - Authentication: `/auth/`
  - File management: `/files/`
  - Platform integrations: `/platform/douyin`, `/platform/weixin`

## External Service Integration

### Volcano Engine (ByteDance) Configuration
```bash
# Main voice service
VOLCANO_VOICE_APPID=2393689094
VOLCANO_VOICE_ACCESS_TOKEN=fQsIoCui-VRAhDKSG2uGPjkmK8GeZ8sr
VOLCANO_VOICE_CLUSTER=volcano_icl

# API endpoints
Voice Clone API: https://openspeech.bytedance.com/api/v1/mega_tts/audio/upload
TTS API: https://openspeech.bytedance.com/api/v1/tts
WebSocket API: wss://openspeech.bytedance.com/api/v1/tts/ws_binary
```

## Development Commands

Since the project is not yet implemented, these are the intended commands based on the architecture:

### Backend Development
```bash
# Navigate to backend directory
cd backend/

# Install dependencies (when implemented)
pip install -r requirements.txt

# Run database migrations (when implemented)
alembic upgrade head

# Start development server (when implemented)
uvicorn app.main:app --reload --port 8000

# Run tests (when implemented)
pytest

# Run linting (when implemented)
flake8 app/
black app/
```

### Frontend Development
```bash
# Navigate to frontend directory
cd frontend/

# Install dependencies (when implemented)
npm install

# Start development server (when implemented)
npm run dev

# Build for production (when implemented)
npm run build

# Run tests (when implemented)
npm run test

# Run linting (when implemented)
npm run lint
```

### Docker Development
```bash
# Start all services (when implemented)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## File Structure Conventions

Follow the naming conventions from user's global CLAUDE.md:
**Naming and Directory Conventions**: All Programming Languages Must Strictly Adhere to the Following Principles
- Name folders using business names
- Split directories by business classification, not by technology or architecture  
- Use [Business Module][Data Object][Action][Attribute/Modifier] to name directories, files, and functions
- When coding, must verify the implementation of this naming convention

### Complete Naming Convention Examples

#### Backend API Structure
```bash
backend/app/api/v1/
├── text/
│   ├── text_content_create.py      # [text][content][create]
│   ├── text_content_manage.py      # [text][content][manage]
│   ├── text_analyse_submit.py      # [text][analyse][submit]
│   └── text_template_manage.py     # [text][template][manage]
├── voice/
│   ├── timbre/
│   │   ├── voice_timbre_create.py  # [voice][timbre][create]
│   │   ├── voice_timbre_manage.py  # [voice][timbre][manage]
│   │   ├── voice_timbre_clone.py   # [voice][timbre][clone]
│   │   └── voice_timbre_template.py # [voice][timbre][template]
│   └── audio/
│       ├── voice_audio_create.py   # [voice][audio][create]
│       ├── voice_audio_manage.py   # [voice][audio][manage]
│       ├── voice_audio_analyse.py  # [voice][audio][analyse]
│       └── voice_audio_template.py # [voice][audio][template]
├── image/
│   ├── image_content_create.py     # [image][content][create]
│   ├── image_content_manage.py     # [image][content][manage]
│   ├── image_content_analyse.py    # [image][content][analyse]
│   └── image_template_manage.py    # [image][template][manage]
├── mixall/
│   ├── mixall_content_create.py    # [mixall][content][create]
│   └── mixall_content_manage.py    # [mixall][content][manage]
├── files/
│   ├── file_storage_upload.py      # [file][storage][upload]
│   ├── file_storage_download.py    # [file][storage][download]
│   └── file_storage_manage.py      # [file][storage][manage]
└── auth/
    ├── user_auth_login.py          # [user][auth][login]
    ├── user_auth_register.py       # [user][auth][register]
    └── user_auth_token.py          # [user][auth][token]
```

#### Database Models Structure
```bash
backend/app/models/
├── user_auth/
│   ├── user_auth_basic.py          # [user][auth][basic]
│   └── user_auth_session.py        # [user][auth][session]
├── file_storage/
│   └── file_storage_basic.py       # [file][storage][basic]
├── text_content/
│   ├── text_content_basic.py       # [text][content][basic]
│   ├── text_analyse_result.py      # [text][analyse][result]
│   └── text_template_basic.py      # [text][template][basic]
├── voice_timbre/
│   ├── voice_timbre_basic.py       # [voice][timbre][basic]
│   ├── voice_timbre_clone.py       # [voice][timbre][clone]
│   └── voice_timbre_template.py    # [voice][timbre][template]
├── voice_audio/
│   ├── voice_audio_basic.py        # [voice][audio][basic]
│   ├── voice_audio_analyse.py      # [voice][audio][analyse]
│   └── voice_audio_template.py     # [voice][audio][template]
└── mixall_content/
    └── mixall_content_basic.py     # [mixall][content][basic]
```

#### Frontend Components Structure
```bash
frontend/src/pages/
├── text/
│   ├── TextContentCreate.tsx       # [Text][Content][Create]
│   ├── TextContentManage.tsx       # [Text][Content][Manage]
│   ├── TextAnalyseSubmit.tsx       # [Text][Analyse][Submit]
│   └── TextTemplateManage.tsx      # [Text][Template][Manage]
├── voice/
│   ├── timbre/
│   │   ├── VoiceTimbreCreate.tsx   # [Voice][Timbre][Create]
│   │   ├── VoiceTimbreManage.tsx   # [Voice][Timbre][Manage]
│   │   ├── VoiceTimbreClone.tsx    # [Voice][Timbre][Clone]
│   │   └── VoiceTimbreTemplate.tsx # [Voice][Timbre][Template]
│   └── audio/
│       ├── VoiceAudioCreate.tsx    # [Voice][Audio][Create]
│       ├── VoiceAudioManage.tsx    # [Voice][Audio][Manage]
│       ├── VoiceAudioAnalyse.tsx   # [Voice][Audio][Analyse]
│       └── VoiceAudioTemplate.tsx  # [Voice][Audio][Template]
└── mixall/
    ├── MixallContentCreate.tsx     # [Mixall][Content][Create]
    └── MixallContentManage.tsx     # [Mixall][Content][Manage]
```

#### Function Naming Examples
```python
# Backend Function Examples
async def voice_timbre_create_from_audio():     # [voice][timbre][create][from_audio]
async def voice_timbre_manage_list_by_user():  # [voice][timbre][manage][list_by_user]
async def voice_audio_create_from_text():      # [voice][audio][create][from_text]
async def voice_audio_analyse_quality():       # [voice][audio][analyse][quality]
async def text_content_create_from_prompt():   # [text][content][create][from_prompt]
async def file_storage_upload_with_validation(): # [file][storage][upload][with_validation]
```

```typescript
// Frontend Function Examples
const voiceTimbreCreateFromAudio = async () => {} // [voice][timbre][create][from_audio]
const voiceAudioManageListByUser = async () => {} // [voice][audio][manage][list_by_user]
const textContentAnalyseQuality = async () => {}  // [text][content][analyse][quality]
const imageContentCreateFromPrompt = async () => {} // [image][content][create][from_prompt]
```

#### Database Table Examples
```sql
-- Table naming follows [business_module][data_object][attribute]
CREATE TABLE user_auth_basic;          -- [user][auth][basic]
CREATE TABLE voice_timbre_basic;       -- [voice][timbre][basic]
CREATE TABLE voice_timbre_clone;       -- [voice][timbre][clone]
CREATE TABLE voice_audio_basic;        -- [voice][audio][basic]
CREATE TABLE voice_audio_analyse;      -- [voice][audio][analyse]
CREATE TABLE text_content_basic;       -- [text][content][basic]
CREATE TABLE mixall_content_basic;     -- [mixall][content][basic]
```

#### API Endpoint Examples
```
# API routes follow /[business_module]/[data_object]/[action]
POST /text/content/create               # [text][content][create]
GET  /voice/timbre/list                 # [voice][timbre][list]
POST /voice/timbre/clone/submit         # [voice][timbre][clone][submit]
POST /voice/audio/create                # [voice][audio][create]
POST /voice/audio/analyse/submit        # [voice][audio][analyse][submit]
GET  /mixall/content/status/{id}        # [mixall][content][status]
```
     
## Important Notes

- The project contains sensitive API keys and credentials in `.env` - never commit these to version control
- Voice cloning requires specific cluster configurations (`volcano_icl` vs `volcano_icl_concurr`)
- The system is designed for high-concurrency voice processing with async operations
- Database uses async SQLAlchemy 2.0 patterns throughout
- All voice processing should be handled through async task queues (Celery)

## Next Development Steps

1. Implement basic FastAPI application structure in `backend/`
2. Set up database models and Alembic migrations
3. Create authentication system with JWT
4. Implement Volcano Engine API integration
5. Build React frontend applications
6. Set up Docker containerization
7. Implement monitoring and logging systems