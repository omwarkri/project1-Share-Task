from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import Group, Permission

# Custom User Model
class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    tasks = models.ManyToManyField('task.Task', related_name='users', blank=True)
    score = models.IntegerField(default=0)
    

    # Custom related names to avoid conflicts
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # Custom related name
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',  # Custom related name
        blank=True
    )

    def __str__(self):
        return self.username

# Activity Log Model (for tracking user activities)
class UserActivity(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    activity_date = models.DateField(auto_now_add=True)
    activity_type = models.CharField(max_length=50, default='Task Completed')

    class Meta:
        unique_together = ('user', 'activity_date')

    def __str__(self):
        return f"{self.user.username} - {self.activity_date} - {self.activity_type}"

# Badge Model
class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='badge_icons/', blank=True, null=True)
    min_score = models.IntegerField(default=0)

    def __str__(self):
        return self.name

# UserBadge Model for linking Users and Badges (Through Model for Many-to-Many)
class UserBadge(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"

