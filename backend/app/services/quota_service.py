"""
额度服务 - 核心服务，所有AI功能通用
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import logging

from app.models.user_quota import UserQuota
from app.models.quota_log import QuotaLog, QuotaLogType
from app.core.redis import RedisUtil, get_quota_key, get_quota_lock_key
from app.core.exceptions import QuotaException

logger = logging.getLogger(__name__)


class QuotaService:
    """额度服务"""
    
    @staticmethod
    async def get_user_quota(db: AsyncSession, user_id: int) -> Optional[UserQuota]:
        """获取用户额度"""
        # 先查Redis缓存
        cache_key = get_quota_key(user_id)
        cached = await RedisUtil.get_json(cache_key)
        
        if cached:
            return UserQuota(**cached)
        
        # 查数据库
        result = await db.execute(
            select(UserQuota).where(UserQuota.user_id == user_id, UserQuota.is_deleted == False)
        )
        quota = result.scalar_one_or_none()
        
        if quota:
            # 缓存到Redis
            await RedisUtil.set_json(cache_key, {
                "id": quota.id,
                "user_id": quota.user_id,
                "free_quota": quota.free_quota,
                "remaining_quota": quota.remaining_quota,
                "total_recharge": quota.total_recharge,
                "total_used": quota.total_used,
            }, expire=300)
        
        return quota
    
    @staticmethod
    async def check_quota(db: AsyncSession, user_id: int, required: int = 1) -> bool:
        """检查额度是否充足"""
        quota = await QuotaService.get_user_quota(db, user_id)
        if not quota:
            return False
        return quota.remaining_quota >= required
    
    @staticmethod
    async def lock_quota(db: AsyncSession, user_id: int, amount: int = 1, 
                         biz_type: str = "", biz_id: int = None, description: str = "") -> bool:
        """
        锁定并扣减额度
        使用Redis分布式锁防止超扣
        """
        lock_key = get_quota_lock_key(user_id)
        
        # 尝试获取锁
        if not await RedisUtil.acquire_lock(lock_key, expire_seconds=10):
            raise QuotaException("系统繁忙，请稍后重试")
        
        try:
            # 检查额度
            quota = await QuotaService.get_user_quota(db, user_id)
            if not quota:
                raise QuotaException("用户额度不存在")
            
            if quota.remaining_quota < amount:
                raise QuotaException(f"额度不足，需要{amount}，剩余{quota.remaining_quota}")
            
            # 扣减额度
            new_remaining = quota.remaining_quota - amount
            new_total_used = quota.total_used + amount
            
            # 更新数据库
            await db.execute(
                update(UserQuota)
                .where(UserQuota.user_id == user_id)
                .values(
                    remaining_quota=new_remaining,
                    total_used=new_total_used
                )
            )
            
            # 记录日志
            log = QuotaLog(
                user_id=user_id,
                log_type=QuotaLogType.DEDUCT,
                amount=-amount,
                balance_before=quota.remaining_quota,
                balance_after=new_remaining,
                biz_type=biz_type,
                biz_id=biz_id,
                description=description or f"{biz_type}扣费"
            )
            db.add(log)
            await db.commit()
            
            # 更新缓存
            cache_key = get_quota_key(user_id)
            await RedisUtil.delete(cache_key)
            
            logger.info(f"User {user_id} quota deducted: {amount}, remaining: {new_remaining}")
            return True
            
        finally:
            # 释放锁
            await RedisUtil.release_lock(lock_key)
    
    @staticmethod
    async def recharge_quota(db: AsyncSession, user_id: int, amount: int,
                             log_type: QuotaLogType = QuotaLogType.RECHARGE,
                             biz_type: str = "", description: str = ""):
        """充值额度"""
        quota = await QuotaService.get_user_quota(db, user_id)
        
        if not quota:
            # 创建新额度记录
            quota = UserQuota(
                user_id=user_id,
                free_quota=0,
                remaining_quota=amount,
                total_recharge=amount if log_type == QuotaLogType.RECHARGE else 0,
                total_used=0
            )
            db.add(quota)
            await db.flush()
            balance_before = 0
            balance_after = amount
        else:
            balance_before = quota.remaining_quota
            balance_after = quota.remaining_quota + amount
            
            # 更新额度
            if log_type == QuotaLogType.RECHARGE:
                await db.execute(
                    update(UserQuota)
                    .where(UserQuota.user_id == user_id)
                    .values(
                        remaining_quota=balance_after,
                        total_recharge=UserQuota.total_recharge + amount
                    )
                )
            else:  # GIFT
                await db.execute(
                    update(UserQuota)
                    .where(UserQuota.user_id == user_id)
                    .values(
                        remaining_quota=balance_after,
                        free_quota=UserQuota.free_quota + amount
                    )
                )
        
        # 记录日志
        log = QuotaLog(
            user_id=user_id,
            log_type=log_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            biz_type=biz_type,
            description=description
        )
        db.add(log)
        await db.commit()
        
        # 清除缓存
        cache_key = get_quota_key(user_id)
        await RedisUtil.delete(cache_key)
        
        logger.info(f"User {user_id} quota recharged: {amount}, total: {balance_after}")
        return True
    
    @staticmethod
    async def init_user_quota(db: AsyncSession, user_id: int, free_quota: int = 100):
        """初始化用户额度（注册赠送）"""
        return await QuotaService.recharge_quota(
            db, user_id, free_quota,
            log_type=QuotaLogType.GIFT,
            biz_type="register",
            description="注册赠送额度"
        )
