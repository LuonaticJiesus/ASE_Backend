import json
from datetime import datetime

from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from four_s.models import Block, Permission, Post, UserInfo, PostLike, Comment, PostChosen, PostFavor


def wrap_post(p, user_id):
    p_dict = p.to_dict()
    p_dict['user_name'] = UserInfo.objects.get(user_id=p.user_id).name
    p_dict['block_name'] = Block.objects.get(block_id=p.block_id).name
    p_dict['like_cnt'] = PostLike.objects.filter(post_id=p.post_id).count()
    p_dict['comment_cnt'] = Comment.objects.filter(post_id=p.post_id).count()
    p_dict['like_state'] = 1 if PostLike.objects.filter(user_id=user_id).filter(post_id=p.post_id).exists() else 0
    p_dict['permission'] = Permission.objects.get(block_id=p.block_id, user_id=p.user_id).permission
    comment_query_set = Comment.objects.filter(post_id=p.post_id).order_by('-time')
    if comment_query_set is None:
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
                return JsonResponse({'status': -1, 'info': '约束错误'})
            if not Permission.objects.filter(user_id=user_id).filter(block_id=block_id).filter(
                    permission__gte=1).exists():
                return JsonResponse({'status': -1, 'info': '权限不足'})
            post = Post(title=title, user_id=user_id, txt=txt, block_id=block_id, time=datetime.now())
            post.save()
            return JsonResponse({'status': 0, 'info': '已发布'})
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
            if user_permission < 2 or user_id != post.user_id:
                return JsonResponse({'status': -1, 'info': '权限不足'})
            # delete
            Comment.objects.filter(post_id=post_id).delete()
            PostChosen.objects.filter(post_id=post_id).delete()
            PostFavor.objects.filter(post_id=post_id).delete()
            PostLike.objects.filter(post_id=post_id).delete()
            Post.objects.filter(post_id=post_id).delete()
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
        like = data.get('like')
        # check params
        if post_id is None or like is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        post_id = int(post_id)
        like = int(like)
        if like not in [0, 1]:
            return JsonResponse({'status': -1, 'info': '参数错误'})
        # db
        with transaction.atomic():
            post_query_set = Post.objects.filter(post_id=post_id)
            if not post_query_set.exists():
                return JsonResponse({'status': -1, 'info': '帖子不存在'})
            block_id = post_query_set[0].block_id
            if not Permission.objects.filter(user_id=user_id).filter(block_id=block_id).filter(
                    permission__gte=1).exists():
                return JsonResponse({'status': -1, 'info': '权限错误'})
            if like == 0:
                PostLike.objects.filter(post_id=post_id).filter(user_id=user_id).delete()
            elif not PostLike.objects.filter(post_id=post_id).filter(user_id=user_id).exists():
                new_like = PostLike(post_id=post_id, user_id=user_id)
                new_like.save()
            return JsonResponse({'status': 0, 'info': '操作成功'})
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
        chosen = data.get('chosen')
        # check params
        if post_id is None or chosen is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        post_id = int(post_id)
        chosen = int(chosen)
        if chosen not in [0, 1]:
            return JsonResponse({'status': -1, 'info': '参数错误'})
        # db
        with transaction.atomic():
            post_query_set = Post.objects.filter(post_id=post_id)
            if not post_query_set.exists():
                return JsonResponse({'status': -1, 'info': '帖子不存在'})
            block_id = post_query_set[0].block_id
            if not Permission.objects.filter(user_id=user_id).filter(block_id=block_id).filter(
                    permission__gte=2).exists():
                return JsonResponse({'status': -1, 'info': '权限错误'})
            if chosen == 0:
                PostChosen.objects.filter(block_id=block_id).delete()
            elif not PostChosen.objects.filter(block_id=block_id).filter(post_id=post_id).exists():
                post_chosen = PostChosen(post_id=post_id, block_id=block_id)
                post_chosen.save()
            return JsonResponse({'status': 0, 'info': '操作成功'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误'})
