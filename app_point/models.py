from django.db import models


class Contribution(models.Model):
    user_id = models.IntegerField()
    post_id = models.IntegerField()
    contribution = models.IntegerField()
