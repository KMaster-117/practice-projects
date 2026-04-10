from fastapi import APIRouter, Request, Depends
from tortoise.expressions import Q

from models import User
from schemas import (
    PageSelect,
    UserLogin,
    UserRegist,
    UserCreate,
    UserUpdate,
    UserUpdatePassword,
    UserUpdateStatus,
    UserRefreshToken,
    UserDelete,
)
from utils import (
    PageResponse,
    APIException,
    APIResponse,
    get_password_hash,
    verify_password,
    get_current_user,
    create_access_token,
    create_refresh_token,
    refresh_access_token,
    redis_add,
    redis_delete,
)


router = APIRouter(prefix="/user", tags=["用户管理"])


@router.get(path="/select")
async def select_all(
    req: Request,
    item: PageSelect = Depends(),
    current_user: User = Depends(get_current_user),
):
    """获取所有用户"""
    # 必须为管理员
    if current_user.is_admin == 0:
        raise APIException(msg="没有操作权限", code=401)
    # 获取所有用户
    offset = (item.page - 1) * item.page_size
    user_list = (
        await User.filter(is_delete=0).offset(offset).limit(item.page_size).all()
    )

    total = await User.filter(is_delete=0).count()

    result = [
        user.to_dict(only=["id", "username", "phone", "state", "is_admin"])
        for user in user_list
    ]

    return PageResponse(
        items=result,
        page=item.page,
        page_size=item.page_size,
        total=total,
    )


@router.post(path="/regist")
async def user_regist(req: Request, item: UserRegist):
    """注册用户"""
    # 一次性检查是否有重复
    is_duplicate = await User.filter(
        Q(username=item.username) | Q(phone=item.phone) | Q(email=item.email)
    ).exists()

    if is_duplicate:
        # 进一步判断具体哪个字段重复
        duplicate_fields = []
        if await User.filter(username=item.username).exists():
            duplicate_fields.append("用户名")
        if await User.filter(phone=item.phone).exists():
            duplicate_fields.append("手机号")
        if await User.filter(email=item.email).exists():
            duplicate_fields.append("邮箱")

        raise APIException(
            msg=f"以下数据已存在: {', '.join(duplicate_fields)}", code=400
        )
    # 加密密码
    hash_password = await get_password_hash(item.password)
    # 注册用户
    result = await User.create(
        username=item.username,
        phone=item.phone,
        email=item.email,
        hash_password=hash_password,
    )
    # 只返回部分用户数据
    user = (await User.filter(id=result.id).first()).to_dict(
        only=["id", "username", "phone", "state", "is_admin"]
    )

    return APIResponse(items=user)


@router.post(path="/create")
async def user_create(
    req: Request,
    item: UserCreate,
    current_user: User = Depends(get_current_user),
):
    """新建用户"""
    # 必须为管理员
    if current_user.is_admin == 0:
        raise APIException(msg="没有操作权限", code=401)
    # 一次性检查是否有重复
    is_duplicate = await User.filter(
        Q(username=item.username) | Q(phone=item.phone) | Q(email=item.email)
    ).exists()

    if is_duplicate:
        # 进一步判断具体哪个字段重复
        duplicate_fields = []
        if await User.filter(username=item.username).exists():
            duplicate_fields.append("用户名")
        if await User.filter(phone=item.phone).exists():
            duplicate_fields.append("手机号")
        if await User.filter(email=item.email).exists():
            duplicate_fields.append("邮箱")

        raise APIException(
            msg=f"以下数据已存在: {', '.join(duplicate_fields)}", code=400
        )
    # 加密密码
    hash_password = await get_password_hash(item.password)
    # 新建用户
    result = await User.create(
        username=item.username,
        phone=item.phone,
        email=item.email,
        hash_password=hash_password,
        is_admin=item.is_admin,
    )
    # 只返回部分用户数据
    user = (await User.filter(id=result.id).first()).to_dict(
        only=["id", "username", "phone", "state", "is_admin"]
    )

    return APIResponse(items=user)


