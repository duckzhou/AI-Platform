# AI 创作平台

一个功能完整的 AI 创作平台，支持 AI 对话、文生图、图生图、图生视频等多种 AI 创作功能。

## ✨ 特性

### 🎯 核心功能

- **AI 对话** - 支持通义千问多个模型，具备深度思考和联网搜索能力
- **文生图** - 根据文字描述生成精美图片
- **图生图** - 根据参考图片生成新图片
- **图生视频** - 将静态图片转换为动态视频
- **任务管理** - 查看和管理所有 AI 创作任务
- **素材管理** - 管理创作的图片和视频素材
- **额度系统** - 完善的额度充值和消费记录

### 🚀 技术亮点

- **前后端分离架构** - Vue 3 + FastAPI
- **流式响应** - SSE 实时流式输出，打字机效果
- **深度思考** - 支持显示 AI 思考过程
- **异步任务** - Celery 异步任务处理
- **数据库迁移** - Alembic 版本管理
- **响应式设计** - 适配不同屏幕尺寸

## 🛠️ 技术栈

### 后端

- **框架**: FastAPI
- **数据库**: PostgreSQL / MySQL (通过 SQLAlchemy ORM)
- **缓存**: Redis
- **异步任务**: Celery
- **AI 服务**: 
  - DashScope (通义千问) - 对话和文生图
  - Wanx (通义万相) - 图像生成
  - 通义万象视频 - 视频生成
- **对象存储**: 阿里云 OSS
- **数据库迁移**: Alembic

### 前端

- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **UI 组件库**: Element Plus
- **路由**: Vue Router
- **状态管理**: Pinia
- **Markdown 渲染**: marked
- **代码高亮**: highlight.js

## 📦 安装部署

### 环境要求

- Python 3.9+
- Node.js 16+
- Redis
- MySQL 5.7+ 或 PostgreSQL 12+

### Docker 部署（推荐）

**快速部署到阿里云**：

```bash
# 1. 上传项目到服务器
scp -r ./AI-Platform root@your-server-ip:/opt/

# 2. 配置环境变量
cd /opt/AI-Platform
cp .env.production .env
vim .env  # 编辑配置

# 3. 一键部署
chmod +x setup.sh
sudo ./setup.sh
```

**服务访问**：
- 前端：http://your-server-ip
- API：http://your-server-ip:8000
- API 文档：http://your-server-ip:8000/docs

详细 Docker 部署文档请查看：[DEPLOY.md](DEPLOY.md)

### 本地开发部署
### 后端部署

1. **克隆项目**
```bash
cd backend
```

2. **安装依赖**
```bash
pip install -r pyproject.toml
# 或使用 uv
uv sync
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，配置必要参数
```

4. **数据库迁移**
```bash
alembic upgrade head
```

5. **启动服务**
```bash
# 启动主服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动 Celery Worker
celery -A app.tasks.celery_app worker -l info
```

### 前端部署

1. **进入前端目录**
```bash
cd frontend
```

2. **安装依赖**
```bash
npm install
```

3. **启动开发服务器**
```bash
npm run dev
```

4. **构建生产版本**
```bash
npm run build
```

## 📁 项目结构

```
AI-Platform/
├── backend/
│   ├── app/
│   │   ├── api/          # API 路由
│   │   │   └── v1/       # V1 版本 API
│   │   ├── core/         # 核心配置
│   │   ├── models/       # 数据模型
│   │   ├── services/     # 业务逻辑
│   │   ├── tasks/        # Celery 任务
│   │   └── main.py       # 应用入口
│   ├── alembic/          # 数据库迁移
│   ├── .env.example      # 环境配置示例
│   └── pyproject.toml    # 依赖配置
├── frontend/
│   ├── src/
│   │   ├── api/          # API 调用
│   │   ├── layouts/      # 布局组件
│   │   ├── router/       # 路由配置
│   │   ├── stores/       # 状态管理
│   │   ├── views/        # 页面组件
│   │   └── main.js       # 应用入口
│   └── package.json
└── README.md
```

## 🔑 API 接口

### 认证相关
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/register` - 用户注册

### AI 对话
- `GET /api/v1/chat/models` - 获取模型列表
- `POST /api/v1/chat/send` - 发送消息

### AI 创作
- `POST /api/v1/tasks/text-to-image` - 文生图
- `POST /api/v1/tasks/image-to-image` - 图生图
- `GET /api/v1/tasks` - 获取任务列表
- `GET /api/v1/tasks/{task_id}` - 获取任务详情

### 额度管理
- `GET /api/v1/quota/info` - 获取额度信息
- `GET /api/v1/quota/logs` - 获取额度日志

## ⚠️ 重要提示

**请勿将真实密钥提交到代码库！**

- OSS_ACCESS_KEY_ID 和 OSS_ACCESS_KEY_SECRET 必须使用环境变量
- DASHSCOPE_API_KEY 等所有 API 密钥都应从环境变量读取
- 生产环境请使用 .env 文件或环境变量配置
- 敏感密钥泄露后请立即轮换

## 📄 许可证

MIT License