from django.contrib import admin
from django.urls import path

from four_s.four_s_block import *
from four_s.four_s_comment import *
from four_s.four_s_file import *
from four_s.four_s_notice import *
from four_s.four_s_permission import *
from four_s.four_s_post import *
from four_s.four_s_user import *
from four_s.four_s_message import *

urlpatterns = [
    # admin
    path('admin/', admin.site.urls),

    # user
    path('user/signup/', user_signup, name='user_signup'),
    path('user/login/', user_login, name='user_login'),
    path('user/info/', user_info, name='user_info'),
    path('user/myInfo/', user_my_info, name='user_my_info'),
    path('user/modify/', user_modify, name='user_modify'),
    path('user/changePwd/', user_change_pwd, name='user_change_pwd'),
    path('user/active/', active_email, name='user_check_email'),

    # block
    path('block/queryAll/', block_query_all, name='block_query_all'),
    path('block/queryPermission/', block_query_permission, name='block_query_permission'),
    path('block/searchAll/', block_search_all, name='block_search_all'),
    path('block/searchMy/', block_search_my, name='block_search_my'),
    path('block/subscribe/', block_subscribe, name='block_subscribe'),
    path('block/info/', block_info, name='block_info'),
    path('block/random/', block_random, name='block_random'),
    path('block/modify/', block_modify, name='block_modify'),
    path('block/delete/', block_delete, name='block_delete'),

    # post
    path('post/queryTitle/', post_query_title, name='post_query_title'),
    path('post/queryByID/', post_query_by_id, name='post_query_by_id'),
    path('post/queryBlock/', post_query_block, name='post_query_block'),
    path('post/queryUser/', post_query_user, name='post_query_user'),
    path('post/queryUserBlock/', post_query_user_block, name='post_query_user_block'),
    path('post/queryChosen/', post_query_chosen, name='post_query_chosen'),
    path('post/detail/', post_detail, name='post_detail'),
    path('post/publish/', post_publish, name='post_publish'),
    path('post/delete/', post_delete, name='post_delete'),
    path('post/like/', post_like, name='post_like'),
    path('post/choose/', post_choose, name='post_choose'),
    path('post/favor/', post_favor, name='post_favor'),
    path('post/queryFavor/', post_query_favor, name='post_query_favor'),


    # comment
    path('comment/queryPost/', comment_queryPost, name='comment_queryPost'),
    path('comment/publish/', comment_publish, name='comment_publish'),
    path('comment/delete/', comment_delete, name='comment_delete'),
    path('comment/like/', comment_like, name='comment_like'),

    # notice
    path('notice/queryRecv/', notice_query_recv, name='notice_query_recv'),
    path('notice/querySend/', notice_query_send, name='notice_query_send'),
    path('notice/queryById/', notice_query_by_id, name='notice_query_by_id'),
    path('notice/queryBlock/', notice_query_block, name='notice_query_block'),
    path('notice/publish/', notice_publish, name='notice_publish'),
    path('notice/confirm/', notice_confirm, name='notice_confirm'),
    path('notice/delete/', notice_delete, name='notice_delete'),

    # permission
    path('permission/queryUser/', permission_query_user, name='permission_query_user'),
    path('permission/query/', permission_query, name='permission_query'),
    path('permission/set/', permission_set, name='permission_set'),

    # message
    path('message/queryRec/', message_query_rec, name='message_query_rec'),
    path('message/confirm/', message_confirm, name='message_confirm'),
    path('message/confirmAll/', message_confirm_all, name='message_confirm_all'),

    # file
    path('file/upload/', file_upload, name='file_upload'),
]