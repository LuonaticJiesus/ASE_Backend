import json

from django.contrib.auth.hashers import make_password, check_password
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from four_s.models import UserInfo
from utils.auth_util import create_token


@csrf_exempt
def user_signup(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        card_id = data.get('card_id')
        phone = data.get('phone')
        email = data.get('email')
        with transaction.atomic():
            if username is None or password is None:
                return JsonResponse({'status': -1, 'info': '用户名或密码为空'})
            if UserInfo.objects.filter(name=username).exists():
                return JsonResponse({'status': -1, 'info': '用户名已存在'})
            if UserInfo.objects.filter(card_id=card_id).exists():
                return JsonResponse({'status': -1, 'info': '卡id已存在'})
            password = make_password(password)
            user = UserInfo(name=username, password=password, avatar=None,
                            card_id=card_id, phone=phone, email=email, point=50)
            user.save()
            return JsonResponse({'status': 0, 'info': '注册成功'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，注册失败'})


@csrf_exempt
def user_login(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        with transaction.atomic():
            if username is None or password is None:
                return JsonResponse({'status': -1, 'info': '用户名或密码为空'})
            user_query_set = UserInfo.objects.filter(name=username)
            if not user_query_set.exists():
                return JsonResponse({'status': -1, 'info': '用户名不存在'})
            user = user_query_set[0]
            if not check_password(password, user.password):
                return JsonResponse({'status': -1, 'info': '用户名不存在'})
            user_token = create_token(str(user.user_id))
            user_id = user.user_id
            return JsonResponse({'status': 0, 'info': '已登录', 'data': {
                'userid': user_id,
                'token': user_token
            }})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，注册失败'})


@csrf_exempt
def user_info(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        with transaction.atomic():
            user_query_set = UserInfo.objects.filter(user_id=user_id)
            if not user_query_set.exists():
                return JsonResponse({'status': -1, 'info': '用户不存在'})
            u_dict = user_query_set[0].to_dict()
            return JsonResponse({'status': 0, 'info': '查询成功', 'data': u_dict})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误'})


@csrf_exempt
def user_my_info(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = request.META.get('HTTP_USERID')
        user = UserInfo.objects.get(user_id=user_id)
        u_dict = user.to_dict()
        u_dict['password'] = user.password
        return JsonResponse({'status': 0, 'info': '查询成功', 'data': u_dict})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误'})


@csrf_exempt
def user_modify(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = request.META.get('HTTP_USERID')
        data = json.loads(request.body)
        with transaction.atomic():
            user = UserInfo.objects.filter(user_id=user_id)
            if data.get('name') is not None:
                if UserInfo.objects.filter(name=data.get('name')).exists():
                    return JsonResponse({'status': -1, 'info': '用户名已存在'})
                user.update(name=data.get('name'))
            if data.get('card_id') is not None:
                user.update(card_id=data.get('card_id'))
            if data.get('phone') is not None:
                user.update(phone=data.get('phone'))
            if data.get('email') is not None:
                user.update(email=data.get('email'))
            if data.get('avatar') is not None:
                user.update(avatar=data.get('avatar'))
            if data.get('password') is not None:
                user.update(password=data.get('password'))
            return JsonResponse({'status': 0, 'info': '已修改'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，注册失败'})


@csrf_exempt
def user_change_pwd(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = request.META.get('HTTP_USERID')
        data = json.loads(request.body)
        new_pwd = data.get('new_pwd')
        with transaction.atomic():
            if user_id is None or new_pwd is None:
                return JsonResponse({'status': -1, 'info': '用户名或密码为空'})
            user_id = int(user_id)
            user = UserInfo.objects.get(user_id=user_id)
            if user is None:
                return JsonResponse({'status': -1, 'info': '用户不存在'})
            user.password = make_password(new_pwd)
            user.save()
            return JsonResponse({'status': 0, 'info': '已修改'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，注册失败'})
