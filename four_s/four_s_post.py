import json
from datetime import datetime

from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from four_s.models import Block, Permission, Post, UserInfo, PostLike, Comment, PostChosen, PostFavor


def wrap_post(p, user_id):
    p_dict = p.to_dict()
    post_author = UserInfo.objects.get(user_id=p.user_id)
    p_dict['user_name'] = post_author.name
    if post_author.avatar is not None:
        p_dict['user_avatar'] = post_author.avatar
    p_dict['block_name'] = Block.objects.get(block_id=p.block_id).name
    p_dict['like_cnt'] = PostLike.objects.filter(post_id=p.post_id).count()
    p_dict['comment_cnt'] = Comment.objects.filter(post_id=p.post_id).count()
    p_dict['favor_cnt'] = PostFavor.objects.filter(post_id=p.post_id).count()
    p_dict['favor_state'] = 1 if PostFavor.objects.filter(user_id=user_id).filter(post_id=p.post_id).exists() else 0
    p_dict['like_state'] = 1 if PostLike.objects.filter(user_id=user_id).filter(post_id=p.post_id).exists() else 0
    comment_query_set = Comment.objects.filter(post_id=p.post_id).order_by('-time')
    if not comment_query_set.exists():
        p_dict['latest_update_user'] = p_dict['user_name']
        p_dict['latest_time'] = p.time
    else:
        comment_user_id = comment_query_set[0].user_id
        p_dict['latest_update_user'] = UserInfo.objects.get(user_id=comment_user_id).name
        p_dict['latest_time'] = comment_query_set[0].time
    return p_dict


def wrap_posts(post_query_set, user_id):
    posts = []
    for p in post_query_set:
        posts.append(wrap_post(p, user_id))
    return posts


def check_title(title: str):
    return 0 < len(title) < 200


def check_txt(txt: str):
    return len(txt) > 0


@csrf_exempt
def post_query_title(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        title = request.GET.get('title')
        # check params
        if title is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        title = str(title)
        # db
        with transaction.atomic():
            post_query_set = Post.objects.filter(title__contains=title)
            posts = wrap_posts(post_query_set, user_id)
            return JsonResponse({'status': 0, 'info': '查询成功', 'data': posts})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})


@csrf_exempt
def post_query_by_id(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        post_id = request.GET.get('post_id')
        # check params
        if post_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        post_id = str(post_id)
        # db
        with transaction.atomic():
            post_query_set = Post.objects.filter(post_id=post_id)
            if not post_query_set.exists():
                return JsonResponse({'status': -1, 'info': '帖子不存在'})
            posts = wrap_posts(post_query_set, user_id)
            return JsonResponse({'status': 0, 'info': '查询成功', 'data': posts})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})


@csrf_exempt
def post_query_block(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        block_id = request.GET.get('block_id')
        # check params
        if block_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        block_id = int(block_id)
        # db
        with transaction.atomic():
            if not Block.objects.filter(block_id=block_id).exists():
                return JsonResponse({'status': -1, 'info': '模块不存在'})
            post_query_set = Post.objects.filter(block_id=block_id).order_by('-time')
            posts = wrap_posts(post_query_set, user_id)
            return JsonResponse({'status': 0, 'info': '查询成功', 'data': posts})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})


@csrf_exempt
def post_query_user_block(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        userid = int(request.META.get('HTTP_USERID'))
        user_id = request.GET.get('user_id')
        block_id = request.GET.get('block_id')
        # check params
        if block_id is None or user_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        user_id = int(user_id)
        block_id = int(block_id)
        # db
        with transaction.atomic():
            if not Block.objects.filter(block_id=block_id).exists():
                return JsonResponse({'status': -1, 'info': '模块不存在'})
            post_query_set = Post.objects.filter(block_id=block_id).filter(user_id=user_id).order_by('-time')
            posts = wrap_posts(post_query_set, userid)
            return JsonResponse({'status': 0, 'info': '查询成功', 'data': posts})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})


