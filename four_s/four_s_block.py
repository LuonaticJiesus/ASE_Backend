from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from four_s.models import Block, UserInfo, Permission, Contribution


@csrf_exempt
def get_all_blocks(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = request.GET.get('user_id')
        if user_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        user_id = int(user_id)
        permission_queryset = Permission.objects.filter(user_id=user_id).filter(permission__gte=1)
        block_set = Block.objects.all()
        blocks = []
        for block in block_set:
            b_dict = block.to_dict()
            blocks.append(b_dict)

        return JsonResponse({'status': 0, 'info': '查询成功', 'data': blocks})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})

@csrf_exempt
def get_user_blocks(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = request.GET.get('user_id')
        if user_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        user_id = int(user_id)
        # permission_queryset = Permission.objects.filter(user_id=user_id).filter(permission__gte=1)
        contribution_queryset = Contribution.objects.filter(user_id=user_id)
        # block_id_set = set()
        # for c in contribution_queryset:
        #     block_id_set.add(c.block_id)
        blocks = []
        for contrib in contribution_queryset:
            block = Block.objects.get(block_id=contrib.block_id)
            b_dict = block.to_dict()
            blocks.append(b_dict)

        return JsonResponse({'status': 0, 'info': '查询成功', 'data': blocks})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})

@csrf_exempt
def get_block_users(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        block_id = request.GET.get('block_id')
        if block_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        block_id = int(block_id)
        # permission_queryset = Permission.objects.filter(block_id=block_id).filter(permission__gte=1)
        contribution_queryset = Contribution.objects.filter(block_id=block_id)
        # block_id_set = set()
        # for c in contribution_queryset:
        #     block_id_set.add(c.block_id)
        users = []
        for contrib in contribution_queryset:
            user = UserInfo.objects.filter(user_id=contrib.user_id)
            u_dict = user.to_dict()
            users.append(u_dict)

        return JsonResponse({'status': 0, 'info': '查询成功', 'data': users})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})