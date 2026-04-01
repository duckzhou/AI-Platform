"""
充值订单模型
"""
from sqlalchemy import Column, Integer, ForeignKey, String, Enum, BigInteger, Numeric, Text
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class OrderStatus(str, enum.Enum):
    """订单状态"""
    PENDING = "pending"     # 待支付
    PAID = "paid"          # 已支付
    CANCELLED = "cancelled" # 已取消
    REFUNDED = "refunded"   # 已退款


class PaymentChannel(str, enum.Enum):
    """支付渠道"""
    ALIPAY = "alipay"
    WECHAT = "wechat"


class Order(BaseModel):
    """充值订单表"""
    __tablename__ = "order"
    
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, comment="用户ID")
    
    # 订单信息
    order_no = Column(String(50), unique=True, nullable=False, comment="订单号")
    
    # 支付信息
    payment_channel = Column(Enum(PaymentChannel), nullable=False, comment="支付渠道")
    amount = Column(Numeric(10, 2), nullable=False, comment="支付金额")
    quota_amount = Column(BigInteger, nullable=False, comment="额度数量")
    
    # 状态
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False, comment="状态")
    
    # 支付详情
    paid_at = Column(String(20), nullable=True, comment="支付时间")
    transaction_id = Column(String(100), nullable=True, comment="第三方支付流水号")
    
    # 描述
    description = Column(Text, nullable=True, comment="描述")
    
    # 关联关系
    user = relationship("User", back_populates="orders")
