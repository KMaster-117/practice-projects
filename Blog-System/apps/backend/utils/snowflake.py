# utils/snowflake.py
import time
from threading import Lock
from datetime import datetime
from config import settings


class LeafSnowflake:
    """
    美团 Leaf 风格 雪花ID生成器
    特点：
    - 不使用 MAC 地址
    - 纯本地生成, 不联网
    - 基于系统时间
    - 防闰秒、防重复
    - 单进程绝对安全
    """

    # 初始设置的时间
    year, month, day = 2020, 1, 1
    try:
        year, month, day = map(int, settings.PROJECT_CREATION_TIME.split("."))
    except Exception as e:
        pass

    # 开始时间戳：2020-01-01 00:00:00 UTC(可自定义)
    EPOCH = int(datetime(year, month, day).timestamp() * 1000)

    # 位数分配(和标准雪花、Leaf 完全一致)
    SEQUENCE_BITS = 12
    WORKER_BITS = 10  # 机器ID 10位(0~1023)
    TIMESTAMP_SHIFT = SEQUENCE_BITS + WORKER_BITS

    # 最大值
    MAX_WORKER_ID = (1 << WORKER_BITS) - 1
    MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1

    def __init__(self, worker_id: int = 1):
        """
        :param worker_id: 手动指定机器ID(0~1023), 不依赖MAC/硬件
        """
        if not (0 <= worker_id <= self.MAX_WORKER_ID):
            raise ValueError(f"机器ID必须在 0 ~ {self.MAX_WORKER_ID} 之间")

        self.worker_id = worker_id
        self.last_timestamp = -1
        self.sequence = 0
        self.lock = Lock()  # 线程安全

    def _get_timestamp(self) -> int:
        """获取系统当前毫秒时间(绝对依赖系统时间)"""
        return int(time.time() * 1000)

    def next_id(self) -> int:
        """生成下一个ID(线程安全、防闰秒、防回拨)"""
        with self.lock:
            timestamp = self._get_timestamp()

            # ==================== 核心：防时间回拨 / 防闰秒 ====================
            # 时间变小 = 闰秒或系统异常, 强制等待直到时间追上
            while timestamp < self.last_timestamp:
                timestamp = self._get_timestamp()

            # 同一毫秒内, 序列号自增
            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.MAX_SEQUENCE
                # 序列号用尽, 等待下一毫秒
                if self.sequence == 0:
                    while timestamp == self.last_timestamp:
                        timestamp = self._get_timestamp()
            else:
                # 新毫秒, 序列号重置
                self.sequence = 0

            self.last_timestamp = timestamp

            # ==================== 拼接ID(Leaf 标准格式) ====================
            return (
                ((timestamp - self.EPOCH) << self.TIMESTAMP_SHIFT)
                | (self.worker_id << self.SEQUENCE_BITS)
                | self.sequence
            )
