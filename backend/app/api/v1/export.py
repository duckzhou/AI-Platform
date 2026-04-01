"""
导出下载API
"""
from fastapi import APIRouter, Depends, Response
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import zipfile
import io
import os

from app.api.deps import DBDep, CurrentUser
from app.core.response import success, error

router = APIRouter(prefix="/export", tags=["导出下载"])


@router.get("/download/{task_id}")
async def download_task_output(
    task_id: int,
    file_index: int = 0,
    user_id: int = CurrentUser,
    db: AsyncSession = DBDep
):
    """下载单个任务输出文件"""
    from app.services.task_service import TaskService
    
    task = await TaskService.get_task(db, task_id, user_id)
    if not task:
        return error("任务不存在", code=404)
    
    if task.status.value != "success":
        return error("任务未完成", code=400)
    
    output_urls = task.output_urls or []
    if file_index >= len(output_urls):
        return error("文件不存在", code=404)
    
    file_url = output_urls[file_index]
    
    # 返回文件URL
    return success({"download_url": file_url})


@router.post("/download/batch")
async def batch_download(
    task_ids: list,
    user_id: int = CurrentUser,
    db: AsyncSession = DBDep
):
    """批量下载，打包为ZIP"""
    from app.services.task_service import TaskService
    
    # 创建内存中的ZIP文件
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for task_id in task_ids:
            task = await TaskService.get_task(db, task_id, user_id)
            if task and task.status.value == "success" and task.output_urls:
                for i, url in enumerate(task.output_urls):
                    # 这里应该下载文件内容，这里仅添加URL作为示例
                    filename = f"task_{task_id}_file_{i}.txt"
                    zip_file.writestr(filename, f"File URL: {url}")
    
    zip_buffer.seek(0)
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=download.zip"}
    )


@router.post("/copy-url")
async def copy_url(task_id: int, file_index: int = 0, user_id: int = CurrentUser, db: AsyncSession = DBDep):
    """复制文件URL"""
    from app.services.task_service import TaskService
    
    task = await TaskService.get_task(db, task_id, user_id)
    if not task or task.status.value != "success":
        return error("任务不存在或未完成", code=404)
    
    output_urls = task.output_urls or []
    if file_index >= len(output_urls):
        return error("文件不存在", code=404)
    
    return success({"url": output_urls[file_index]})


from fastapi import Depends
from app.core.security import get_current_user_id
