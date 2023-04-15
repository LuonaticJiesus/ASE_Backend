from django.urls import path

from four_s.four_s_comment import *
from four_s.four_s_notice import *
from four_s.four_s_post import *
from four_s.four_s_user import *

urlpatterns = [
    # user
    path('user/signup/', user_signup, name='user_signup'),
    path('user/login/', user_login, name='user_login'),
    path('user/changePwd/', user_change_pwd, name='user_change_pwd'),

    # notice
    path(r'notice/queryRecv/', notice_query_recv, name='notice_query_recv'),
    path(r'notice/querySend/', notice_query_send, name='notice_query_send'),
    path(r'notice/queryBlock/', notice_query_block, name='notice_query_block'),
    path('notice/publish/', notice_publish, name='notice_publish'),
    path('notice/delete/', notice_delete, name='notice_delete'),

    # post
    path('post/queryTitle/', post_query_title, name='post_query_title'),
    path('post/queryBlock/', post_query_block, name='post_query_block'),
    path('post/queryUser/', post_query_user, name='post_query_user'),
    path('post/publish/', post_publish, name='post_publish'),
    path('post/delete/', post_delete, name='post_delete'),
    path('post/like/', post_like, name='post_like'),
    path('post/choose/', post_choose, name='post_choose'),

    # comment
    path('comment/publish/', comment_publish, name='comment_publish'),
    path('comment/queryPost/', comment_queryPost, name='comment_queryPost'),
    path('comment/delete/', comment_delete, name='comment_delete'),
    path('comment/like/', comment_like, name='comment_like'),
]