"""
Redis 连接和操作封装
"""
import json
import redis.asyncio as redis
from typing import Optional, Any, Union

from app.core.config import settings

# Redis连接池
redis_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
    max_connections=100,
)

# Redis客户端
redis_client = redis.Redis(connection_pool=redis_pool)


class RedisUtil:
    """Redis工具类"""
    
    @staticmethod
    async def get(key: str) -> Optional[str]:
        """获取值"""
        return await redis_client.get(key)
    
    @staticmethod
    async def set(key: str, value: Union[str, int, float], expire: Optional[int] = None):
        """设置值"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        await redis_client.set(key, value, ex=expire)
    
    @staticmethod
    async def delete(key: str):
        """删除键"""
        await redis_client.delete(key)
    
    @staticmethod
    async def exists(key: str) -> bool:
        """检查键是否存在"""
        return await redis_client.exists(key) > 0
    
    @staticmethod
    async def expire(key: str, seconds: int):
        """设置过期时间"""
        await redis_client.expire(key, seconds)
    
    @staticmethod
    async def incr(key: str, amount: int = 1) -> int:
        """自增"""
        return await redis_client.incr(key, amount)
    
    @staticmethod
    async def decr(key: str, amount: int = 1) -> int:
        """自减"""
        return await redis_client.decr(key, amount)
    
    @staticmethod
    async def setnx(key: str, value: Any) -> bool:
        """仅当键不存在时设置"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        return await redis_client.setnx(key, value)
    
    @staticmethod
    async def get_json(key: str) -> Optional[Any]:
        """获取JSON值"""
        value = await redis_client.get(key)
        if value:
            try:
                return json.loads(value)
            except:
                return value
        return None
    
    @staticmethod
    async def set_json(key: str, value: Any, expire: Optional[int] = None):
        """设置JSON值"""
        await redis_client.set(key, json.dumps(value, ensure_ascii=False), ex=expire)
    
    @staticmethod
    async def acquire_lock(lock_key: str, expire_seconds: int = 10) -> bool:
        """获取分布式锁"""
        return await redis_client.set(lock_key, "1", nx=True, ex=expire_seconds)
    
    @staticmethod
    async def release_lock(lock_key: str):
        """释放分布式锁"""
        await redis_client.delete(lock_key)


# 额度相关的Redis键
def get_quota_key(user_id: int) -> str:
    """用户额度键"""
    return f"quota:{user_id}"


def get_quota_lock_key(user_id: int) -> str:
    """额度扣减锁键"""
    return f"quota:lock:{user_id}"


def get_task_status_key(task_id: int) -> str:
    """任务状态键"""
    return f"task:status:{task_id}"
