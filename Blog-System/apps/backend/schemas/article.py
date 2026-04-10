from pydantic import BaseModel, Field
from typing import Optional


class ArticleCreate(BaseModel):
    """新建文章"""

    user_id: int
    title: str
    body: str
    state: int = Field(
        ..., ge=0, le=2, description="状态: 0-草稿 1-已发布 2-仅自己可见"
    )


class ArticleUpdate(BaseModel):
    """修改文章"""

    id: int
    title: Optional[str] = None
    body: Optional[str] = None
    state: Optional[int] = Field(
        None, ge=0, le=2, description="状态: 0-草稿 1-已发布 2-仅自己可见"
    )


class ArticleDelete(BaseModel):
    """删除文章"""

    id: int
