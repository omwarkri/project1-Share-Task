# myapp/views.py
from django.shortcuts import render
from .models import Task

from notes_app.models import TaskNotes

from django.shortcuts import render, redirect
from .models import Task
from .forms import TaskForm

from django.contrib.auth.decorators import login_required


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Task,ActivityLog
from django.contrib.auth import get_user_model

User = get_user_model()
from django.db.models import Q

from django.db.models import Q

from django.contrib.auth import get_user_model
from user.models import CustomUser
from django.db.models import Q


User = get_user_model()

from django.contrib.auth import get_user_model

def get_suggested_users(task, current_user):
    """
    Fetch users working on or who have completed similar tasks.
    Exclude the current user and non-shareable tasks.
    """
    # Find shareable tasks with similar titles, excluding the current task
    similar_tasks = Task.objects.filter(title__icontains=task.title, shareable=True).exclude(id=task.id)
    print(similar_tasks)
    # Users working on similar tasks (pending status)
    users_in_progress = CustomUser.objects.filter(
        task_user__in=similar_tasks.filter(status='pending')
    ).exclude(id=current_user.id).distinct()
    print(users_in_progress)
    # Users who completed similar tasks
    users_completed =  CustomUser.objects.filter(
        task_user__in=similar_tasks.filter(status='completed')
    ).exclude(id=current_user.id).distinct()

    print(users_completed,"completed users")

    # Collect user details with associated tasks
    def get_user_tasks(users, task_status):
        return [
            {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "tasks": [
                    {"task_id": t.id, "task_title": t.title}
                    for t in similar_tasks.filter(status=task_status, user=user)
                ],
            }
            for user in users
        ]

    response = {
        "users_in_progress": get_user_tasks(users_in_progress, "pending"),
        "users_completed": get_user_tasks(users_completed, "completed"),
    }
    print("Suggested Users Response:", response)
    return response




from .forms import TaskForm

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Task
from .forms import TaskForm,TaskDependenciesForm

    


from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Task
from .forms import TaskForm, TaskDependenciesForm
@login_required
def home(request):
    # Get filter and sorting parameters from the request
    status_filter = request.GET.get('status', None)
    priority_filter = request.GET.get('priority', None)
    sort_by = request.GET.get('sort_by', 'created_at')  # Default: Sort by creation date
    order = request.GET.get('order', 'desc')  # Default: Descending order
    search_query = request.GET.get('q', None)  # Search query for tasks

   
    tasks = Task.objects.filter(
        Q(user=request.user) | Q(assigned_to=request.user)
    ).distinct()
  
    # Apply search query filter
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Apply status filter if provided
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    # Apply priority filter if provided
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)

    # Define sorting fields
    sorting_fields = {
        'title': 'title',
        'created_at': 'created_at',
        'due_date': 'due_date',
        'priority': 'priority',
        'status': 'status',
    }

    # Validate sorting field
    if sort_by not in sorting_fields:
        sort_by = 'created_at'  # Default to sorting by creation date if invalid

    # Determine the sorting order
    sort_by = f"-{sorting_fields[sort_by]}" if order == 'desc' else sorting_fields[sort_by]

    # Apply sorting to the tasks
    tasks = tasks.order_by(sort_by)

    # Add suggested users to each task
    tasks_with_suggestions = []
  
    
    for task in tasks:
        print(task.assigned_to)
        # Check if the task is overdue or approaching due date
        is_overdue = task.is_overdue()
        is_approaching = task.is_approaching_due_date()

        # Add notification flags
        tasks_with_suggestions.append({
            'task': task,
            
            'users_in_progress': [],
            'users_completed': [],
            'is_overdue': is_overdue,
            'is_approaching': is_approaching,
        })

    # Prepare context
    context = {
        'tasks_with_suggestions': tasks_with_suggestions,
        'app_name': 'Share Task',
        'form': TaskForm(),
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'sort_by': sort_by.lstrip('-'),  # Remove '-' for display purposes
        'order': order,
        'search_query': search_query,
        'TaskDependenciesForm': TaskDependenciesForm(),
        
    }

    return render(request, 'task/home.html', context)



