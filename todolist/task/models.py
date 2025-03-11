from django.db import models
from django.contrib.auth import get_user_model  # Dynamically fetches the user model
from user.models import CustomUser
from datetime import timedelta
from django.utils import timezone



from django.contrib.auth.models import User
from django.db import models
from user.models import CustomUser

from django.db import models
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

class Team(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    team_lead = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="leading_teams")
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="teams")
    members = models.ManyToManyField(CustomUser, related_name="team_members", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_appreciations(self):
        return self.appreciations.all()

    def is_team_lead(self, user):
        """Check if the user is the team lead."""
        return self.team_lead == user

    def is_member(self, user):
        """Check if the user is a member of the team."""
        return self.members.filter(id=user.id).exists()

    def has_permission(self, user, permission_codename):
        """
        Check if the user has a specific permission in the team.
        """
        if self.is_team_lead(user):
            return True  # Team lead has all permissions

        # Check if the user has the permission via TeamPermission
        return TeamPermission.objects.filter(
            team=self,
            user=user,
            permission__codename=permission_codename
        ).exists()

    def add_permission(self, user, permission_codename):
        """
        Add a permission to a user in the team.
        """
        permission = Permission.objects.get(codename=permission_codename)
        TeamPermission.objects.get_or_create(team=self, user=user, permission=permission)

    def remove_permission(self, user, permission_codename):
        """
        Remove a permission from a user in the team.
        """
        permission = Permission.objects.get(codename=permission_codename)
        TeamPermission.objects.filter(team=self, user=user, permission=permission).delete()
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string


class TeamPermission(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="team_permissions")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="team_permissions")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("team", "user", "permission")  # Ensure no duplicate permissions

    def __str__(self):
        return f"{self.user.username} - {self.permission.codename} in {self.team.name}"

User = get_user_model()

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string

User = get_user_model()

class TeamInvitation(models.Model):
    team = models.ForeignKey("Team", on_delete=models.CASCADE, related_name="invitations")
    email = models.EmailField(unique=True)  # Email of the invited person
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_invitations")
    token = models.CharField(max_length=50, unique=True, default=get_random_string)
    invited_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="received_invites")
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invitation to {self.email} for {self.team.name}"



class TeamScoreboard(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="scoreboard")
    member = models.ForeignKey("user.CustomUser", on_delete=models.CASCADE, related_name="scores")
    score = models.IntegerField(default=0)  # Tracks the member's score

    def update_score(self, points):
        """Updates the score of the member in the scoreboard."""
        self.score += points
        self.save()

    @classmethod
    def update_or_create_score(cls, member, team, points):
    
        """Updates score or creates a new scoreboard entry."""
        scoreboard, created = cls.objects.get_or_create(team=team, member=member)
        scoreboard.update_score(points)

    def __str__(self):
        return f"{self.member.username} - {self.score} points"


from django.db import models
from django.conf import settings

class Appreciation(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="appreciations_given")
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="appreciations_received")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="appreciations")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user', 'team')  # Prevent duplicate appreciations within the same team

    def __str__(self):
        return f"Appreciation from {self.from_user} to {self.to_user} in {self.team}"



class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    user = models.ForeignKey(
        CustomUser,
        related_name='task_user',
        on_delete=models.CASCADE,
        default=1
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')

    allowed_users = models.ManyToManyField(CustomUser, related_name='allowed_tasks', blank=True)
    task_partner = models.ForeignKey(CustomUser, related_name='partnered_tasks', on_delete=models.SET_NULL, null=True, blank=True)
    shareable = models.BooleanField(default=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    dependencies = models.ManyToManyField('self', through='TaskDependency', symmetrical=False, related_name='dependent_tasks')
    procedure = models.TextField(blank=True, null=True)
    reminder_sent = models.BooleanField(default=False)

    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True, related_name="team_tasks")
    escalated_to = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name="escalated_tasks", null=True, blank=True)
    escalation_reason = models.TextField(blank=True, null=True)  # Add this field   
    assigned_to = models.ForeignKey(
        CustomUser,
        related_name='assigned_tasks',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    is_daily = models.BooleanField(default=False)  # New field to mark daily tasks
    vector = models.JSONField(null=True, blank=True)  # Store embedding directly

    def __str__(self):
        return self.title

    def is_overdue(self):
        """Check if the task is overdue, but exclude completed tasks."""
        if self.status == 'completed':
            return False
        return bool(self.due_date and self.due_date < timezone.now())

    def is_approaching_due_date(self):
        """Check if the task is approaching its due date (within 2 days), but exclude completed tasks."""
        if self.status == 'completed':
            return False
        return bool(self.due_date and 0 <= (self.due_date - timezone.now()).days <= 2)
    
    def escalate_task(self, escalated_to):
        """Escalate task to another team member"""
        self.status = "escalated"
        self.escalated_to = escalated_to
        self.save()

    def can_be_completed(self):
        """Check if all dependencies are completed before marking this task as completed."""
        if self.dependencies.exists():
            for dependency in self.dependencies.all():
                if dependency.status != 'completed':
                    return False  # Block completion if any dependency is not completed
        return True

    def save(self, *args, **kwargs):
        previous_status = None
        if self.pk:
            previous_status = Task.objects.get(pk=self.pk).status  # Get previous status before saving

        super().save(*args, **kwargs)  # Save the task

        # If task status changed to completed, update scores
        if previous_status != 'completed' and self.status == 'completed':

            if self.assigned_to and self.team:
                TeamScoreboard.update_or_create_score(self.assigned_to, self.team, points=10)  # Update team score

    def get_all_likes(self):
        """
        Returns all Like objects associated with this task.
        """
        return self.likes.all()
    def get_users_who_liked(self):
        """
        Returns a list of users who liked this task.
        """
        return [like.user for like in self.likes.all()]
    
    
    class Meta:
        ordering = ['-created_at']

    
from django.db import models
from django.conf import settings

class Like(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='likes')
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} liked {self.task.title}"

    class Meta:
        unique_together = ('user', 'task')  # Ensure a user can like a task only once






