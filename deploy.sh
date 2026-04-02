# AI Platform 部署脚本

echo "🚀 开始部署 AI Platform..."

# 1. 复制生产环境配置
echo "📋 复制环境配置文件..."
cp .env.production .env

# 2. 构建并启动所有服务
echo "🏗️  构建 Docker 容器..."
docker-compose -f docker-compose.yml build

# 3. 启动服务
echo "🎯 启动服务..."
docker-compose -f docker-compose.yml up -d

# 4. 执行数据库迁移
echo "🗄️  执行数据库迁移..."
docker-compose exec -T api alembic upgrade head

# 5. 查看服务状态
echo "📊 服务状态："
docker-compose ps

echo ""
echo "✅ 部署完成！"
echo ""
echo "🌐 前端地址：http://your-server-ip"
echo "🔧 API 地址：http://your-server-ip:8000"
echo "📚 API 文档：http://your-server-ip:8000/docs"
echo ""
echo "常用命令："
echo "  查看日志：docker-compose logs -f [service_name]"
echo "  停止服务：docker-compose down"
echo "  重启服务：docker-compose restart"
echo "  查看状态：docker-compose ps"