from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required

@login_required
@require_GET
def search_tasks(request):
    query = request.GET.get('q', '')
    print(query)
    tasks = Task.objects.filter(user=request.user, title__icontains=query) if query else Task.objects.filter(user=request.user)
    
    task_data = [
        {
            "id": task.id,
            "title": task.title,
            "priority": task.get_priority_display(),
            "status": task.get_status_display(),
            "due_date": task.due_date.strftime("%B %d, %Y, %I:%M %p") if task.due_date else "N/A",
        }
        for task in tasks
    ]
    
    return JsonResponse({"tasks": task_data})






from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import TaskForm
from user.models import UserActivity
from datetime import date

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import TaskForm

from datetime import date
from django.utils import timezone

# Create a timezone-aware date (you can convert to midnight or current time)
activity_date = timezone.localdate()  # This gives the current date in the active timezone


@login_required
def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            is_private = request.POST.get('private') == 'on'  # 'on' is the value when the checkbox is checked
            task.shareable = not is_private  # If private is True, shareable is False, and vice versa

            task.save()

            # Log the task creation
            ActivityLog.objects.create(
                task=task,
                user=request.user,
                action='created',
                details=f"Task '{task.title}' was created."
            )

            # UserActivity logic (optional)
            activity, created = UserActivity.objects.get_or_create(
                user=task.user,
                activity_date=timezone.localdate(),
                defaults={'activity_type': 'Task Created'}
            )

            return redirect('home')
    else:
        form = TaskForm()

    return render(request, 'task/add_task.html', {'form': form})





from django.shortcuts import get_object_or_404, redirect
from .models import Task

def change_task_status(request, task_id, new_status):
    # Fetch the task by ID
    task = get_object_or_404(Task, id=task_id)
    
    # Update the status
    task.status = new_status
    UserActivity.objects.get_or_create(user=task.user, activity_date=date.today(), activity_type='Task updated')
    task.save()
    
    # Redirect back to the task list or any other page
    return redirect('home')

from django.shortcuts import get_object_or_404, redirect
from .models import Task

def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # Log the task deletion
    ActivityLog.objects.create(
        task=task,
        user=request.user,
        action='deleted',
        details=f"Task '{task.title}' was deleted."
    )

    task.delete()
    return redirect('home')


from django.shortcuts import render, get_object_or_404
from .models import Task

from django.shortcuts import render, get_object_or_404, redirect
from .models import Task
from .forms import TaskForm  # Assuming you have a TaskForm

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Task,  Comment,SubTask
from .forms import TaskForm, TaskCommentForm, SubTaskForm

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    subtasks = task.subtasks.all()
    comments = task.comments.all()

    if request.method == 'POST':
        # Handle task editing
        if "edit_task" in request.POST and request.user == task.user:
            task_form = TaskForm(request.POST, instance=task)
            if task_form.is_valid():
                task_form.save()

                # Log the task update
                ActivityLog.objects.create(
                    task=task,
                    user=request.user,
                    action='updated',
                    details=f"Task '{task.title}' was updated."
                )

                return redirect("task_detail", task_id=task.id)

        # Handle adding a new comment
        elif "add_comment" in request.POST:
            comment_form = TaskCommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.task = task
                comment.user = request.user
                comment.save()

                # Log the comment addition
                ActivityLog.objects.create(
                    task=task,
                    user=request.user,
                    action='comment_added',
                    details=f"Comment added: '{comment.text}'."
                )

                return redirect("task_detail", task_id=task.id)

    else:
        task_form = TaskForm(instance=task) if request.user == task.user else None
        comment_form = TaskCommentForm()
   
    return render(request, "task/task_detail.html", {
        "task": task,
        "task_form": task_form,
        "comment_form": comment_form,
        "comments": comments,
        'subtasks': subtasks,
        'subtask_form': SubTaskForm()
    })


