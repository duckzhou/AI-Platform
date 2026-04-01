"""
用户模型
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.base import BaseModel


class UserStatus(str, enum.Enum):
    """用户状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"


class User(BaseModel):
    """用户表"""
    __tablename__ = "user"
    
    # 基本信息
    username = Column(String(50), unique=True, index=True, nullable=True, comment="用户名")
    email = Column(String(100), unique=True, index=True, nullable=True, comment="邮箱")
    phone = Column(String(20), unique=True, index=True, nullable=True, comment="手机号")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    
    # 用户状态
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False, comment="状态")
    
    # 注册信息
    register_ip = Column(String(50), nullable=True, comment="注册IP")
    last_login_at = Column(DateTime, nullable=True, comment="最后登录时间")
    last_login_ip = Column(String(50), nullable=True, comment="最后登录IP")
    
    # 关联关系
    quota = relationship("UserQuota", back_populates="user", uselist=False)
    quota_logs = relationship("QuotaLog", back_populates="user")
    materials = relationship("Material", back_populates="user")
    ai_tasks = relationship("AITask", back_populates="user")
    chat_histories = relationship("ChatHistory", back_populates="user")
    orders = relationship("Order", back_populates="user")
