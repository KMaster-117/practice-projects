from fastapi import APIRouter, Request, Depends

from models import Articles, User
from schemas import PageSelect, ArticleCreate, ArticleUpdate, ArticleDelete
from utils import APIException, APIResponse, PageResponse, get_current_user


router = APIRouter(prefix="/article", tags=["文章管理"])


@router.get(path="/select")
async def select_all(
    req: Request,
    item: PageSelect = Depends(),
    current_user: User = Depends(get_current_user),
):
    """获取所有文章"""

    offset = (item.page - 1) * item.page_size
    article_list = (
        await Articles.filter(state=1).offset(offset).limit(item.page_size).all()
    )
    total = await Articles.filter(state=1).count()

    result = [article.to_dict() for article in article_list]

    return PageResponse(
        items=result,
        page=item.page,
        page_size=item.page_size,
        total=total,
    )


@router.get(path="/get")
async def article_get(
    req: Request,
    item: PageSelect = Depends(),
    current_user: User = Depends(get_current_user),
):
    # 返回用户的文章
    offset = (item.page - 1) * item.page_size
    article_list = (
        await Articles.filter(user_id=current_user.id)
        .offset(offset)
        .limit(item.page_size)
        .all()
    )
    total = await Articles.filter(user_id=current_user.id).count()

    result = [article.to_dict() for article in article_list]

    return PageResponse(
        items=result,
        page=item.page,
        page_size=item.page_size,
        total=total,
    )


@router.post(path="/create")
async def article_create(
    req: Request,
    item: ArticleCreate,
    current_user: User = Depends(get_current_user),
):
    """新建文章"""
    result = await Articles.create(
        user_id=current_user.id,
        username=current_user.username,
        title=item.title,
        body=item.body,
        state=item.state,
    )
    return APIResponse(items=result.to_dict())


@router.put(path="/update")
async def article_update(
    req: Request,
    item: ArticleUpdate,
    current_user: User = Depends(get_current_user),
):
    """修改文章"""
    # 获取文章数据
    article_data = await Articles.get_or_none(id=item.id, user_id=current_user.id)
    if not article_data:
        raise APIException(msg="文章不存在", code=404)
    if item.title:
        article_data.title = item.title
    if item.body:
        article_data.body = item.body
    if item.state:
        article_data.state = item.state
    # 修改时刷新用户数据
    if current_user.id == article_data.user_id:
        article_data.username = current_user.username
    await article_data.save()

    return APIResponse(items=article_data.to_dict())


@router.delete(path="/delete")
async def article_delete(
    req: Request,
    item: ArticleDelete,
    current_user: User = Depends(get_current_user),
):
    """删除文章"""
    # 获取文章数据
    is_flag = await Articles.filter(id=item.id, user_id=current_user.id).exists()
    if is_flag:
        await Articles.filter(id=item.id).delete()

    return APIResponse(msg="文章删除成功")
