from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


def validate_phone(v: str | None) -> str | None:
    """校验手机号"""
    if v is None:
        return v

    if len(v) != 11:
        raise ValueError("手机号必须是11位")
    if not v.isdigit():
        raise ValueError("手机号必须是纯数字")
    return v


class UserLogin(BaseModel):
    """用户登陆"""

    username: str
    password: str


class UserRegist(BaseModel):
    """用户注册"""

    username: str
    phone: str
    email: EmailStr
    password: str

    @field_validator("phone")
    def check_phone(cls, v):
        return validate_phone(v)


class UserCreate(UserRegist):
    """用户创建"""

    is_admin: int = Field(..., ge=0, le=1, description="管理员: 0-否 1-是")


class UserUpdate(BaseModel):
    """用户修改"""

    id: int
    username: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    is_admin: Optional[int] = Field(None, ge=0, le=1, description="管理员: 0-否 1-是")

    @field_validator("phone")
    def check_phone(cls, v):
        return validate_phone(v)


class UserUpdateStatus(BaseModel):
    """用户修改状态"""

    id: int
    state: int = Field(..., ge=0, le=1, description="状态: 0-禁用, 1-正常")


class UserUpdatePassword(BaseModel):
    """用户修改密码"""

    id: int
    old_password: str
    new_password: str


class UserRefreshToken(BaseModel):
    """用户刷新令牌"""

    refresh_token: str


class UserDelete(BaseModel):
    """删除用户"""

    id: int
