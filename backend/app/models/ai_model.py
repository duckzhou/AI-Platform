"""
AI模型配置模型
"""
from sqlalchemy import Column, String, Integer, Enum, BigInteger, Text, Boolean
import enum

from app.models.base import BaseModel


class ModelType(str, enum.Enum):
    """模型类型"""
    CHAT = "chat"           # 对话模型
    IMAGE_GEN = "image_gen" # 文生图
    IMAGE_EDIT = "image_edit" # 图生图
    VIDEO_GEN = "video_gen" # 视频生成
    AUDIO_GEN = "audio_gen" # 音频生成


class AIModel(BaseModel):
    """AI模型配置表"""
    __tablename__ = "ai_model"
    
    # 模型信息
    name = Column(String(100), nullable=False, comment="模型名称")
    code = Column(String(50), unique=True, nullable=False, comment="模型代码")
    model_type = Column(Enum(ModelType), nullable=False, comment="模型类型")
    
    # 提供商信息
    provider = Column(String(50), nullable=False, comment="提供商")
    api_endpoint = Column(String(500), nullable=True, comment="API端点")
    api_key = Column(String(500), nullable=True, comment="API密钥")
    
    # 计费信息
    quota_cost = Column(BigInteger, default=1, nullable=False, comment="单次扣费额度")
    
    # 配置信息
    config = Column(Text, nullable=True, comment="模型配置JSON")
    description = Column(Text, nullable=True, comment="描述")
    
    # 状态
    is_active = Column(Boolean, default=True, nullable=False, comment="是否启用")
    sort_order = Column(Integer, default=0, nullable=False, comment="排序")
