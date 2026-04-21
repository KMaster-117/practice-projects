import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, FileResponse

from tortoise.contrib.fastapi import register_tortoise

from schemas import ChatRequest
from openai_client import ai_client
from config import settings


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
    # redoc_url=True,  # 禁用 ReDoc
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,  # 开发环境自动生成表结构
    add_exception_handlers=True,  # 添加异常处理
)


# ==================================================


def chat_stream(prompt: str):
    """流式返回内容"""
    completion = ai_client.chat.completions.create(
        model=settings.CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    content_parts = []

    for chunk in completion:
        if chunk.choices:
            content = chunk.choices[0].delta.content or ""
            yield chunk.choices[0].delta.content
            content_parts.append(content)
        elif chunk.usage:
            logger.debug("\n--- 请求用量 ---")
            logger.debug(f"输入 Tokens: {chunk.usage.prompt_tokens}")
            logger.debug(f"输出 Tokens: {chunk.usage.completion_tokens}")
            logger.debug(f"总计 Tokens: {chunk.usage.total_tokens}")

    full_response = "".join(content_parts)
    logger.debug(f"\n--- 完整回复 ---\n{full_response}")


# ==================================================
app.mount("/static", StaticFiles(directory="./static"), name="static")


@app.get("/")
async def root():
    return FileResponse("/static/index.html")


# ==================================================


@app.post(path="/chat", summary="聊天机器人(流式返回)")
async def chat_request(item: ChatRequest):
    return StreamingResponse(
        chat_stream(item.prompt),
        media_type="text/plain; charset=utf-8",
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