# views.py
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Task
from user.models import CustomUser

@login_required
def add_allowed_user(request, task_id, user_id):
    task = get_object_or_404(Task, id=task_id)
    user_to_add = get_object_or_404(CustomUser, id=user_id)

    if task.user != request.user:
        return HttpResponseForbidden("You do not have permission to add users to this task.")

    task.allowed_users.add(user_to_add)

    # Log the user addition
    ActivityLog.objects.create(
        task=task,
        user=request.user,
        action='user_added',
        details=f"User '{user_to_add.username}' was added to the allowed users list."
    )

        # Construct the URL with query parameters
    url = reverse('chat', args=[task.id]) + f"?receiver_id={user_to_add.id}"

    # Redirect to the constructed URL
    return HttpResponseRedirect(url)

@login_required
def remove_allowed_user(request, task_id, user_id):
    task = get_object_or_404(Task, id=task_id)
    user_to_remove = get_object_or_404(CustomUser, id=user_id)

    if task.user != request.user:
        return HttpResponseForbidden("You do not have permission to remove users from this task.")

    task.allowed_users.remove(user_to_remove)

    # Log the user removal
    ActivityLog.objects.create(
        task=task,
        user=request.user,
        action='user_removed',
        details=f"User '{user_to_remove.username}' was removed from the allowed users list."
    )

  
    # Construct the URL with query parameters
    url = reverse('chat', args=[task.id]) + f"?receiver_id={user_to_remove.id}"

    # Redirect to the constructed URL
    return HttpResponseRedirect(url)

def add_subtask(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    can_add_subtask = (
        task.user == request.user or
        request.user in task.allowed_users.all()
    )

    if request.method == 'POST' and can_add_subtask:
        form = SubTaskForm(request.POST)
        if form.is_valid():
            subtask = form.save(commit=False)
            subtask.task = task
            subtask.save()

            # Log the subtask creation
            ActivityLog.objects.create(
                task=task,
                user=request.user,
                action='subtask_added',
                details=f"Subtask '{subtask.title}' was added."
            )

            return redirect('task_detail', task_id=task.id)

    return redirect('task_detail', task_id=task.id)

def toggle_subtask(request, subtask_id):
    subtask = get_object_or_404(SubTask, id=subtask_id)
    subtask.completed = not subtask.completed
    subtask.save()
    return redirect('task_detail', task_id=subtask.task.id)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Task, SubTask

def get_subtasks(request, task_id):
    subtasks = SubTask.objects.filter(task_id=task_id).values("id", "title", "completed")
    return JsonResponse(list(subtasks), safe=False)

@csrf_exempt
def add_subtask(request, task_id):
    if request.method == "POST":
        data = json.loads(request.body)
        task = Task.objects.get(id=task_id)
        print(task,)
        subtask = SubTask.objects.create(task=task, title=data["title"], completed=False)
        return JsonResponse({"id": subtask.id, "title": subtask.title, "completed": subtask.completed})

@csrf_exempt
def toggle_subtask(request, subtask_id):
    subtask = SubTask.objects.get(id=subtask_id)
    subtask.completed = not subtask.completed
    subtask.save()
    return JsonResponse({"id": subtask.id, "completed": subtask.completed})


from django.shortcuts import render

def landing_page(request):
    """
    Renders the landing page for the Share Task app.
    """
    return render(request, 'task/landing_page.html')

from django.shortcuts import render, get_object_or_404, redirect
from .models import Task
from .forms import TaskForm  # Assuming you have a TaskForm

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Task
from subscription.models import Subscription
from .forms import TaskForm

@login_required
def edit_task(request, task_id):
    # Check if the user has an active subscription
    try:
        subscription = Subscription.objects.get(user=request.user)
        if not subscription.is_subscription_valid():
            return HttpResponseForbidden("You need an active subscription to edit tasks.")
    except Subscription.DoesNotExist:
        return HttpResponseForbidden("You need an active subscription to edit tasks.")

    # Get the task by ID
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)  # Bind the form with the existing task data
        if form.is_valid():
            form.save()  # Save the updated task data
            ActivityLog.objects.create(
                task=task,
                user=request.user,
                action='updated',
                details=f"Task '{task.title}' was updated."
            )

            return redirect('task_detail', task_id=task.id)  # Redirect to the task detail page after saving
    else:
        form = TaskForm(instance=task)  # Pre-fill the form with the task's existing data

    return render(request, 'task/edit_task.html', {'form': form, 'task': task})



