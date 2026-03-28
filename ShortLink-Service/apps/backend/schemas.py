from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional


class ShortLinkRequest(BaseModel):
    """创建短链接请求"""

    url: HttpUrl
    expire_days: Optional[int] = None
    custom_code: Optional[str] = None  # 自定义短码


class ShortLinkResponse(BaseModel):
    """创建短链接响应"""

    short_code: str
    short_url: str
    original_url: str
    expire_at: Optional[datetime]
    created_at: datetime


class StatsResponse(BaseModel):
    """统计信息响应"""

    short_code: str
    original_url: str
    access_count: int
    created_at: datetime
    expire_at: Optional[datetime]


class HealthResponse(BaseModel):
    """健康检查响应"""

    status: str
    database: bool
    redis: bool
