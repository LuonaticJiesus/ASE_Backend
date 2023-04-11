from django.db import models


class Comment(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    post_id = models.IntegerField()
    parent_id = models.IntegerField()
    text = models.TextField()
    time = models.DateTimeField()
