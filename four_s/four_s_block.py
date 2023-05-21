import json
import random

from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from four_s.models import Block, Permission, Post, Comment, CommentLike, PostFavor, PostChosen, PostLike, Notice, \
    Contribution


def check_name(name: str):
    return 0 < len(name) < 200


def check_avatar(avatar: str):
    return 0 < len(avatar) < 200


def check_info(info: str):
    return 0 < len(info) < 200


def check_approve_permission(perm: int):
    return 0 <= perm <= 4


def wrap_block(block_dict):
    block_id = block_dict['block_id']
    block_dict['population'] = Permission.objects.filter(block_id=block_id).filter(
        permission__gte=1).count()  # count students only
    return block_dict


@csrf_exempt
def block_query_all(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        # db
        with transaction.atomic():
            block_set = Block.objects.all()
            blocks = []
            for block in block_set:
                b_dict = block.to_dict()
                blocks.append(wrap_block(b_dict))
            return JsonResponse({'status': 0, 'info': '查询成功', 'data': blocks})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})


@csrf_exempt
def block_query_permission(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        permission = request.GET.getlist('permission[]', None)
        # check params
        if permission is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        perms = set()
        for perm in permission:
            perm = int(perm)
            if not -1 <= perm <= 4:
                return JsonResponse({'status': -1, 'info': '参数错误'})
            perms.add(perm)
        # db
        with transaction.atomic():
            blocks = []
            perm_query_set = Permission.objects.filter(user_id=user_id)
            sub_block_perm = {}  # 订阅的block，block_id->permission
            block_ids = set()  # 需要返回的block
            for p in perm_query_set:
                sub_block_perm[p.block_id] = p.permission
            sub_block_ids = sub_block_perm.keys()
            if -1 in perms:
                all_blocks = Block.objects.filter()
                for b in all_blocks:
                    if b.block_id not in sub_block_ids:
                        block_ids.add(b.block_id)
            for block_id in sub_block_ids:
                permission = sub_block_perm[block_id]
                if permission in perms:
                    block_ids.add(block_id)
            for block_id in block_ids:
                b_dict = Block.objects.get(block_id=block_id).to_dict()
                blocks.append(wrap_block(b_dict))
            return JsonResponse({'status': 0, 'info': '查询成功', 'data': blocks})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})


@csrf_exempt
def block_info(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        block_id = request.GET.get('block_id')
        # check params
        if block_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        block_id = int(block_id)
        # db
        with transaction.atomic():
            block_query_set = Block.objects.filter(block_id=block_id)
            if not block_query_set.exists():
                return JsonResponse({'status': -1, 'info': '模块不存在'})
            b_dict = block_query_set[0].to_dict()
            b_dict = wrap_block(b_dict)
            return JsonResponse({'status': 0, 'info': '查询成功', 'data': b_dict})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})


@csrf_exempt
def block_search_all(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        keyword = request.GET.get('keyword')
        # check params
        if keyword is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        keyword = str(keyword).strip('\t').strip(' ')
        if len(keyword) < 0:
            return JsonResponse({'status': -1, 'info': '参数不合法'})
        # db
        with transaction.atomic():
            block_query_set = Block.objects.filter(Q(name__icontains=keyword) | Q(info__icontains=keyword))
            blocks = []
            for block in block_query_set:
                b_dict = block.to_dict()
                blocks.append(wrap_block(b_dict))
            return JsonResponse({'status': 0, 'info': '查询成功', 'data': blocks})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})


@csrf_exempt
def block_search_my(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        keyword = request.GET.get('keyword')
        # check params
        if keyword is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        keyword = str(keyword).strip('\t').strip(' ')
        if len(keyword) < 0:
            return JsonResponse({'status': -1, 'info': '参数不合法'})
        # db
        with transaction.atomic():
            block_id_set = set()
            for b in Permission.objects.filter(user_id=user_id):
                block_id_set.add(b.block_id)
            blocks = []
            for bid in block_id_set:
                block_query_set = Block.objects.filter(block_id=bid) \
                    .filter(name__contains=keyword, info__contains=keyword)
                if not block_query_set.exists():
                    continue
                block = block_query_set[0]
                b_dict = block.to_dict()
                blocks.append(b_dict)
            return JsonResponse({'status': 0, 'info': '查询成功', 'data': blocks})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})


