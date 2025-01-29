# myapp/views.py
from django.shortcuts import render
from .models import Task



from django.shortcuts import render, redirect
from .models import Task
from .forms import TaskForm

from django.contrib.auth.decorators import login_required


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Task
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
    users_completed = CustomUser.objects.filter(
        tasks__in=similar_tasks.filter(status='completed')
    ).exclude(id=current_user.id).distinct()

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






@login_required
def home(request):
    tasks = Task.objects.filter(user=request.user)
    print(tasks)
    # Add suggested users to each task
    tasks_with_suggestions = []
    for task in tasks:

        response = get_suggested_users(task, request.user)

        print(response)
        tasks_with_suggestions.append({
            'task': task,
            'users_in_progress': response.get("users_in_progress"),
            'users_completed': response.get("users_completed"),
        })

    context = {
        'tasks_with_suggestions': tasks_with_suggestions,
        'app_name': 'ToDo App',
    }
    return render(request, 'task/home.html', context)





from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import TaskForm

@login_required  # Ensure the user is authenticated
def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)  # Don't save to database yet
            task.user = request.user       # Set the current user as the task owner
            task.save()                    # Save the task to the database
            return redirect('home')        # Redirect to the home page or task list
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
    task.save()
    
    # Redirect back to the task list or any other page
    return redirect('home')

from django.shortcuts import get_object_or_404, redirect
from .models import Task

def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return redirect('home')  # Redirect back to the task list


from django.shortcuts import render, get_object_or_404
from .models import Task

from django.shortcuts import render, get_object_or_404, redirect
from .models import Task
from .forms import TaskForm  # Assuming you have a TaskForm

def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_detail', task_id=task.id)  # Redirect to the updated task detail page
    else:
        form = TaskForm(instance=task)  # Pre-fill the form with the current task data

    return render(request, 'task/task_detail.html', {'task': task, 'form': form})



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
            return redirect('task_detail', task_id=task.id)  # Redirect to the task detail page after saving
    else:
        form = TaskForm(instance=task)  # Pre-fill the form with the task's existing data

    return render(request, 'task/edit_task.html', {'form': form, 'task': task})



from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Task, TaskCompletionDetails

def complete_task(request, task_id):
    task = Task.objects.get(id=task_id)

    if request.method == 'POST':
        skip_sharing = request.POST.get('skip_sharing')  # Check if the user chose to skip sharing

        # If the user chose to skip sharing, just mark the task as completed
        if skip_sharing:
            task.status = 'completed'
            task.save()
            messages.success(request, 'Task marked as completed without sharing completion details.')
            return redirect('task_detail', task_id=task.id)

        # If the user wants to share completion details, save them
        completion_details = request.POST.get('completion_details')
        uploaded_image = request.FILES.get('uploaded_image')
        uploaded_file = request.FILES.get('uploaded_file')

        # Create a new TaskCompletionDetails object
        TaskCompletionDetails.objects.create(
            task=task,
            completion_details=completion_details,
            uploaded_image=uploaded_image,
            uploaded_file=uploaded_file
        )

        # Mark the task as completed
        task.status = 'completed'
        task.save()

        messages.success(request, 'Task completed and details shared successfully.')
        return redirect('task_detail', task_id=task.id)
    
    return render(request, 'task_detail.html', {'task': task})



from django.shortcuts import render
from .models import Task
from user.models import CustomUser  # Import your models


def suggested_users(request, task_id):
    task = Task.objects.get(id=task_id)
    task_data = get_suggested_users(task,request.user)
    
    return render(request, 'task/suggested_users.html', {
        'task': task,
        'task_data': task_data,
    })
