# views.py

from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

class ProtectedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({"message": "You have access to this protected view!"})


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from user.models import CustomUser
from task.models import TeamInvitation

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from task.models import TeamInvitation

def login_view(request, token=None):
    invitation = get_object_or_404(TeamInvitation, token=token) if token else None

    if request.method == 'POST':
        token = token or request.POST.get("token")
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            return render(request, 'user/login.html', {'error': 'Username and password are required'})

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)

            if invitation:
               

                # Add user to the team
                team = invitation.team

                return redirect('view_team_tasks', team_id=team.id)

            return redirect('home')  # Replace 'home' with your desired homepage
        else:
            return render(request, 'user/login.html', {'error': 'Invalid credentials'})
    if token:
        return render(request, 'user/login.html' ,{'token': token})
    else:
        return render(request, 'user/login.html')


from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import CustomUser


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.urls import reverse


CustomUser = get_user_model()
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import CustomUser

def register_view(request, token=None):
    invitation = None

    # If a token is provided, check if it corresponds to a valid invitation
    if token:
        invitation = get_object_or_404(TeamInvitation, token=token, is_accepted=False)

    if request.method == 'POST':
        token = token or request.POST.get("token")
        print(token)
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # If registering via invitation, use the invited email
        if invitation:
            email = invitation.email  

        # Check if the username already exists
        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'user/register.html', {'error': 'Username already exists'})

        # Create a new user
        user = CustomUser.objects.create_user(username=username, email=email, password=password)

        # If registering via an invitation, link the user and mark the invitation as accepted
        if invitation:
            invitation.invited_user = user
            invitation.is_accepted = True
            invitation.save()
            team = invitation.team
            team.members.add(user)

            return redirect("login_with_token", token=token)

        return redirect('login')
    if token:

        return render(request, 'user/register.html', {'token': token, 'email': invitation.email if invitation else ''})
    else:
        return render(request, 'user/register.html')





from datetime import date, timedelta
from django.utils import timezone
from django.db.models import Count
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import UserActivity
from task.models import Task
import datetime


from django.db.models import Count

from datetime import date, timedelta, datetime
from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone
from .models import UserActivity
from task.models import Task, PartnerFeedback
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm

@login_required
def profile_view(request):
    print("hii")

    if request.method == 'POST':
        print(request.POST)
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        print(form)
        if form.is_valid():
            print("updating profile")
            form.save()
            return redirect('profile')  # Redirect to the profile page after saving
        
    else:
        today = date.today()
        dates = [(today - timedelta(days=i)) for i in range(364, -1, -1)]  # Ensure full year (365 days)

        # Get the current month and previous year for reference
        current_month = timezone.now()
        previous_month = current_month - timedelta(days=365)

        # Fetch user activities within the past year
        task_activities = UserActivity.objects.filter(user=request.user, activity_date__in=dates)

        # Initialize activity and color maps
        activity_map = {}
        color_map = {}

        # Populate activity map with task data
        for activity in task_activities:
            # Use timezone-aware dates
            activity_date_aware = timezone.make_aware(datetime.combine(activity.activity_date, datetime.min.time()))

            # Fetch task counts for the specific activity date
            task_counts = Task.objects.filter(
                user=request.user, created_at__date=activity_date_aware.date()
            ).values('status').annotate(status_count=Count('id'))

            # Ensure the date has an entry in the activity map
            if activity.activity_date not in activity_map:
                activity_map[activity.activity_date] = {"completed": 0, "created": 0, "updated": 0}

            # Update activity map based on task statuses
            for task_count in task_counts:
                task_state = task_count['status']
                count = task_count['status_count']

                if task_state == "completed":
                    activity_map[activity.activity_date]["completed"] += count
                elif task_state == "pending":
                    activity_map[activity.activity_date]["created"] += count
                else:
                    activity_map[activity.activity_date]["updated"] += count

            # Track activity type (Task Created, Completed, or Updated)
            if activity.activity_type == 'Task Created':
                activity_map[activity.activity_date]["created"] += 1
            elif activity.activity_type == 'Task Completed':
                activity_map[activity.activity_date]["completed"] += 1
            elif activity.activity_type == 'Task Updated':
                activity_map[activity.activity_date]["updated"] += 1

        # Set color logic for task activities
        for activity_date, tasks in activity_map.items():
            if tasks["completed"] > 2:
                color_map[activity_date] = "dark_green"
            elif tasks["completed"] > 0:
                color_map[activity_date] = "green"
            else:
                color_map[activity_date] = "yellow"

        # Fetch partner feedbacks
        feedbacks = PartnerFeedback.objects.filter(partner=request.user)
        user = CustomUser.objects.prefetch_related('user_badges__badge').get(id=request.user.id)

        user_badges=user.user_badges.all()
        # Accessing the badges
        level = user_badges.count()
        next_level_xp = (level + 1) * 50
        progress = (user.score / next_level_xp) * 100

        # Prepare context for the template
        context = {
            'user': user,
            'level': level,
            'progress': progress,
            'xp_required': next_level_xp,
            'user_badges':user_badges,
            'dates': dates,
            'color_map': color_map,
            'current_month': current_month,
            'previous_month': previous_month,
            'feedbacks': feedbacks,
        }

       
        return render(request, 'user/profile.html', context)


