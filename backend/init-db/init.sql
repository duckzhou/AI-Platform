#!/bin/bash
# 数据库初始化脚本
set -e

# 创建扩展（如果需要）
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- 这里可以添加额外的数据库初始化逻辑
    -- Alembic 会自动创建所有表
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
EOSQL

echo "✅ 数据库初始化完成！"
