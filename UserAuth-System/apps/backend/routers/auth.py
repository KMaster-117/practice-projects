import bcrypt
import uuid
import json
from fastapi import APIRouter, HTTPException, status, Request
from typing import Optional
from datetime import datetime

from models import User
from schemas import UserRegister, UserLogin, PasswordChange
from redis_client import redis_client
from utils import create_access_token, verify_access_token

router = APIRouter(prefix="/auth", tags=["权限管理"])


@router.post("/register")
async def user_register(item: UserRegister):
    """
    用户注册
    """
    user = await User.get_or_none(username=item.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在"
        )

    # 检查邮箱是否已存在（如果提供了邮箱）
    if item.email:
        email = await User.get_or_none(email=item.email)
        if email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已被注册"
            )

    try:
        hashed_password = bcrypt.hashpw(item.password.encode("utf-8"), bcrypt.gensalt())

        new_user = await User.create(
            username=item.username,
            password=hashed_password.decode("utf-8"),
            nickname=item.nickname,
            email=item.email,
            is_active=1,
            is_superuser=0,
            is_black=0,
        )

        # 5. 返回用户信息（不返回密码）
        return {
            "message": "注册成功",
            "user": {
                "id": new_user.id,
                "username": new_user.username,
                "nickname": new_user.nickname,
                "email": new_user.email,
                "created_at": new_user.created_at,
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}",
        )


@router.post("/login")
async def user_login(req: Request, item: UserLogin):
    # 1. 查询用户
    user = await User.get_or_none(username=item.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误"
        )

    # 2. 检查用户状态
    if user.is_active == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="账号已被禁用，请联系管理员"
        )

    if user.is_black == 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="账号已被拉黑，请联系管理员"
        )

    # 3. 验证密码
    if not bcrypt.checkpw(item.password.encode("utf-8"), user.password.encode("utf-8")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误"
        )

    # 生成 token
    # token = uuid.uuid4().hex
    token = await create_access_token(user.id)

    last_login = datetime.now()

    # 构建会话数据
    session_data = {
        "user_id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "email": user.email,
        "is_superuser": user.is_superuser,
        "login_time": last_login,
        "ip": req.client.host if req.client else "unknown",
    }

    # 存入 Redis，2小时过期
    await redis_client.setex(
        f"session:{token}", 7200, json.dumps(session_data)  # 2小时 = 7200秒
    )

    # 记录用户的所有活跃会话（用于多设备管理）
    await redis_client.sadd(f"user_sessions:{user.id}", token)
    await redis_client.expire(f"user_sessions:{user.id}", 7200)

    # 更新最后登录时间
    user.last_login = last_login
    await user.save()

    # 返回 token
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 7200,
        "user": {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "email": user.email,
            "is_superuser": user.is_superuser,
        },
    }


@router.post("/logout")
async def user_logout(req: Request):
    """
    用户注销 - 删除 Redis 中的会话
    """
    # 获取 token
    token = req.headers.get("Authorization")
    user_id = await verify_access_token(token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="未提供正确token"
        )

    # 1. 获取会话数据
    session_key = f"session:{token}"
    session_data = await redis_client.get(session_key)

    if session_data:
        session = json.loads(session_data)
        user_id = session.get("user_id")

        # 2. 删除会话
        await redis_client.delete(session_key)

        # 3. 从用户会话集合中移除
        if user_id:
            await redis_client.srem(f"user_sessions:{user_id}", token)

    return {"message": "注销成功"}
