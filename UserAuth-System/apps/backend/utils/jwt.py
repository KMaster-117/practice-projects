# utils/jwt.py
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional
from config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS


async def create_access_token(
    user_id: int, expires_delta: Optional[timedelta] = None
) -> str:
    """生成访问令牌"""
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {"sub": str(user_id), "exp": expire, "type": "access"}

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def create_refresh_token(user_id: int) -> str:
    """生成刷新令牌"""
    expire = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {"sub": str(user_id), "exp": expire, "type": "refresh"}

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def decode_token(token: str) -> dict:
    """解码并验证 token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise ValueError(f"Token验证失败: {e}")


async def verify_access_token(token: str) -> int:
    """验证访问令牌, 返回用户ID"""
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise ValueError("无效的 token 类型")

    return int(payload.get("sub"))


def verify_refresh_token(token: str) -> int:
    """验证刷新令牌, 返回用户ID"""
    payload = decode_token(token)

    if payload.get("type") != "refresh":
        raise ValueError("无效的 token 类型")

    return int(payload.get("sub"))
