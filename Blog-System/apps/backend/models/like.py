from tortoise import fields
from .comment import BaseModel


class Likes(BaseModel):
    """点赞表"""

    user_id = fields.BigIntField(description="用户id")
    article_id = fields.BigIntField(description="文章id")

    class Meta:
        table = "tbl_likes"
        unique_together = [("user_id", "article_id")]
