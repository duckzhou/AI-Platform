"""
大模型对话记录模型
"""
from sqlalchemy import Column, Integer, ForeignKey, String, Text, Enum, JSON
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class ChatRole(str, enum.Enum):
    """对话角色"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatHistory(BaseModel):
    """对话记录表"""
    __tablename__ = "chat_history"
    
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, comment="用户ID")
    
    # 会话信息
    session_id = Column(String(100), index=True, nullable=False, comment="会话ID")
    session_name = Column(String(200), nullable=True, comment="会话名称")
    
    # 消息信息
    role = Column(Enum(ChatRole), nullable=False, comment="角色")
    content = Column(Text, nullable=False, comment="内容")
    
    # 模型信息
    model_code = Column(String(50), nullable=True, comment="模型代码")
    
    # 扩展信息
    meta_info = Column(JSON, nullable=True, comment="元数据")
    # meta_info 示例：
    # {
    #   "is_deep_think": true,
    #   "is_web_search": true,
    #   "tokens_used": 150,
    #   "quota_cost": 1
    # }
    
    # 关联关系
    user = relationship("User", back_populates="chat_histories")
