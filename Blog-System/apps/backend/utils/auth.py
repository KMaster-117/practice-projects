from fastapi import Request
from passlib.context import CryptContext
from datetime import datetime, timezone

from .response import APIException
from .jwt import verify_token
from .redis_client import redis_client

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # 选择加密方式


async def get_password_hash(password: str) -> str:
    """加密密码"""
    return pwd_context.hash(password)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验密码"""
    return pwd_context.verify(plain_password, hashed_password)


async def get_current_user(req: Request):
    from models import User

    """全局通用：获取当前登录用户（全校验）"""
    # 1. 获取 token
    token = req.headers.get("Authorization")
    if not token:
        raise APIException("请先登录", 401)

    # 2. 去掉前缀
    if token.startswith("Bearer "):
        token = token[7:]
    else:
        raise APIException("令牌格式错误", 401)

    # 3. 校验 token
    user_id = await verify_token(token)
    if not user_id:
        raise APIException("令牌无效或已过期", 401)

    # 4. 从Redis中获取token，判断令牌是否无效或已过期
    redis_token = redis_client.get(f"user_id:{user_id}")
    if not redis_token:
        raise APIException("令牌无效或已过期", 401)

    # 5. 校验用户是否存在
    user = await User.get_or_none(id=user_id, is_delete=0)
    if not user:
        raise APIException("用户不存在", 404)

    # 全部通过 → 返回用户完整信息
    return user


async def redis_add(user_id: int, expire: datetime, token: str):
    """Redis添加数据"""
    expire_seconds = int((expire - datetime.now()).total_seconds())
    redis_client.setex(f"user_id:{user_id}", expire_seconds, token)


async def redis_delete(user_id: int):
    """Redis添加数据"""
    redis_client.delete(f"user_id:{user_id}")
