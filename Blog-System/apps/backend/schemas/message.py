from pydantic import BaseModel
from typing import Optional

from .comment import PageSelect


class MessageGet(PageSelect):
    """获取文章评论"""

    user_id: int
    article_id: int


class MessageCreate(BaseModel):
    """新建评论"""

    user_id: int
    article_id: int
    message: str


class MessageDelete(BaseModel):
    """删除评论"""

    id: int
