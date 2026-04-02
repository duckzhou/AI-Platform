#!/bin/bash

# AI Platform 快速部署脚本 for 阿里云

set -e

echo "======================================"
echo "  AI Platform 快速部署脚本"
echo "======================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then 
  echo -e "${RED}请使用 sudo 运行此脚本${NC}"
  exit 1
fi

# 1. 检查 Docker 是否安装
echo -e "${YELLOW}[1/5] 检查 Docker 安装...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker 未安装，请先安装 Docker${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker 已安装：$(docker --version)${NC}"

# 2. 检查 Docker Compose 是否安装
echo -e "${YELLOW}[2/5] 检查 Docker Compose 安装...${NC}"
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose 未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose 已安装：$(docker-compose --version)${NC}"

# 3. 配置环境变量
echo -e "${YELLOW}[3/5] 配置环境变量...${NC}"
if [ ! -f .env ]; then
    cp .env.production .env
    echo -e "${GREEN}✓ 已创建 .env 文件${NC}"
else
    echo -e "${YELLOW}⚠ .env 文件已存在，跳过${NC}"
fi

echo ""
echo "请编辑 .env 文件，配置以下必要参数："
echo "  - POSTGRES_PASSWORD (数据库密码)"
echo "  - SECRET_KEY (JWT 密钥)"
echo "  - OSS_ACCESS_KEY_ID (阿里云 OSS)"
echo "  - OSS_ACCESS_KEY_SECRET (阿里云 OSS)"
echo "  - DASHSCOPE_API_KEY (通义千问)"
echo ""
read -p "是否已完成配置？(y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}请先配置 .env 文件${NC}"
    exit 1
fi

# 4. 构建并启动服务
echo -e "${YELLOW}[4/5] 构建 Docker 镜像...${NC}"
docker-compose build

echo -e "${YELLOW}[5/5] 启动服务...${NC}"
docker-compose up -d

# 等待服务启动
echo ""
echo -e "${YELLOW}等待服务启动...${NC}"
sleep 10

# 执行数据库迁移
echo -e "${YELLOW}执行数据库迁移...${NC}"
docker-compose exec -T api alembic upgrade head

# 显示服务状态
echo ""
echo -e "${GREEN}======================================"
echo "  部署完成！"
echo "======================================${NC}"
echo ""
docker-compose ps
echo ""
echo -e "${YELLOW}服务访问地址:${NC}"
echo "  前端：http://$(hostname -I | awk '{print $1}')"
echo "  API: http://$(hostname -I | awk '{print $1}'):8000"
echo "  API 文档：http://$(hostname -I | awk '{print $1}'):8000/docs"
echo ""
echo -e "${YELLOW}常用运维命令:${NC}"
echo "  查看日志：docker-compose logs -f [service]"
echo "  停止服务：docker-compose down"
echo "  重启服务：docker-compose restart"
echo "  查看状态：docker-compose ps"
echo ""
