from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Task, ActivityLog, SubTask
from .forms import TaskForm
from django.utils import timezone
from django.db.models import Q, F
from django.db.models.functions import Coalesce
from django.db.models import ExpressionWrapper, DateTimeField
from user.forms import UserInterestGoalForm
from notes_app.models import TaskNotes
import time
import functools
import logging

logger = logging.getLogger(__name__)

def execution_time_logger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        print(f"{func.__name__} took {elapsed_time:.2f} seconds")
        return result
    return wrapper

@login_required
@execution_time_logger
def home(request):
    status_filter = request.GET.get('status', None)
    priority_filter = request.GET.get('priority', None)
    sort_by = request.GET.get('sort_by', 'created_at')
    order = request.GET.get('order', 'desc')
    search_query = request.GET.get('q', None)
    UserInterestGoalForms = UserInterestGoalForm()
    
    tasks = Task.objects.filter(
        Q(user=request.user) | Q(assigned_to=request.user)
    ).distinct()
  
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if status_filter:
        tasks = tasks.filter(status=status_filter)

    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)

    if sort_by == "created_at":
        tasks = tasks.order_by('-is_active', '-is_pinned', '-created_at')
    elif sort_by == "last_visited":
        tasks = tasks.order_by(
            '-is_active',
            '-is_pinned',
            F('last_visited_at').desc(nulls_last=True)
        )

    tasks_with_suggestions = []
    for task in tasks:
        is_overdue = task.is_overdue()
        is_approaching = task.is_approaching_due_date()

        tasks_with_suggestions.append({
            'task': task,
            'users_in_progress': [],
            'users_completed': [],
            'is_overdue': is_overdue,
            'is_approaching': is_approaching,
        })

    context = {
        'tasks_with_suggestions': tasks_with_suggestions,
        'app_name': 'Share Task',
        'form': TaskForm(),
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'sort_by': sort_by.lstrip('-'),
        'order': order,
        'search_query': search_query,
        'TaskDependenciesForm': TaskDependenciesForm(),
        'UserInterestGoalForm': UserInterestGoalForms
    }
    return render(request, 'task/home.html', context)

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    subtasks = task.subtasks.all()
    comments = task.comments.all()

    if request.method == 'POST':
        if "edit_task" in request.POST and request.user == task.user:
            task_form = TaskForm(request.POST, instance=task)
            if task_form.is_valid():
                task_form.save()
                ActivityLog.objects.create(
                    task=task,
                    user=request.user,
                    action='updated',
                    details=f"Task '{task.title}' was updated."
                )
                return redirect("task_detail", task_id=task.id)
        elif "add_comment" in request.POST:
            comment_form = TaskCommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.task = task
                comment.user = request.user
                comment.save()
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

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    ActivityLog.objects.create(
        task=task,
        user=request.user,
        action='deleted',
        details=f"Task '{task.title}' was deleted."
    )
    task.delete()
    return redirect('home')