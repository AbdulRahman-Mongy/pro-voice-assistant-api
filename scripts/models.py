from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models

from users.models import CustomUser


class BaseScript(models.Model):
    name = models.TextField(default='_New')
    file = models.FileField(upload_to='files/', null=True)
    dependency = models.FileField(upload_to='files/', null=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    type = models.CharField(default='py', max_length=100)

    def __str__(self):
        return self.file.name


class BaseCommand(models.Model):
    name = models.CharField(max_length=250)
    script = models.ForeignKey(BaseScript, on_delete=models.CASCADE)
    description = models.TextField(null=True)
    executable_url = models.URLField(null=True, max_length=1024)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    state = models.CharField(
        max_length=100,
        choices=[
            ('public', 'Public'),
            ('private', 'Private'),
        ],
        default='private',
    )
    icon = models.ImageField(upload_to='images/', default='images/default_icon.jpg')
    used_by = models.ManyToManyField(CustomUser, related_name='used_by')

    def __str__(self):
        return self.name


class Patterns(models.Model):
    syntax = models.TextField()
    command = models.ForeignKey(BaseCommand, on_delete=models.CASCADE)


class Parameters(models.Model):
    order = models.IntegerField()
    name = models.CharField(max_length=250)
    type = models.CharField(max_length=250)
    command = models.ForeignKey(BaseCommand, on_delete=models.CASCADE)


class CommandApproveRequest(models.Model):
    """
    This model is used to store the requests for approving a command.
    when a user set the visibility of a command to public, the command is saved as private,
    and a request is created for the admin to approve the command to be public.
    when the admin approve the command, the command is set to public.
    if the admin reject the command, the command is set to private.
    if the status was updated to pending again, the command is set to private.
    """
    command = models.ForeignKey(BaseCommand, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=100,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='pending',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.status == 'approved':
            self.command.state = 'public'
            self.command.save()

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'notification_{self.command.owner.id}',
                {'type': 'send_notification',
                 'message': {
                     "type": "approved",
                     "id": self.command.id,
                     "name": "",
                     "message": "",
                     "status": ""}
                 }
            )
        else:
            self.command.state = 'private'
            self.command.save()

        super().save(*args, **kwargs)
