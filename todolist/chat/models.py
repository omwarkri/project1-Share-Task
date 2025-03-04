from django.conf import settings
from django.db import models
from task.models import Task

class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='received_messages'
    )
    task = models.ForeignKey(  # Added task field
        Task,  # Assuming Task is in the same app; otherwise, use 'app_name.Task'
        on_delete=models.CASCADE, 
        related_name='messages', 
        null=True, 
        blank=True
    )
    content = models.TextField()  # Message content
    timestamp = models.DateTimeField(auto_now_add=True)  # Timestamp of message creation
    attachment = models.FileField(
        upload_to="chat_attachments/",  # Directory to store attachments
        blank=True, 
        null=True
    )

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']  # Order messages by timestamp (newest first)

from django.db import models

class ChatAIMessage(models.Model):
    task_id = models.IntegerField()  # Task related to this chat
    sender = models.CharField(max_length=50, choices=[("User", "User"), ("AI", "AI")])
    message = models.TextField()  # Message content from user or AI
    timestamp = models.DateTimeField(auto_now_add=True)  # Time when the message was created

    class Meta:
        ordering = ['timestamp']  # Messages ordered by timestamp

    def __str__(self):
        return f"{self.sender}: {self.message[:50]}... ({self.timestamp})"
    




from django.db import models
from django.utils import timezone
from user.models import CustomUser  # Import your user model
from task.models import Team  # Import the Team model

class TeamChat(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="team_chats")
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="team_sent_messages")
    message = models.TextField()
    attachment = models.FileField(
        upload_to="chat_attachments/",  # Directory to store attachments
        blank=True, 
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.message[:30]}"

  
