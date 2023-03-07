from django.db import models
from users.models import CustomUser


class BaseScript(models.Model):
    name = models.CharField(max_length=250)
    file = models.FileField(upload_to='files/', null=True)
    dependency = models.FileField(upload_to='files/', null=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_reviewed = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class BaseCommand(models.Model):

    name = models.CharField(max_length=250)
    script = models.ForeignKey(BaseScript, on_delete=models.CASCADE)
    description = models.TextField(null=True)
    parameters = models.TextField(null=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_reviewed = models.BooleanField(default=False)
    state = models.CharField(
        max_length=100,
        choices=[
            ('public', 'Public'),
            ('private', 'Private'),
        ],
        default='private',
    )
    icon = models.ImageField(upload_to='images/', default='images/default_icon.jpg')

    def __str__(self):
        return self.name
