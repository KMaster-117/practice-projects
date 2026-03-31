from pydantic import BaseModel
from typing import Optional, Generic, TypeVar
from datetime import datetime

T = TypeVar("T")


class BaseResponse(BaseModel):
    """基础响应"""

    code: int = 200
    message: str = "success"
    timestamp: datetime = datetime.now()


class DataResponse(BaseResponse, Generic[T]):
    """带数据的响应"""

    data: Optional[T] = None


class PageResponse(BaseModel):
    """分页响应"""

    items: list
    total: int
    page: int
    size: int
    pages: int
