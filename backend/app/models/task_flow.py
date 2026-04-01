"""
任务编排模板模型
"""
from sqlalchemy import Column, Integer, String, Text, JSON, Boolean

from app.models.base import BaseModel


class TaskFlow(BaseModel):
    """任务编排模板表"""
    __tablename__ = "task_flow"
    
    # 模板信息
    name = Column(String(200), nullable=False, comment="模板名称")
    code = Column(String(50), unique=True, nullable=False, comment="模板代码")
    description = Column(Text, nullable=True, comment="描述")
    
    # 编排配置
    flow_config = Column(JSON, nullable=False, comment="编排配置JSON")
    # flow_config 示例：
    # {
    #   "steps": [
    #     {"order": 1, "name": "抠图", "model_code": "remove_bg", "input_from": "user"},
    #     {"order": 2, "name": "图生图", "model_code": "img2img", "input_from": "step_1"},
    #     {"order": 3, "name": "图生视频", "model_code": "img2video", "input_from": "step_2"}
    #   ]
    # }
    
    # 分类标签
    category = Column(String(50), nullable=True, comment="分类")
    tags = Column(String(500), nullable=True, comment="标签")
    
    # 预览图
    thumbnail_url = Column(String(500), nullable=True, comment="缩略图")
    
    # 状态
    is_system = Column(Boolean, default=False, nullable=False, comment="是否系统预设")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否启用")
    sort_order = Column(Integer, default=0, nullable=False, comment="排序")
