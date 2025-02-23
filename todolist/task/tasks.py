from apscheduler.schedulers.background import BackgroundScheduler
from django.utils.timezone import now, timedelta
from django.core.mail import send_mail
from .models import Task
from django.conf import settings

def send_task_reminders():
    """Send email reminders for approaching and overdue tasks."""
    
    current_time = now()
    approaching_time = current_time + timedelta(days=2)  # Tasks due in the next 2 days

    # Fetch tasks that are overdue or approaching their due date but haven't been notified yet
    tasks = Task.objects.filter(
        due_date__lte=approaching_time, 
        due_date__gte=current_time,  # Ensure we only get upcoming tasks, not past ones
       
        reminder_sent=False
    )
    print(f"Tasks found: {tasks}")

    for task in tasks:
        subject = f"Reminder: {task.title} is due soon!"
        message = f"Your task '{task.title}' is due on {task.due_date.strftime('%Y-%m-%d %H:%M')}.\n\nDon't forget to complete it!"
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER  ,
            recipient_list=["shantanuchavhan002@gmail.com"],
        )

        task.reminder_sent = True  # Mark as notified
        task.save()

def start_scheduler():
    """Start the scheduler when Django starts."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_task_reminders, "interval", minutes=20)  # Runs every 1 minute
    scheduler.start()
