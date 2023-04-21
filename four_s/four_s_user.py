import json
import re

from django.contrib.auth.hashers import make_password, check_password
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from four_s.models import UserInfo
from utils.auth_util import create_token


# 长度 5-20，字母数字下划线
def check_name(name: str):
    if len(name) < 5 or len(name) > 20:
        return False
    return re.match(r'[0-9a-zA-Z_]*', name) is not None


def check_pwd(password: str):
    if len(password) < 8 or len(password) > 16:
        return False
    has_num = False
    has_alpha = False
    for c in password:
        if '0' <= c <= '9':
            has_num = True
        if 'a' <= c <= 'z' or 'A' <= c <= 'Z':
            has_alpha = True
        if has_alpha and has_num:
            return True
    return False


def check_card_id(card_id: str):
    return True


def check_phone(phone: str):
    return re.match(r'^[1][3-9][0-9]{9}$', phone) is not None


def check_email(email: str):
    return re.match(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', email) is not None


def check_avatar(avatar: str):
    return True


@csrf_exempt
def user_signup(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        data = json.loads(request.body)
        name = data.get('name')
        password = data.get('password')
        card_id = data.get('card_id')
        phone = data.get('phone')
        email = data.get('email')
        # check params
        if name is None or password is None:
            return JsonResponse({'status': -1, 'info': '用户名或密码为空'})
        name = str(name)
        if not check_name(name):
            return JsonResponse({'status': -1, 'info': '用户名格式错误'})
        password = str(password)
        if not check_pwd(password):
            return JsonResponse({'status': -1, 'info': '密码格式错误'})
        if card_id is not None:
            card_id = str(card_id)
            if not check_card_id(card_id):
                return JsonResponse({'status': -1, 'info': '学工卡格式错误'})
        if phone is not None:
            phone = str(phone)
            if not check_phone(phone):
                return JsonResponse({'status': -1, 'info': '手机格式错误'})
        if email is not None:
            email = str(email)
            if not check_email(email):
                return JsonResponse({'status': -1, 'info': '邮箱格式错误'})
        # db
        with transaction.atomic():
            if UserInfo.objects.filter(name=name).exists():
                return JsonResponse({'status': -1, 'info': '用户名已存在'})
            if card_id is not None and UserInfo.objects.filter(card_id=card_id).exists():
                return JsonResponse({'status': -1, 'info': '卡id已存在'})
            password = make_password(password)
            user = UserInfo(name=name, password=password, avatar=None,
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
        name = data.get('name')
        password = data.get('password')
        # check params
        if name is None or password is None:
            return JsonResponse({'status': -1, 'info': '用户名或密码为空'})
        name = str(name)
        password = str(password)
        # db
        with transaction.atomic():
            user_query_set = UserInfo.objects.filter(name=name)
            if not user_query_set.exists():
                return JsonResponse({'status': -1, 'info': '用户名不存在'})
            user = user_query_set[0]
            if not check_password(password, user.password):
                return JsonResponse({'status': -1, 'info': '密码错误'})
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
        # check params
        if user_id is None:
            return JsonResponse({'status': -1, 'info': '用户名不存在'})
        user_id = str(user_id)
        # db
        with transaction.atomic():
            user_query_set = UserInfo.objects.filter(user_id=user_id)
            if not user_query_set.exists():
                return JsonResponse({'status': -1, 'info': '用户不存在'})
            user = user_query_set[0]
            u_dict = {'name': user.name}
            if user.avatar is not None:
                u_dict['avatar'] = user.avatar
            return JsonResponse({'status': 0, 'info': '查询成功', 'data': u_dict})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误'})


@csrf_exempt
def user_my_info(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        user = UserInfo.objects.get(user_id=user_id)
        u_dict = user.to_dict()
        return JsonResponse({'status': 0, 'info': '查询成功', 'data': u_dict})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误'})


@csrf_exempt
def user_modify(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        data = json.loads(request.body)
        card_id = data.get('card_id')
        phone = data.get('phone')
        email = data.get('email')
        avatar = data.get('avatar')
        # check params
        if card_id is not None:
            card_id = str(card_id)
            if not check_card_id(card_id):
                return JsonResponse({'status': -1, 'info': '学工卡格式错误'})
        if phone is not None:
            phone = str(phone)
            if not check_phone(phone):
                return JsonResponse({'status': -1, 'info': '手机格式错误'})
        if email is not None:
            email = str(email)
            if not check_email(email):
                return JsonResponse({'status': -1, 'info': '邮箱格式错误'})
        if avatar is not None:
            avatar = str(avatar)
            if not check_avatar(avatar):
                return JsonResponse({'status': -1, 'info': '头像格式错误'})
        # db
        with transaction.atomic():
            user = UserInfo.objects.filter(user_id=user_id)
            if card_id is not None:
                user.update(card_id=card_id)
            if phone is not None:
                user.update(phone=phone)
            if email is not None:
                user.update(email=email)
            if avatar is not None:
                user.update(avatar=avatar)
            return JsonResponse({'status': 0, 'info': '已修改'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，注册失败'})


@csrf_exempt
def user_change_pwd(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        data = json.loads(request.body)
        password = data.get('password')
        # check params
        if password is None:
            return JsonResponse({'status': -1, 'info': '新密码不存在'})
        password = str(password)
        if not check_pwd(password):
            return JsonResponse({'status': -1, 'info': '新密码格式错误'})
        # db
        with transaction.atomic():
            user_id = int(user_id)
            user = UserInfo.objects.filter(user_id=user_id)
            if not user.exists():
                return JsonResponse({'status': -1, 'info': '用户不存在'})
            user.update(password=make_password(password))
            return JsonResponse({'status': 0, 'info': '已修改'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，注册失败'})
