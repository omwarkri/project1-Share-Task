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
        print(user.profile_picture  )

        # Prepare context for the template
        context = {
            'user': user,
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
