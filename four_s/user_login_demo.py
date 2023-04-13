# from django.http import JsonResponse
# from .models import user_login as user_login_table
# from .models import user_info as user_info_table
# from django.views.decorators.csrf import csrf_exempt  # 关闭校验，方便测试，但是可能会有安全问题
# import json
#
# @csrf_exempt
# def register(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         user_id = data.get('user_id')
#         token = data.get('token')
#         user_name = data.get('name')
#         # 检查 user_id 是否已经存在
#         if user_login_table.objects.filter(user_id=user_id).exists():
#             return JsonResponse({'message': '该用户已注册'})
#         # 注册用户
#         user = user_login_table(user_id=user_id, token=token)
#         user.save()
#         user_info = user_info_table(user_id=user_id, name=user_name, point=50)
#         user_info.save()
#         return JsonResponse({'message': '注册成功'})
#     return JsonResponse({'message': '注册失败'})
#
#
# @csrf_exempt
# def user_login(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         user_id = data.get('user_id')
#         token = data.get('token')
#         # 验证用户
#         if user_login_table.objects.filter(user_id=user_id, token=token).exists():
#             # 登录成功
#             request.session['user_id'] = user_id  # 将用户 id 存入 session
#             return JsonResponse({'message': '登录成功'})
#     # 登录失败
#     return JsonResponse({'message': '登录失败'})
#
#
# @csrf_exempt
# def user_logout(request):
#     if 'user_id' in request.session:
#         del request.session['user_id']  # 删除 session 中的用户 id
#     return JsonResponse({'message': '注销成功'})
#
#
# @csrf_exempt
# def get_user_info(request):
#     data = json.loads(request.body)
#     user_id = data.get('user_id')
#     user_info = user_info_table.objects.filter(user_id=user_id).values('name', 'point').first()
#     if user_info is not None:
#         return JsonResponse(user_info, safe=False)
#     else:
#         return JsonResponse({'error': '用户不存在'}, status=404)