# schemas/comment.py
from pydantic import BaseModel, Field
from typing import Optional


class PageSelect(BaseModel):
    """分页查询"""

    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)
