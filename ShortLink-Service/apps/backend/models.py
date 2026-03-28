from tortoise import fields, models
from datetime import datetime


class URLMapping(models.Model):
    """短链接映射表"""

    id = fields.BigIntField(pk=True)
    short_code = fields.CharField(
        max_length=16, unique=True, index=True, desciription="短码"
    )
    original_url = fields.CharField(max_length=2048, description="原始URL")
    access_count = fields.IntField(default=0, description="访问次数")
    created_at = fields.DatetimeField(auto_now_add=True, descriptoin="创建时间")
    expire_at = fields.DatetimeField(null=True, descriptoin="过期时间")

    class Meta:
        table = "url_mapping"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.short_code} -> {self.original_url}"
