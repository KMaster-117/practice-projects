from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt

from config import settings


async def generate_expire_time(minutes: float):
    """生成过期时间"""
    expire = datetime.now() + timedelta(minutes=minutes)
    return expire


async def create_access_token(subject: Union[str, Any]):
    """生成 access_token"""
    expire = await generate_expire_time(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt, expire


async def create_refresh_token(subject: Union[str, Any]) -> str:
    """生成 refresh_token"""
    expire = await generate_expire_time(settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def verify_token(token: str) -> int | None:
    """校验令牌 是否有效 返回 user_id"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if not user_id:
            return None
        return int(user_id)
    except jwt.JWTError:
        return None


async def refresh_access_token(refresh_token: str):
    """刷新 access_token 用 refresh_token 换取新的 access_token"""
    user_id = await verify_token(refresh_token)
    if not user_id:
        return None
    encoded_jwt, expire = await create_access_token(user_id)
    return user_id, encoded_jwt, expire
