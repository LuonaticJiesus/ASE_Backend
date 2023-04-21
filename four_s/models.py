# python manage.py makemigrations, python manage.py migrate
# python manage.py createsuperuser
from django.db import models


class UserInfo(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    card_id = models.CharField(max_length=20)
    phone = models.CharField(max_length=20, null=True)
    email = models.CharField(max_length=50, null=True)
    avatar = models.CharField(max_length=200)
    point = models.IntegerField()

    def to_dict(self):
        ret = {
            'user_id': self.user_id,
            'name': self.name,
            'card_id': self.card_id,
            'point': self.point,
            'avatar': self.avatar,
        }
        if self.phone is not None:
            ret['phone'] = self.phone
        if self.email is not None:
            ret['email'] = self.email
        return ret


class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    user_id = models.IntegerField()
    txt = models.TextField()
    block_id = models.IntegerField()
    time = models.DateTimeField()

    def to_dict(self):
        return {
            'post_id': self.post_id,
            'title': self.title,
            'user_id': self.user_id,
            'txt': self.txt,
            'block_id': self.block_id,
            'time': self.time
        }


class PostLike(models.Model):
    user_id = models.IntegerField()
    post_id = models.IntegerField()


class PostFavor(models.Model):
    user_id = models.IntegerField()
    post_id = models.IntegerField()


class PostChosen(models.Model):
    post_id = models.IntegerField()
    block_id = models.IntegerField()


class Block(models.Model):
    block_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    time = models.DateTimeField()
    avatar = models.CharField(max_length=200)
    info = models.CharField(max_length=200)
    # <0: 无需认证，0:需要路人认证，1:成员认证，2:助理认证，3:管理认证，>=4：超管认证
    approve_permission = models.IntegerField()

    def to_dict(self):
        ret = {
            'block_id': self.block_id,
            'name': self.name,
            'avatar': self.avatar,
            'info': self.info,
            'time': self.time.strftime('%Y-%m-%d %H:%I:%S'),
            'approve_permission': self.approve_permission
        }
        return ret


class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    post_id = models.IntegerField()
    parent_id = models.IntegerField(null=True)
    txt = models.TextField()
    time = models.DateTimeField()

    def to_dict(self):
        ret = {
            'comment_id': self.comment_id,
            'user_id': self.user_id,
            'post_id': self.post_id,
            'txt': self.txt,
            'time': self.time.strftime('%Y-%m-%d %H:%I:%S')
        }
        if self.parent_id is not None:
            ret['parent_id'] = self.parent_id
        return ret


class CommentLike(models.Model):
    user_id = models.IntegerField()
    comment_id = models.IntegerField()


class Notice(models.Model):
    notice_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    txt = models.TextField()
    user_id = models.IntegerField()
    block_id = models.IntegerField()
    time = models.DateTimeField()
    ddl = models.DateTimeField()

    def to_dict(self):
        return {
            'notice_id': self.notice_id,
            'title': self.title,
            'txt': self.txt,
            'user_id': self.user_id,
            'block_id': self.block_id,
            'time': self.time.strftime('%Y-%m-%d %H:%I:%S'),
            'ddl': self.ddl.strftime('%Y-%m-%d %H:%I:%S')
        }


class NoticeConfirm(models.Model):
    user_id = models.IntegerField()
    notice_id = models.IntegerField()


class Message(models.Model):
    message_id = models.AutoField(primary_key=True)
    sender_id = models.IntegerField()
    receiver_id = models.IntegerField()
    content = models.CharField(max_length=200)
    source_type = models.IntegerField()  # (1: Post, 2: Comment)
    source_id = models.IntegerField()
    time = models.DateTimeField()
    status = models.IntegerField()  # (0:未查看, 1:已查看)

    def to_dict(self):
        return {
            'message_id': self.message_id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'content': self.content,
            'source_type': self.source_type,
            'source_id': self.source_id,
            'status': self.status,
            'time': self.time.strftime('%Y-%m-%d %H:%I:%S')
        }


class Permission(models.Model):
    user_id = models.IntegerField()
    block_id = models.IntegerField()
    permission = models.IntegerField()


class Contribution(models.Model):
    user_id = models.IntegerField()
    block_id = models.IntegerField()
    contribution = models.IntegerField()
