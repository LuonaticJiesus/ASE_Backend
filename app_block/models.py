from django.db import models


class Block(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    teachers = models.JSONField(default=list)


class BlockUser(models.Model):
    block_id = models.IntegerField()
    user_id = models.IntegerField()