@router.put(path="/update")
async def user_update(
    req: Request,
    item: UserUpdate,
    current_user: User = Depends(get_current_user),
):
    """修改用户"""
    # 非管理员校验
    if current_user.is_admin == 0 and current_user.id != item.id:
        raise APIException(msg="没有操作权限", code=401)

    args = Q()
    if item.username:
        args &= Q(username=item.username)
    if item.phone:
        args &= Q(phone=item.phone)
    if item.email:
        args &= Q(email=item.email)
    if args.children:
        # 一次性检查是否有重复
        is_duplicate = await User.filter(args).exists()
    else:
        is_duplicate = None

    if is_duplicate:
        # 进一步判断具体哪个字段重复
        duplicate_fields = []
        if await User.filter(username=item.username).exists():
            duplicate_fields.append("用户名")
        if await User.filter(phone=item.phone).exists():
            duplicate_fields.append("手机号")
        if await User.filter(email=item.email).exists():
            duplicate_fields.append("邮箱")

        raise APIException(
            msg=f"以下数据已存在: {', '.join(duplicate_fields)}", code=400
        )
    # 查询用户
    user = await User.get_or_none(id=item.id)
    # 修改用户
    if item.username:
        user.username = item.username
    if item.phone:
        user.phone = item.phone
    if item.email:
        user.email = item.email
    if item.is_admin == 1:
        if item.is_admin is not None and user.is_admin != item.is_admin:
            user.is_admin = item.is_admin
    await user.save()

    # 只返回部分用户数据
    user = (await User.filter(id=user.id).first()).to_dict(
        only=["id", "username", "phone", "state", "is_admin"]
    )

    return APIResponse(items=user)


@router.delete(path="/delete")
async def user_delete(
    req: Request,
    item: UserDelete,
    current_user: User = Depends(get_current_user),
):
    """删除用户"""
    # 非管理员校验
    if current_user.is_admin == 0 or item.id == 1:
        raise APIException(msg="没有操作权限", code=401)
    # 获取用户数据
    user = await User.get_or_none(id=item.id, is_delete=0)
    if not user:
        raise APIException(msg="用户不存在", code=404)
    # 删除用户（逻辑删除）
    user.is_delete = 1
    await user.save()
    # 用户注销
    await redis_delete(user_id=user.id)

    return APIResponse(msg="用户删除成功")


@router.post(path="/login")
async def user_login(req: Request, item: UserLogin):
    """用户登陆"""
    # 获取用户
    user = await User.filter(username=item.username).first()
    if not user:
        raise APIException(msg="用户不存在", code=404)
    # 校验密码
    is_flag = await verify_password(item.password, user.hash_password)
    if not is_flag:
        raise APIException(msg="密码输入错误", code=400)
    # 返回令牌
    access_token, expire = await create_access_token(user.id)
    refresh_token = await create_refresh_token(user.id)

    # Redis写入
    await redis_add(
        user_id=user.id,
        expire=expire,
        token=access_token,
    )

    result = {"access_token": access_token, "refresh_token": refresh_token}

    return APIResponse(items=result)


@router.post(path="/logout")
async def user_logout(req: Request, current_user: User = Depends(get_current_user)):
    """用户注销"""
    await redis_delete(user_id=current_user.id)
    return APIResponse(msg="用户注销成功")


@router.post(path="/refresh/token")
async def user_refresh_token(
    req: Request,
    item: UserRefreshToken,
):
    """用户刷新访问令牌"""
    # 新访问令牌
    user_id, access_token, expire = await refresh_access_token(
        refresh_token=item.refresh_token
    )
    # Redis写入
    await redis_add(
        user_id=user_id,
        expire=expire,
        token=access_token,
    )

    result = {"access_token": access_token}

    return APIResponse(items=result)


@router.put(path="/update/password")
async def user_update_password(
    req: Request,
    item: UserUpdatePassword,
    current_user: User = Depends(get_current_user),
):
    """修改用户密码"""
    # 非管理员校验
    if current_user.is_admin == 0:
        if current_user.id != item.id:
            raise APIException(msg="没有操作权限", code=401)
    if item.old_password == item.new_password:
        raise APIException(msg="新密码不能与旧密码相同", code=400)
    # 获取用户数据
    user = await User.get_or_none(id=item.id, is_delete=0)
    if not user:
        raise APIException(msg="用户不存在", code=404)
    # 校验旧密码
    is_flag = await verify_password(item.old_password, user.hash_password)
    if not is_flag:
        raise APIException(msg="密码输入有误", code=401)
    # 生成新加密密码
    hash_password = await get_password_hash(item.new_password)
    # 修改用户密码
    user.hash_password = hash_password
    await user.save()
    # 用户注销
    await redis_delete(user_id=user.id)

    return APIResponse(msg="用户密码修改成功")


@router.put(path="/update/status")
async def user_update_status(
    req: Request,
    item: UserUpdateStatus,
    current_user: User = Depends(get_current_user),
):
    """修改用户状态"""
    # 非管理员校验
    if current_user.is_admin == 0:
        raise APIException(msg="没有操作权限", code=401)
    # 获取用户数据
    user = await User.get_or_none(id=item.id, is_delete=0)
    if not user:
        raise APIException(msg="用户不存在", code=404)

    if user.state == item.state:
        raise APIException(msg="请不要重复修改状态", doe=404)
    # 修改用户状态
    user.state = item.state
    await user.save()
    # 用户注销
    await redis_delete(user_id=user.id)

    return APIResponse(msg="用户状态修改成功")
