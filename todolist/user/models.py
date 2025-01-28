from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    # Adding related_name to avoid clashes with auth.User
    groups = models.ManyToManyField(
        'auth.Group', 
        related_name='customuser_set',  # Change this related name to avoid clash
        blank=True,
        null=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', 
        related_name='customuser_set',  # Change this related name to avoid clash
        blank=True,
        null=True
    )
    
    def __str__(self):
        return self.username
