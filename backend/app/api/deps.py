"""
API依赖
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_id


# 数据库依赖
DBDep = Depends(get_db)

# 当前用户依赖
CurrentUser = Depends(get_current_user_id)
