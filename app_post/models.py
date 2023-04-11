from django.db import models


class Post(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=200)
    text = models.TextField()
    user_id = models.IntegerField()
    block_id = models.IntegerField()
    time = models.DateTimeField()


class UserLike(models.Model):
    user_id = models.IntegerField()
    post_id = models.IntegerField()
