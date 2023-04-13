# Create your models here.
from django.db import models

# class Blog(models.Model):
#     title = models.CharField(max_length=200)
#     content = models.TextField()
#     pub_date = models.DateTimeField(auto_now_add=True)


class user_login(models.Model):
    user_id = models.IntegerField()
    token = models.CharField(max_length=200)

class user_info(models.Model):
    user_id = models.IntegerField()
    name = models.CharField(max_length=200)
    point = models.IntegerField()
    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=50)

class post(models.Model):
    post_id = models.IntegerField()
    title = models.CharField(max_length=200)
    user_id = models.IntegerField()
    txt = models.TextField()
    block_id = models.IntegerField()
    time = models.DateTimeField()

class block(models.Model):
    block_id = models.IntegerField()
    name = models.CharField(max_length=200)
    time = models.DateTimeField()
    approve_permission = models.IntegerField()

class comment(models.Model):
    comment_id = models.IntegerField()
    user_id = models.IntegerField()
    post_id = models.IntegerField()
    parent_id = models.IntegerField()
    txt = models.TextField()
    time = models.DateTimeField()

class notion(models.Model):
    inform_id = models.IntegerField()
    title = models.CharField(max_length=200)
    txt = models.TextField()
    user_id = models.IntegerField()
    block_id = models.IntegerField()
    time = models.DateTimeField()
    ddl = models.DateTimeField()

class notion_confirm(models.Model):
    user_id = models.IntegerField()
    inform_id = models.IntegerField()

class comment_like(models.Model):
    user_id = models.IntegerField()
    comment_id = models.IntegerField()

class post_like(models.Model):
    user_id = models.IntegerField()
    post_id = models.IntegerField()

class permission(models.Model):
    user_id = models.IntegerField()
    course_id = models.IntegerField()
    permission = models.IntegerField()

class contribution(models.Model):
    user_id = models.IntegerField()
    course_id = models.IntegerField()
    contribution = models.IntegerField()

class favor(models.Model):
    user_id = models.IntegerField()
    post_id = models.IntegerField()

