# myapp/views.py
from django.shortcuts import render
from .models import Task



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
from .forms import TaskForm

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Task
from .forms import TaskForm  # Ensure you have the TaskForm for creating tasks


@login_required
def home(request):
    # Get filter parameters from the request
    status_filter = request.GET.get('status', None)
    priority_filter = request.GET.get('priority', None)

    # Start with tasks for the logged-in user
    tasks = Task.objects.filter(user=request.user)

    # Apply status filter if provided
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    # Apply priority filter if provided
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)

    # Order tasks by status and priority
    # Custom order for status: pending -> in_progress -> completed -> archived
    status_order = {
        'pending': 0,
        'in_progress': 1,
        'completed': 2,
        'archived': 3,
    }

    # Custom order for priority: critical -> high -> medium -> low
    priority_order = {
        'critical': 0,
        'high': 1,
        'medium': 2,
        'low': 3,
    }

    # Annotate tasks with custom ordering values
    tasks = sorted(
        tasks,
        key=lambda task: (
            status_order.get(task.status, 4),  # Sort by status first
            priority_order.get(task.priority, 4),  # Then sort by priority
        )
    )

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

    context = {
        'tasks_with_suggestions': tasks_with_suggestions,
        'app_name': 'Share Task',
        'form': TaskForm(),
        'chats': chats,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
    }
    return render(request, 'task/home.html', context)






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