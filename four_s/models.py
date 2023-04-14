# python manage.py makemigrations, python manage.py migrate
from django.db import models


class UserLogin(models.Model):
    user_id = models.IntegerField()
    token = models.CharField(max_length=200)


class UserInfo(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    card_id = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=50)
    point = models.IntegerField()


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
    # <0: 无需认证，0:需要路人认证，1:成员认证，2:助理认证，3:管理认证，>=4：超管认证
    approve_permission = models.IntegerField()


class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    post_id = models.IntegerField()
    parent_id = models.IntegerField(null=True)
    txt = models.TextField()
    time = models.DateTimeField()


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


class Permission(models.Model):
    user_id = models.IntegerField()
    block_id = models.IntegerField()
    permission = models.IntegerField()


class Contribution(models.Model):
    user_id = models.IntegerField()
    block_id = models.IntegerField()
    contribution = models.IntegerField()
