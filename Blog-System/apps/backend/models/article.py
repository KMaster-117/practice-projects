from tortoise import fields
from .comment import BaseModel


class Articles(BaseModel):
    """文章表"""

    user_id = fields.BigIntField(description="用户id")
    username = fields.CharField(max_length=255, description="用户名称")
    title = fields.CharField(max_length=100, description="文章标题")
    body = fields.TextField(default="", description="文章正文")
    state = fields.SmallIntField(
        default=0, description="文章状态 0草稿 1已发布 2仅自己可见"
    )
    is_delete = fields.SmallIntField(default=0, description="是否删除 0不删除 1删除")
    reads = fields.IntField(default=0, description="阅读数")
    likes = fields.IntField(default=0, description="点赞数")
    messages = fields.IntField(default=0, description="评论数")

    class Meta:
        table = "tbl_articles"
