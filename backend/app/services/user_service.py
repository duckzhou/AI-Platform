"""
用户服务
"""
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.user import User, UserStatus
from app.models.user_quota import UserQuota
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.exceptions import AuthException, BusinessException
from app.core.config import settings
from app.services.quota_service import QuotaService


class UserService:
    """用户服务"""
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        result = await db.execute(
            select(User).where(User.id == user_id, User.is_deleted == False)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        result = await db.execute(
            select(User).where(User.email == email, User.is_deleted == False)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_phone(db: AsyncSession, phone: str) -> Optional[User]:
        """根据手机号获取用户"""
        result = await db.execute(
            select(User).where(User.phone == phone, User.is_deleted == False)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        result = await db.execute(
            select(User).where(User.username == username, User.is_deleted == False)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def register(db: AsyncSession, email: str = None, phone: str = None, 
                       username: str = None, password: str = None, register_ip: str = None) -> User:
        """用户注册"""
        # 检查密码
        if not password:
            raise BusinessException("密码不能为空")
        if len(password) < 6:
            raise BusinessException("密码至少6位")
        
        # 检查是否至少提供了邮箱或手机号
        if not email and not phone:
            raise BusinessException("邮箱或手机号至少填写一个")
        
        # 检查邮箱是否已注册
        if email:
            existing = await UserService.get_user_by_email(db, email)
            if existing:
                raise BusinessException("该邮箱已注册")
        
        # 检查手机号是否已注册
        if phone:
            existing = await UserService.get_user_by_phone(db, phone)
            if existing:
                raise BusinessException("该手机号已注册")
        
        # 检查用户名是否已存在
        if username:
            existing = await UserService.get_user_by_username(db, username)
            if existing:
                raise BusinessException("该用户名已被使用")
        
        # 创建用户
        user = User(
            email=email,
            phone=phone,
            username=username,
            password_hash=get_password_hash(password),
            register_ip=register_ip,
            status=UserStatus.ACTIVE
        )
        db.add(user)
        await db.flush()
        
        # 初始化用户额度（注册赠送）
        await QuotaService.init_user_quota(db, user.id, settings.FREE_QUOTA_ON_REGISTER)
        
        await db.commit()
        return user
    
    @staticmethod
    async def login(db: AsyncSession, account: str, password: str, login_ip: str = None) -> dict:
        """用户登录"""
        # 判断账号类型（邮箱/手机号/用户名）
        if "@" in account:
            user = await UserService.get_user_by_email(db, account)
        elif account.isdigit():
            user = await UserService.get_user_by_phone(db, account)
        else:
            user = await UserService.get_user_by_username(db, account)
        
        if not user:
            raise AuthException("账号或密码错误")
        
        if user.status == UserStatus.BANNED:
            raise AuthException("账号已被禁用")
        
        if not verify_password(password, user.password_hash):
            raise AuthException("账号或密码错误")
        
        # 更新登录信息
        await db.execute(
            update(User)
            .where(User.id == user.id)
            .values(
                last_login_at=datetime.utcnow(),
                last_login_ip=login_ip
            )
        )
        await db.commit()
        
        # 生成Token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "phone": user.phone,
                "username": user.username,
            }
        }
    
    @staticmethod
    async def update_profile(db: AsyncSession, user_id: int, **kwargs) -> User:
        """更新用户信息"""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise BusinessException("用户不存在")
        
        allowed_fields = ["username"]
        update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if update_data:
            await db.execute(
                update(User).where(User.id == user_id).values(**update_data)
            )
            await db.commit()
        
        return await UserService.get_user_by_id(db, user_id)
    
    @staticmethod
    async def change_password(db: AsyncSession, user_id: int, old_password: str, new_password: str):
        """修改密码"""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise BusinessException("用户不存在")
        
        if not verify_password(old_password, user.password_hash):
            raise BusinessException("原密码错误")
        
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(password_hash=get_password_hash(new_password))
        )
        await db.commit()
        return True
