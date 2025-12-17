from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    language = models.CharField(max_length=5, default='en_US')
    theme = models.CharField(max_length=32, default='light')
