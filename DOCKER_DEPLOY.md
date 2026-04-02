# Docker 部署文件清单

## 📁 已创建的文件

### Docker 相关配置文件

1. **`docker-compose.yml`** (根目录)
   - 主 Docker Compose 配置文件
   - 包含：前端、后端、Worker、PostgreSQL、Redis

2. **`frontend/Dockerfile`**
   - 前端 Docker 镜像构建文件
   - 使用 Node 18 构建，Nginx 提供静态服务

3. **`frontend/nginx.conf`**
   - Nginx 配置文件
   - 处理前端路由和 API 反向代理

4. **`backend/Dockerfile`** (已存在)
   - 后端 Docker 镜像构建文件
   - 使用 Python 3.11 + uv 包管理

5. **`backend/docker-compose.yml`** (已存在)
   - 后端独立的 docker-compose（本地开发用）

6. **`backend/init-db/init.sql`**
   - 数据库初始化脚本

### 环境配置文件

7. **`.env.production`** (根目录)
   - 生产环境变量配置模板
   - 包含数据库、OSS、API 密钥等配置

8. **`.gitignore`** (已更新)
   - 添加了 `.env.production` 到忽略列表

### 部署脚本

9. **`setup.sh`**
   - 一键部署脚本（带交互）
   - 检查环境、构建镜像、启动服务

10. **`deploy.sh`**
    - 快速部署脚本（无交互）
    - 适合自动化部署

### 文档

11. **`DEPLOY.md`**
    - 完整部署文档
    - 包含阿里云部署、安全配置、运维指南

12. **`README.md`** (已更新)
    - 添加了 Docker 部署快速指南

## 🚀 部署到阿里云步骤

### 第一步：准备服务器

登录阿里云服务器，确保已安装：
```bash
# 检查 Docker
docker --version

# 检查 Docker Compose
docker-compose --version
```

### 第二步：上传项目

```bash
# 方式一：使用 Git
git clone <your-repo-url>
cd AI-Platform

# 方式二：使用 SCP
# 在本地执行
scp -r ./AI-Platform root@your-server-ip:/opt/
```

### 第三步：配置环境变量

```bash
cd /opt/AI-Platform
cp .env.production .env
vim .env
```

**必须修改的配置**：

```bash
# 1. 数据库密码（强密码）
POSTGRES_PASSWORD=YourStrongPassword123!

# 2. JWT 密钥（随机生成）
SECRET_KEY=$(openssl rand -hex 32)

# 3. OSS 配置（替换为真实密钥）
OSS_ACCESS_KEY_ID=LTAI5tXXXXXXXXXXXX
OSS_ACCESS_KEY_SECRET=XXXXXXXXXXXXXXXXXX

# 4. 大模型 API 密钥
DASHSCOPE_API_KEY=sk-XXXXXXXXXXXXXXXXX
```

### 第四步：执行部署

```bash
# 赋予执行权限
chmod +x setup.sh

# 执行部署脚本
sudo ./setup.sh
```

### 第五步：验证部署

```bash
# 查看所有服务状态
docker-compose ps

# 应该看到 5 个服务都在运行：
# - ai_platform_frontend
# - ai_platform_api
# - ai_platform_worker
# - ai_platform_postgres
# - ai_platform_redis

# 查看日志
docker-compose logs -f
```

## 📊 服务架构

```
┌─────────────┐
│   Nginx     │ 端口 80
│  (前端)     │
└──────┬──────┘
       │
       │ /api/* → http://api:8000
       │
       ▼
┌─────────────┐      ┌─────────────┐
│ FastAPI     │──────│ PostgreSQL  │
│   (API)     │      │  (数据库)   │
└──────┬──────┘      └─────────────┘
       │
       │ Celery 任务
       │
       ▼
┌─────────────┐      ┌─────────────┐
│   Celery    │──────│    Redis    │
│   Worker    │      │   (缓存)    │
└─────────────┘      └─────────────┘
```

## 🔐 安全建议

### 1. 配置防火墙

```bash
# Ubuntu
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# 只开放必要端口
```

### 2. 配置 HTTPS

```bash
# 安装 certbot
apt-get install certbot python3-certbot-nginx

# 获取 SSL 证书
certbot --nginx -d your-domain.com
```

### 3. 数据库安全

- 不要修改默认的外部访问端口（5432）
- 使用强密码
- 定期备份数据

### 4. 定期备份

```bash
# 备份数据库
docker-compose exec postgres pg_dump -U postgres ai_platform > backup_$(date +%Y%m%d).sql

# 每周备份一次
0 2 * * 0 docker-compose exec -T postgres pg_dump -U postgres ai_platform > /backup/ai_platform_$(date +\%Y\%m\%d).sql
```

## 📝 常用运维命令

### 查看服务状态
```bash
docker-compose ps
```

### 查看日志
```bash
# 所有服务
docker-compose logs -f

# 特定服务
docker-compose logs -f api
docker-compose logs -f frontend
```

### 重启服务
```bash
# 重启所有
docker-compose restart

# 重启单个
docker-compose restart api
```

### 停止服务
```bash
docker-compose down
```

### 更新部署
```bash
# 拉取最新代码
git pull

# 重新构建
docker-compose build

# 启动
docker-compose up -d

# 迁移数据库
docker-compose exec -T api alembic upgrade head
```

## ⚠️ 注意事项

1. **不要提交敏感信息**
   - `.env` 和 `.env.production` 已在 `.gitignore` 中
   - 不要将真实密钥提交到代码库

2. **数据持久化**
   - PostgreSQL 数据存储在 `postgres_data` 卷中
   - Redis 数据存储在 `redis_data` 卷中
   - 删除容器不会丢失数据

3. **资源限制**
   - 建议服务器配置：2 核 4GB 以上
   - 生产环境建议限制容器资源

4. **监控告警**
   - 配置日志监控
   - 设置服务健康检查
   - 配置告警通知

## 📞 技术支持

如有问题，请参考完整文档：[DEPLOY.md](DEPLOY.md)

或联系：
- 作者：duckzhou
- 电话：15001793929
