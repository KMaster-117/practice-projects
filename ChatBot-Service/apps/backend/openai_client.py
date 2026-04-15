import os
from openai import OpenAI

from config import settings


ai_client = OpenAI(
    # 建议通过环境变量配置API Key，避免硬编码。
    api_key=settings.DASHSCOPE_API_KEY,
    # API Key与地域强绑定，请确保base_url与API Key的地域一致。
    base_url=settings.BASE_URL,
)
