"""
额度日志模型
"""
from sqlalchemy import Column, Integer, ForeignKey, BigInteger, String, Enum, Text
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class QuotaLogType(str, enum.Enum):
    """额度日志类型"""
    DEDUCT = "deduct"      # 扣费
    RECHARGE = "recharge"  # 充值
    GIFT = "gift"          # 赠送
    REFUND = "refund"      # 退款


class QuotaLog(BaseModel):
    """额度日志表"""
    __tablename__ = "quota_log"
    
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, comment="用户ID")
    
    # 日志信息
    log_type = Column(Enum(QuotaLogType), nullable=False, comment="日志类型")
    amount = Column(BigInteger, nullable=False, comment="变动金额")
    balance_before = Column(BigInteger, nullable=False, comment="变动前余额")
    balance_after = Column(BigInteger, nullable=False, comment="变动后余额")
    
    # 业务信息
    biz_type = Column(String(50), nullable=True, comment="业务类型")
    biz_id = Column(Integer, nullable=True, comment="业务ID")
    description = Column(Text, nullable=True, comment="描述")
    
    # 关联关系
    user = relationship("User", back_populates="quota_logs")
