from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "短链接服务"
    DEBUG: bool = True

    # MySQL配置
    DB_URL: str = "mysql://root:root@localhost:3306/shortlink"

    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    # 短链接配置
    SHORT_CODE_LENGTH: int = 6
    CACHE_TTL: int = 3600

    class Config:
        env_file: str = ".env"


settings = Settings()
