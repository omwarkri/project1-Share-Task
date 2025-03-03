from apscheduler.schedulers.background import BackgroundScheduler
from django.utils.timezone import now, timedelta
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Task
from chat.models import ChatAIMessage
from user.models import CustomUser
import openai
from google import generativeai
import re

# Configure Gemini API
generativeai.configure(api_key="AIzaSyDx3rr0MzUPaumvdII3WIffmtsZqAz7JIs")
model = generativeai.GenerativeModel('gemini-1.5-flash')
from django.utils import timezone
from django.db.models import Q

def update_daily_tasks():
    """Reset daily tasks' status to 'pending' if they are completed or overdue."""
    now = timezone.now()
    Task.objects.filter(is_daily=True).update(status='pending', reminder_sent=False)


# Reusable Email Template Function
def generate_html_email(title, content, button_text=None, button_link=None, home_page_link=None):
    """Generate a styled HTML email template with an optional home page button."""
    home_page_button = ""
    if home_page_link:
        home_page_button = f'<a href="{home_page_link}" class="btn" style="background-color: #3498db;">Go to Home Page</a>'

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
                background-color: #f9f9f9;
            }}
            .email-container {{
                max-width: 600px;
                margin: 20px auto;
                padding: 20px;
                background-color: #fff;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            .email-header {{
                text-align: center;
                padding-bottom: 20px;
                border-bottom: 1px solid #ddd;
            }}
            .email-header h1 {{
                margin: 0;
                font-size: 24px;
                color: #1abc9c;
            }}
            .email-body {{
                padding: 20px 0;
            }}
            .email-body p {{
                margin: 10px 0;
            }}
            .email-footer {{
                text-align: center;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                font-size: 14px;
                color: #777;
            }}
            .btn {{
                display: inline-block;
                padding: 10px 20px;
                margin: 10px 0;
                background-color: #1abc9c;
                color: #fff;
                text-decoration: none;
                border-radius: 5px;
                text-align: center;
            }}
            .btn:hover {{
                opacity: 0.9;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="email-header">
                <h1>{title}</h1>
            </div>
            <div class="email-body">
                {content}
                {f'<a href="{button_link}" class="btn">{button_text}</a>' if button_text and button_link else ''}
                {home_page_button}
            </div>
            <div class="email-footer">
                <p>This is an automated message. Please do not reply.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

# AI Response Generation
def generate_ai_response(task_id):
    """Generate AI-guided task procedure."""
    task = Task.objects.get(id=task_id)
    task_title = task.title
    task_description = task.description

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

# Task Reminders
def send_task_reminders():
    """Send email reminders for approaching and overdue tasks with AI-generated task procedures."""
    print("Running sent email functionality")
    current_time = now()
    approaching_time = current_time + timedelta(days=2)  # Tasks due in the next 2 days

    # Fetch tasks that are due soon and haven't completed all 8 reminders
    tasks = Task.objects.filter(
        due_date__lte=approaching_time,
        due_date__gte=current_time,
        status__in=['pending', 'in_progress']  # Only pending or in-progress tasks
    ).exclude(status='completed')  # Explicitly exclude completed tasks

    print(tasks, "This is all filtered tasks")

    for task in tasks:
        if not task.user:
            continue  # Skip tasks without users

        total_reminders = 8
        if task.reminder_sent >= total_reminders:
            continue  # Skip if all reminders are already sent

        time_span = (task.due_date - current_time).total_seconds()  # Time until due date in seconds
        interval = time_span / total_reminders  # Equal intervals

        next_reminder_time = current_time + timedelta(seconds=interval * task.reminder_sent)
        print(now(), next_reminder_time)
        if now() >= next_reminder_time:
            # Generate AI-guided task procedure
            ai_procedure = generate_ai_response(task.id)

            # Generate task detail link
            task_detail_link = f"{settings.BASE_URL}/task/{task.id}/"  # Task detail URL

            # Generate HTML email content
            title = f"Reminder: '{task.title}' is due soon!"
            content = (
                f"<p>Hello,</p>"
                f"<p>Your task <strong>{task.title}</strong> is due on <strong>{task.due_date.strftime('%Y-%m-%d %H:%M')}</strong>.</p>"
                f"<p>Here’s a simple 5-step guide to complete it:</p>"
                f"<p>{ai_procedure}</p>"
                f"<p>Don't forget to complete it!</p>"
            )
            home_page_link = f"{settings.BASE_URL}"  # Home page URL
            html_content = generate_html_email(
                title,
                content,
                button_text="View Task Details",  # Button text
                button_link=task_detail_link,  # Task detail link
                home_page_link=home_page_link+"/task/"  # Home page link
            )

            # Send the email
            print("Sending mail")
            send_mail(
                subject=title,
                message=strip_tags(content),  # Plain text fallback
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[task.user.email],
                html_message=html_content,  # HTML version
            )

            # Update reminder count
            task.reminder_sent += 1
            task.save()
# Daily Task Schedule
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

        # Generate HTML email content
        user = CustomUser.objects.get(id=user)
        title = "📅 Your AI-Powered Task Schedule for Today"
        content = (
            f"<p>Hello {user.username},</p>"
            f"<p>Here is your <strong>AI-optimized task schedule</strong> for today:</p>"
            f"{ai_schedule_html}"
            f"<p>✅ Prioritize high-importance tasks in the morning.<br>"
            f"☕ Take short breaks to stay focused.<br>"
            f"📌 Adjust the schedule as needed.</p>"
            f"<p>Stay productive! 🚀</p>"
        )
        home_page_link = f"{settings.BASE_URL}/task/"  # Add your home page URL
        html_content = generate_html_email(title, content, home_page_link=home_page_link)

        # Send the email
        send_mail(
            subject=title,
            message=strip_tags(content),  # Plain text fallback
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=["shantanuchavhan002@gmail.com"],  # Send to each user
            html_message=html_content,  # HTML version
        )

    print("✅ Daily task schedules sent successfully!")


from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

# Scheduler Setup
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

def start_scheduler():
    """Start the scheduler when Django starts."""
    scheduler = BackgroundScheduler()

    # Run `send_task_reminders` every 20 minutes
    scheduler.add_job(send_task_reminders, IntervalTrigger(minutes=20))

    # Run `send_daily_task_schedule` every day at 9 AM
    scheduler.add_job(send_daily_task_schedule, CronTrigger(hour=9, minute=0))

    # Run `update_daily_tasks` every day at midnight
    scheduler.add_job(update_daily_tasks, CronTrigger(hour=0, minute=0))

    scheduler.start()
