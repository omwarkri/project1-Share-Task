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
from chat.views import all_chats
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

    



@login_required
def home(request):
    # Get filter and sorting parameters from the request
    status_filter = request.GET.get('status', None)
    priority_filter = request.GET.get('priority', None)
    sort_by = request.GET.get('sort_by', 'created_at')  # Default: Sort by creation date
    order = request.GET.get('order', 'desc')  # Default: Descending order
    search_query = request.GET.get('q', None)  # Search query for tasks
    # Start with tasks for the logged-in user
    tasks = Task.objects.filter(user=request.user)

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
    if order == 'desc':
        sort_by = f'-{sorting_fields[sort_by]}'  # Add '-' for descending order
    else:
        sort_by = sorting_fields[sort_by]  # Ascending order

    # Apply sorting to the tasks
    tasks = tasks.order_by(sort_by)

    # Add suggested users to each task
    tasks_with_suggestions = []
    for task in tasks:
        response = get_suggested_users(task, request.user)
        tasks_with_suggestions.append({
            'task': task,
            'users_in_progress': response.get("users_in_progress"),
            'users_completed': response.get("users_completed"),
        })

    # Get all chats for the user
    chats = all_chats(request)

    TaskDependencies = TaskDependenciesForm()

    context = {
        'tasks_with_suggestions': tasks_with_suggestions,
        'app_name': 'Share Task',
        'form': TaskForm(),
        'chats': chats,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'sort_by': sort_by.lstrip('-'),  # Remove '-' for display purposes
        'order': order,
        'search_query': search_query,
        'TaskDependenciesForm':TaskDependencies
    }
    return render(request, 'task/home.html', context)


from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required

@login_required
@require_GET
def search_tasks(request):
    query = request.GET.get('q', '')
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

    return redirect('chat', task_id=task.id, receiver_id=user_to_add.id)

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

    return redirect('chat', task_id=task.id, receiver_id=user_to_remove.id)

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
        subtask = SubTask.objects.create(task=task, title=data["title"], completed=False)
        return JsonResponse({"id": subtask.id, "title": subtask.title, "completed": subtask.completed})

@csrf_exempt
def toggle_subtask(request, subtask_id):
    subtask = SubTask.objects.get(id=subtask_id)
    subtask.completed = not subtask.completed
    subtask.save()
    return JsonResponse({"id": subtask.id, "completed": subtask.completed})




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

    return redirect('chat', task_id=task_id, receiver_id=user_id)

@login_required
def remove_task_partner(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # Ensure only the task owner can remove the task partner
    if task.user == request.user:
        task.task_partner = None
        task.save()

    return redirect('chat', task_id=task_id, receiver_id=task.task_partner.id if task.task_partner else None)



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
