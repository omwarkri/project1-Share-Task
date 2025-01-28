from django.db import models
from django.contrib.auth import get_user_model  # Dynamically fetches the user model

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
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='tasks',
        blank=True,
        null=True
    )  # Relates the task to a user (creator)

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
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
    shareable = models.BooleanField(default=True)  # Flag to indicate if the task is shareable
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']  # Orders tasks by creation date (newest first)



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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Completion Details for Task {self.task.id}"
