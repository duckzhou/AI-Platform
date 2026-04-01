"""
项目配置
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "AI Platform"
    DEBUG: bool = True
    VERSION: str = "1.0.0"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置 (PostgreSQL)
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DATABASE: str = "ai_platform"
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    
    # 额度配置
    FREE_QUOTA_ON_REGISTER: int = 100  # 注册赠送额度
    
    # OSS配置
    OSS_ACCESS_KEY_ID: Optional[str] = None
    OSS_ACCESS_KEY_SECRET: Optional[str] = None
    OSS_BUCKET_NAME: Optional[str] = "aipl"
    OSS_ENDPOINT: Optional[str] = "oss-cn-hangzhou.aliyuncs.com"
    
    # 大模型配置
    OPENAI_API_KEY: Optional[str] = None
    DASHSCOPE_API_KEY: Optional[str] = "sk-f552a712562647d89eeec5e16503e454"  # 通义千问
    DEEPSEEK_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
