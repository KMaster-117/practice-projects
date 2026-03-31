from tortoise import fields, models


class UserRole(models.Model):
    """用户角色关联表"""

    id = fields.BigIntField(pk=True)
    user_id = fields.BigIntField(description="用户id")
    role_id = fields.BigIntField(description="角色id")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "user_role"
        unique_together = ("user_id", "role_id")