from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Task, TaskCompletionDetails, PartnerFeedback, ActivityLog

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    


    if request.method == 'POST':

        if task.can_be_completed():
            skip_sharing = request.POST.get('skip_sharing')

            if skip_sharing:
                task.status = 'completed'
                task.save()

                # Log the task completion
                ActivityLog.objects.create(
                    task=task,
                    user=request.user,
                    action='completed',
                    details=f"Task '{task.title}' was marked as completed without sharing details."
                )

                # Increment user score
                task.user.score += 1
                task.user.save()

                messages.success(request, 'Task marked as completed without sharing completion details.')
                return redirect('task_detail', task_id=task.id)

            # Save completion details
            completion_details = request.POST.get('completion_details')
            uploaded_image = request.FILES.get('uploaded_image')
            uploaded_file = request.FILES.get('uploaded_file')

            completion = TaskCompletionDetails.objects.create(
                task=task,
                completion_details=completion_details,
                uploaded_image=uploaded_image,
                uploaded_file=uploaded_file
            )

            task.status = 'completed'
            task.save()

            # Save partner feedback if provided
            partner_rating = request.POST.get('partner_rating')
            partner_comment = request.POST.get('partner_comment')
            if partner_rating and partner_comment and task.task_partner:
                partner_feedback = PartnerFeedback.objects.create(
                    task=task,
                    partner=task.task_partner,
                    rating=partner_rating,
                    comment=partner_comment
                )
                completion.partner_feedback = partner_feedback
                completion.save()

            # Award points to the task partner (if any)
            if task.task_partner:
                task.task_partner.score += 5  # Example: 5 points for helping
                task.task_partner.save()

            # Log the task completion
            ActivityLog.objects.create(
                task=task,
                user=request.user,
                action='completed',
                details=f"Task '{task.title}' was completed with details shared."
            )

            # Increment user score
            task.user.score += 1
            task.user.save()

            messages.success(request, 'Task completed and details shared successfully.')
            return redirect('task_detail', task_id=task.id)
        
        else:
            # Inform the user that task cannot be completed due to pending dependencies
            messages.error(request, "Cannot complete this task as some dependencies are not yet completed.")
        

    return render(request, 'task/task_detail.html', {'task': task})


from django.shortcuts import render
from .models import Task
from user.models import CustomUser  # Import your models


def suggested_users(request, task_id):
    task = Task.objects.get(id=task_id)
    task_data = get_suggested_users(task,request.user)
    print(task.id)
    return render(request, 'task/suggested_users.html', {
        'task': task,
        'task_data': task_data,
    })



from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Task, CustomUser

@login_required
def add_task_partner(request, task_id, user_id):
    task = get_object_or_404(Task, id=task_id)
    user = get_object_or_404(CustomUser, id=user_id)

    # Ensure only the task owner can add a task partner
    if task.user == request.user:
        task.task_partner = user
        task.save()

    url = reverse('chat', args=[task_id]) + f"?receiver_id={user_id}"
    # Redirect to the constructed URL
    return HttpResponseRedirect(url)

