from tortoise import fields, models


class User(models.Model):
    """用户表"""

    id = fields.BigIntField(pk=True)
    username = fields.CharField(max_length=64, unique=True, description="账户名称")
    password = fields.CharField(max_length=255, description="密码")
    email = fields.CharField(max_length=100, null=True, description="邮箱")
    nickname = fields.CharField(max_length=64, description="用户名称")
    is_active = fields.SmallIntField(default=1, description="用户状态 0禁用 1启用")
    is_superuser = fields.SmallIntField(default=0, description="超级用户 0否 1是")
    is_black = fields.SmallIntField(default=0, description="黑名单用户 0否 1是")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="修改时间")
    last_login = fields.DatetimeField(null=True, description="最近登录时间")

    class Meta:
        table = "users"
        ordering = ["-created_at"]
