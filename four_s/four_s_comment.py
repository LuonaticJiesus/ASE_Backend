import json
from datetime import datetime

from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from four_s.models import Post, Permission, Comment, CommentLike, UserInfo, Message


def wrap_comment(comm_dict, user_id):
    comm_id = comm_dict['comment_id']
    user = UserInfo.objects.get(user_id=comm_dict['user_id'])
    comm_dict['like_cnt'] = CommentLike.objects.filter(comment_id=comm_id).count()
    comm_dict['user_name'] = user.name
    comm_dict['like_state'] = 1 if CommentLike.objects.filter(user_id=user_id).filter(
        comment_id=comm_id).exists() else 0
    if user.avatar is not None:
        comm_dict['user_avatar'] = user.avatar


def check_txt(txt: str):
    return len(txt) > 0


@csrf_exempt
def comment_queryPost(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        post_id = request.GET.get('post_id')
        # check params
        if post_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        post_id = int(post_id)
        # db
        with transaction.atomic():
            if not Post.objects.filter(post_id=post_id).exists():
                return JsonResponse({'status': -1, 'info': '帖子不存在'})
            comment_query_set = Comment.objects.filter(post_id=post_id)
            first_comments = {}
            second_comments = {}
            for c in comment_query_set:
                # first_class
                if c.root_comment_id is None:
                    c_dict = c.to_dict()
                    first_comments[c.comment_id] = c_dict
                    c_dict['sub_comments'] = []
                # second_class
                else:
                    second_comments[c.comment_id] = c.to_dict()
            for cid in second_comments.keys():
                c_second_dict = second_comments[cid]
                first_comments[c_second_dict['root_comment_id']]['sub_comments'].append(c_second_dict)

            def cmp(element):
                return element['time']

            comments = []
            for cid in first_comments.keys():
                c_dict = first_comments[cid]
                wrap_comment(c_dict, user_id)
                c_dict['sub_comments'].sort(key=cmp, reverse=True)
                for sub_dict in c_dict['sub_comments']:
                    wrap_comment(sub_dict, user_id)
                comments.append(c_dict)
            comments.sort(key=cmp, reverse=True)
            return JsonResponse({'status': 0, 'info': '查询成功', 'data': comments})

    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})


@csrf_exempt
def comment_publish(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        data = json.loads(request.body)
        post_id = data.get('post_id')
        parent_id = data.get('parent_id')
        txt = data.get('txt')
        # check params
        if post_id is None or txt is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        post_id = int(post_id)
        txt = str(txt).strip(' ').strip('\t')
        if not check_txt(txt):
            return JsonResponse({'status': -1, 'info': '内容格式错误'})
        if parent_id is not None:
            parent_id = int(parent_id)
        # db
        with transaction.atomic():
            post_query_set = Post.objects.filter(post_id=post_id)
            if not post_query_set.exists():
                return JsonResponse({'status': -1, 'info': '帖子不存在'})
            root_comment_id = None
            post = Post.objects.get(post_id=post_id)
            if parent_id is not None:
                parent_query_set = Comment.objects.filter(comment_id=parent_id)
                if not parent_query_set.exists():
                    return JsonResponse({'status': -1, 'info': '约束错误'})
                parent_comment = parent_query_set[0]
                if parent_comment.post_id != post_id:
                    return JsonResponse({'status': -1, 'info': '约束错误'})
                root_comment_id = parent_comment.root_comment_id
            if not Permission.objects.filter(block_id=post.block_id).filter(user_id=user_id).filter(
                    permission__gte=1).exists():
                return JsonResponse({'status': -1, 'info': '权限不足'})
            comment = Comment(user_id=user_id, post_id=post_id, parent_id=parent_id, root_comment_id=root_comment_id,
                              txt=txt, time=datetime.now())
            comment.save()
            # send a message
            user_name = UserInfo.objects.get(user_id=user_id).name
            content = f"{user_name}回复了您的帖子[{post.title}]!"
            message = Message(sender_id=user_id,
                              receiver_id=post.user_id,
                              content=content,
                              source_type=1,  # 帖子
                              source_id=post_id,
                              time=datetime.now(),
                              status=0)
            message.save()
            if parent_id is not None:
                content = f"{user_name}在帖子[{post.title}]中回复了您的评论!"
                receiver_id = Comment.objects.get(comment_id=parent_id).user_id
                message = Message(sender_id=user_id,
                                  receiver_id=receiver_id,
                                  content=content,
                                  source_type=1,  # 帖子
                                  source_id=post_id,
                                  time=datetime.now(),
                                  status=0)
                message.save()
            return JsonResponse({'status': 0, 'info': '已发布'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，发布失败'})


@csrf_exempt
def comment_delete(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        data = json.loads(request.body)
        comment_id = data.get('comment_id')
        # check params
        if comment_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        comment_id = int(comment_id)
        # db
        with transaction.atomic():
            comment_query_set = Comment.objects.filter(comment_id=comment_id)
            if not comment_query_set.exists():
                return JsonResponse({'status': -1, 'info': '评论不存在'})
            comment = comment_query_set[0]
            block_id = Post.objects.get(post_id=comment.post_id).block_id
            user_permission_query_set = Permission.objects.filter(user_id=user_id).filter(block_id=block_id)
            if not user_permission_query_set.exists():
                return JsonResponse({'status': -1, 'info': '权限不足'})
            user_permission = user_permission_query_set[0].permission
            if user_permission < 2 or user_id != comment.user_id:
                return JsonResponse({'status': -1, 'info': '权限不足'})
            # delete
            if comment.parent_id is None:
                Comment.objects.filter(root_comment_id=comment.comment_id).delete()
                Comment.objects.filter(comment_id=comment.comment_id).delete()
            else:
                # 并查集
                comm_parents = []  # [[c1_id, c1_parent_id], [c2_id, c2_parent_id]]
                comm_query_set = Comment.objects.filter(root_comment_id=comment.root_comment_id)
                for c in comm_query_set:
                    if c.comment_id == comment.comment_id or c.comment_id == comment.root_comment_id:
                        comm_parents.append([c.comment_id, c.comment_id])
                    else:
                        comm_parents.append([c.comment_id, c.parent_id])

                def query_parent(parents: list, idx: int):
                    if parents[idx][1] != parents[idx][0]:
                        parents[idx][1] = query_parent(parents, parents[idx][1])
                    return parents[idx][1]

                for i in range(len(comm_parents)):
                    comm_parents[i][1] = query_parent(comm_parents, i)
                for i in range(len(comm_parents)):
                    if comm_parents[i][1] == comment.comment_id:
                        Comment.objects.filter(comment_id=comm_parents[i][0]).delete()
            return JsonResponse({'status': 0, 'info': '已删除'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，删除失败'})


@csrf_exempt
def comment_like(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        data = json.loads(request.body)
        comment_id = data.get('comment_id')
        # check params
        if comment_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        comment_id = int(comment_id)
        # db
        with transaction.atomic():
            comment_query_set = Comment.objects.filter(comment_id=comment_id)
            if not comment_query_set.exists():
                return JsonResponse({'status': -1, 'info': '约束错误'})
            now_like = CommentLike.objects.filter(comment_id=comment_id).filter(user_id=user_id)
            if now_like.exists():
                now_like.delete()
                return JsonResponse({'status': 0, 'info': '已取消点赞'})
            else:
                new_like = CommentLike(user_id=user_id, comment_id=comment_id)
                new_like.save()
                return JsonResponse({'status': 0, 'info': '点赞成功'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误'})
