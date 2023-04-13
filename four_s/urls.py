from django.urls import path

from four_s.four_s_user import user_signup

urlpatterns = [
    # 路由配置
    # path('user_login', user_login_demo.user_login, name='user_login'),
    # path('register', user_login_demo.register, name='register'),
    # path('user_logout', user_login_demo.user_logout, name='user_logout'),
    # path('get_user_info', user_login_demo.get_user_info, name='get_user_info'),

    # user
    path('user/signup/', user_signup, name='user_signup')

    # notice

]