"""
AI 任务处理
"""
import asyncio
from celery import shared_task
from typing import Dict, Any
import time
import random

from app.tasks.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3)
def process_text_to_image(self, task_id: int, user_id: int, input_params: Dict[str, Any]):
    """
    处理文生图任务
    """
    try:
        # 更新任务状态为运行中
        _update_task_status(task_id, "running")
        
        # 模拟AI处理过程
        time.sleep(random.randint(5, 15))
        
        # 模拟生成图片URL
        output_urls = [
            f"https://oss.example.com/outputs/{user_id}/{task_id}/image_1.png"
        ]
        
        # 更新任务状态为成功
        _update_task_status(task_id, "success", output_urls=output_urls)
        
        return {"status": "success", "task_id": task_id, "output_urls": output_urls}
    
    except Exception as exc:
        # 更新任务状态为失败
        _update_task_status(task_id, "failed", error_message=str(exc))
        
        # 重试
        if self.request.retries < 3:
            raise self.retry(exc=exc, countdown=60)
        
        return {"status": "failed", "task_id": task_id, "error": str(exc)}


@celery_app.task(bind=True, max_retries=3)
def process_image_to_image(self, task_id: int, user_id: int, input_params: Dict[str, Any]):
    """
    处理图生图任务
    """
    try:
        _update_task_status(task_id, "running")
        
        # 模拟处理
        time.sleep(random.randint(5, 15))
        
        output_urls = [
            f"https://oss.example.com/outputs/{user_id}/{task_id}/edited_image.png"
        ]
        
        _update_task_status(task_id, "success", output_urls=output_urls)
        
        return {"status": "success", "task_id": task_id}
    
    except Exception as exc:
        _update_task_status(task_id, "failed", error_message=str(exc))
        if self.request.retries < 3:
            raise self.retry(exc=exc, countdown=60)
        return {"status": "failed", "task_id": task_id}


@celery_app.task(bind=True, max_retries=2)
def process_image_to_video(self, task_id: int, user_id: int, input_params: Dict[str, Any]):
    """
    处理图生视频任务（耗时较长）
    """
    try:
        _update_task_status(task_id, "running")
        
        # 视频生成需要更长时间
        time.sleep(random.randint(30, 120))
        
        output_urls = [
            f"https://oss.example.com/outputs/{user_id}/{task_id}/video.mp4"
        ]
        
        _update_task_status(task_id, "success", output_urls=output_urls)
        
        return {"status": "success", "task_id": task_id}
    
    except Exception as exc:
        _update_task_status(task_id, "failed", error_message=str(exc))
        if self.request.retries < 2:
            raise self.retry(exc=exc, countdown=120)
        return {"status": "failed", "task_id": task_id}


@celery_app.task(bind=True, max_retries=2)
def process_text_to_video(self, task_id: int, user_id: int, input_params: Dict[str, Any]):
    """
    处理文生视频任务
    """
    try:
        _update_task_status(task_id, "running")
        
        time.sleep(random.randint(30, 120))
        
        output_urls = [
            f"https://oss.example.com/outputs/{user_id}/{task_id}/video.mp4"
        ]
        
        _update_task_status(task_id, "success", output_urls=output_urls)
        
        return {"status": "success", "task_id": task_id}
    
    except Exception as exc:
        _update_task_status(task_id, "failed", error_message=str(exc))
        if self.request.retries < 2:
            raise self.retry(exc=exc, countdown=120)
        return {"status": "failed", "task_id": task_id}


@celery_app.task(bind=True)
def process_workflow_task(self, task_id: int, user_id: int, flow_config: Dict[str, Any]):
    """
    处理编排任务
    按顺序执行子任务
    """
    try:
        from app.tasks.celery_app import celery_app
        
        steps = flow_config.get("steps", [])
        
        for i, step in enumerate(steps):
            # 更新子任务状态
            _update_task_item_status(task_id, i + 1, "running")
            
            try:
                # 模拟执行子任务
                time.sleep(random.randint(3, 10))
                
                # 模拟成功
                output_url = f"https://oss.example.com/outputs/{user_id}/{task_id}/step_{i+1}_output.png"
                _update_task_item_status(task_id, i + 1, "success", output_url=output_url)
                
            except Exception as step_exc:
                # 子任务失败，整体失败
                _update_task_item_status(task_id, i + 1, "failed", error_message=str(step_exc))
                _update_task_status(task_id, "failed", error_message=f"步骤{i+1}失败: {str(step_exc)}")
                return {"status": "failed", "task_id": task_id, "failed_step": i + 1}
        
        # 所有步骤成功
        _update_task_status(task_id, "success")
        return {"status": "success", "task_id": task_id}
    
    except Exception as exc:
        _update_task_status(task_id, "failed", error_message=str(exc))
        return {"status": "failed", "task_id": task_id}


def _update_task_status(task_id: int, status: str, output_urls: list = None, error_message: str = None):
    """更新任务状态"""
    # 这里应该调用数据库更新
    # 实际使用时需要异步数据库操作
    print(f"[Task {task_id}] Status: {status}, URLs: {output_urls}, Error: {error_message}")


def _update_task_item_status(task_id: int, step_order: int, status: str, output_url: str = None, error_message: str = None):
    """更新子任务状态"""
    print(f"[Task {task_id} Step {step_order}] Status: {status}")


@celery_app.task
def cleanup_old_tasks():
    """清理旧任务"""
    print("Cleaning up old tasks...")
    return "Cleanup completed"


# 定时任务配置
celery_app.conf.beat_schedule = {
    "cleanup-old-tasks": {
        "task": "app.tasks.ai_tasks.cleanup_old_tasks",
        "schedule": 3600.0,  # 每小时执行一次
    },
}
