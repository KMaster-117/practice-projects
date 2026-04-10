from fastapi import APIRouter, Request, Depends

from models import Articles, Likes, User
from schemas import PageSelect, LikeGet, LikeCreate, LikeDelete
from utils import APIException, APIResponse, PageResponse, get_current_user


router = APIRouter(prefix="/like", tags=["点赞管理"])


@router.get(path="/select")
async def select_all(
    req: Request,
    item: PageSelect = Depends(),
    current_user: User = Depends(get_current_user),
):
    """获取用户点赞的所有文章"""
    offset = (item.page - 1) * item.page_size
    like_list = (
        await Likes.filter(user_id=current_user.id)
        .offset(offset)
        .limit(item.page_size)
        .all()
    )
    total = await Likes.filter(user_id=current_user.id).count()

    result = [like.to_dict() for like in like_list]

    return PageResponse(
        items=result,
        page=item.page,
        page_size=item.page_size,
        total=total,
    )


@router.get(path="/get")
async def like_get(
    req: Request,
    item: LikeGet = Depends(),
    current_user: User = Depends(get_current_user),
):
    """获取指定文章点赞状态"""
    # 获取文章数据
    is_flag = await Articles.filter(id=item.article_id).exists()
    if not is_flag:
        raise APIException(msg="文章不存在", code=404)
    # 获取点赞状态
    is_liked = await Likes.filter(
        user_id=current_user.id, article_id=item.article_id
    ).exists()

    result = {"is_liked": is_liked}

    return APIResponse(items=result)


@router.post(path="/create")
async def like_create(
    req: Request,
    item: LikeCreate,
    current_user: User = Depends(get_current_user),
):
    """新建点赞"""
    # 获取文章数据
    is_flag = await Articles.filter(id=item.article_id).exists()
    if not is_flag:
        raise APIException(msg="文章不存在", code=404)
    # 新建点赞
    result = await Likes.create(user_id=current_user.id, artiles_id=item.article_id)

    return APIResponse(items=result.to_dict())


@router.delete(path="/delete")
async def like_delete(
    req: Request,
    item: LikeDelete,
    current_user: User = Depends(get_current_user),
):
    """删除点赞"""
    # 点赞过，则直接删除
    is_flag = await Likes.filter(id=item.id, user_id=current_user.id).exists()
    if is_flag:
        await Likes.filter(id=item.id).delete()

    return APIResponse(msg="点赞删除成功")
