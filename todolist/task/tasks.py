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




from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.utils.timezone import now, timedelta
from django.core.mail import send_mail
from django.conf import settings
from .models import Task
from chat.models import ChatAIMessage
import openai
from google import generativeai

# Configure Gemini API
generativeai.configure(api_key="AIzaSyDx3rr0MzUPaumvdII3WIffmtsZqAz7JIs")
model = generativeai.GenerativeModel('gemini-1.5-flash')

def generate_daily_schedule(user, tasks):
    """Generate an optimized daily task schedule using AI."""

    if not tasks:
        return "No tasks scheduled for today."

    task_list = "\n".join([
        f"- {task.title} (Due: {task.due_date.strftime('%I:%M %p') if task.due_date else 'No due time'})"
        for task in tasks
    ])

    prompt = (
        f"You are an AI task manager. Arrange the user's daily tasks in an optimized schedule.\n\n"
        f"Today's Tasks:\n{task_list}\n\n"
        f"Create a structured, step-by-step **hourly** schedule for the day.\n"
        f"Use a timeline format from morning to evening.\n"
        f"Ensure high-priority tasks come first, breaks are included, and tasks are realistically scheduled."
    )

    response = model.generate_content(prompt)
    ai_schedule = response.text

    return ai_schedule



 



from django.core.mail import send_mail
from django.conf import settings
import re
from user.models import CustomUser

def convert_markdown_to_html(text):
    """Convert Markdown-like formatting to HTML for email compatibility."""
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)  # Convert **bold** to <b>bold</b>
    text = re.sub(r'^- (.*?)$', r'<li>\1</li>', text, flags=re.MULTILINE)  # Convert - item to <li>item</li>
    
    # Wrap bullet points in <ul> if any <li> exists
    if "<li>" in text:
        text = "<ul>" + text + "</ul>"

    return text.replace("\n", "<br>")  # Replace new lines with <br> for email formatting

def send_daily_task_schedule():
    """Send AI-optimized daily task schedule to users at 9 AM."""
    print("Generating and sending daily task schedule at 9 AM...")
    current_time = now()
    users = Task.objects.values_list("user", flat=True).distinct()  # Get unique users with tasks

    for user in users:
        tasks = Task.objects.filter(
            user=user,
            due_date__date=current_time.date(),
            status__in=['pending', 'in_progress']
        ).exclude(status='completed')

        if not tasks.exists():
            continue  # Skip users without tasks
        # Generate AI-optimized schedule
        ai_schedule = generate_daily_schedule(user, tasks)
        ai_schedule_html = convert_markdown_to_html(ai_schedule)  # Convert to HTML format

        # Email content
        user = CustomUser.objects.get(id=user)

        subject = f"📅 Your AI-Powered Task Schedule for Today"
        message = f"""
        <html>
            <body>
                <p>Hello {user.username},</p>
                <p>Here is your <b>AI-optimized task schedule</b> for today:</p>
                {ai_schedule_html}  <!-- Inject formatted schedule -->
                <p>✅ Prioritize high-importance tasks in the morning.<br>
                ☕ Take short breaks to stay focused.<br>
                📌 Adjust the schedule as needed.</p>
                <p>Stay productive! 🚀</p>
                <p><b>Best Regards,</b><br>Your Task Manager</p>
            </body>
        </html>
        """

        send_mail(
            subject=subject,
            message="This is a fallback plain-text version of the email.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=["shantanuchavhan002@gmail.com"],  # Send to each user 
            html_message=message  # Send HTML-formatted email
        )

    print("✅ Daily task schedules sent successfully!")



from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

def start_scheduler():
    """Start the scheduler when Django starts."""
    scheduler = BackgroundScheduler()

    # Run `send_task_reminders` every minute
    scheduler.add_job(send_task_reminders, IntervalTrigger(minutes=20))

    # Run `send_daily_task_schedule` every day at 9 AM
    scheduler.add_job(send_daily_task_schedule, IntervalTrigger(minutes=1))

    scheduler.start()