def update_team_member_score(member, team, points=10):
    """Increase the score of a team member when a task is completed."""
    if member and team:
        scoreboard, created = TeamScoreboard.objects.get_or_create(member=member, team=team)
        scoreboard.score += points
        scoreboard.save()






class PartnerFeedback(models.Model):
    task = models.ForeignKey(
        Task, 
        on_delete=models.CASCADE, 
        related_name='partner_feedbacks'  # Allows accessing feedbacks from a task
    )
    partner = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='partner_feedbacks'  # Allows accessing feedbacks for a partner
    )
    rating = models.IntegerField(
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],  # Rating from 1 to 5
        default=5
    )
    comment = models.TextField(blank=True, null=True)  # Optional comment
    created_at = models.DateTimeField(default=timezone.now)  # Timestamp for when the feedback was created

    def __str__(self):
        return f"Feedback for {self.partner.username} on Task {self.task.id}"

    class Meta:
        ordering = ['-created_at']  # Orders feedbacks by creation date (newest first)

    class Meta:
        ordering = ['-created_at']  # Orders feedbacks by creation date (newest first)

class TaskCompletionDetails(models.Model):
    task = models.OneToOneField(
        Task, 
        on_delete=models.CASCADE, 
        related_name='completion_details'
    )  # Links completion details to a single task
    completion_details = models.TextField()
    completion_files = models.JSONField(default=list)  # Stores file URLs as a JSON list
    uploaded_file = models.FileField(
        upload_to='completion_files/', 
        blank=True, 
        null=True
    )  # For videos or general files
    uploaded_image = models.ImageField(
        upload_to='completion_images/', 
        blank=True, 
        null=True
    )  # For images
    partner_feedback = models.OneToOneField(
        PartnerFeedback, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='completion_details'
    )  # Links feedback to completion details
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Completion Details for Task {self.task.id}"

    def has_details(self):
        """Check if completion details are provided."""
        return bool(self.completion_details)

    def has_files(self):
        """Check if completion files are provided."""
        return bool(self.completion_files)

    def has_uploaded_file(self):
        """Check if an uploaded file (e.g., video) is provided."""
        return bool(self.uploaded_file)

    def has_uploaded_image(self):
        """Check if an uploaded image is provided."""
        return bool(self.uploaded_image)

    def has_partner_feedback(self):
        """Check if partner feedback is provided."""
        return bool(self.partner_feedback)



# models.py
from django.db import models
from django.utils import timezone
from .models import Task, CustomUser  # Import your existing models

class Comment(models.Model):
    task = models.ForeignKey(
        Task, 
        on_delete=models.CASCADE, 
        related_name='comments'  # Allows accessing comments from a task
    )
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='task_comments'  # Allows accessing comments by a user
    )
    text = models.TextField()  # The comment content
    created_at = models.DateTimeField(default=timezone.now)  # Timestamp for when the comment was created

    def __str__(self):
        return f"{self.user.username}: {self.text[:50]}"  # Short preview of the comment

    class Meta:
        ordering = ['created_at']  # Orders comments by creation date (oldest first)



class SubTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    


class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('subtask_added', 'Subtask Added'),
        ('subtask_completed', 'Subtask Completed'),
        ('comment_added', 'Comment Added'),
        ('user_added', 'User Added'),
        ('user_removed', 'User Removed'),
    ]

    task = models.ForeignKey(Task, related_name='activity_logs', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    details = models.TextField(blank=True, null=True)  # Additional details about the action
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} {self.action} on {self.task.title} at {self.timestamp}"
    



class TaskDependency(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_dependencies')
    dependent_on = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='dependent_task_dependencies')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.task.title} depends on {self.dependent_on.title}"

    class Meta:
        unique_together = ('task', 'dependent_on')  # Prevents duplicate dependencies





