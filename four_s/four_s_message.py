import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from datetime import datetime

from four_s.models import Message, UserInfo


def message_gen(sender_id, receiver_id, content, source_type, source_id):
    try:
        with transaction.atomic():
            message = Message(
                sender_id=sender_id,
                receiver_id=receiver_id,
                content=content,
                source_type=source_type,
                source_id=source_id,
                time=datetime.now(),
                status=0
            )
            message.save()
            return message

    except Exception as e:
        print(e)
        return None


@csrf_exempt
def message_query_rec(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        receiver_id = request.GET.get('receiver_id')
        if receiver_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        receiver_id = int(receiver_id)
        with transaction.atomic():
            messages_queryset = Message.objects.filter(receiver_id=receiver_id)
            messages = []
            for message in messages_queryset:
                m_dict = message.to_dict()
                m_dict['sender_name'] = UserInfo.objects.get(user_id=message.sender_id).name
                m_dict['receiver_name'] = UserInfo.objects.get(user_id=message.receiver_id).name
                messages.append(m_dict)

            def cmp(element):
                return element['time']

            messages.sort(key=cmp, reverse=True)
            return JsonResponse({'status': 0, 'info': '查询成功', 'data': messages})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})


@csrf_exempt
def message_confirm(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})

    try:
        user_id = int(request.META.get('HTTP_USERID'))
        data = json.loads(request.body)
        message_id = data.get('message_id')
        if message_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})

        message_id = int(message_id)

        with transaction.atomic():
            message = Message.objects.get(message_id=message_id)
            message.status = 1
            message.save()

            return JsonResponse({'status': 0, 'info': '消息状态已更新'})

    except Message.DoesNotExist:
        return JsonResponse({'status': -1, 'info': '找不到指定的消息'})

    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，更新失败'})

@csrf_exempt
def message_confirm_all(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})

    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        if user_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})

        user_id = int(user_id)

        with transaction.atomic():
            messages = Message.objects.filter(receiver_id=user_id, status=0)
            for message in messages:
                message.status = 1
                message.save()

            return JsonResponse({'status': 0, 'info': '所有消息状态已更新'})

    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，更新失败'})