# utils/auth.py
import json
from typing import Optional, List, Dict, Tuple
from redis_client import redis_client


async def check_login(token: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
    """
    校验用户登录状态
    返回: (是否成功, 用户信息, 错误信息)
    """
    if not token:
        return False, None, "未提供认证令牌"

    # 去除 Bearer 前缀
    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    # 从 Redis 获取会话
    session_key = f"session:{token}"
    session_data = await redis_client.get(session_key)

    if not session_data:
        return False, None, "token 无效或已过期"

    # 解析会话数据
    session = json.loads(session_data)

    # 可选：延长过期时间（滑动窗口）
    await redis_client.expire(session_key, 7200)

    return True, session, None


async def check_permission(user_id: int, required_permission: str) -> Tuple[bool, str]:
    """
    校验用户权限
    返回: (是否有权限, 错误信息)
    """
    # 1. 先查缓存
    cache_key = f"user_permissions:{user_id}"
    permissions = await redis_client.get(cache_key)

    if permissions:
        permissions = json.loads(permissions)
    else:
        # 2. 从数据库查询用户权限
        permissions = await get_user_permissions(user_id)
        # 缓存权限，5分钟过期
        await redis_client.setex(cache_key, 300, json.dumps(permissions))

    # 3. 校验权限
    if required_permission not in permissions:
        return False, f"缺少权限: {required_permission}"

    return True, ""


async def get_user_permissions(user_id: int) -> List[str]:
    """
    从数据库获取用户的所有权限
    基于用户角色和超级用户标识
    """
    from models import User, Role, UserRole

    user = await User.get_or_none(id=user_id)
    if not user:
        return []

    # 超级用户拥有所有权限
    if user.is_superuser == 1:
        return ["*"]  # 通配符表示所有权限

    # 查询用户角色
    user_roles = await UserRole.filter(user_id=user_id).select_related("role")

    # 根据角色等级返回权限
    permissions = set()
    for ur in user_roles:
        role = ur.role
        if role.level >= 0:
            permissions.add("read")
        if role.level >= 1:
            permissions.add("write")
        if role.level >= 2:
            permissions.add("admin")

    return list(permissions)


async def get_current_user(token: str):
    """
    获取当前登录用户信息
    返回: (用户信息, 错误信息)
    """
    from models import User

    success, session, error = await check_login(token)
    if not success:
        return None, error

    # 可以额外从数据库获取最新用户信息
    user = await User.get_or_none(id=session["user_id"])
    if not user:
        return None, "用户不存在"

    if user.is_active == 0:
        return None, "账号已被禁用"

    if user.is_black == 1:
        return None, "账号已被拉黑"

    return user, None
