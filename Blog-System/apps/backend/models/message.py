from tortoise import fields
from .comment import BaseModel


class Messages(BaseModel):
    """评论表"""

    user_id = fields.BigIntField(description="用户id")
    username = fields.CharField(max_length=255, description="用户名称")
    article_id = fields.BigIntField(description="文章id")
    message = fields.TextField(description="评论内容")
    is_delete = fields.SmallIntField(default=0, description="是否删除 0不删除 1删除")

    class Meta:
        table = "tbl_messages"
