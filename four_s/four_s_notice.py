import json
from datetime import datetime

from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from four_s.models import Notice, UserInfo, Block, NoticeConfirm, Permission


def check_title(title: str):
    return 0 < len(title) < 200


def check_txt(txt: str):
    return 0 < len(txt)


def check_ddl(ddl: str):
    try:
        _ = datetime.strptime(ddl, '%Y-%m-%d %H:%M:%S')
        return True
    except ValueError as e:
        return False


def wrap_notice(notice, user_id):
    n_dict = notice.to_dict()
    n_dict['user_name'] = UserInfo.objects.get(user_id=notice.user_id).name
    n_dict['block_name'] = Block.objects.get(block_id=notice.block_id).name
    n_dict['confirm_state'] = 1 if NoticeConfirm.objects.filter(user_id=user_id).filter(
        notice_id=notice.notice_id).exists() else 0
    return n_dict


@csrf_exempt
def notice_query_recv(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        confirm_op = request.GET.get('confirm_op')
        undue_op = request.GET.get('undue_op')
        # check params
        if confirm_op is None:
            confirm_op = 0
        if undue_op is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        confirm_op = int(confirm_op)
        undue_op = int(undue_op)
        if confirm_op not in [-1, 0, 1] or undue_op not in [-1, 0, 1]:
            return JsonResponse({'status': -1, 'info': '参数错误'})
        # db
        with transaction.atomic():
            subscribe_query_set = Permission.objects.filter(user_id=user_id)
            notice_id_set = set()
            now_time = datetime.now()
            for sub in subscribe_query_set:
                bid = sub.block_id
                if undue_op == 0:
                    block_notice_queryset = Notice.objects.filter(block_id=bid)
                elif undue_op > 0:
                    block_notice_queryset = Notice.objects.filter(block_id=bid).filter(ddl__gt=now_time)
                else:
                    block_notice_queryset = Notice.objects.filter(block_id=bid).filter(ddl__lte=now_time)
                for notice in block_notice_queryset:
                    notice_id_set.add(notice.notice_id)
            confirm_id_set = set()
            for notice in NoticeConfirm.objects.filter(user_id=user_id):
                confirm_id_set.add(notice.notice_id)
            if confirm_op == 1:  # not confirmed
                notice_id_set = notice_id_set - confirm_id_set
            elif confirm_op == -1:  # confirmed
                notice_id_set = notice_id_set & confirm_id_set
            notices = []
            for nid in notice_id_set:
                notice = Notice.objects.get(notice_id=nid)
                n_dict = wrap_notice(notice, user_id)
                notices.append(n_dict)

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
        user_id = int(request.META.get('HTTP_USERID'))
        # db
        with transaction.atomic():
            user_query_set = UserInfo.objects.filter(id=user_id)
            if not user_query_set.exists():
                return JsonResponse({'status': -1, 'info': '用户不存在'})
            notice_query_set = Notice.objects.filter(user_id=user_id).order_by('-time')
            notices = []
            for n in notice_query_set:
                n_dict = wrap_notice(n, user_id)
                notices.append(n_dict)
            return JsonResponse({'status': 0, 'info': '查询成功', 'data': notices})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})


def notice_query_by_id(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        notice_id = request.GET.get('notice_id')
        # check params
        if notice_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        notice_id = int(notice_id)
        # db
        with transaction.atomic():
            notice_query_set = Notice.objects.filter(notice_id=notice_id)
            if not notice_query_set.exists():
                return JsonResponse({'status': -1, 'info': '通知不存在'})
            notice = notice_query_set[0]
            n_dict = wrap_notice(notice, user_id)
            return JsonResponse({'status': 0, 'info': '查询成功', 'data': [n_dict]})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})


@csrf_exempt
def notice_query_block(request):
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
            block_query_set = Block.objects.filter(block_id=block_id)
            if not block_query_set.exists():
                return JsonResponse({'status': -1, 'info': '模块不存在'})
            block_name = block_query_set[0].name
            notice_query_set = Notice.objects.filter(block_id=block_id).order_by('-time')
            notices = []
            for n in notice_query_set:
                n_dict = wrap_notice(n, user_id)
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
        ddl = data.get('ddl')
        # check params
        if title is None or txt is None or user_id is None or block_id is None or ddl is None:
            return JsonResponse({'status': -1, 'info': '参数缺失'})
        title = str(title).strip(' ').strip('\t')
        if not check_title(title):
            return JsonResponse({'status': -1, 'info': '标题格式错误'})
        txt = str(txt).strip(' ').strip('\t')
        if not check_txt(txt):
            return JsonResponse({'status': -1, 'info': '内容格式错误'})
        ddl = str(ddl)
        if not check_ddl(ddl):
            return JsonResponse({'status': -1, 'info': '截止日期格式错误'})
        block_id = int(block_id)
        # db
        with transaction.atomic():
            if not UserInfo.objects.filter(user_id=user_id).exists() or not Block.objects.filter(
                    block_id=block_id).exists():
                return JsonResponse({'status': -1, 'info': '约束错误'})
            if not Permission.objects.filter(user_id=user_id).filter(block_id=block_id).filter(
                    permission__gte=2).exists():
                return JsonResponse({'status': -1, 'info': '缺少权限'})
            notice = Notice(title=title, txt=txt, user_id=user_id, block_id=block_id,
                            time=datetime.now(),  # publish_time
                            ddl=datetime.strptime(ddl, '%Y-%m-%d %H:%M:%S'))
            notice.save()
            return JsonResponse({'status': 0, 'info': '已发布', 'data': {'notice_id': notice.notice_id}})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})


@csrf_exempt
def notice_confirm(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        data = json.loads(request.body)
        notice_id = data.get('notice_id')
        # check params
        if notice_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        notice_id = int(notice_id)
        # db
        with transaction.atomic():
            notice_query_set = Notice.objects.filter(notice_id=notice_id)
            if not notice_query_set.exists():
                return JsonResponse({'status': -1, 'info': '通知不存在'})
            notice = notice_query_set[0]
            block_id = notice.block_id
            if not Permission.objects.filter(block_id=block_id).filter(user_id=user_id).exists():
                return JsonResponse({'status': 0, 'info': '未订阅模块'})
            now_confirm = NoticeConfirm.objects.filter(user_id=user_id).filter(notice_id=notice_id)
            if now_confirm.exists():
                now_confirm.delete()
                return JsonResponse({'status': 0, 'info': '已取消确认'})
            else:
                new_confirm = NoticeConfirm(user_id=user_id, notice_id=notice_id)
                new_confirm.save()
                return JsonResponse({'status': 0, 'info': '已确认'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})


@csrf_exempt
def notice_delete(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        data = json.loads(request.body)
        notice_id = data.get('notice_id')
        # check params
        if notice_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        notice_id = int(notice_id)
        # db
        with transaction.atomic():
            notice_query_set = Notice.objects.filter(notice_id=notice_id)
            if not notice_query_set.exists():
                return JsonResponse({'status': -1, 'info': '通知不存在'})
            notice = notice_query_set[0]
            if not Permission.objects.filter(block_id=notice.block_id).filter(user_id=user_id).filter(
                    permission__gte=2).exists():
                return JsonResponse({'status': -1, 'info': '权限不足'})
            # delete
            NoticeConfirm.objects.filter(notice_id=notice_id).delete()
            notice.delete()
            return JsonResponse({'status': 0, 'info': '已删除'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})
