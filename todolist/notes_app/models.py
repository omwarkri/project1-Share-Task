from django.db import models
from user.models import CustomUser
from task.models import Task
from django.utils import timezone


class TaskNotes(models.Model):
    task = models.ForeignKey(Task, related_name='task_notes', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    note_text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Note for {self.task.title} by {self.user.username if self.user else 'N/A'}"