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
generativeai.configure(api_key="AIzaSyAlvIwjLl9S5tr3IQa3RtZf0Li7i8wXHXg")
model = generativeai.GenerativeModel('gemini-2.5-flash')
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

def generate_ai_response(task_id):
    """Generate AI-guided task procedure with a sense of urgency."""
    task = Task.objects.get(id=task_id)
    task_title = task.title
    task_description = task.description

    prompt = (
        f"Generate a 5-step procedure for completing the task. Each step must have exactly 16 words.\n\n"
        f"Task Title: {task_title}\n"
        f"Task Description: {task_description}\n\n"
        f"Make the steps actionable and include motivational language to create a sense of urgency.\n"
        f"Example:\n"
        f"1. Start immediately by gathering all necessary materials to avoid last-minute stress.\n"
        f"2. Break the task into smaller parts and tackle the first part right now.\n"
        f"3. Set a timer for 25 minutes and focus solely on the task without distractions.\n"
        f"4. Review your progress and adjust your approach to stay on track today.\n"
        f"5. Complete the task ahead of time to reduce stress and feel accomplished.\n\n"
        f"Now generate the steps for this task:"
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

            # Render HTML email template
            html_content = render_to_string(
                'emails/task_reminder.html',  # Path to your HTML template
                {
                    'task': task,
                    'ai_procedure': ai_procedure,
                    'task_detail_link': task_detail_link,
                    'home_page_link': f"{settings.BASE_URL}",
                }
            )

            # Plain text fallback
            plain_text_content = strip_tags(html_content)

            # Send the email
            print("Sending mail")
            send_mail(
                subject=f"Reminder: '{task.title}' is due soon!",
                message=plain_text_content,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[task.user.email],
                html_message=html_content,
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
        f"You are an AI task manager. The user has the following tasks today:\n\n"
        f"{task_list}\n\n"
        f"Generate an optimized, realistic schedule using this exact format:\n"
        f"06:00 AM - 07:00 AM: [Task name]\n"
        f"07:00 AM - 07:30 AM: [Next task or break]\n\n"
        f"Use time intervals from morning to evening. Prioritize tasks with earlier due times, group similar tasks, and include breaks. "
        f"Do NOT use markdown tables. Do NOT format with bullet points or bold text. Make it human-friendly and fluid."
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
            assigned_to =user,
            due_date__date=current_time.date(),
            status__in=['pending', 'in_progress']
        ).exclude(status='completed')

        if not tasks.exists():
            continue  # Skip users without tasks

        # Generate AI-optimized schedule
        ai_schedule = generate_daily_schedule(user, tasks)
        ai_schedule_html = convert_markdown_to_html(ai_schedule)  # Convert to HTML format

        # Render HTML email template
        user = CustomUser.objects.get(id=user)
        html_content = render_to_string(
            'emails/daily_task_schedule.html',  # Path to your HTML template
            {
                'user': user,
                'ai_schedule': ai_schedule_html,
                'home_page_link': f"{settings.BASE_URL}/task/",
            }
        )

        # Plain text fallback
        plain_text_content = strip_tags(html_content)

        # Send the email
        send_mail(
            subject="📅 Your AI-Powered Task Schedule for Today",
            message=plain_text_content,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            html_message=html_content,
        )

    print("✅ Daily task schedules sent successfully! to",user.email)


generativeai.configure(api_key="AIzaSyAlvIwjLl9S5tr3IQa3RtZf0Li7i8wXHXg")

# Initialize the Gemini model
model = generativeai.GenerativeModel('gemini-2.5-flash')

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Team, Task
from user.models import CustomUser

def generate_team_task_suggestions(team):
    print("Generating team task suggestions...")
    completed_tasks = [task.title for task in Task.objects.filter(team=team)]
    monthly_goals = team.monthly_goals or []
    yearly_goals = team.yearly_goals or []
    vision = team.vision or ""

    prompt = f"""
    You are a task recommendation system. Based on the team's completed tasks, monthly goals, yearly goals, and vision, suggest 20 specific, actionable, and relevant tasks for the team.

    **Team Context:**
    - Completed Tasks: {completed_tasks}
    - Monthly Goals: {monthly_goals}
    - Yearly Goals: {yearly_goals}
    - Vision: {vision}

    **Task Attributes:**
    - Specific: Each task should be clear and well-defined.
    - Actionable: Each task should be something the team can start working on immediately.
    - Relevant: Each task should align with the team's goals and vision.

    **Output Format:**
    - Provide exactly 10 tasks.
    - Each task should be a single sentence.
    - Start each task with a verb (e.g., "Develop", "Plan", "Research").

    **Task Suggestions:**
    """

    # Simulating AI model response
    response = model.generate_content(prompt)  # Replace with actual AI model call
    suggestions = response.text.strip().split('\n') if response and response.text else []
    suggestions = [s.strip() for s in suggestions if s.strip()]
    return suggestions[:10] 
 
def generate_task_suggestions(user, task=Task):
    print("Generating task suggestions...")
    all_tasks = [task.title for task in task.objects.filter(user=user)]
    print(f"User: {user}, Completed Tasks: {all_tasks}")
    interests = user.interests
    goals = user.goals

    # Construct a detailed and structured prompt
    prompt = f"""
    You are a task recommendation system. Based on the user's completed tasks, interests, and goals, suggest 20 specific, actionable, and relevant tasks for the user.

    **User Context:**
    - Completed Tasks: {all_tasks}
    - Interests: {interests}
    - Goals: {goals}

    **Task Attributes:**
    - Specific: Each task should be clear and well-defined.
    - Actionable: Each task should be something the user can start working on immediately.
    - Relevant: Each task should align with the user's interests and goals.

    **Output Format:**
    - Provide exactly 10 tasks.
    - Each task should be a single sentence.
    - Start each task with a verb (e.g., "Learn", "Build", "Read").
    - Avoid vague or generic tasks.

    **Example Tasks:**
    1. Learn advanced Python concepts like decorators and generators.
    2. Build a personal portfolio website to showcase your projects.
    3. Read a book on software development best practices.

    **Task Suggestions:**
    """

    # Generate suggestions using the AI model
    response = model.generate_content(prompt)
    suggestions = response.text.strip().split('\n') if response and response.text else []

    # Clean and format the suggestions
    suggestions = [s.strip() for s in suggestions if s.strip()]
    return suggestions[:10]  # Return up to 20 suggestions  send 10 daily task ans use above functions to generate task


from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.conf import settings
from django.utils.timezone import now
from .models import Team, Task
from user.models import CustomUser
def send_daily_suggested_tasks_to_user():
    """Send daily AI-suggested tasks to individual users."""
    print("Generating and sending daily suggested tasks to users...")
    users = CustomUser.objects.all()

    for user in users:
        # Generate task suggestions for the user
        suggested_tasks = generate_task_suggestions(user)
        if not suggested_tasks:
            continue

        # Limit to 10 tasks
        suggested_tasks = suggested_tasks[:10]

        # Render HTML email template
        html_content = render_to_string(
            'emails/daily_suggested_tasks.html',  # Path to your HTML template
            {
                'user': user,
                'suggested_tasks': suggested_tasks,
                'home_page_link': f"{settings.BASE_URL}/task/",
            }
        )

        # Plain text fallback
        plain_text_content = strip_tags(html_content)

        # Send the email
        send_mail(
            subject="✨ Your AI-Suggested Tasks for Today",
            message=plain_text_content,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            html_message=html_content,
        )

    print("✅ Suggested tasks sent to individual users successfully!")

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_daily_suggested_tasks_to_team_owner():
    print("Generating and sending daily suggested tasks to team owners...")
    teams = Team.objects.all()

    for team in teams:
        team_owner = team.created_by
        suggested_tasks = generate_team_task_suggestions(team)
        if not suggested_tasks:
            continue

        # Limit to 10 tasks
        suggested_tasks = suggested_tasks[:10]

        # Render the HTML email template
        html_content = render_to_string(
            'emails/daily_suggested_teamtasks.html',  # Path to your HTML template
            {
                'team_owner': team_owner,
                'team': team,
                'suggested_tasks': suggested_tasks,
                'home_page_link': f"{settings.BASE_URL}/team/{team.id}/tasks/",
                'team_page_link': f"{settings.BASE_URL}/teams/{team.id}/",
            }
        )

        # Plain text fallback for email clients that don't support HTML
        plain_text_content = strip_tags(html_content)

        # Send the email
        send_mail(
            subject=f"🚀 Suggested Tasks for Your Team: {team.name}",
            message=plain_text_content,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[team_owner.email],
            html_message=html_content,
        )
    print("✅ Suggested tasks sent to team owners successfully!")

def generate_html_email(title, content, home_page_link):
    return (
        f"<html>"
        f"<body>"
        f"<h2>{title}</h2>"
        f"{content}"
        f"<p><a href='{home_page_link}'>Visit Dashboard</a></p>"
        f"</body>"
        f"</html>"
    )



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
    scheduler.add_job(send_daily_suggested_tasks_to_team_owner,  CronTrigger(hour=8, minute=0))
    scheduler.add_job(send_daily_suggested_tasks_to_user, CronTrigger(hour=8, minute=0))

    # Run `update_daily_tasks` every day at midnight
    scheduler.add_job(update_daily_tasks, CronTrigger(hour=0, minute=0))

    scheduler.start()
