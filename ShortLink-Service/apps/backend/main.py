import uvicorn
import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from tortoise.contrib.fastapi import register_tortoise
from datetime import datetime, timedelta
from tortoise.exceptions import DoesNotExist

from config import settings
from models import URLMapping
from redis_client import redis_client
from schemas import *
from utils import generate_short_code

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
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url=None,  # 禁用 Swagger UI
    redoc_url=None,  # 禁用 ReDoc
)

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,  # 开发环境自动生成表结构
    add_exception_handlers=True,  # 添加异常处理
)


# ==================================================
@app.post(
    "/shorten", response_model=ShortLinkResponse, status_code=status.HTTP_201_CREATED
)
async def create_short_link(request: ShortLinkRequest):
    """创建短链接"""

    # 若提供短码，判断是否存在
    short_code = request.custom_code
    if short_code:
        exists = await URLMapping.filter(short_code=short_code).exists()
        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="已存在短码"
            )
    else:
        # 自动生成短码
        while True:
            short_code = generate_short_code()
            exists = await URLMapping.filter(short_code=short_code).exists()
            if not exists:
                break

    # 计算过期时间
    expire_at = None
    if request.expire_days:
        expire_at = datetime.now() + timedelta(days=request.expire_days)

    # 创建记录
    url_mapping = await URLMapping.create(
        short_code=short_code, original_url=request.url, expire_at=expire_at
    )

    # 写入缓存
    redis_client.setex(short_code, settings.CACHE_TTL, str(request.url))

    logger.info(f"创建短链接:{short_code} -> {str(request.url)}")

    return ShortLinkResponse(
        short_code=short_code,
        short_url=f"http://localhost:8000/{short_code}",
        original_url=str(request.url),
        expire_at=expire_at,
        created_at=url_mapping.created_at,
    )


@app.get("/{short_code}")
async def redirect_to_original(short_code: str):
    """短链接跳转"""
    # 查询缓存
    cache_url = redis_client.get(short_code)
    if cache_url:
        logger.info(f"缓存命中:{short_code} -> {cache_url}")
        # 增加计数
        redis_client.incr(f"count:{short_code}")
        return RedirectResponse(url=cache_url)

    # 缓存不存在，查询数据库
    try:
        url_mapping = await URLMapping.get(short_code=short_code)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到短码")

    # 查出来，判断是否过期
    if url_mapping.expire_at and url_mapping.expire_at < datetime.now():
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="短码已过期")

    # 更新数据库访问次数
    url_mapping.access_count += 1
    await url_mapping.save(update_fields=["access_count"])

    # 写入缓存
    redis_client.setex(short_code, settings.CACHE_TTL, url_mapping.original_url)

    logger.info(
        f"缓存未命中:{short_code} -> {url_mapping.original_url}, 访问次数:{url_mapping.access_count}"
    )

    return RedirectResponse(url=url_mapping.original_url)


@app.get("/stats/{short_code}", response_model=StatsResponse)
async def get_stats(short_code: str):
    # 获取短链接统计信息

    try:
        url_mapping = await URLMapping.get(short_code=short_code)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到短码")

    # 获取缓存中的计数
    redis_count = redis_client.get(f"count:{short_code}")
    access_count = url_mapping.access_count

    if redis_count:
        access_count += int(redis_count)

    return StatsResponse(
        short_code=short_code,
        original_url=url_mapping.original_url,
        access_count=access_count,
        created_at=url_mapping.created_at,
        expire_at=url_mapping.expire_at,
    )


@app.delete("/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_short_link(short_code: str):
    """删除短链接"""

    try:
        url_mapping = await URLMapping.get(short_code=short_code)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到短码")

    # 删除短链接数据
    await url_mapping.delete()
    # 删除缓存数据
    redis_client.delete(short_code)
    redis_client.delete(f"count:{short_code}")

    logger.info(f"删除短链接: {short_code}")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查接口"""

    # 检查数据库
    db_ok = False
    try:
        await URLMapping.all().limit(1)
        db_ok = True
    except Exception as e:
        logger.error(f"数据库健康检查失败:{e}")
    # 检查Redis
    redis_ok = False
    try:
        redis_client.ping()
        redis_ok = True
    except Exception as e:
        logger.error(f"Redis健康检查失败:{e}")

    status_code = (
        status.HTTP_200_OK
        if (db_ok and redis_ok)
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )
    # 判断整体健康状态
    is_healthy = db_ok and redis_ok

    return JSONResponse(
        status_code=(
            status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
        ),
        content={
            "status": "healthy" if is_healthy else "unhealthy",
            "database": db_ok,
            "redis": redis_ok,
        },
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
