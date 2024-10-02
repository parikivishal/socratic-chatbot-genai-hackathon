from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# Create your models here.
class UserRegistration(models.Model):
    email = models.CharField(max_length=200, unique=True)
    username = models.CharField(max_length=200, default='blume')
    password = models.CharField(max_length=200)