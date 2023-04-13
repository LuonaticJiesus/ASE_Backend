# python manage.py makemigrations, python manage.py migrate
from django.db import models


class UserLogin(models.Model):
    user_id = models.IntegerField()
    token = models.CharField(max_length=200)


class UserInfo(models.Model):
    user_id = models.IntegerField()
    name = models.CharField(max_length=200)
    card_id = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=50)
    point = models.IntegerField()


class Post(models.Model):
    post_id = models.IntegerField()
    title = models.CharField(max_length=200)
    user_id = models.IntegerField()
    txt = models.TextField()
    block_id = models.IntegerField()
    time = models.DateTimeField()


class PostLike(models.Model):
    user_id = models.IntegerField()
    post_id = models.IntegerField()


class PostFavor(models.Model):
    user_id = models.IntegerField()
    post_id = models.IntegerField()


class Block(models.Model):
    block_id = models.IntegerField()
    name = models.CharField(max_length=200)
    time = models.DateTimeField()
    approve_permission = models.IntegerField()


class Comment(models.Model):
    comment_id = models.IntegerField()
    user_id = models.IntegerField()
    post_id = models.IntegerField()
    parent_id = models.IntegerField(null=True)
    txt = models.TextField()
    time = models.DateTimeField()


class CommentLike(models.Model):
    user_id = models.IntegerField()
    comment_id = models.IntegerField()


class Notice(models.Model):
    notice_id = models.IntegerField()
    title = models.CharField(max_length=200)
    txt = models.TextField()
    user_id = models.IntegerField()
    block_id = models.IntegerField()
    time = models.DateTimeField()
    ddl = models.DateTimeField()


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
