from apscheduler.schedulers.background import BackgroundScheduler
from django.utils.timezone import now, timedelta
from django.core.mail import send_mail
from .models import Task
from django.conf import settings

import openai
from chat.models import ChatAIMessage
from task.models import Task
from google import generativeai

# Configure Gemini API
generativeai.configure(api_key="AIzaSyDx3rr0MzUPaumvdII3WIffmtsZqAz7JIs")
model = generativeai.GenerativeModel('gemini-1.5-flash')

def generate_ai_response(task_id):
    # Fetch task details
    task = Task.objects.get(id=task_id) 
    print(task)
    task_title = task.title
    task_description = task.description

    # Fetch recent chat history for context


    # Define prompt with task title & description
    prompt = (
        f"Generate a 5-step procedure for completing the task.\n\n"
        f"Task Title: {task_title}\n"
        f"Task Description: {task_description}\n\n"
        f"Each step must have exactly 16 words:\n"
    )

    response = model.generate_content(prompt)
    ai_response = response.text

    # Save AI response in the database
    ChatAIMessage.objects.create(task_id=task_id, sender="AI", message=ai_response)

    return ai_response

from datetime import timedelta
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings
from .models import Task

def send_task_reminders():
    """Send email reminders for approaching and overdue tasks with AI-generated task procedures."""
    print("running sent email functionality")
    current_time = now()
    approaching_time = current_time + timedelta(days=2)  # Tasks due in the next 2 days

    # Fetch tasks that are due soon and haven't completed all 8 reminders
    tasks = Task.objects.filter(
    due_date__lte=approaching_time,
    due_date__gte=current_time,
    status__in=['pending', 'in_progress']  # Only pending or in-progress tasks
).exclude(status='completed')  # Explicitly exclude completed tasks


    print(tasks,"this is all filter tasks")

    for task in tasks:
        if not task.user:
            continue  # Skip tasks without users

        total_reminders = 8
        if task.reminder_sent >= total_reminders:
            continue  # Skip if all reminders are already sent

        time_span = (task.due_date - current_time).total_seconds()  # Time until due date in seconds
        interval = time_span / total_reminders  # Equal intervals

        next_reminder_time = current_time + timedelta(seconds=interval * task.reminder_sent)
        print(now(),next_reminder_time)
        if now() >= next_reminder_time:
            # Generate AI-guided task procedure
            ai_procedure = generate_ai_response(task.id)
            
            subject = f"Reminder: '{task.title}' is due soon!"
            message = (
                f"Hello,\n\nYour task '{task.title}' is due on {task.due_date.strftime('%Y-%m-%d %H:%M')}.\n\n"
                f"Here’s a simple 5-step guide to complete it:\n\n"
                f"{ai_procedure}\n\n"
                "Don't forget to complete it!\n\nBest regards,\nYour Task Manager"
            )
            print("sending mail")
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=["shantanuchavhan002@gmail.com"],
            )

            # Update reminder count
            task.reminder_sent += 1
            task.save()


def start_scheduler():
    """Start the scheduler when Django starts."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_task_reminders, "interval", minutes=1)  # Runs every 1 minute
    scheduler.start()
