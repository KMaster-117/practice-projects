from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 项目
    PROJECT_NAME: str
    DEBUG: bool
    HOST: str
    PORT: int
    ENV: str

    # MySQL
    DB_URL: str

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    REDIS_DB: int

    # JWT
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int

    # Snowflake配置F
    WORK_ID: int

    # CORS
    CORS_ORIGINS: list = ["*"]

    # 项目创建时间
    PROJECT_CREATION_TIME: str

    class Config:
        env_file: str = ".env"


settings = Settings()
