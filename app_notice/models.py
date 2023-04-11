from django.db import models


class Notice(models.Model):
    id = models.BigIntegerField(primary_key=True)
    title = models.CharField(max_length=200)
    text = models.TextField()
    user_id = models.IntegerField()
    post_id = models.IntegerField()
    time = models.DateTimeField()
    ddl = models.DateTimeField()
    state = models.IntegerField()
