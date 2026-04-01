"""
额度相关API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DBDep, CurrentUser
from app.core.response import success
from app.services.quota_service import QuotaService

router = APIRouter(prefix="/quota", tags=["额度"])


@router.get("/info")
async def get_quota_info(user_id: int = CurrentUser, db: AsyncSession = DBDep):
    """获取用户额度信息"""
    quota = await QuotaService.get_user_quota(db, user_id)
    if not quota:
        return success({
            "free_quota": 0,
            "remaining_quota": 0,
            "total_recharge": 0,
            "total_used": 0
        })
    return success({
        "free_quota": quota.free_quota,
        "remaining_quota": quota.remaining_quota,
        "total_recharge": quota.total_recharge,
        "total_used": quota.total_used
    })


@router.get("/logs")
async def get_quota_logs(
    page: int = 1, 
    size: int = 20,
    user_id: int = CurrentUser, 
    db: AsyncSession = DBDep
):
    """获取额度日志"""
    from sqlalchemy import select, desc
    from app.models.quota_log import QuotaLog
    
    result = await db.execute(
        select(QuotaLog)
        .where(QuotaLog.user_id == user_id, QuotaLog.is_deleted == False)
        .order_by(desc(QuotaLog.created_at))
        .offset((page - 1) * size)
        .limit(size)
    )
    logs = result.scalars().all()
    
    return success({
        "list": [
            {
                "id": log.id,
                "log_type": log.log_type.value,
                "amount": log.amount,
                "balance_before": log.balance_before,
                "balance_after": log.balance_after,
                "biz_type": log.biz_type,
                "description": log.description,
                "created_at": log.created_at.isoformat()
            }
            for log in logs
        ]
    })
