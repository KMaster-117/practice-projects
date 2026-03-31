
# 用户认证系统（User Authentication System）

基于 FastAPI + Tortoise-ORM + Redis + MySQL 的用户认证系统，支持用户注册、登录、权限管理等功能。

## ✨ 功能特性

* 👤  **用户注册** （用户名、密码、邮箱）
* 🔐  **用户登录** （Token 认证）
* 🚪  **用户注销** （Token 销毁）
* 👑  **角色管理** （只读/可写/管理员三级权限）
* 🔧  **用户管理** （增删改查）
* 🔒  **权限控制** （基于角色的访问控制）
* 💾  **Redis 会话存储** （Token 管理）
* 🔄  **会话自动续期** （滑动窗口机制）
* 🏥 **健康检查接口**

## 🛠️ 技术栈

* **FastAPI** - Web 框架
* **Tortoise-ORM** - 异步 ORM
* **MySQL** - 数据库
* **Redis** - 会话存储
* **bcrypt** - 密码加密
* **Pydantic** - 数据验证
* **Uvicorn** - ASGI 服务器

## 🚀 快速开始

### 环境要求

* Python 3.13+
* MySQL 5.7+
* Redis 3.0+
