from pydantic import BaseModel
from typing import Optional


class LikeGet(BaseModel):
    """获取点赞"""

    article_id: int


class LikeCreate(BaseModel):
    """新建点赞"""

    user_id: int
    article_id: int


class LikeDelete(BaseModel):
    """删除点赞"""

    id: int
