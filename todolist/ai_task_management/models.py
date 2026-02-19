from django.db import models

# Create your models here.
from task.models import Task
from task.models import SubTask

# in models.py

class Microtask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="microtasks")
    subtask = models.ForeignKey(SubTask, on_delete=models.CASCADE, related_name="microtasks", null=True, blank=True)
    title = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('subtask', 'title')


    def __str__(self):
        return self.title
