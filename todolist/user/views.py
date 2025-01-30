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



def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print(username)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Replace 'home' with your desired page
        else:
            return render(request, 'user/login.html', {'error': 'Invalid credentials'})
    return render(request, 'user/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if not CustomUser.objects.filter(username=username).exists():
            user = CustomUser.objects.create_user(username=username, email=email, password=password)
            return redirect('login')
        else:
            return render(request, 'user/register.html', {'error': 'Username already exists'})
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

def profile_view(request):
    today = date.today()
    dates = [(today - timedelta(days=i)) for i in range(363, -1, -1)]

    current_month = datetime.datetime.now()
    previous_month = current_month - timedelta(days=365)  # Adjust logic for 11 month
    # Get all user activities within the past 365 days
    task_activities = UserActivity.objects.filter(user=request.user, activity_date__in=dates)

    # Initialize the activity_map and color_map
    activity_map = {}
    color_map = {}

    # Create a map of activities to track task completion, creation, and updates
    for activity in task_activities:
        # Convert the activity_date to datetime object with midnight time (00:00:00)
        activity_datetime = datetime.datetime.combine(activity.activity_date, datetime.time.min)

        # Make the datetime object timezone aware
        activity_date_aware = timezone.make_aware(activity_datetime)

        # Count tasks with different statuses on the same date as the activity date
        task_counts = Task.objects.filter(user=request.user, created_at__date=activity_date_aware.date()) \
            .values('status') \
            .annotate(status_count=Count('id'))

        # Initialize date entry if not already present
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

    # Color logic: Dark Green for more than 2 completed tasks, Green for completed tasks, Yellow for created/updated
    for activity_date, tasks in activity_map.items():
        if tasks["completed"] > 2:
            color_map[activity_date] = "dark_green"
        elif tasks["completed"] > 0:
            color_map[activity_date] = "green"
        else:
            color_map[activity_date] = "yellow"

    # Pass the data to the template
    context = {
        'user': request.user,
        'dates': dates,
        'color_map': color_map,  # Pass the color map to the template
        'current_month': current_month,
        'previous_month': previous_month,
    }

    return render(request, 'user/profile.html', context)
