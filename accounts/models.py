from django.db import models
from django.contrib.auth.models import User


class Token(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='auth_token')
    key = models.CharField(max_length=64, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user.email}"
