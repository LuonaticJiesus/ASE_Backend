import json
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from four_s.models import Notice, UserInfo, Block, NoticeConfirm, Permission


@csrf_exempt
def notice_query_recv(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = request.GET.get('user_id')
        show_confirm = request.GET.get('show_confirm')
        undue_op = request.GET.get('undue_op')
        if user_id is None or show_confirm is None or undue_op is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        user_id = int(user_id)
        show_confirm = int(show_confirm) != 0
        undue_op = int(undue_op)
        permission_queryset = Permission.objects.filter(user_id=user_id).filter(permission__gte=1)
        block_id_set = set()
        for p in permission_queryset:
            block_id_set.add(p.block_id)
        notice_id_set = set()
        now_time = datetime.now()
        for bid in block_id_set:
            if undue_op == 0:
                block_notice_queryset = Notice.objects.filter(block_id=bid)
            elif undue_op > 0:
                block_notice_queryset = Notice.objects.filter(block_id=bid).filter(ddl__gt=now_time)
            else:
                block_notice_queryset = Notice.objects.filter(block_id=bid).filter(ddl__lte=now_time)
            for nid in block_notice_queryset:
                notice_id_set.add(nid)
        if not show_confirm:
            for notice in NoticeConfirm.objects.filter(user_id=user_id):
                notice_id_set.remove(notice.notice_id)
        notices = []
        for nid in notice_id_set:
            notice = Notice.objects.get(notice_id=nid)
            n_dict = notice.to_dict()
            n_dict['user_name'] = UserInfo.objects.get(user_id=notice.user_id).name
            n_dict['block_name'] = Block.objects.get(block_id=notice.block_id).name

        def cmp(element):
            return element['time']

        notices.sort(key=cmp, reverse=True)
        return JsonResponse({'status': 0, 'info': '查询成功', 'data': notices})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})


@csrf_exempt
def notice_query_send(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = request.GET.get('user_id')
        if user_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        user_id = int(user_id)
        user_query_set = UserInfo.objects.filter(id=user_id)
        if user_query_set is None:
            return JsonResponse({'status': -1, 'info': '用户不存在'})
        user_name = user_query_set[0].name
        notice_query_set = Notice.objects.filter(user_id=user_id).order_by('-time')
        notices = []
        for n in notice_query_set:
            n_dict = n.to_dict()
            n_dict['user_name'] = user_name
            n_dict['block_name'] = Block.objects.get(block_id=n.block_id)
            notices.append(n_dict)
        return JsonResponse({'status': 0, 'info': '查询成功', 'data': notices})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})


@csrf_exempt
def notice_query_block(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        block_id = request.GET.get('block_id')
        block_query_set = Block.objects.filter(block_id=block_id)
        if block_query_set is None:
            return JsonResponse({'status': -1, 'info': '模块不存在'})
        block_name = block_query_set[0].name
        notice_query_set = Notice.objects.filter(block_id=block_id).order_by('-time')
        notices = []
        for n in notice_query_set:
            n_dict = n.to_dict()
            n_dict['user_name'] = UserInfo.objects.get(user_id=n.user_id).name
            n_dict['block_name'] = block_name
            notices.append(n_dict)
        return JsonResponse({'status': 0, 'info': '查询成功', 'data': notices})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})


@csrf_exempt
def notice_publish(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        data = json.loads(request.body)
        title = data.get('title')
        txt = data.get('txt')
        block_id = data.get('block_id')
        publish_time = data.get('time')
        ddl = data.get('ddl')
        if title is None or txt is None or user_id is None or block_id is None or publish_time is None or ddl is None:
            return JsonResponse({'status': -1, 'info': '参数缺失'})
        user_id = int(user_id)
        block_id = int(block_id)
        if not UserInfo.objects.filter(user_id=user_id).exists() or not Block.objects.filter(
                block_id=block_id).exists():
            return JsonResponse({'status': -1, 'info': '约束错误'})
        if not Permission.objects.filter(user_id=user_id).filter(block_id=block_id).filter(permission__gte=2).exists():
            return JsonResponse({'status': -1, 'info': '缺少权限'})
        notice = Notice(title=title, txt=txt, user_id=user_id, block_id=block_id,
                        publish_time=datetime.strptime(publish_time, '%Y-%m-%d %H:%M:%S'),
                        ddl=datetime.strptime(ddl, '%Y-%m-%d %H:%M:%S'))
        notice.save()
        return JsonResponse({'status': 0, 'info': '已发布'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})


@csrf_exempt
def notice_delete(request):
    if request.method != 'DELETE':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        data = json.loads(request.body)
        user_id = request.META.get('HTTP_USERID')
        notice_id = data.get('notice_id')
        if notice_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        notice_query_set = Notice.objects.filter(notice_id=notice_id)
        if notice_query_set is None:
            return JsonResponse({'status': -1, 'info': '通知不存在'})
        notice = notice_query_set[0]
        if notice.user_id != user_id:
            return JsonResponse({'status': -1, 'info': '权限不足'})
        notice.delete()
        NoticeConfirm.objects.filter(notice_id=notice_id).delete()
        return JsonResponse({'status': 0, 'info': '已删除'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})
