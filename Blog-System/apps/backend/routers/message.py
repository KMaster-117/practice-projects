from fastapi import APIRouter, Request, Depends

from models import Articles, Messages, User
from schemas import MessageGet, MessageCreate, MessageDelete
from utils import PageResponse, APIException, APIResponse, get_current_user

router = APIRouter(prefix="/message", tags=["文章评论管理"])


# @router.get(path="/select")
# """ 获取所有评论 """
# async def select_all(req: Request, current_user: User = Depends(get_current_user)):
#     #
#     message_list = await Messages.all(user_id=current_user.id)


@router.get(path="/get")
async def message_get(
    req: Request,
    item: MessageGet = Depends(),
    current_user: User = Depends(get_current_user),
):
    """获取文章评论"""
    # 获取文章数据
    is_flag = await Articles.filter(id=item.article_id).exists()
    if not is_flag:
        raise APIException(msg="文章不存在", code=404)
    # 获取文章下评论
    offset = (item.page - 1) * item.page_size
    message_list = (
        await Messages.filter(article_id=item.article_id, is_delete=0)
        .offset(offset)
        .limit(item.page_size)
        .all()
    )
    total = await Messages.filter(article_id=item.article_id, is_delete=0).count()

    result = [message.to_dict() for message in message_list]

    return PageResponse(
        items=result,
        page=item.page,
        page_size=item.page_size,
        total=total,
    )


@router.post(path="/create")
async def message_create(
    req: Request, item: MessageCreate, current_user: User = Depends(get_current_user)
):
    """新建评论"""
    # 获取文章数据
    is_flag = await Articles.filter(id=item.article_id).exists()
    if not is_flag:
        raise APIException(msg="文章不存在", code=404)
    # 新建评论
    result = await Messages.create(
        user_id=current_user.id, article_id=item.article_id, message=item.message
    )
    return APIResponse(items=result.to_dict())


@router.delete(path="/delete")
async def message_delete(
    req: Request, item: MessageDelete, current_user: User = Depends(get_current_user)
):
    """删除评论"""
    # 获取评论
    message_data = await Messages.get_or_none(id=item.id, user_id=current_user.id)
    if message_data:
        # 删除评论（逻辑删除）
        message_data.is_delete = 1
        await message_data.save()

    return APIResponse(msg="评论删除成功")
