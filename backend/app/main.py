"""
FastAPI 主入口
"""
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.database import init_db

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 确保上传目录存在
os.makedirs("uploads", exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("Starting AI Platform Server...")
    await init_db()
    logger.info("Database initialized")
    yield
    # 关闭时执行
    logger.info("Shutting down...")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # 注册CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册异常处理器
    register_exception_handlers(app)
    
    # 注册路由
    from app.api.v1 import auth, quota, chat, task, material, export
    
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(quota.router, prefix="/api/v1")
    app.include_router(chat.router, prefix="/api/v1")
    app.include_router(task.router, prefix="/api/v1")
    app.include_router(material.router, prefix="/api/v1")
    app.include_router(export.router, prefix="/api/v1")
    
    # 挂载静态文件目录
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
    
    @app.get("/")
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.VERSION,
            "docs": "/docs"
        }
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
