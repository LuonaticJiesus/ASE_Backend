import datetime
import json
import re
from random import Random

import pytz
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from BackEnd.settings import EMAIL_HOST_USER, SERVER_IP, SERVER_PORT, TIME_ZONE
from four_s.models import UserInfo, EmailPro
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
    return len(card_id) > 0


def check_phone(phone: str):
    return re.match(r'^[1][3-9][0-9]{9}$', phone) is not None


def check_email(email: str):
    return re.match(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', email) is not None


def check_avatar(avatar: str):
    return 0 < len(avatar) < 200


def random_str(randomlength=8):
    str = ''
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str


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
        if name is None or password is None or email is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        name = str(name).strip('\t').strip(' ')
        if not check_name(name):
            return JsonResponse({'status': -1, 'info': '用户名格式错误'})
        password = str(password)
        if not check_pwd(password):
            return JsonResponse({'status': -1, 'info': '密码格式错误'})
        if card_id is not None:
            card_id = str(card_id).strip('\t').strip(' ')
            if not check_card_id(card_id):
                return JsonResponse({'status': -1, 'info': '学工卡格式错误'})
        if phone is not None:
            phone = str(phone).strip('\t').strip(' ')
            if not check_phone(phone):
                return JsonResponse({'status': -1, 'info': '手机格式错误'})
        email = str(email).strip('\t').strip(' ')
        if not check_email(email):
            return JsonResponse({'status': -1, 'info': '邮箱格式错误'})
        # db
        with transaction.atomic():
            if UserInfo.objects.filter(name=name).exists():
                return JsonResponse({'status': -1, 'info': '用户名已存在'})
            if card_id is not None and UserInfo.objects.filter(card_id=card_id).exists():
                return JsonResponse({'status': -1, 'info': '卡id已存在'})
            if UserInfo.objects.filter(email=email).exists():
                return JsonResponse({'status': -1, 'info': '邮箱已注册'})
            password = make_password(password)

            # send verification email
            send_type = 'register'
            code = random_str(16)  # 生成16位的随机字符串
            email_recode = EmailPro(code=code, email=email, send_type=send_type,
                                    name=name, password=password, card_id=card_id,
                                    phone=phone)
            email_recode.save()

            email_title = ''
            email_body = ''
            if send_type == 'register':
                email_title = '注册激活链接'
                email_body = '请点击下方的链接激活你的账号：http://' + SERVER_IP + ':' + SERVER_PORT + '/?active_code={}'.format(
                    code)
            else:
                pass  # 忘记密码--暂时不写
            send_status = send_mail(email_title, email_body, EMAIL_HOST_USER, [email])
            if send_status:
                return JsonResponse({'status': 0, 'info': '发送成功，请查看邮箱'})
            return JsonResponse({'status': -1, 'info': '操作错误，发送失败'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，注册失败'})


@csrf_exempt
def active_email(request):
    if request.method != 'GET':
        return HttpResponse("请求方式错误")
    try:
        active_code = request.GET.get('active_code')
        # check params
        if active_code is None:
            return HttpResponse("缺少参数")
        active_code = str(active_code)
        # db
        with transaction.atomic():
            all_codes = EmailPro.objects.filter(code=active_code)
            if not all_codes.exists():
                return HttpResponse("验证码错误，注册失败")
            info = all_codes[0]
            if datetime.datetime.now() + datetime.timedelta(minutes=30) < info.send_time:
                return HttpResponse("验证超时，请重新注册")
            user = UserInfo(name=info.name, password=info.password, avatar=None,
                            card_id=info.card_id, phone=info.phone, email=info.email, point=50)
            user.save()
            all_codes.delete()
            return HttpResponse("注册成功，请登录")
    except Exception as e:
        print(e)
        return HttpResponse("操作错误，注册失败")


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
        name = str(name).strip(' ').strip('\t')
        password = str(password).strip(' ').strip('\t')
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
            card_id = str(card_id).strip('\t').strip(' ')
            if not check_card_id(card_id):
                return JsonResponse({'status': -1, 'info': '学工卡格式错误'})
        if phone is not None:
            phone = str(phone).strip('\t').strip(' ')
            if not check_phone(phone):
                return JsonResponse({'status': -1, 'info': '手机格式错误'})
        if email is not None:
            email = str(email).strip('\t').strip(' ')
            if not check_email(email):
                return JsonResponse({'status': -1, 'info': '邮箱格式错误'})
        if avatar is not None:
            avatar = str(avatar).strip('\t').strip(' ')
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
        old_password = data.get('old_password')
        # check params
        if password is None or old_password is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        password = str(password)
        old_password = str(old_password)
        if not check_pwd(password):
            return JsonResponse({'status': -1, 'info': '新密码格式错误'})
        # db
        with transaction.atomic():
            user_id = int(user_id)
            user_filter = UserInfo.objects.filter(user_id=user_id)
            if not user_filter.exists():
                return JsonResponse({'status': -1, 'info': '用户不存在'})
            user = user_filter[0]
            if not check_password(old_password, user.password):
                return JsonResponse({'status': -1, 'info': '旧密码错误'})
            user.password = make_password(password)
            user.save()
            return JsonResponse({'status': 0, 'info': '已修改'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，注册失败'})
