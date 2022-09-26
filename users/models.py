from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    phone_number = models.CharField(max_length=255)
    password2 = models.CharField(max_length=255)



class Properties(models.Model):
    name = models.CharField(max_length=250)
    category = models.CharField(max_length=200)
    address = models.CharField(max_length=500)
    price = models.CharField(max_length=20)
    images = models.ImageField(upload_to='uploads/images', null=False, blank=False)

    def __str__(self):
        return self.name
