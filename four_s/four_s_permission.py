import json

from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from four_s.models import Permission, UserInfo, Block


@csrf_exempt
def permission_query_user(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        block_id = request.GET.get('block_id')
        permission = request.GET.get('permission')
        # check params
        if permission is None or block_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        block_id = int(block_id)
        permission = int(permission)
        if permission > 4:
            return JsonResponse({'status': -1, 'info': '参数错误'})
        # db
        with transaction.atomic():
            if permission < 0:
                perm_query_set = Permission.objects.filter(block_id=block_id)
            else:
                perm_query_set = Permission.objects.filter(block_id=block_id).filter(permission=permission)
            users = []
            for p in perm_query_set:
                user_dict = UserInfo.objects.get(user_id=p.user_id).to_dict()
                user_dict['approve_permission'] = p.permission
                users.append(user_dict)

            return JsonResponse({'status': 0, 'info': '查询成功', 'data': users})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})


@csrf_exempt
def permission_query(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = request.GET.get('user_id')
        block_id = request.GET.get('block_id')
        # check params
        if user_id is None or block_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        user_id = int(user_id)
        block_id = int(block_id)
        # db
        with transaction.atomic():
            perm_query_set = Permission.objects.filter(user_id=user_id).filter(block_id=block_id)
            if not perm_query_set.exists():
                return JsonResponse({'status': 0, 'info': '查询成功', 'data': -1})
            return JsonResponse({'status': 0, 'info': '查询成功', 'data': perm_query_set[0].permission})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})


@csrf_exempt
def permission_set(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        userid = int(request.META.get('HTTP_USERID'))
        data = json.loads(request.body)
        user_id = data.get('user_id')
        block_id = data.get('block_id')
        permission = data.get('permission')
        # check params
        if user_id is None or permission is None or block_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        user_id = int(user_id)
        block_id = int(block_id)
        permission = int(permission)
        if permission not in [0, 1, 2, 3, 4]:
            return JsonResponse({'status': -1, 'info': '权限错误'})
        # db
        with transaction.atomic():
            if not UserInfo.objects.filter(user_id=user_id).exists():
                return JsonResponse({'status': -1, 'info': '约束错误'})
            if not Block.objects.filter(block_id=block_id).exists():
                return JsonResponse({'status': -1, 'info': '约束错误'})
            user_perm_query_set = Permission.objects.filter(user_id=userid).filter(block_id=block_id)
            if not user_perm_query_set.exists():
                return JsonResponse({'status': -1, 'info': '权限不足'})
            user_perm = user_perm_query_set[0].permission
            block_perm = Block.objects.get(block_id=block_id).approve_permission
            if user_perm < block_perm:
                return JsonResponse({'status': -1, 'info': '权限不足'})
            if permission > user_perm:
                return JsonResponse({'status': -1, 'info': '权限不足'})
            target_perm_query_set = Permission.objects.filter(user_id=user_id).filter(block_id=block_id)
            if not target_perm_query_set.exists() and permission >= 0:
                new_perm = Permission(user_id=user_id, block_id=block_id, permission=permission)
                new_perm.save()
                return JsonResponse({'status': 0, 'info': '设置成功'})
            target_perm = target_perm_query_set[0].permission
            if user_perm < target_perm:
                return JsonResponse({'status': -1, 'info': '权限不足'})
            Permission.objects.filter(user_id=user_id).filter(block_id=block_id).update(permission=permission)
            return JsonResponse({'status': 0, 'info': '设置成功'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误'})
