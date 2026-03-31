from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class UserRegister(BaseModel):
    """用户注册"""

    username: str
    password: str
    nickname: str
    email: Optional[str] = None


class UserLogin(BaseModel):
    """用户登陆"""

    username: str
    password: str
