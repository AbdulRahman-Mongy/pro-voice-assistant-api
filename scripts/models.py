from django.db import models
from users.models import CustomUser


class BaseScript(models.Model):
    name = models.CharField(max_length=250, unique=True)
    file = models.FileField(upload_to='files/')
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_reviewed = models.BooleanField(null=True)

    state = models.CharField(
        max_length=100,
        choices=[
            ('public', 'Public'),
            ('private', 'Private'),
        ],
        default='private',
    )
    description = models.TextField(null=True)

    def __str__(self):
        return self.name
