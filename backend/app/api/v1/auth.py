"""
认证相关API
"""
from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DBDep
from app.core.response import success, error
from app.core.security import get_current_user_id
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["认证"])


class RegisterRequest(BaseModel):
    """注册请求"""
    email: EmailStr = None
    phone: str = None
    username: str = None
    password: str


class LoginRequest(BaseModel):
    """登录请求"""
    account: str
    password: str


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str
    new_password: str


@router.post("/register")
async def register(request: Request, req: RegisterRequest, db: AsyncSession = DBDep):
    """用户注册"""
    client_ip = request.client.host
    user = await UserService.register(
        db, 
        email=req.email, 
        phone=req.phone,
        username=req.username,
        password=req.password,
        register_ip=client_ip
    )
    return success({
        "id": user.id,
        "email": user.email,
        "phone": user.phone,
        "username": user.username
    }, "注册成功")


@router.post("/login")
async def login(request: Request, req: LoginRequest, db: AsyncSession = DBDep):
    """用户登录"""
    client_ip = request.client.host
    result = await UserService.login(db, req.account, req.password, client_ip)
    return success(result, "登录成功")


@router.get("/profile")
async def get_profile(user_id: int = Depends(get_current_user_id), db: AsyncSession = DBDep):
    """获取用户信息"""
    from app.services.user_service import UserService
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        return error("用户不存在", code=404)
    return success({
        "id": user.id,
        "email": user.email,
        "phone": user.phone,
        "username": user.username,
        "status": user.status.value,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None
    })


@router.put("/profile")
async def update_profile(req: dict, user_id: int = Depends(get_current_user_id), db: AsyncSession = DBDep):
    """更新用户信息"""
    user = await UserService.update_profile(db, user_id, **req)
    return success({
        "id": user.id,
        "username": user.username
    }, "更新成功")


@router.post("/change-password")
async def change_password(req: ChangePasswordRequest, user_id: int = Depends(get_current_user_id), db: AsyncSession = DBDep):
    """修改密码"""
    await UserService.change_password(db, user_id, req.old_password, req.new_password)
    return success(None, "密码修改成功")



