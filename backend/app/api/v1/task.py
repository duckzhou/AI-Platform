"""
AI任务相关API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional

from app.api.deps import DBDep, CurrentUser
from app.core.response import success, error
from app.services.task_service import TaskService
from app.services.quota_service import QuotaService
from app.services.wanx_service import WanxService, VideoService
from app.models.ai_task import TaskType, TaskStatus
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["AI任务"])


class CreateTaskRequest(BaseModel):
    """创建任务请求"""
    task_type: str
    task_name: str = None
    model_id: int = None
    input_params: dict = {}


class TextToImageRequest(BaseModel):
    """文生图请求"""
    prompt: str
    size: str = "1024x1024"
    task_name: str = None


class ImageToImageRequest(BaseModel):
    """图生图请求"""
    prompt: str
    image_url: str  # 参考图片URL（可以是素材库的URL或上传的URL）
    size: str = "1024x1024"
    task_name: str = None


class ImageToVideoRequest(BaseModel):
    """图生视频请求"""
    image_url: str  # 首帧图片URL
    prompt: str = ""  # 可选的描述
    duration: int = 5  # 视频时长
    task_name: str = None


class CreateWorkflowRequest(BaseModel):
    """创建编排任务请求"""
    flow_id: int
    input_params: dict = {}


@router.get("/flows")
async def get_task_flows(category: str = None, db: AsyncSession = DBDep):
    """获取任务编排模板"""
    flows = await TaskService.get_task_flows(db, category)
    return success({
        "list": [
            {
                "id": f.id,
                "name": f.name,
                "code": f.code,
                "description": f.description,
                "category": f.category,
                "thumbnail_url": f.thumbnail_url,
                "is_system": f.is_system
            }
            for f in flows
        ]
    })


@router.get("")
async def get_tasks(
    page: int = 1,
    size: int = 20,
    status: str = None,
    user_id: int = CurrentUser,
    db: AsyncSession = DBDep
):
    """获取任务列表"""
    task_status = TaskStatus(status) if status else None
    tasks, total = await TaskService.get_user_tasks(db, user_id, page, size, task_status)
    return success({
        "list": [
            {
                "id": t.id,
                "task_name": t.task_name,
                "task_type": t.task_type.value,
                "status": t.status.value,
                "quota_cost": t.quota_cost,
                "output_urls": t.output_urls,
                "created_at": t.created_at.isoformat(),
                "completed_at": t.completed_at
            }
            for t in tasks
        ],
        "total": total
    })


@router.get("/{task_id}")
async def get_task_detail(task_id: int, user_id: int = CurrentUser, db: AsyncSession = DBDep):
    """获取任务详情"""
    task = await TaskService.get_task(db, task_id, user_id)
    if not task:
        return error("任务不存在", code=404)
    
    # 获取子任务
    items = await TaskService.get_task_items(db, task_id)
    
    return success({
        "id": task.id,
        "task_name": task.task_name,
        "task_type": task.task_type.value,
        "status": task.status.value,
        "input_params": task.input_params,
        "output_urls": task.output_urls,
        "quota_cost": task.quota_cost,
        "error_message": task.error_message,
        "retry_count": task.retry_count,
        "created_at": task.created_at.isoformat(),
        "started_at": task.started_at,
        "completed_at": task.completed_at,
        "items": [
            {
                "id": item.id,
                "step_order": item.step_order,
                "step_name": item.step_name,
                "status": item.status.value,
                "output_urls": item.output_urls,
                "error_message": item.error_message
            }
            for item in items
        ]
    })


@router.post("/text-to-image")
async def create_text_to_image_task(req: TextToImageRequest, user_id: int = CurrentUser, db: AsyncSession = DBDep):
    """创建文生图任务（同步，直接返回结果）"""
    quota_cost = 5
    if not await QuotaService.check_quota(db, user_id, quota_cost):
        return error("额度不足", code=1001)
    
    try:
        # 同步调用 Qwen-Image 生成图片
        image_urls = WanxService.text_to_image(
            prompt=req.prompt,
            size=req.size,
            n=1
        )
        
        # 下载并保存到 OSS
        saved_results = await WanxService.save_results(image_urls)
        output_urls = [r["save_url"] for r in saved_results]
        
        # 扣减额度
        await QuotaService.lock_quota(db, user_id, quota_cost, "text_to_image", description="文生图")
        
        # 创建已完成的任务记录
        task = await TaskService.create_task(
            db, user_id, TaskType.TEXT_TO_IMAGE, req.task_name or "文生图",
            None, {"prompt": req.prompt, "size": req.size}, quota_cost,
            output_urls=output_urls
        )
        
        await db.commit()
        
        return success({
            "task_id": task.id,
            "status": "success",
            "output_urls": output_urls
        }, "生成成功")
        
    except Exception as e:
        logger.error(f"文生图失败: {str(e)}")
        return error(f"生成失败: {str(e)}")


@router.post("/image-to-image")
async def create_image_to_image_task(req: ImageToImageRequest, user_id: int = CurrentUser, db: AsyncSession = DBDep):
    """创建图生图任务（同步，直接返回结果）"""
    quota_cost = 5
    if not await QuotaService.check_quota(db, user_id, quota_cost):
        return error("额度不足", code=1001)
    
    try:
        # 同步调用 Qwen-Image 生成图片
        image_urls = WanxService.image_to_image(
            prompt=req.prompt,
            image_url=req.image_url,
            size=req.size,
            n=1
        )
        
        # 下载并保存到 OSS
        saved_results = await WanxService.save_results(image_urls)
        output_urls = [r["save_url"] for r in saved_results]
        
        # 扣减额度
        await QuotaService.lock_quota(db, user_id, quota_cost, "image_to_image", description="图生图")
        
        # 创建已完成的任务记录
        task = await TaskService.create_task(
            db, user_id, TaskType.IMAGE_TO_IMAGE, req.task_name or "图生图",
            None, {"prompt": req.prompt, "image_url": req.image_url, "size": req.size}, quota_cost,
            output_urls=output_urls
        )
        
        await db.commit()
        
        return success({
            "task_id": task.id,
            "status": "success",
            "output_urls": output_urls
        }, "生成成功")
        
    except Exception as e:
        logger.error(f"图生图失败: {str(e)}")
        return error(f"生成失败: {str(e)}")


@router.post("/image-to-video")
async def create_image_to_video_task(req: ImageToVideoRequest, user_id: int = CurrentUser, db: AsyncSession = DBDep):
    """创建图生视频任务（异步轮询）"""
    quota_cost = 20
    if not await QuotaService.check_quota(db, user_id, quota_cost):
        return error("额度不足", code=1001)
    
    try:
        # 提交到万象视频API
        external_task_id = VideoService.submit_image_to_video(
            image_url=req.image_url,
            prompt=req.prompt,
            duration=req.duration
        )
        
        # 扣减额度
        await QuotaService.lock_quota(db, user_id, quota_cost, "image_to_video", description="图生视频")
        
        # 创建任务记录（运行中状态）
        task = await TaskService.create_task(
            db, user_id, TaskType.IMAGE_TO_VIDEO, req.task_name or "图生视频",
            None, {"image_url": req.image_url, "prompt": req.prompt, "duration": req.duration}, quota_cost,
            external_task_id=external_task_id
        )
        
        await db.commit()
        
        logger.info(f"图生视频任务已创建: task_id={task.id}, external_task_id={external_task_id}")
        
        return success({
            "task_id": task.id,
            "status": "running",
            "external_task_id": external_task_id
        }, "任务已提交，请稍后查看结果")
        
    except Exception as e:
        logger.error(f"图生视频失败: {str(e)}")
        return error(f"提交失败: {str(e)}")


@router.post("/text-to-video")
async def create_text_to_video_task(req: CreateTaskRequest, user_id: int = CurrentUser, db: AsyncSession = DBDep):
    """创建文生视频任务"""
    quota_cost = 20
    if not await QuotaService.check_quota(db, user_id, quota_cost):
        return error("额度不足", code=1001)
    
    await QuotaService.lock_quota(db, user_id, quota_cost, "text_to_video", description="文生视频")
    
    task = await TaskService.create_task(
        db, user_id, TaskType.TEXT_TO_VIDEO, req.task_name,
        req.model_id, req.input_params, quota_cost
    )
    
    await db.commit()

    return success({"task_id": task.id}, "任务创建成功")


@router.post("/workflow")
async def create_workflow_task(req: CreateWorkflowRequest, user_id: int = CurrentUser, db: AsyncSession = DBDep):
    """创建编排任务"""
    # 计算总消耗额度
    from app.models.task_flow import TaskFlow
    from sqlalchemy import select
    
    result = await db.execute(
        select(TaskFlow).where(TaskFlow.id == req.flow_id)
    )
    flow = result.scalar_one_or_none()
    
    if not flow:
        return error("编排模板不存在", code=404)
    
    # 计算总额度消耗
    steps = flow.flow_config.get("steps", [])
    total_quota = sum(step.get("quota_cost", 1) for step in steps)
    
    if not await QuotaService.check_quota(db, user_id, total_quota):
        return error(f"额度不足，需要{total_quota}", code=1001)
    
    # 扣减额度
    await QuotaService.lock_quota(db, user_id, total_quota, "workflow", description=f"编排任务：{flow.name}")
    
    # 创建编排任务
    task = await TaskService.create_workflow_task(db, user_id, req.flow_id, req.input_params, total_quota)
    
    await db.commit()

    return success({"task_id": task.id}, "编排任务创建成功")


@router.post("/{task_id}/cancel")
async def cancel_task(task_id: int, user_id: int = CurrentUser, db: AsyncSession = DBDep):
    """取消任务"""
    await TaskService.cancel_task(db, task_id, user_id)
    return success(None, "任务已取消")


@router.post("/{task_id}/retry")
async def retry_task(task_id: int, user_id: int = CurrentUser, db: AsyncSession = DBDep):
    """重试任务"""
    await TaskService.retry_task(db, task_id, user_id)
    return success(None, "任务已重试")


@router.post("/{task_id}/poll")
async def poll_task_status(task_id: int, user_id: int = CurrentUser, db: AsyncSession = DBDep):
    """轮询任务状态（检查异步任务完成情况）"""
    task = await TaskService.get_task(db, task_id, user_id)
    if not task:
        return error("任务不存在", code=404)
    
    # 如果已完成，直接返回
    if task.status == TaskStatus.SUCCESS:
        return success({
            "status": "success",
            "output_urls": task.output_urls
        })
    
    if task.status == TaskStatus.FAILED:
        return success({
            "status": "failed",
            "error": task.error_message
        })
    
    # 检查外部任务状态
    if not task.external_task_id:
        return success({"status": task.status.value})
    
    try:
        # 根据任务类型选择不同的轮询方式
        if task.task_type == TaskType.IMAGE_TO_VIDEO:
            # 视频任务轮询
            result = VideoService.check_video_task(task.external_task_id)
            
            if result["status"] == "SUCCEEDED":
                # 下载视频并保存到 OSS
                video_url = result["video_url"]
                save_url = await VideoService.download_and_upload_video(video_url)
                output_urls = [save_url]
                
                # 更新任务状态
                await TaskService.update_task_status(db, task_id, TaskStatus.SUCCESS, output_urls=output_urls)
                
                logger.info(f"视频任务完成: task_id={task_id}")
                return success({
                    "status": "success",
                    "output_urls": output_urls
                })
            elif result["status"] == "FAILED":
                await TaskService.update_task_status(db, task_id, TaskStatus.FAILED, error_message=result.get("error"))
                return success({
                    "status": "failed",
                    "error": result.get("error")
                })
            else:
                return success({"status": "running"})
        else:
            return success({"status": "running"})
            
    except Exception as e:
        logger.error(f"轮询任务失败: {str(e)}")
        return success({"status": "running", "message": str(e)})


from fastapi import Depends
from app.core.security import get_current_user_id
