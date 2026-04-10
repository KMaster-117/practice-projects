from tortoise import fields
from .comment import BaseModel


class User(BaseModel):
    """用户表"""

    username = fields.CharField(unique=True, max_length=255, description="用户名称")
    phone = fields.CharField(unique=True, max_length=11, description="手机号")
    email = fields.CharField(unique=True, max_length=64, description="邮箱")
    state = fields.SmallIntField(default=0, description="账号状态 0正常 1禁用")
    is_admin = fields.SmallIntField(default=0, description="是否为管理员 0否 1是")
    is_delete = fields.SmallIntField(default=0, description="是否删除 0不删除 1删除")
    hash_password = fields.CharField(max_length=255, description="加密的密码")
    last_login = fields.DatetimeField(null=True, description="最近登录时间")

    class Meta:
        table = "tbl_user"
