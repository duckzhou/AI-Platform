"""
用户素材包模型
"""
from sqlalchemy import Column, Integer, ForeignKey, String, Enum, Text, BigInteger
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class MaterialType(str, enum.Enum):
    """素材类型"""
    IMAGE = "image"
    VIDEO = "video"
    TEXT = "text"
    AUDIO = "audio"


class Material(BaseModel):
    """用户素材表"""
    __tablename__ = "material"
    
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, comment="用户ID")
    
    # 素材信息
    name = Column(String(200), nullable=False, comment="素材名称")
    material_type = Column(Enum(MaterialType), nullable=False, comment="素材类型")
    
    # 文件信息
    file_url = Column(String(500), nullable=False, comment="文件URL")
    file_size = Column(BigInteger, default=0, nullable=False, comment="文件大小")
    file_format = Column(String(20), nullable=True, comment="文件格式")
    
    # 分类标签
    category = Column(String(50), nullable=True, comment="分类")
    tags = Column(String(500), nullable=True, comment="标签")
    
    # 预览
    thumbnail_url = Column(String(500), nullable=True, comment="缩略图URL")
    
    # 关联关系
    user = relationship("User", back_populates="materials")
