# utils/response.py
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from typing import List, Dict, Any


class APIException(HTTPException):
    """统一接口异常封装"""

    def __init__(
        self,
        msg: str = "操作失败",
        code: int = status.HTTP_400_BAD_REQUEST,
        success: bool = False,
    ):
        self.success = success
        self.code = code
        self.msg = msg
        super().__init__(status_code=code, detail=msg)


class APIResponse(JSONResponse):
    """统一接口响应封装"""

    def __init__(
        self,
        items: List = [],
        msg: str = "操作成功",
        code: int = status.HTTP_200_OK,
        success: bool = True,
    ):
        self.success = success
        self.code = code
        self.msg = msg

        # 构建响应内容
        content = {
            "success": success,
            "code": code,
            "msg": msg,
            "data": items,
        }

        super().__init__(status_code=code, content=content)


class PageResponse(JSONResponse):
    """分页统一接口响应封装"""

    def __init__(
        self,
        items: List = [],
        page: int = 1,
        page_size: int = 10,
        total: int = 0,
        msg: str = "操作成功",
        code: int = status.HTTP_200_OK,
        success: bool = True,
    ):
        # 计算总页数
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0

        # 构建响应内容
        content = {
            "success": success,
            "code": code,
            "msg": msg,
            "data": {
                "items": items,
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
        }

        super().__init__(status_code=code, content=content)
