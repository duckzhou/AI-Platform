# AI Platform 部署指南

## 📋 部署前准备

### 1. 阿里云服务器配置

- **操作系统**: Ubuntu 20.04+ 或 CentOS 7+
- **CPU**: 2 核及以上
- **内存**: 4GB 及以上
- **存储**: 40GB 及以上
- **网络**: 开放端口 80, 443（可选）

### 2. 已安装软件

- Docker 20.10+
- Docker Compose 2.0+
- Git（可选，用于拉取代码）

## 🚀 快速部署

### 步骤 1：上传项目到服务器

```bash
# 方式一：使用 Git 克隆
git clone <your-repo-url>
cd AI-Platform

# 方式二：使用 SCP 上传
scp -r ./AI-Platform root@your-server-ip:/opt/
```

### 步骤 2：配置环境变量

```bash
# 复制生产环境配置
cp .env.production .env

# 编辑配置文件，填写真实信息
vim .env
```

**必须配置的环境变量**：

```bash
# 数据库密码（修改为强密码）
POSTGRES_PASSWORD=your_strong_password

# JWT 密钥（生成随机字符串）
SECRET_KEY=$(openssl rand -hex 32)

# OSS 配置（替换为您的真实密钥）
OSS_ACCESS_KEY_ID=LTAI5tXXXXXXXXXXXXX
OSS_ACCESS_KEY_SECRET=XXXXXXXXXXXXXXXXXXXXXX

# 大模型 API 密钥
DASHSCOPE_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXX
```

### 步骤 3：一键部署

```bash
# 赋予执行权限
chmod +x deploy.sh

# 执行部署脚本
./deploy.sh
```

### 步骤 4：验证部署

```bash
# 查看所有服务状态
docker-compose ps

# 查看前端日志
docker-compose logs frontend

# 查看后端日志
docker-compose logs api

# 查看数据库日志
docker-compose logs postgres
```

## 🔧 手动部署步骤

如果不使用部署脚本，可以手动执行：

### 1. 构建镜像

```bash
# 构建所有服务
docker-compose build

# 或单独构建
docker-compose build frontend
docker-compose build api
```

### 2. 启动服务

```bash
# 后台启动所有服务
docker-compose up -d

# 查看启动日志
docker-compose logs -f
```

### 3. 数据库迁移

```bash
# 进入后端容器
docker-compose exec api bash

# 执行数据库迁移
alembic upgrade head

# 退出容器
exit
```

## 🔐 安全配置

### 1. 配置防火墙

```bash
# Ubuntu (UFW)
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# CentOS (Firewalld)
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload
```

### 2. 配置 HTTPS（推荐）

使用 Nginx 反向代理配置 SSL：

```bash
# 安装 certbot
apt-get install certbot python3-certbot-nginx

# 获取证书
certbot --nginx -d your-domain.com
```

### 3. 数据库安全

- 不要将数据库端口（5432）暴露到公网
- 使用强密码
- 定期备份数据

## 📊 服务监控

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f worker
```

### 查看资源使用

```bash
# 查看容器资源使用
docker stats

# 查看容器状态
docker-compose ps
```

### 查看数据库状态

```bash
# 进入数据库容器
docker-compose exec postgres psql -U postgres -d ai_platform

# 查看表
\dt

# 退出
\q
```

## 🔄 日常运维

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart api
docker-compose restart frontend
```

### 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷（危险！）
docker-compose down -v
```

### 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose build
docker-compose up -d

# 执行数据库迁移
docker-compose exec -T api alembic upgrade head
```

### 数据备份

```bash
# 备份数据库
docker-compose exec postgres pg_dump -U postgres ai_platform > backup_$(date +%Y%m%d).sql

# 恢复数据库
docker-compose exec -T postgres psql -U postgres ai_platform < backup_20260402.sql
```

## ⚠️ 常见问题

### 1. 容器启动失败

```bash
# 查看详细日志
docker-compose logs api

# 检查配置文件
docker-compose config
```

### 2. 数据库连接失败

- 检查 `.env` 文件中的数据库配置
- 确保 PostgreSQL 和 Redis 容器正常运行
- 检查网络配置

### 3. 端口被占用

修改 `.env.production` 中的端口：

```bash
POSTGRES_PORT_EXTERNAL=5433  # 改为其他端口
```

### 4. 内存不足

调整 Docker 容器资源限制或升级服务器配置。

## 📞 技术支持

如有问题，请联系：
- 作者：duckzhou
- 电话：15001793929
