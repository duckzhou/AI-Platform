"""
AI任务服务 - 状态机核心
"""
import uuid
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc
from transitions import Machine

from app.models.ai_task import AITask, TaskStatus, TaskType
from app.models.task_item import TaskItem, TaskItemStatus
from app.models.task_flow import TaskFlow
from app.models.ai_model import AIModel
from app.core.redis import RedisUtil, get_task_status_key
from app.core.exceptions import BusinessException


class TaskStateMachine:
    """任务状态机"""
    
    states = ['pending', 'running', 'success', 'failed', 'retry', 'cancelled', 'timeout']
    
    transitions = [
        {'trigger': 'start', 'source': 'pending', 'dest': 'running'},
        {'trigger': 'complete', 'source': 'running', 'dest': 'success'},
        {'trigger': 'fail', 'source': 'running', 'dest': 'failed'},
        {'trigger': 'retry', 'source': 'failed', 'dest': 'retry'},
        {'trigger': 'restart', 'source': 'retry', 'dest': 'running'},
        {'trigger': 'cancel', 'source': ['pending', 'running', 'retry'], 'dest': 'cancelled'},
        {'trigger': 'timeout', 'source': 'running', 'dest': 'timeout'},
        {'trigger': 'reset', 'source': ['failed', 'cancelled', 'timeout'], 'dest': 'pending'},
    ]
    
    def __init__(self, task: AITask):
        self.task = task
        self.machine = Machine(
            model=self,
            states=TaskStateMachine.states,
            transitions=TaskStateMachine.transitions,
            initial=task.status.value if task else 'pending'
        )
    
    def on_enter_running(self):
        """进入运行状态时"""
        self.task.started_at = datetime.utcnow().isoformat()
        self.task.status = TaskStatus.RUNNING
    
    def on_enter_success(self):
        """进入成功状态时"""
        self.task.completed_at = datetime.utcnow().isoformat()
        self.task.status = TaskStatus.SUCCESS
    
    def on_enter_failed(self):
        """进入失败状态时"""
        self.task.completed_at = datetime.utcnow().isoformat()
        self.task.status = TaskStatus.FAILED


