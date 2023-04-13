import json

from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from four_s.models import UserInfo


@csrf_exempt
def user_signup(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})

    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        card_id = data.get('card_id') if data.__contains__('card_id') else ''
        phone = data.get('phone') if data.__contains__('phone') else ''
        email = data.get('email') if data.__contains__('email') else ''

        with transaction.atomic():
            if username is None or password is None:
                return JsonResponse({'status': -1, 'info': '用户名或密码为空'})
            if UserInfo.objects.filter(name=username).exists():
                return JsonResponse({'status': -1, 'info': '用户名已存在'})
            if UserInfo.objects.filter(card_id=card_id).exists():
                return JsonResponse({'status': -1, 'info': '用户名已存在'})
            password = make_password(password)
            user = UserInfo(name=username, password=password,
                            card_id=card_id, phone=phone, email=email, point=50)
            user.save()
            return JsonResponse({'status': 0, 'info': '注册成功'})

    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '服务器错误，注册失败'})

