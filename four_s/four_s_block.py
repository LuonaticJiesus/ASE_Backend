import json
import random

from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from four_s.models import Block, Permission


def wrap_block(block_dict):
    block_id = block_dict['block_id']
    block_dict['population'] = Permission.objects.filter(block_id=block_id).filter(permission__gte=1).count()    # count students only
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
        permission = request.GET.get('permission')
        # check params
        if permission is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        permission = int(permission)
        if permission not in [0, 1, 2, 3, 4]:
            return JsonResponse({'status': -1, 'info': '参数错误'})
        # db
        with transaction.atomic():
            permission_query_set = Permission.objects.filter(user_id=user_id).filter(permission=permission)
            blocks = []
            for p in permission_query_set:
                block = Block.objects.get(block_id=p.block_id)
                blocks.append(wrap_block(block.to_dict()))
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
            update_perm = 1 if block_perm < 0 else 0
            if perm_query_set.exists():
                perm_query_set.update(permission=update_perm)
                return JsonResponse({'status': 0, 'info': '已订阅'})
            new_perm = Permission(user_id=user_id, block_id=block_id, permission=update_perm)
            new_perm.save()
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
