import requests
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    name = models.CharField(blank=True, max_length=255)
    port = models.IntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        last_user = CustomUser.objects.last()
        if last_user:
            if last_user.port:
                self.port = last_user.port + 1
            else:
                self.port = 8100
        else:
            self.port = 8100

        # send to nlp manger to create the user
        requests.post('http://localhost:8002/user/', json={
            'user_id': self.id,
        })

        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
