from django.urls import path
from . import user_login_demo

urlpatterns = [
    # 路由配置
    path('user_login', user_login_demo.user_login, name='user_login'),
    path('register', user_login_demo.register, name='register'),
    path('user_logout', user_login_demo.user_logout, name='user_logout'),
    path('get_user_info', user_login_demo.get_user_info, name='get_user_info'),

    # 其他路由配置
]