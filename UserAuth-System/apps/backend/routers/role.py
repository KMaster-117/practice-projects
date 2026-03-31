from fastapi import APIRouter, HTTPException, status, Request


from models import User, Role
from utils import check_login, check_permission, get_current_user, get_user_permissions
from schemas import (
    RoleLevel,
    RoleResponse,
    RoleCreate,
    RoleUpdate,
    RoleDelete,
    PasswordChange,
)

router = APIRouter(prefix="/role", tags=["角色管理"])


@router.get("/select")
async def select_role(req: Request, rolename: str):
    # 1. 获取 token
    if not token:
        token = req.headers.get("Authorization")

    # 2. 用户校验
    user_info, error = await get_current_user(token)
    if error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error)

    role = await Role.get_or_none(name=rolename)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")


@router.post("/create")
async def create_role(req: Request, item: RoleCreate):
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

    role = await Role.get_or_none(name=item.name)
    if role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="角色已存在"
        )

    new_role = await Role.create(name=item.name, level=item.level)

    return new_role


@router.put("/update")
async def update_role(req: Request, item: RoleUpdate):
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

    role = await Role.get_or_none(name=item.name)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")

    if item.name:
        role.name = item.name
    if item.level:
        role.level = item.level

    await role.save()

    return role


@router.delete("/delete")
async def delete_role(req: Request, item: RoleDelete):
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

    role = await Role.get_or_none(name=item.name)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")

    await role.delete()

    return {"message": "角色删除成功"}