@csrf_exempt
def block_subscribe(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        data = json.loads(request.body)
        block_id = data.get('block_id')
        subscribe = data.get('subscribe')
        # check params
        if block_id is None or subscribe is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        block_id = int(block_id)
        subscribe = int(subscribe)
        if subscribe not in [0, 1]:
            return JsonResponse({'status': -1, 'info': '参数错误'})
        # db
        with transaction.atomic():
            if not Block.objects.filter(block_id=block_id).exists():
                return JsonResponse({'status': -1, 'info': '模块不存在'})
            if subscribe == 0:
                Permission.objects.filter(user_id=user_id).filter(block_id=block_id).delete()
                return JsonResponse({'status': 0, 'info': '已取消订阅'})
            block_perm = Block.objects.get(block_id=block_id).approve_permission
            perm_query_set = Permission.objects.filter(user_id=user_id).filter(block_id=block_id)
            if perm_query_set.exists():
                return JsonResponse({'status': 0, 'info': '已订阅'})
            update_perm = 1 if block_perm < 0 else 0
            new_subscribe = Permission(block_id=block_id, user_id=user_id, permission=update_perm)
            new_subscribe.save()
            return JsonResponse({'status': 0, 'info': '已订阅'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})


@csrf_exempt
def block_random(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        number = request.GET.get('number')
        # check params
        if number is None:
            number = 20
        number = int(number)
        if number <= 0:
            number = 20
        # db
        with transaction.atomic():
            headers = ['block_id', 'name', 'avatar', 'info']
            header = headers[random.randint(0, 3)]
            if random.randint(0, 1) == 0:
                header = '-' + header
            block_query_set = Block.objects.all().order_by(header)[:number]
            blocks = []
            for b in block_query_set:
                b_dict = b.to_dict()
                blocks.append(wrap_block(b_dict))
            return JsonResponse({'status': 0, 'info': '查询成功', 'data': blocks})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})


@csrf_exempt
def block_modify(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        data = json.loads(request.body)
        block_id = data.get('block_id')
        name = data.get('block_id')
        avatar = data.get('avatar')
        info = data.get('info')
        approve_permission = data.get('approve_permission')
        # check params
        if block_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        block_id = int(block_id)
        if name is not None:
            name = str(name).strip('\t').strip(' ')
            if not check_name(name):
                return JsonResponse({'status': -1, 'info': '名字不合法'})
        if avatar is not None:
            avatar = str(avatar)
            if not check_avatar(avatar):
                return JsonResponse({'status': -1, 'info': '头像不合法'})
        if info is not None:
            info = str(info).strip('\t').strip(' ')
            if not check_info(info):
                return JsonResponse({'status': -1, 'info': '简介不合法'})
        if approve_permission is not None:
            approve_permission = int(approve_permission)
            if not check_approve_permission(approve_permission):
                return JsonResponse({'status': -1, 'info': '权限不合法'})
        # db
        with transaction.atomic():
            block = Block.objects.filter(block_id=block_id)
            if not block.exists():
                return JsonResponse({'status': -1, 'info': '模块不存在'})
            if not Permission.objects.filter(block_id=block_id).filter(user_id=user_id).filter(permission=4).exists():
                return JsonResponse({'status': -1, 'info': '权限不足'})
            if name is not None:
                block.update(name=name)
            if avatar is not None:
                block.update(avatar=avatar)
            if info is not None:
                block.update(info=info)
            if approve_permission is not None:
                block.update(approve_permission=approve_permission)
            return JsonResponse({'status': 0, 'info': '已修改'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，修改失败'})


@csrf_exempt
def block_delete(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        data = json.loads(request.body)
        block_id = data.get('block_id')
        # check params
        if block_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        block_id = int(block_id)
        # db
        with transaction.atomic():
            block = Block.objects.filter(block_id=block_id)
            if not block.exists():
                return JsonResponse({'status': -1, 'info': '模块不存在'})
            if not Permission.objects.filter(user_id=user_id).filter(block_id=block_id).filter(permission=4).exists():
                return JsonResponse({'status': -1, 'info': '权限不足'})
            post_ids = set()
            comment_ids = set()
            post_query_set = Post.objects.filter(block_id=block_id)
            for p in post_query_set:
                post_ids.add(p.post_id)
                comm_query_set = Comment.objects.filter(post_id=p.post_id)
                for c in comm_query_set:
                    comment_ids.add(c.comment_id)
            # del comment
            for comm_id in comment_ids:
                CommentLike.objects.filter(comment_id=comm_id).delete()
                Comment.objects.filter(comment_id=comm_id).delete()
            # del post
            for post_id in post_ids:
                PostFavor.objects.filter(post_id=post_id).delete()
                PostChosen.objects.filter(post_id=post_id).delete()
                PostLike.objects.filter(post_id=post_id).delete()
                Post.objects.filter(post_id=post_id).delete()
            # del block
            Permission.objects.filter(block_id=block_id).delete()
            Notice.objects.filter(block_id=block_id).delete()
            Contribution.objects.filter(block_id=block_id).delete()
            Block.objects.filter(block_id=block_id).delete()
            return JsonResponse({'status': 0, 'info': '已删除'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，删除失败'})
