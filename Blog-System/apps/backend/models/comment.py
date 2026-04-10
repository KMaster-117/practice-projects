# models/comment.py
import json
from tortoise import Model, fields
from typing import Optional, List, Dict, Any
from datetime import datetime, date

from utils import LeafSnowflake
from config import settings

sf = LeafSnowflake(worker_id=settings.WORK_ID)


class BaseModel(Model):
    """通用基类"""

    id = fields.BigIntField(
        pk=True, auto_increment=False, generated=False, description="主键ID(雪花算法)"
    )
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="修改时间")

    class Meta:
        # 基类标识符
        abstract = True
        ordering = ["created_at"]

    async def save(self, *args, **kwargs):
        """保存时自动生成雪花ID"""
        if not self.id:
            self.id = sf.next_id()
        await super().save(*args, **kwargs)

    def to_dict(
        self, exclude: Optional[List[str]] = None, only: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        转换为字典
        """
        if exclude is None:
            exclude = []
        if only is None:
            only = []

        data = {}

        for field_name in self._meta.fields:
            # 字段名可能带点（关联字段）
            if "." in field_name:
                continue

            # 过滤
            if only and field_name not in only:
                continue
            if field_name in exclude:
                continue

            value = getattr(self, field_name)

            # 类型转换
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, date):
                value = value.isoformat()

            data[field_name] = value

        return data

    def to_json(self, **kwargs) -> str:
        """转换为 JSON"""
        return json.dumps(self.to_dict(**kwargs), ensure_ascii=False)