from django.db.models import F
def profile_view_id(request,user_id):
    user=CustomUser.objects.get(id=user_id)
    print(user)
    today = date.today()
    dates = [(today - timedelta(days=i)) for i in range(364, -1, -1)]  # Ensure full year (365 days)

    # Get the current month and previous year for reference
    current_month = timezone.now()
    previous_month = current_month - timedelta(days=365)

    # Fetch user activities within the past year
    task_activities = UserActivity.objects.filter(user=user, activity_date__in=dates)

    # Initialize activity and color maps
    activity_map = {}
    color_map = {}

    # Populate activity map with task data
    for activity in task_activities:
        # Use timezone-aware dates
        activity_date_aware = timezone.make_aware(datetime.combine(activity.activity_date, datetime.min.time()))

        # Fetch task counts for the specific activity date
        task_counts = Task.objects.filter(
            user=request.user, created_at__date=activity_date_aware.date()
        ).values('status').annotate(status_count=Count('id'))

        # Ensure the date has an entry in the activity map
        if activity.activity_date not in activity_map:
            activity_map[activity.activity_date] = {"completed": 0, "created": 0, "updated": 0}

        # Update activity map based on task statuses
        for task_count in task_counts:
            task_state = task_count['status']
            count = task_count['status_count']

            if task_state == "completed":
                activity_map[activity.activity_date]["completed"] += count
            elif task_state == "pending":
                activity_map[activity.activity_date]["created"] += count
            else:
                activity_map[activity.activity_date]["updated"] += count

        # Track activity type (Task Created, Completed, or Updated)
        if activity.activity_type == 'Task Created':
            activity_map[activity.activity_date]["created"] += 1
        elif activity.activity_type == 'Task Completed':
            activity_map[activity.activity_date]["completed"] += 1
        elif activity.activity_type == 'Task Updated':
            activity_map[activity.activity_date]["updated"] += 1

    # Set color logic for task activities
    for activity_date, tasks in activity_map.items():
        if tasks["completed"] > 2:
            color_map[activity_date] = "dark_green"
        elif tasks["completed"] > 0:
            color_map[activity_date] = "green"
        else:
            color_map[activity_date] = "yellow"

    completed_shareable_tasks = Task.objects.filter(
        user=user,  # Tasks owned by the user
        status='completed',  # Completed tasks
        shareable=True  # Shareable tasks
    ).select_related('completion_details').order_by(
        F('completion_details__created_at').desc(nulls_last=True)
    )   

    # Fetch partner feedbacks
    feedbacks = PartnerFeedback.objects.filter(partner=request.user)
    user = CustomUser.objects.prefetch_related('user_badges__badge').get(id=user.id)

    user_badges=user.user_badges.all()
    # Accessing the badges
    print(user_badges)

    

    # Prepare context for the template
    context = {
        'user': user,
        'completed_shareable_tasks':completed_shareable_tasks,
        'user_badges':user_badges,
        'dates': dates,
        'color_map': color_map,
        'current_month': current_month,
        'previous_month': previous_month,
        'feedbacks': feedbacks,
    }

    return render(request, 'user/profile_id.html', context)




# views.py

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserRegistrationSerializer, CustomTokenObtainPairSerializer
from .models import CustomUser

class UserRegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "This is a protected view!"})


from django.shortcuts import render
from django.http import JsonResponse
from .models import UserTaskAnalytics

