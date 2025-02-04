from django.db import models
from django.contrib.auth import get_user_model  # Dynamically fetches the user model
from user.models import CustomUser
from django.utils import timezone


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
    category = models.CharField(max_length=100,blank=True, null=True)
    priority = models.CharField(
        max_length=10, 
        choices=PRIORITY_CHOICES, 
        default='medium'
    )
    status = models.CharField(
        max_length=15, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    allowed_users = models.ManyToManyField(
        CustomUser, 
        related_name='allowed_tasks', 
        blank=True
    )  # Users allowed to access the task
    task_partner = models.ForeignKey(
        CustomUser, 
        related_name='partnered_tasks', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )  # User who partnered to complete the task
    shareable = models.BooleanField(default=True)  # Flag to indicate if the task is shareable
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']  # Orders tasks by creation date (newest first)

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
    


