from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import Group, Permission

# Custom User Model
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

from cloudinary.models import CloudinaryField


from django.contrib.auth.models import AbstractUser, Group, Permission
from cloudinary.models import CloudinaryField
from django.db import models

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = CloudinaryField('image', blank=True, null=True)
    tasks = models.ManyToManyField('task.Task', related_name='users', blank=True)
    score = models.IntegerField(default=0)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)
    interests = models.JSONField(default=list, blank=True)
    goals = models.JSONField(default=list, blank=True)
    onboarding_completed = models.BooleanField(default=False)
    pomodoro_count = models.IntegerField(default=0)

    groups = models.ManyToManyField(Group, related_name='customuser_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_set', blank=True)

    def follow(self, user):
        self.following.add(user)

    def unfollow(self, user):
        self.following.remove(user)

    def is_following(self, user):
        return self.following.filter(id=user.id).exists()

    def get_followers_count(self):
        return self.followers.count()

    def get_following_count(self):
        return self.following.count()

    def increment_pomodoro_count(self):
        self.pomodoro_count += 1
        self.save()




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
    icon = CloudinaryField('image', folder='badges', blank=True, null=True)
    min_score = models.IntegerField(default=0)

    def __str__(self):
        return self.name  # ⚠️ if name is None, this causes TypeError


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
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='task_analytics'
    )

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




# models.py

from django.db import models
from datetime import date

class ChallengeTemplate(models.Model):
    CHALLENGE_TYPE_CHOICES = [
        ('pomodoro', 'Pomodoro'),
        ('tasks', 'Tasks'),
        # ('early_bird', 'Early Bird'),
        # ('focus', 'Focus Time'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    challenge_type = models.CharField(max_length=20, choices=CHALLENGE_TYPE_CHOICES)
    target = models.IntegerField()
    xp_reward = models.IntegerField(default=50)

    def __str__(self):
        return self.title

class DailyChallenge(models.Model):
    template = models.ForeignKey(ChallengeTemplate, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)

    def __str__(self):
        return f"{self.template.title} - {self.date}"

class UserChallenge(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    daily_challenge = models.ForeignKey(DailyChallenge, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    progress = models.IntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)  # Optional: track when

    def __str__(self):
        return f"{self.user.username} - {self.daily_challenge.template.title}"
    







from django.db import models
from django.utils import timezone
from .models import CustomUser

class Schedule(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    task = models.CharField(max_length=255, blank=True, null=True)  # Now just a text field
    created_at = models.DateTimeField(default=timezone.now)
    completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.date} {self.start_time}-{self.end_time} ({self.task or 'Free Time'})"
