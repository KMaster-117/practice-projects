# 短链接服务 (ShortLink Service)

基于 FastAPI + Tortoise-ORM + Redis + MySQL 的短链接服务，支持自定义短码、访问统计、缓存加速等功能。

## ✨ 功能特性

- 🔗 创建短链接（自动生成 / 自定义短码）
- 🔄 短链接跳转（302 重定向）
- 📊 访问统计（数据库 + Redis 计数）
- 🗑️ 删除短链接
- 💾 Redis 缓存加速
- 🏥 健康检查接口

## 🛠️ 技术栈

- **FastAPI** - Web 框架
- **Tortoise-ORM** - 异步 ORM
- **MySQL** - 数据库
- **Redis** - 缓存与计数
- **Pydantic** - 数据验证
- **Uvicorn** - ASGI 服务器

## 🚀 快速开始

### 环境要求

- Python 3.13+
- MySQL 5.7+
- Redis 3.0+
