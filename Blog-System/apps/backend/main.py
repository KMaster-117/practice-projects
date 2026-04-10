import uvicorn
import logging
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from config import settings
from routers import *

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(f"{__name__}->")


TORTOISE_ORM = {
    "connections": {"default": settings.DB_URL},
    "apps": {
        "models": {
            "models": [
                "models"
                # "aerich.models"
            ],
            "default_connection": "default",
        },
    },
    # 连接池配置（推荐）
    "use_tz": False,  # 是否使用时区
    "timezone": "UTC",  # 默认时区
    "db_pool": {
        "max_size": 10,  # 最大连接数
        "min_size": 1,
        # 最小连接数
        "idle_timeout": 30,  # 空闲连接超时（秒）
    },
}


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url=None,  # 禁用 Swagger UI
    # redoc_url=None,  # 禁用 ReDoc
)

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,  # 开发环境自动生成表结构
    add_exception_handlers=True,  # 添加异常处理
)


# ==================================================

app.include_router(article_router)
app.include_router(like_router)
app.include_router(message_router)
app.include_router(user_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
