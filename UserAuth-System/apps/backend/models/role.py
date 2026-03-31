from tortoise import fields, models


class Role(models.Model):
    """角色表"""

    id = fields.BigIntField(pk=True)
    name = fields.CharField(max_length=64, unique=True, description="角色名称")
    level = fields.SmallIntField(
        default=0, description="角色等级 0:read 1:write 2:admin"
    )
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "roles"
        ordering = ["-created_at"]