@login_required
def remove_task_partner(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # Ensure only the task owner can remove the task partner
    if task.user == request.user:
        task.task_partner = None
        task.save()

    receiver_id = task.task_partner.id if task.task_partner else None
    if receiver_id:
        url = reverse('chat', args=[task_id]) + f"?receiver_id={receiver_id}"
    else:
        # Handle the case where task_partner is None
        url = reverse('chat', args=[task_id])  # No receiver_id in the query parameters
    
    # Redirect to the constructed URL
    return HttpResponseRedirect(url)



from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from .forms import TaskDependenciesForm
from .models import Task
from django.urls import reverse




from django.http import JsonResponse
from .models import Task

def get_task_dependencies(request, task_id):
    task = Task.objects.get(id=task_id)
    dependencies = task.dependencies.all()
    all_tasks = Task.objects.exclude(id=task_id)  # Exclude the current task

    data = {
        'dependencies': [{'id': dep.id, 'title': dep.title} for dep in dependencies],
        'all_tasks': [{'id': task.id, 'title': task.title} for task in all_tasks],
    }
    return JsonResponse(data)


from django.shortcuts import get_object_or_404, redirect
from .models import Task

def update_task_dependencies(request, task_id):
    print(task_id)
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        form = TaskDependenciesForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = TaskDependenciesForm(instance=task)
    
    return render(request, 'task/task_detail.html', {'form': form, 'task': task})


# views.py
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Task
from .forms import TaskNotesForm

@login_required
def add_task_note(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        form = TaskNotesForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.task = task
            note.user = request.user
            note.save()
            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskNotesForm()
    return render(request, 'task/task_detail.html', {'form': form, 'task': task})   






# from google import genai



from google import generativeai  # Note the capital 'C' in Client

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
ai_key = os.getenv("AI_KEY")

from chat.models import ChatAIMessage

def generate_ai_procedure(request, task_id):
    client =  generativeai.configure(api_key=ai_key)
    model=generativeai.GenerativeModel('gemini-1.5-flash')
    if request.method == "GET":
        task = get_object_or_404(Task, id=task_id)  # Assuming Task is your model
        title = task.title
        description = task.description
        
        # Example prompt to fetch procedure
        prompt = f"Provide a step-by-step procedure to accomplish the task '{title}''{description}"
        try:
            response = model.generate_content(
                prompt
            )
            print(response.text)
            procedure = response.text
            ChatAIMessage.objects.create(task_id=task_id, sender="AI", message=f"These is Procedure :- {procedure}")
            task.procedure=procedure
            task.save()
        except Exception as e:
            procedure = f"Error generating procedure: {str(e)}"
        
        return JsonResponse({"procedure": procedure})
    





from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Team
from .forms import TeamForm

@login_required
def create_team(request):
    if request.method == "POST":
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.created_by = request.user
            team.save()
            team.members.add(request.user)  # Auto-add creator as a member
            return redirect("team_list")
    else:
        form = TeamForm()
    return render(request, "tasks/create_team.html", {"form": form})




from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Team
from .forms import TeamForm

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Team
from .forms import TeamForm
from django.db.models import Q
@login_required
def teams_list(request):
    # Handle team creation form submission
    if request.method == "POST":
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.created_by = request.user
            team.save()
            team.members.add(request.user)  # Add creator as a team member
            return redirect('teams_list')  # Refresh page after submission

    # Fetch all teams
    teams = Team.objects.filter(
        Q(members=request.user) | Q(created_by=request.user)
    ).distinct()
    form = TeamForm()  # Initialize the form

    teams_data = [
        {
            'id': team.id,
            'name': team.name,
            'description': team.description,
            'created_by': team.created_by.username,
            'members': [member.username for member in team.members.all()],
        }
        for team in teams
    ]
    return JsonResponse({'teams': teams_data})

    # Render the HTML template for normal requests



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Team, Task
from .forms import AddMemberForm, TeamTaskForm # Import the TaskForm

@login_required
def view_team_tasks(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    tasks = Task.objects.filter(team=team)  # Fetch tasks for the team
    add_member_form = AddMemberForm()
    task_form = TeamTaskForm()  # Task creation form

    if request.method == "POST":
        if "add_member" in request.POST:
            add_member_form = AddMemberForm(request.POST)
            if add_member_form.is_valid():
                user = add_member_form.cleaned_data['user']
                if user not in team.members.all():
                    team.members.add(user)
                    messages.success(request, f"{user.username} added to the team!")
                else:
                    messages.warning(request, f"{user.username} is already in the team!")
                return redirect('view_team_tasks', team_id=team.id)

        elif "add_task" in request.POST:
            task_form = TeamTaskForm(request.POST)
            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.team = team  # Assign the task to the current team
                task.created_by = request.user  # Assign task creator
                task.save()
                messages.success(request, "Task added successfully!")
                return redirect('view_team_tasks', team_id=team.id)

    return render(request, 'teams/team_tasks.html', {
        'team': team,
        'tasks': tasks,
        'add_member_form': add_member_form,
        'task_form': task_form
    })


from django.shortcuts import render, get_object_or_404
from .models import Team, TeamScoreboard

def team_leaderboard(request, team_id):
    print(team_id)
    team = get_object_or_404(Team, id=team_id)
    leaderboard = TeamScoreboard.objects.filter(team=team).order_by('-score')
    print(leaderboard)


    context = {
        'team': team,
        'leaderboard': leaderboard,
    }
    return render(request, 'teams/team_leaderboard.html', context)



from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from .models import Team, TeamInvitation

User = get_user_model()
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

@login_required
def send_team_invite(request, team_id):
    if request.method == "POST":

        email = request.POST.get("email")
        message = request.POST.get("message", "")  # Get the optional message
        team = get_object_or_404(Team, id=team_id)

        print(email)

        # Check if the user already exists
        invited_user = User.objects.filter(email=email).first()

        # Prevent inviting existing team members
        if invited_user and invited_user in team.members.all():
            messages.warning(request, "This user is already in the team.")
            return redirect("team_leaderboard", team_id=team_id)

        # Generate a unique token
        token = get_random_string(32)

        # Create an invitation
        invitation, created = TeamInvitation.objects.get_or_create(
            team=team, email=email, defaults={"invited_by": request.user, "token": token, "invited_user": invited_user}
        )

        # Send email with accept link
        invite_link = request.build_absolute_uri(f"/accept-invite/{invitation.token}/")

        # Render HTML email template
        html_content = render_to_string("teams/email_invitation.html", {
            "team_name": team.name,
            "invite_link": invite_link,
            "message": message,  # Include the optional message
            "invited_by": request.user.username,
        })
        text_content = strip_tags(html_content)  # Fallback for plain text email clients

        # Send the email
        email = EmailMultiAlternatives(
            subject=f"Invitation to Join {team.name}",
            body=text_content,
            from_email="no-reply@example.com",
            to=[email],
        )

        email.attach_alternative(html_content, "text/html")
        email.send()

        messages.success(request, "Invitation sent successfully!")
        return redirect("team_leaderboard", team_id=team_id)

    return render(request, "teams/send_invite.html", {"team_id": team_id})


from django.contrib.auth import login

def accept_invite(request, token):
    invitation = get_object_or_404(TeamInvitation, token=token, is_accepted=False)
    

    # If user is not logged in, redirect them to sign up
    if not request.user.is_authenticated :
        messages.info(request, "You need to create an account before accepting the invite.")
        return redirect("register_with_token", token=token)  # Redirect to sign-up with token
    if invitation.email!=request.user.email:
        messages.info(request, "You need to create an account before accepting the invite.")
        return redirect("register_with_token", token=token)  # Redirect to sign-up with token

    # If user email matches the invited email, allow them to accept
    if invitation.email == request.user.email:
        invitation.invited_user = request.user
        invitation.is_accepted = True
        invitation.save()

        # Add user to the team
        team = invitation.team
        team.members.add(request.user)

        messages.success(request, f"You have successfully joined {team.name}!")
        return redirect("team_leaderboard", team_id=team.id)
    
    messages.error(request, "This invitation is not for your account.")
    return redirect("home")






