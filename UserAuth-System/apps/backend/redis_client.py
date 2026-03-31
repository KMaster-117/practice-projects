import redis
from config import settings


class RedisClient:
    _instance = None

    def __new__(cls):
        """初始化Redis"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD or None,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
        return cls._instance

    def get(self, key: str):
        """获取值"""
        return self.client.get(key)

    def setex(self, key: str, ttl: int, value: str):
        """设置值, 并指定过期时间"""
        return self.client.setex(key, ttl, value)

    def incr(self, key: str):
        """自增1"""
        return self.client.incr(key)

    def delete(self, key: str):
        """删除值"""
        return self.client.delete(key)

    def ping(self):
        """检查连接"""
        return self.client.ping()


redis_client = RedisClient()
