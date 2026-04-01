"""
子任务模型
"""
from sqlalchemy import Column, Integer, ForeignKey, String, Enum, Text, JSON, BigInteger
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class TaskItemStatus(str, enum.Enum):
    """子任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskItem(BaseModel):
    """子任务表"""
    __tablename__ = "task_item"
    
    task_id = Column(Integer, ForeignKey("ai_task.id"), nullable=False, comment="主任务ID")
    
    # 子任务信息
    step_order = Column(Integer, nullable=False, comment="执行顺序")
    step_name = Column(String(100), nullable=False, comment="步骤名称")
    status = Column(Enum(TaskItemStatus), default=TaskItemStatus.PENDING, nullable=False, comment="状态")
    
    # 模型信息
    model_id = Column(Integer, ForeignKey("ai_model.id"), nullable=True, comment="模型ID")
    
    # 输入输出
    input_params = Column(JSON, nullable=True, comment="输入参数")
    output_urls = Column(JSON, nullable=True, comment="输出URL")
    
    # 额度
    quota_cost = Column(BigInteger, default=0, nullable=False, comment="消耗额度")
    
    # 执行信息
    started_at = Column(String(20), nullable=True, comment="开始时间")
    completed_at = Column(String(20), nullable=True, comment="完成时间")
    error_message = Column(Text, nullable=True, comment="错误信息")
    
    # 关联关系
    task = relationship("AITask", back_populates="task_items")
    model = relationship("AIModel")
