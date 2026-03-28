import secrets
import string
from config import settings

ALPHABET = string.ascii_letters + string.digits  # 62个字符


def generate_short_code(length: int = None) -> str:
    """生成随机短码"""
    if length is None:
        length = settings.SHORT_CODE_LENGTH
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def encode_base62(num: int) -> str:
    """将数字转为base62编码, ID自增"""
    if num == 0:
        return ALPHABET[0]

    result = []
    base = len(ALPHABET)
    while num > 0:
        result.append(ALPHABET[num % base])
        num //= base

    return "".join(reversed(result))
