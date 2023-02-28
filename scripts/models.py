from django.db import models
from users.models import CustomUser
from django.conf import settings


class BaseScript(models.Model):
    name = models.CharField(max_length=250)
    file = models.FileField(upload_to='files/', null=True)
    dependency = models.FileField(upload_to='files/', null=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_reviewed = models.BooleanField(default=False)

    def __str__(self):
        return self.name
