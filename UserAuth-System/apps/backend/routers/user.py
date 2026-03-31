import bcrypt
from fastapi import APIRouter, HTTPException, status, Request
from typing import Optional

from models import User
from utils import check_login, check_permission, get_current_user, get_user_permissions
from schemas import UserSelect, UserCreate, UserUpdate, UserDelete, PasswordChange

router = APIRouter(prefix="/user", tags=["用户管理"])


@router.get("/select")
async def get_current_user(req: Request, item: UserSelect):
    """
    查询用户信息 - 第一步校验用户
    """
    # 1. 获取 token
    token = req.headers.get("Authorization")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="无效的 token"
        )

    # 2. 用户校验
    user_info, error = await get_current_user(token)
    if error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error)

    # 3. 业务逻辑：查询用户
    target_user = await User.get_or_none(username=item.username)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    # 4. 权限校验：只能查询自己或拥有查询权限
    if target_user.id != user_info["id"]:
        # 检查是否有查询其他用户的权限
        has_permission, perm_error = await check_permission(
            user_info["id"], "user:query"
        )
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=perm_error
            )

    # 5. 返回用户信息
    return {
        "id": target_user.id,
        "username": target_user.username,
        "nickname": target_user.nickname,
        "email": target_user.email,
        "is_active": target_user.is_active,
        "created_at": target_user.created_at.isoformat(),
    }


@router.post("/create")
async def create_user(req: Request, user: UserCreate):
    # 1. 用户校验
    if not token:
        token = req.headers.get("Authorization")

    user_info, error = await get_current_user(token)
    if error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error)
    # 2. 权限校验：需要创建用户权限
    has_permission, perm_error = await check_permission(user_info["id"], "user:create")
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=perm_error)
    # 3. 业务逻辑：检查用户名是否已存在
    existing = await User.get_or_none(username=user.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在"
        )
    # 4. 创建用户
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())

    new_user = await User.create(
        username=user.username,
        password=hashed_password.decode("utf-8"),
        nickname=user.nickname,
        email=user.email,
        is_active=1,
        is_superuser=0,
        is_black=0,
    )

    # 5. 返回用户信息
    return {
        "message": "用户创建成功",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "nickname": new_user.nickname,
        },
    }


@router.put("/update")
async def update_user(req: Request, user: UserUpdate):
    # 1. 用户校验
    if not token:
        token = req.headers.get("Authorization")

    user_info, error = await get_current_user(token)
    if error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error)

    # 2. 查找目标用户
    target_user = await User.get_or_none(username=user.username)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    # 3. 权限校验：可以修改自己，或拥有更新权限
    if target_user.id != user_info["id"]:
        has_permission, perm_error = await check_permission(
            user_info["id"], "user:update"
        )
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=perm_error
            )

    # 4. 更新用户信息
    if user.nickname:
        target_user.nickname = user.nickname
    if user.email:
        target_user.email = user.email

    await target_user.save()

    # 5. 返回更新后的信息
    return {
        "message": "用户更新成功",
        "user": {
            "id": target_user.id,
            "username": target_user.username,
            "nickname": target_user.nickname,
            "email": target_user.email,
        },
    }


@router.delete("/delete")
async def delete_user(req: Request, user: UserDelete):
    """
    删除用户（逻辑删除）- 需要删除权限
    """
    # 1. 用户校验
    if not token:
        token = req.headers.get("Authorization")

    user_info, error = await get_current_user(token)
    if error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error)

    # 2. 权限校验：需要删除权限
    has_permission, perm_error = await check_permission(user_info["id"], "user:delete")
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=perm_error)

    # 3. 查找目标用户
    target_user = await User.get_or_none(username=user.username)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    # 4. 逻辑删除（设置状态为禁用）
    target_user.is_active = 0
    await target_user.save()

    return {"message": "用户删除成功"}


@router.post("/update/password")
async def update_user_password(req: Request, user: PasswordChange):
    """
    修改密码 - 可修改自己或管理员修改他人
    """
    # 1. 用户校验
    if not token:
        token = req.headers.get("Authorization")

    user_info, error = await get_current_user(token)
    if error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error)

    # 2. 查找目标用户
    target_user = await User.get_or_none(username=user.username)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    # 3. 权限校验
    is_self = target_user.id == user_info["id"]

    if is_self:
        # 修改自己的密码：需要验证旧密码
        if not user.old_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="修改密码需要提供旧密码"
            )

        # 验证旧密码
        if not bcrypt.checkpw(
            user.old_password.encode("utf-8"), target_user.password.encode("utf-8")
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="旧密码错误"
            )
    else:
        # 修改他人密码：需要管理员权限
        has_permission, perm_error = await check_permission(
            user_info["id"], "user:update"
        )
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=perm_error
            )

    # 4. 更新密码
    hashed_password = bcrypt.hashpw(user.new_password.encode("utf-8"), bcrypt.gensalt())
    target_user.password = hashed_password.decode("utf-8")
    await target_user.save()

    return {"message": "密码修改成功"}
