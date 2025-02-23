from django_cron import CronJobBase, Schedule
from django.utils import timezone
from django.core.mail import send_mail
from .models import Task

class SendTaskReminders(CronJobBase):
    RUN_EVERY_MINS = 1  # Run every minute

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'tasks.send_task_reminders'  # Unique identifier for the cron job

    def do(self):
        now = timezone.now()

        # Check for overdue tasks
        overdue_tasks = Task.objects.filter(due_date__lte=now, reminder_sent=False)
        for task in overdue_tasks:
            try:
                send_mail(
                    f'Reminder: {task.title} is overdue!',
                    f'Task: {task.title}\nDescription: {task.description}\nDue Date: {task.due_date}',
                    'from@example.com',  # Replace with your email
                    [task.user.email],  # Send to the task owner
                    fail_silently=False,
                )
                task.reminder_sent = True
                task.save()
            except Exception as e:
                print(f"Failed to send email for task {task.id}: {e}")

        # Check for tasks due soon (within 2 days) but not overdue
        approaching_tasks = Task.objects.filter(
            due_date__gt=now,  # Exclude overdue tasks
            due_date__lte=now + timezone.timedelta(days=2),  # Due within 2 days
            reminder_sent=False,
        )
        for task in approaching_tasks:
            try:
                send_mail(
                    f'Reminder: {task.title} is due soon!',
                    f'Task: {task.title}\nDescription: {task.description}\nDue Date: {task.due_date}',
                    'from@example.com',  # Replace with your email
                    [task.user.email],  # Send to the task owner
                    fail_silently=False,
                )
                task.reminder_sent = True
                task.save()
            except Exception as e:
                print(f"Failed to send email for task {task.id}: {e}")