def get_user_analytics(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    analytics, created = UserTaskAnalytics.objects.get_or_create(user=request.user)

    data = {
        'total_tasks': analytics.total_tasks,
        'completed_tasks': analytics.completed_tasks,
        'overdue_tasks': analytics.overdue_tasks,
        'average_completion_time': analytics.average_completion_time,
        'most_common_category': analytics.most_common_category,
        'last_updated': analytics.last_updated.strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    return JsonResponse(data)




import csv
import io
from datetime import timedelta
from django.utils import timezone
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from task.models import Task

@login_required
def download_task_report(request, report_type):
    """Generate and download daily, weekly, or monthly task reports in CSV format."""
    user = request.user
    now = timezone.now()

    # Filter tasks based on report type
    if report_type == "daily":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif report_type == "weekly":
        start_date = now - timedelta(days=now.weekday())  # Start of the week (Monday)
    elif report_type == "monthly":
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        return HttpResponse("Invalid report type", status=400)

    tasks = Task.objects.filter(user=user, created_at__gte=start_date)

    # Create CSV response
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{report_type}_task_report.csv"'

    writer = csv.writer(response)
    writer.writerow(["Task Name", "Status", "Due Date", "Created At", "Updated At"])

    for task in tasks:
        writer.writerow([task.title, task.status, task.due_date, task.created_at, task.updated_at])

    return response





from reportlab.pdfgen import canvas

@login_required
def download_task_report_pdf(request, report_type):
    user = request.user
    now = timezone.now()

    # Set time range
    if report_type == "daily":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif report_type == "weekly":
        start_date = now - timedelta(days=now.weekday())  # Start of the week
    elif report_type == "monthly":
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        return HttpResponse("Invalid report type", status=400)

    tasks = Task.objects.filter(user=user, created_at__gte=start_date)

    # Create PDF response
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{report_type}_task_report.pdf"'

    p = canvas.Canvas(response)
    p.drawString(60, 800, f"{report_type.capitalize()} Task Report")

    y = 780
    for task in tasks:
        p.drawString(40, y, f"Task: {task.title}, Status: {task.status}, Due: {task.due_date}")
        y -= 20

    p.showPage()
    p.save()
    return response


from django.shortcuts import render, get_object_or_404
from .models import CustomUser

@login_required
def followers_list(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    followers = user.followers.all()
    return render(request, 'followers_list.html', {'user': user, 'followers': followers})

@login_required
def following_list(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    following = user.following.all()
    return render(request, 'following_list.html', {'user': user, 'following': following})




from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser

@login_required
def follow_user(request, user_id):
    # Get the user to follow/unfollow
    user_to_follow = get_object_or_404(CustomUser, id=user_id)

    # Check if the current user is already following the user
    if request.user in user_to_follow.followers.all():
        # Unfollow the user
        user_to_follow.followers.remove(request.user)
        messages.success(request, f'You have unfollowed {user_to_follow.username}.')
    else:
        # Follow the user
        user_to_follow.followers.add(request.user)
        messages.success(request, f'You are now following {user_to_follow.username}.')

    # Redirect back to the completed tasks feed
    return redirect('completed_tasks_feed')



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from task.views import generate_task_suggestions

@login_required
@csrf_exempt  # Required if CSRF token isn't included; ideally, use CSRF token
def update_user_interests_goals(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            interests = str(data.get('interests', '')).strip()
            goals = str(data.get('goals', '')).strip()
            print(interests)
            user = request.user
            user.interests = interests
            user.goals = goals
            user.save()
            user = get_object_or_404(CustomUser, id=request.user.id)
            suggestions=generate_task_suggestions(user, task=Task)
            print(suggestions)
            return JsonResponse({'status': 'success', 'message': 'Interests and goals updated successfully.','suggestions':suggestions})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


from google import generativeai
generativeai.configure(api_key="AIzaSyDx3rr0MzUPaumvdII3WIffmtsZqAz7JIs")

# Initialize the Gemini model
model = generativeai.GenerativeModel('gemini-1.5-flash')

from datetime import date
from .models import DailySchedule

def generate_daily_schedule(user, tasks):
    today = date.today()
    existing = DailySchedule.objects.filter(user=user, date=today).first()
    if existing:
        return existing.schedule
    
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

    # generate new schedule ...
    new_schedule = model.generate_content(prompt).text.strip()

    DailySchedule.objects.create(user=user, date=today, schedule=new_schedule)
    return new_schedule



from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@require_POST
@login_required
def increment_pomodoro_count(request):
    try:
        request.user.increment_pomodoro_count()
        return JsonResponse({'status': 'success', 'count': request.user.pomodoro_count})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)



# utils.py or management/commands/generate_daily_challenges.py

import random
from datetime import date
from .models import ChallengeTemplate, DailyChallenge




from django.http import JsonResponse
from .models import DailyChallenge, UserChallenge
from django.utils import timezone


def generate_daily_challenges(num_challenges=1):
    today = date.today()
    if DailyChallenge.objects.filter(date=today).exists():
        return  # Already generated today

    all_templates = list(ChallengeTemplate.objects.all())

    # Avoid crash if not enough templates
    if len(all_templates) < num_challenges:
        num_challenges = len(all_templates)

    if num_challenges == 0:
        return

    selected = random.sample(all_templates, num_challenges)
    for template in selected:
        DailyChallenge.objects.create(template=template)



def get_daily_challenges(request):
    today = timezone.now().date()

    # Trigger generation
    generate_daily_challenges()

    challenge = DailyChallenge.objects.filter(date=today).first()
    if not challenge:
        return JsonResponse({'challenge': None})

    user_chal = None
    if request.user.is_authenticated:
        user_chal = UserChallenge.objects.filter(user=request.user, daily_challenge=challenge).first()

    data = {
        'title': challenge.template.title,
        'description': challenge.template.description,
        'target': challenge.template.target,
        'reward': challenge.template.xp_reward,
        'accepted': user_chal.accepted if user_chal else False,
        'completed': user_chal.completed if user_chal else False,
        'progress': user_chal.progress if user_chal else 0,
    }

    return JsonResponse({'challenge': data})




def update_progress(user, challenge_type, amount=1):
    today = date.today()
    challenges = DailyChallenge.objects.filter(date=today, template__challenge_type=challenge_type)

    for chal in challenges:
        user_chal, _ = UserChallenge.objects.get_or_create(user=user, daily_challenge=chal)
        if not user_chal.accepted:
            continue
        user_chal.progress += amount
        if user_chal.progress >= chal.template.target:
            user_chal.completed = True
        user_chal.save()



# views.py
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import DailyChallenge, UserChallenge

@require_POST
@login_required
def accept_challenge(request):
    today = timezone.now().date()
    user = request.user

    try:
        challenge = DailyChallenge.objects.get(date=today)
    except DailyChallenge.DoesNotExist:
        return JsonResponse({'error': 'No challenge for today'}, status=404)

    user_chal, created = UserChallenge.objects.get_or_create(
        user=user,
        daily_challenge=challenge,
        defaults={'accepted': True, 'progress': 0, 'completed': False}
    )

    if not created and not user_chal.accepted:
        user_chal.accepted = True
        user_chal.save()

    return JsonResponse({'success': True, 'message': 'Challenge accepted!'})




from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import UserChallenge
import json
from django.utils import timezone

@csrf_exempt
def update_challenge_progress(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    data = json.loads(request.body)
    action_type = data.get('type')  # "task" or "pomodoro"

    today = timezone.now().date()
    user_challenge = UserChallenge.objects.filter(user=request.user, daily_challenge__date=today).first()

    if not user_challenge:
        return JsonResponse({'error': 'No active challenge'}, status=404)

    template_type = user_challenge.daily_challenge.template.challenge_type  # for example: 'task' or 'pomodoro'

    if action_type != template_type:
        return JsonResponse({'message': 'Action does not match today\'s challenge'}, status=200)

    # Update progress
    user_challenge.progress += 1
    if user_challenge.progress >= user_challenge.daily_challenge.template.target:
        user_challenge.completed = True
        # Add reward XP here if needed

    user_challenge.save()

    return JsonResponse({'success': True})





from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from task.models import Task
from .models import Schedule
from django.utils import timezone
import json

@require_http_methods(["GET"])
def get_schedule(request):
    today = timezone.now().date()
    schedule_items = Schedule.objects.filter(
        user=request.user,
        date=today
    ).order_by('start_time')
    
    schedule_data = []
    for item in schedule_items:
        schedule_data.append({
            'start_time': item.start_time.strftime('%H:%M'),
            'end_time': item.end_time.strftime('%H:%M'),
            'task_id': item.task.id if item.task else None,
            'task_name': item.task.title if item.task else None,
            'completed': item.completed
        })
    
    return JsonResponse({'schedule': schedule_data})

from django.utils import timezone
from datetime import timedelta

@require_http_methods(["POST"])
def save_schedule(request):
    try:
        data = json.loads(request.body)
        now = timezone.now()
        cutoff = now - timedelta(hours=24)

        # Delete only old schedules (older than 24 hours)
        Schedule.objects.filter(user=request.user, created_at__lte=cutoff).delete()

        today = now.date()
        for item in data.get('schedule', []):
            Schedule.objects.create(
                user=request.user,
                date=today,
                start_time=item['start_time'],
                end_time=item['end_time'],
                task_id=item['task_id'] or None,
                completed =False
            )

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
