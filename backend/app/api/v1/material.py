"""
素材管理API
"""
from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.api.deps import DBDep, CurrentUser
from app.core.response import success, error
from app.models.material import Material, MaterialType
from app.services.oss_service import OSSService

router = APIRouter(prefix="/materials", tags=["素材管理"])


# 预设分类列表
DEFAULT_CATEGORIES = ["头像", "背景", "素材", "图标", "插画", "照片", "设计", "其他"]

# 预设标签列表
DEFAULT_TAGS = ["人物", "风景", "动物", "植物", "建筑", "美食", "科技", "艺术", "简约", "复古", "现代", "卡通"]


@router.get("/categories")
async def get_categories():
    """获取分类列表"""
    return success({"list": DEFAULT_CATEGORIES})


@router.get("/tags")
async def get_tags():
    """获取标签列表"""
    return success({"list": DEFAULT_TAGS})


@router.get("")
async def get_materials(
    material_type: str = None,
    category: str = None,
    page: int = 1,
    size: int = 20,
    user_id: int = CurrentUser,
    db: AsyncSession = DBDep
):
    """获取素材列表"""
    from sqlalchemy import select, desc
    
    query = select(Material).where(
        Material.user_id == user_id,
        Material.is_deleted == False
    )
    
    if material_type:
        query = query.where(Material.material_type == MaterialType(material_type))
    if category:
        query = query.where(Material.category == category)
    
    query = query.order_by(desc(Material.created_at)).offset((page - 1) * size).limit(size)
    
    result = await db.execute(query)
    materials = result.scalars().all()
    
    return success({
        "list": [
            {
                "id": m.id,
                "name": m.name,
                "material_type": m.material_type.value,
                "file_url": m.file_url,
                "file_size": m.file_size,
                "file_format": m.file_format,
                "category": m.category,
                "tags": m.tags,
                "thumbnail_url": m.thumbnail_url,
                "created_at": m.created_at.isoformat()
            }
            for m in materials
        ]
    })


@router.post("/upload")
async def upload_material(
    file: UploadFile = File(...),
    name: str = Form(None),
    material_type: str = Form(...),
    category: str = Form(None),
    tags: str = Form(None),
    user_id: int = CurrentUser,
    db: AsyncSession = DBDep
):
    """上传素材"""
    # 读取文件内容
    content = await file.read()
    file_size = len(content)
    
    # 上传到 OSS
    upload_result = OSSService.upload_file(content, file.filename, folder="materials")
    file_url = upload_result["file_url"]
    file_key = upload_result["file_key"]
    
    file_ext = file.filename.split(".")[-1] if "." in file.filename else ""
    
    material = Material(
        user_id=user_id,
        name=name or file.filename,
        material_type=MaterialType(material_type),
        file_url=file_url,
        file_size=file_size,
        file_format=file_ext,
        category=category,
        tags=tags,
        thumbnail_url=file_url if material_type == "image" else None
    )
    
    db.add(material)
    await db.commit()
    
    return success({
        "id": material.id,
        "name": material.name,
        "file_url": file_url,
        "file_size": file_size
    }, "上传成功")


@router.delete("/{material_id}")
async def delete_material(material_id: int, user_id: int = CurrentUser, db: AsyncSession = DBDep):
    """删除素材"""
    from sqlalchemy import update
    
    result = await db.execute(
        update(Material)
        .where(Material.id == material_id, Material.user_id == user_id)
        .values(is_deleted=True)
    )
    await db.commit()
    
    if result.rowcount == 0:
        return error("素材不存在", code=404)
    
    return success(None, "删除成功")


from fastapi import Depends
from app.core.security import get_current_user_id
