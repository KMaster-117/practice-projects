from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import IntEnum


class RoleLevel(IntEnum):
    """角色等级"""

    READ = 0
    WRITE = 1
    ADMIN = 2


class RoleResponse(BaseModel):
    """角色响应"""

    id: int
    name: str
    level: RoleLevel
    created_at: datetime

    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    """创建角色"""

    name: str
    level: RoleLevel = RoleLevel.READ


class RoleUpdate(BaseModel):
    """更新角色"""

    name: Optional[str] = None
    level: Optional[RoleLevel] = None


class RoleDelete(BaseModel):
    """删除角色"""

    name: str


class AssignRoleRequest(BaseModel):
    """分配角色请求"""

    user_id: int
    role_id: int
