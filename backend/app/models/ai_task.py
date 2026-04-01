"""
AI任务主表模型
"""
from sqlalchemy import Column, Integer, ForeignKey, String, Enum, Text, BigInteger, JSON
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class TaskStatus(str, enum.Enum):
    """任务状态"""
    PENDING = "pending"     # 待执行
    RUNNING = "running"     # 执行中
    SUCCESS = "success"     # 成功
    FAILED = "failed"       # 失败
    RETRY = "retry"         # 重试中
    CANCELLED = "cancelled" # 已取消
    TIMEOUT = "timeout"     # 超时


class TaskType(str, enum.Enum):
    """任务类型"""
    TEXT_TO_IMAGE = "text_to_image"
    IMAGE_TO_IMAGE = "image_to_image"
    IMAGE_TO_VIDEO = "image_to_video"
    TEXT_TO_VIDEO = "text_to_video"
    CHAT = "chat"
    WORKFLOW = "workflow"


class AITask(BaseModel):
    """AI任务主表"""
    __tablename__ = "ai_task"
    
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, comment="用户ID")
    
    # 任务信息
    task_name = Column(String(200), nullable=True, comment="任务名称")
    task_type = Column(Enum(TaskType), nullable=False, comment="任务类型")
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False, comment="状态")
    
    # 模型信息
    model_id = Column(Integer, ForeignKey("ai_model.id"), nullable=True, comment="模型ID")
    
    # 输入输出
    input_params = Column(JSON, nullable=True, comment="输入参数")
    output_urls = Column(JSON, nullable=True, comment="输出文件URL列表")
    
    # 额度
    quota_cost = Column(BigInteger, default=0, nullable=False, comment="消耗额度")
    
    # 执行信息
    started_at = Column(String(30), nullable=True, comment="开始时间")
    completed_at = Column(String(30), nullable=True, comment="完成时间")
    error_message = Column(Text, nullable=True, comment="错误信息")
    retry_count = Column(Integer, default=0, nullable=False, comment="重试次数")
    
    # 外部任务ID（万象等）
    external_task_id = Column(String(100), nullable=True, comment="外部任务ID")
    
    # 关联关系
    user = relationship("User", back_populates="ai_tasks")
    model = relationship("AIModel")
    task_items = relationship("TaskItem", back_populates="task")
