from django.conf import settings
from django.db import models

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
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to="chat_attachments/", blank=True, null=True)  # For file attachments



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
  
