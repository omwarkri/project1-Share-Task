from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import Group, Permission

# Custom User Model
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from cloudinary.models import CloudinaryField
class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = CloudinaryField('image', folder='profile_pictures', blank=True, null=True)
    tasks = models.ManyToManyField('task.Task', related_name='users', blank=True)
    score = models.IntegerField(default=0)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)
    interests = models.JSONField(default=list, blank=True)  # Store user interests as a list
    goals = models.JSONField(default=list, blank=True)  # Store user goals as a list

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
        return self.username or f"User-{self.id}"

    
    def follow(self, user):
        """Follow another user."""
        self.following.add(user)

    def unfollow(self, user):
        """Unfollow another user."""
        self.following.remove(user)

    def is_following(self, user):
        """Check if the current user is following another user."""
        return self.following.filter(id=user.id).exists()

    def get_followers_count(self):
        """Get the number of followers."""
        return self.followers.count()

    def get_following_count(self):
        """Get the number of users the current user is following."""
        return self.following.count()   

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



from django.db import models
from django.utils import timezone

class UserTaskAnalytics(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="task_analytics")
    total_tasks = models.PositiveIntegerField(default=0)
    completed_tasks = models.PositiveIntegerField(default=0)
    overdue_tasks = models.PositiveIntegerField(default=0)
    average_completion_time = models.FloatField(default=0.0)  # In hours
    most_common_category = models.CharField(max_length=100, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analytics for {self.user.username}"



class DailySchedule(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField()
    schedule = models.TextField()
