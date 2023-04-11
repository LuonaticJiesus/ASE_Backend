from django.db import models


class Permission(models.Model):
    user_id = models.IntegerField()
    block_id = models.IntegerField()
    permission = models.IntegerField()
