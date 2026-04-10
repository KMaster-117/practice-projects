# schemas/__init__.py
from .article import ArticleCreate, ArticleUpdate, ArticleDelete
from .comment import PageSelect
from .like import LikeGet, LikeCreate, LikeDelete
from .message import MessageGet, MessageCreate, MessageDelete
from .user import (
    UserLogin,
    UserRegist,
    UserCreate,
    UserUpdate,
    UserUpdateStatus,
    UserUpdatePassword,
    UserRefreshToken,
    UserDelete,
)
