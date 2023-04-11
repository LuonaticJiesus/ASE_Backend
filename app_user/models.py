from django.db import models


class UserLogin(models.Model):
    user_id = models.IntegerField()
    token = models.CharField(max_length=200)


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    point = models.IntegerField()