@csrf_exempt
def post_query_user(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        userid = int(request.META.get('HTTP_USERID'))
        user_id = request.GET.get('user_id')
        # check_params
        if user_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        user_id = int(user_id)
        # db
        with transaction.atomic():
            if not UserInfo.objects.filter(user_id=user_id).exists():
                return JsonResponse({'status': -1, 'info': '用户不存在'})
            post_query_set = Post.objects.filter(user_id=user_id).order_by('-time')
            posts = wrap_posts(post_query_set, userid)
            return JsonResponse({'status': 0, 'info': '查询成功', 'data': posts})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})


@csrf_exempt
def post_query_chosen(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        block_id = request.GET.get('block_id')
        # check params
        if block_id is None:
            return JsonResponse({'status': -1, 'info': '模块不存在'})
        block_id = int(block_id)
        # db
        with transaction.atomic():
            post_chosen_query_set = PostChosen.objects.filter(block_id=block_id)
            posts = []
            for chosen in post_chosen_query_set:
                post = Post.objects.get(post_id=chosen.post_id)
                posts.append(wrap_post(post, user_id))
            return JsonResponse({'status': 0, 'info': '查询成功', 'data': posts})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误'})


@csrf_exempt
def post_detail(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        post_id = request.GET.get('block_id')
        # check params
        if post_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        post_id = int(post_id)
        # db
        with transaction.atomic():
            post_query_set = Post.objects.filter(post_id=post_id)
            if not post_query_set.exists():
                return JsonResponse({'status': -1, 'info': '帖子不存在'})
            post = post_query_set[0]
            p_dict = wrap_post(post, user_id)
            return JsonResponse({'status': 0, 'info': '查询成功', 'data': p_dict})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误, 查询失败'})


@csrf_exempt
def post_publish(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        data = json.loads(request.body)
        title = data.get('title')
        txt = data.get('txt')
        block_id = data.get('block_id')
        # check params
        if title is None or txt is None or block_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        block_id = int(block_id)
        title = str(title).strip('\t').strip(' ')
        if not check_title(title):
            return JsonResponse({'status': -1, 'info': '标题格式错误'})
        txt = str(txt).strip('\t').strip(' ')
        if not check_txt(txt):
            return JsonResponse({'status': -1, 'info': '内容格式错误'})
        # db
        with transaction.atomic():
            if not Block.objects.filter(block_id=block_id).exists():
                return JsonResponse({'status': -1, 'info': '模块id不存在'})
            if not Permission.objects.filter(user_id=user_id).filter(block_id=block_id).filter(
                    permission__gte=1).exists():
                return JsonResponse({'status': -1, 'info': '权限不足'})
            post = Post(title=title, user_id=user_id, txt=txt, block_id=block_id, time=datetime.now())
            post.save()
            return JsonResponse({'status': 0, 'info': '已发布', 'data': {'post_id': post.post_id}})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，发布失败'})


@csrf_exempt
def post_delete(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        data = json.loads(request.body)
        post_id = data.get('post_id')
        # check_param
        if post_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        post_id = int(post_id)
        # db
        with transaction.atomic():
            post_query_set = Post.objects.filter(post_id=post_id)
            if not post_query_set.exists():
                return JsonResponse({'status': -1, 'info': '帖子不存在'})
            post = post_query_set[0]
            block_id = post.block_id
            user_permission_query_set = Permission.objects.filter(user_id=user_id).filter(block_id=block_id)
            if not user_permission_query_set.exists():
                return JsonResponse({'status': -1, 'info': '权限不足'})
            user_permission = user_permission_query_set[0].permission
            if user_permission < 2 and user_id != post.user_id:
                return JsonResponse({'status': -1, 'info': '权限不足'})
            # delete
            Comment.objects.filter(post_id=post_id).delete()
            PostChosen.objects.filter(post_id=post_id).delete()
            PostFavor.objects.filter(post_id=post_id).delete()
            PostLike.objects.filter(post_id=post_id).delete()
            Post.objects.filter(post_id=post_id).delete()
            return JsonResponse({'status': 0, 'info': '已删除'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，删除失败'})


@csrf_exempt
def post_like(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        data = json.loads(request.body)
        post_id = data.get('post_id')
        # check params
        if post_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        post_id = int(post_id)
        # db
        with transaction.atomic():
            post_query_set = Post.objects.filter(post_id=post_id)
            if not post_query_set.exists():
                return JsonResponse({'status': -1, 'info': '帖子不存在'})
            block_id = post_query_set[0].block_id
            if not Permission.objects.filter(user_id=user_id).filter(block_id=block_id).exists():
                return JsonResponse({'status': -1, 'info': '未订阅模块'})
            now_like = PostLike.objects.filter(post_id=post_id).filter(user_id=user_id)
            if now_like.exists():
                now_like.delete()
                return JsonResponse({'status': 0, 'info': '已取消点赞'})
            else:
                new_like = PostLike(post_id=post_id, user_id=user_id)
                new_like.save()
                return JsonResponse({'status': 0, 'info': '点赞成功'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误'})


@csrf_exempt
def post_choose(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        data = json.loads(request.body)
        post_id = data.get('post_id')
        # check params
        if post_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        post_id = int(post_id)
        # db
        with transaction.atomic():
            post_query_set = Post.objects.filter(post_id=post_id)
            if not post_query_set.exists():
                return JsonResponse({'status': -1, 'info': '帖子不存在'})
            block_id = post_query_set[0].block_id
            if not Permission.objects.filter(user_id=user_id).filter(block_id=block_id).filter(
                    permission__gte=2).exists():
                return JsonResponse({'status': -1, 'info': '权限错误'})
            now_chosen = PostChosen.objects.filter(block_id=block_id).filter(post_id=post_id)
            if now_chosen.exists():
                now_chosen.delete()
                return JsonResponse({'status': 0, 'info': '已取消加精'})
            else:
                new_chosen = PostChosen(block_id=block_id, post_id=post_id)
                new_chosen.save()
                return JsonResponse({'status': 0, 'info': '帖子已加精'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误'})


@csrf_exempt
def post_favor(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        data = json.loads(request.body)
        post_id = data.get('post_id')
        # check params
        if post_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        post_id = int(post_id)
        # db
        with transaction.atomic():
            post_query_set = Post.objects.filter(post_id=post_id)
            if not post_query_set.exists():
                return JsonResponse({'status': -1, 'info': '帖子不存在'})
            block_id = post_query_set[0].block_id
            if not Permission.objects.filter(user_id=user_id).filter(block_id=block_id).exists():
                return JsonResponse({'status': -1, 'info': '未订阅模块'})
            now_favor = PostFavor.objects.filter(user_id=user_id).filter(post_id=post_id)
            if now_favor.exists():
                now_favor.delete()
                return JsonResponse({'status': 0, 'info': '已取消收藏'})
            else:
                new_favor = PostFavor(user_id=user_id, post_id=post_id)
                new_favor.save()
                return JsonResponse({'status': 0, 'info': '已收藏'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误'})


@csrf_exempt
def post_query_favor(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        block_id = request.GET.get('block_id')
        # check params
        if block_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        block_id = int(block_id)
        # db
        with transaction.atomic():
            if not Block.objects.filter(block_id=block_id).exists():
                return JsonResponse({'status': -1, 'info': '模块不存在'})
            favor_post_ids = set()
            favor_query_set = PostFavor.objects.filter(user_id=user_id)
            for f in favor_query_set:
                favor_post_ids.add(f.post_id)
            post_query_set = Post.objects.filter(block_id=block_id).order_by('-time')
            posts = []
            for post in post_query_set:
                if post.post_id in favor_post_ids:
                    p_dict = wrap_post(post, user_id)
                    posts.append(p_dict)
            return JsonResponse({'status': 0, 'info': '查询成功', 'data': posts})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误'})
