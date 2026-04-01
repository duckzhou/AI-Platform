"""
用户额度模型
"""
from sqlalchemy import Column, Integer, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class UserQuota(BaseModel):
    """用户额度表"""
    __tablename__ = "user_quota"
    
    user_id = Column(Integer, ForeignKey("user.id"), unique=True, nullable=False, comment="用户ID")
    
    # 额度信息
    free_quota = Column(BigInteger, default=0, nullable=False, comment="免费额度")
    remaining_quota = Column(BigInteger, default=0, nullable=False, comment="剩余额度")
    total_recharge = Column(BigInteger, default=0, nullable=False, comment="总充值额度")
    total_used = Column(BigInteger, default=0, nullable=False, comment="总使用额度")
    
    # 关联关系
    user = relationship("User", back_populates="quota")
