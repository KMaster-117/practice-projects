from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class UserResponse(BaseModel):
    """用户响应"""

    id: int
    username: str
    email: str
    nickname: Optional[str] = None
    is_active: bool
    is_superuser: bool
    is_black: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserSelect(BaseModel):
    username: str


class UserCreate(BaseModel):
    """创建用户（管理员）"""

    username: str = Field(min_length=3, max_length=64)
    email: Optional[str] = None
    password: str = Field(min_length=6, max_length=64)
    nickname: Optional[str] = Field(max_length=64)
    is_active: Optional[int] = None
    is_superuser: Optional[int] = None
    is_black: Optional[int] = None


class UserUpdate(BaseModel):
    """更新用户"""

    username: str
    email: Optional[str] = None
    nickname: Optional[str] = None
    is_active: Optional[int] = None
    is_superuser: Optional[int] = None
    is_black: Optional[int] = None


class PasswordChange(BaseModel):
    """修改密码"""

    username: str
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=255)


class UserDelete(BaseModel):
    """删除用户"""

    username: str