class TaskService:
    """任务服务"""
    
    @staticmethod
    async def create_task(db: AsyncSession, user_id: int, task_type: TaskType,
                          task_name: str = None, model_id: int = None,
                          input_params: dict = None, quota_cost: int = 0,
                          output_urls: list = None, external_task_id: str = None) -> AITask:
        """创建任务"""
        task = AITask(
            user_id=user_id,
            task_name=task_name or f"任务_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            task_type=task_type,
            model_id=model_id,
            input_params=input_params,
            quota_cost=quota_cost,
            output_urls=output_urls,
            external_task_id=external_task_id,
            status=TaskStatus.SUCCESS if output_urls else TaskStatus.RUNNING
        )
        if output_urls:
            task.completed_at = datetime.utcnow().isoformat()
        else:
            task.started_at = datetime.utcnow().isoformat()
        db.add(task)
        await db.flush()
        return task
    
    @staticmethod
    async def get_task(db: AsyncSession, task_id: int, user_id: int = None) -> Optional[AITask]:
        """获取任务"""
        query = select(AITask).where(AITask.id == task_id, AITask.is_deleted == False)
        if user_id:
            query = query.where(AITask.user_id == user_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_tasks(db: AsyncSession, user_id: int, page: int = 1, 
                             size: int = 20, status: TaskStatus = None) -> tuple:
        """获取用户任务列表和总数"""
        # 查询总数
        from sqlalchemy import func
        count_query = select(func.count(AITask.id)).where(
            AITask.user_id == user_id, 
            AITask.is_deleted == False
        )
        if status:
            count_query = count_query.where(AITask.status == status)
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # 查询任务列表
        query = select(AITask).where(AITask.user_id == user_id, AITask.is_deleted == False)
        
        if status:
            query = query.where(AITask.status == status)
        
        query = query.order_by(desc(AITask.created_at)).offset((page - 1) * size).limit(size)
        result = await db.execute(query)
        tasks = result.scalars().all()
        
        return tasks, total
    
    @staticmethod
    async def update_task_status(db: AsyncSession, task_id: int, status: TaskStatus,
                                  error_message: str = None, output_urls: list = None):
        """更新任务状态"""
        update_data = {"status": status}
        
        if error_message:
            update_data["error_message"] = error_message
        
        if output_urls:
            update_data["output_urls"] = output_urls
        
        if status == TaskStatus.SUCCESS:
            update_data["completed_at"] = datetime.utcnow().isoformat()
        elif status == TaskStatus.RUNNING:
            update_data["started_at"] = datetime.utcnow().isoformat()
        
        await db.execute(
            update(AITask).where(AITask.id == task_id).values(**update_data)
        )
        await db.commit()
        
        # 更新Redis缓存
        cache_key = get_task_status_key(task_id)
        await RedisUtil.set_json(cache_key, {
            "status": status.value,
            "updated_at": datetime.utcnow().isoformat()
        }, expire=3600)
    
    @staticmethod
    async def cancel_task(db: AsyncSession, task_id: int, user_id: int) -> bool:
        """取消任务"""
        task = await TaskService.get_task(db, task_id, user_id)
        if not task:
            raise BusinessException("任务不存在")
        
        if task.status not in [TaskStatus.PENDING, TaskStatus.RUNNING, TaskStatus.RETRY]:
            raise BusinessException("当前状态不可取消")
        
        await TaskService.update_task_status(db, task_id, TaskStatus.CANCELLED)
        return True
    
    @staticmethod
    async def retry_task(db: AsyncSession, task_id: int, user_id: int) -> bool:
        """重试任务"""
        task = await TaskService.get_task(db, task_id, user_id)
        if not task:
            raise BusinessException("任务不存在")
        
        if task.status not in [TaskStatus.FAILED, TaskStatus.TIMEOUT]:
            raise BusinessException("当前状态不可重试")
        
        await db.execute(
            update(AITask)
            .where(AITask.id == task_id)
            .values(
                status=TaskStatus.PENDING,
                retry_count=task.retry_count + 1,
                error_message=None
            )
        )
        await db.commit()
        return True
    
    # ========== 子任务相关 ==========
    
    @staticmethod
    async def create_task_items(db: AsyncSession, task_id: int, flow_config: dict) -> List[TaskItem]:
        """根据编排配置创建子任务"""
        steps = flow_config.get("steps", [])
        items = []
        
        for step in steps:
            item = TaskItem(
                task_id=task_id,
                step_order=step["order"],
                step_name=step["name"],
                model_id=step.get("model_id"),
                input_params=step.get("input_params"),
                quota_cost=step.get("quota_cost", 1),
                status=TaskItemStatus.PENDING
            )
            db.add(item)
            items.append(item)
        
        await db.flush()
        return items
    
    @staticmethod
    async def get_task_items(db: AsyncSession, task_id: int) -> List[TaskItem]:
        """获取子任务列表"""
        result = await db.execute(
            select(TaskItem)
            .where(TaskItem.task_id == task_id, TaskItem.is_deleted == False)
            .order_by(TaskItem.step_order)
        )
        return result.scalars().all()
    
    @staticmethod
    async def update_task_item_status(db: AsyncSession, item_id: int, status: TaskItemStatus,
                                       output_urls: list = None, error_message: str = None):
        """更新子任务状态"""
        update_data = {"status": status}
        
        if output_urls:
            update_data["output_urls"] = output_urls
        if error_message:
            update_data["error_message"] = error_message
        
        if status == TaskItemStatus.RUNNING:
            update_data["started_at"] = datetime.utcnow().isoformat()
        elif status in [TaskItemStatus.SUCCESS, TaskItemStatus.FAILED]:
            update_data["completed_at"] = datetime.utcnow().isoformat()
        
        await db.execute(
            update(TaskItem).where(TaskItem.id == item_id).values(**update_data)
        )
        await db.commit()
    
    # ========== 任务编排模板 ==========
    
    @staticmethod
    async def get_task_flows(db: AsyncSession, category: str = None) -> List[TaskFlow]:
        """获取任务编排模板"""
        query = select(TaskFlow).where(TaskFlow.is_active == True, TaskFlow.is_deleted == False)
        
        if category:
            query = query.where(TaskFlow.category == category)
        
        query = query.order_by(TaskFlow.sort_order)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_task_flow(db: AsyncSession, flow_id: int) -> Optional[TaskFlow]:
        """获取编排模板详情"""
        result = await db.execute(
            select(TaskFlow).where(TaskFlow.id == flow_id, TaskFlow.is_deleted == False)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_workflow_task(db: AsyncSession, user_id: int, flow_id: int,
                                   input_params: dict, quota_cost: int = 0) -> AITask:
        """创建编排任务"""
        flow = await TaskService.get_task_flow(db, flow_id)
        if not flow:
            raise BusinessException("编排模板不存在")
        
        # 创建主任务
        task = await TaskService.create_task(
            db, user_id, TaskType.WORKFLOW, flow.name, None, input_params, quota_cost
        )
        
        # 创建子任务
        await TaskService.create_task_items(db, task.id, flow.flow_config)
        
        return task
