# myapp/views.py
from django.shortcuts import render
from .models import Task
import re
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




import nltk
import re
import numpy as np
from django.db.models import Q
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

from .models import Task
from user.models import CustomUser


# Load model once at startup (better than reloading every call)


SentenceTransformerModel = SentenceTransformer("all-MiniLM-L6-v2")








STOP_WORDS = {"the", "is", "in", "and", "to", "of", "a", "for", "on", "with", "this", "that", "it", "as", "at", "by", "an", "be", "from"}


def preprocess_text(text):
    """Preprocess text by removing special characters, stopwords, and redundant spaces."""
    if not text:
        return ""

    text = text.lower()  # Convert to lowercase
    text = re.sub(r"[^a-z0-9\s]", "", text)  # Remove special characters
    words = text.split()
    words = [word for word in words if word not in STOP_WORDS]  # Remove stopwords

    # Ensure at least 3 words remain (to avoid over-filtering)
    return " ".join(words) if len(words) >= 3 else text.lower()





from django.db.models import Q
import numpy as np

def get_all_task_vectors():
    """
    Retrieve all task vectors from the Task model.
    Returns a dictionary with task_id as key and vector as numpy array.
    """
   
    tasks = Task.objects.filter(~Q(vector=None))  # Get tasks that have vectors

    task_vectors = {}
    for task in tasks:
        if task.vector:
            task_vectors[task.id] = np.array(task.vector, dtype=np.float32)  # Convert JSON list to numpy array

    return task_vectors

def get_suggested_users(task, current_user, top_n=5):
    """
    Suggest users based on task similarity using deep embeddings.
    """
    # Get all task embeddings
    task_vector_dict =get_all_task_vectors()    

    if not task_vector_dict:
        return {"users_in_progress": [], "users_completed": []}

    # Get embedding for the current task
    current_text = preprocess_text(f"{task.title} {task.description}")
    current_vector = SentenceTransformerModel.encode([current_text])

    # Compute cosine similarity
    similarities = {
    task_id: similarity
    for task_id, similarity in sorted(
        [
            (task_id, cosine_similarity(current_vector, task_vector.reshape(1, -1))[0][0])
            for task_id, task_vector in task_vector_dict.items()
            if task_id != task.id
        ],
        key=lambda x: x[1],
        reverse=True,
    )
    if similarity > 0.5  # Only include tasks with at least 50% similarity
}


    # Get top-N most similar tasks
    ranked_tasks = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:top_n]
    similar_task_ids = [task_id for task_id, _ in ranked_tasks]

    if not similar_task_ids:
        return {"users_in_progress": [], "users_completed": []}

    # Fetch similar tasks in a single query
    similar_tasks = Task.objects.filter(id__in=similar_task_ids)

    # Get users who are working on similar tasks (pending/completed)
    users_in_progress = CustomUser.objects.filter(
        task_user__in=similar_tasks.filter(status="pending")
    ).exclude(id=current_user.id).distinct()

    users_completed = CustomUser.objects.filter(
        task_user__in=similar_tasks.filter(status="completed")
    ).exclude(id=current_user.id).distinct()

    # Prepare response
    def format_users(users):
        return [
            {
                "user_id": user.id,
                "username": user.username,
                "tasks": [
                    {
                        "task_id": t.id,
                        "task_title": t.title,
                        "task_description": t.description,
                        "task_due_date": t.due_date,
                    }
                    for t in similar_tasks.filter(user=user)
                ],
            }
            for user in users
        ]

    return {
        "users_in_progress": format_users(users_in_progress),
        "users_completed": format_users(users_completed),
    }



# def get_suggested_users(task, current_user):
#     """
#     Fetch users working on or who have completed similar tasks.
#     Exclude the current user and non-shareable tasks.
#     """
#     # Find shareable tasks with similar titles, excluding the current task
#     similar_tasks = Task.objects.filter(title__icontains=task.title, shareable=True).exclude(id=task.id)
#     print(similar_tasks)
#     # Users working on similar tasks (pending status)
#     users_in_progress = CustomUser.objects.filter(
#         task_user__in=similar_tasks.filter(status='pending')
#     ).exclude(id=current_user.id).distinct()
#     print(users_in_progress)
#     # Users who completed similar tasks
#     users_completed =  CustomUser.objects.filter(
#         task_user__in=similar_tasks.filter(status='completed')
#     ).exclude(id=current_user.id).distinct()

#     print(users_completed,"completed users")

#     # Collect user details with associated tasks
#     def get_user_tasks(users, task_status):
#         return [
#             {
#                 "user_id": user.id,
#                 "username": user.username,
#                 "email": user.email,
#                 "tasks": [
#                     {"task_id": t.id, "task_title": t.title}
#                     for t in similar_tasks.filter(status=task_status, user=user)
#                 ],
#             }
#             for user in users
#         ]

#     response = {
#         "users_in_progress": get_user_tasks(users_in_progress, "pending"),
#         "users_completed": get_user_tasks(users_completed, "completed"),
#     }
#     print("Suggested Users Response:", response)
#     return response 



import time
import functools
import logging

logger = logging.getLogger(__name__)

def execution_time_logger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)  # No `await` since it's synchronous
        elapsed_time = time.time() - start_time
        print(f"{func.__name__} took {elapsed_time:.2f} seconds")
        return result
    return wrapper


from .forms import TaskForm

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Task
from .forms import TaskForm,TaskDependenciesForm

    

from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from concurrent.futures import ThreadPoolExecutor
from .models import Task
from .forms import TaskForm, TaskDependenciesForm
from user.forms import UserInterestGoalForm
    # Determine the sorting order\\

from django.db.models import F
from django.db.models.functions import Coalesce
from django.db.models import ExpressionWrapper, DateTimeField


@login_required
@execution_time_logger
def home(request):
    # Get filter and sorting parameters from the request
    status_filter = request.GET.get('status', None)
    priority_filter = request.GET.get('priority', None)
    sort_by = request.GET.get('sort_by', 'created_at')  # Default: Sort by creation date
    order = request.GET.get('order', 'desc')  # Default: Descending order
    search_query = request.GET.get('q', None)  # Search query for tasks
    UserInterestGoalForms=UserInterestGoalForm()

    
   
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
    # if sort_by in sorting_fields:
    #     sort_field = sorting_fields[sort_by]
    #     order_prefix = '-' if order == 'desc' else ''
    #     tasks = tasks.order_by(f'{order_prefix}{sort_field}')




    # Custom default ordering: active → pinned → created_at
    if sort_by == "created_at":
        tasks = tasks.order_by('-is_active', '-is_pinned', '-created_at')
    elif sort_by == "last_visited":
        tasks = tasks.order_by(
            '-is_active',
            '-is_pinned',
            F('last_visited_at').desc(nulls_last=True)
        )


   

    # Add suggested users to each task
    tasks_with_suggestions = []
  
    
    for task in tasks:
        
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
        'UserInterestGoalForm':UserInterestGoalForms
        
    }

    return render(request, 'task/home.html', context)


from django.http import JsonResponse
from django.utils import timezone
from .models import Task
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect  # Protects against CSRF attacks

import json

@require_POST
@csrf_protect
def mark_task_visited(request):
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        print("Received task_id:", task_id)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    if not task_id:
        return JsonResponse({'status': 'error', 'message': 'Task ID is required'}, status=400)

    try:
        task = Task.objects.get(id=task_id)
        task.last_visited_at = timezone.now()
        task.save()
        return JsonResponse({'status': 'success', 'message': 'Task marked as visited'})
    except Task.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Task not found'}, status=404)






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








from django.http import JsonResponse
import json
from .models import Task

from django.shortcuts import render, redirect
from .forms import TaskForm  # Import your TaskForm

def add_task(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()  # Save the task to the database
            return redirect('home')  # Redirect to the task list view after saving







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
    

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Task, Comment
from .forms import CommentForm  # Assuming you have a form for comments

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from .models import Task, Comment
from .forms import CommentForm

from django.http import JsonResponse
from django.template.loader import render_to_string

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from .models import Task, Comment
from .forms import CommentForm

@require_POST
def add_comment(request, task_id):
    # Get the task or return a 404 error if not found
    task = get_object_or_404(Task, id=task_id)

    # Create a form instance and populate it with data from the request
    form = CommentForm(request.POST)
    if form.is_valid():
        # Create a new comment but don't save it to the database yet
        comment = form.save(commit=False)
        # Associate the comment with the current task and user
        comment.task = task
        comment.user = request.user
        # Save the comment to the database
        comment.save()

        # Return a JSON response with the new comment data
        return JsonResponse({
            'success': True,
            'comment': {
                'text': comment.text,
                'user': {
                    'username': comment.user.username,
                },
                'created_at': comment.created_at.isoformat(),
            },
        })
    else:
        # Return an error response if the form is invalid
        return JsonResponse({
            'success': False,
            'error': 'Invalid form data.',
        }, status=400)
    

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Task, Comment

def get_comments(request, task_id):
    # Get the task or return a 404 error if not found
    task = get_object_or_404(Task, id=task_id)

    # Get all comments for the task
    comments = task.comments.all().values('id', 'text', 'user__username', 'created_at')

    # Convert the comments queryset to a list of dictionaries
    comments_list = list(comments)

    # Return the comments as a JSON response
    return JsonResponse({
        'success': True,
        'comments': comments_list,
    })

from django.http import JsonResponse
from .models import Task, Comment

from django.http import JsonResponse
from .models import Task, CustomUser

from django.http import JsonResponse
from .models import Task, Comment, Like

from django.http import JsonResponse
from django.forms.models import model_to_dict
from .models import Task, TaskCompletionDetails, PartnerFeedback, Like

from django.http import JsonResponse
from django.forms.models import model_to_dict
from .models import Task, TaskCompletionDetails, Like, Comment

def get_task_details(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        
        # Fetch completion details
        completion_details = TaskCompletionDetails.objects.filter(task=task).first()

        # Serialize completion details
        completion_details_data = None
        if completion_details:
            completion_details_data = model_to_dict(completion_details, exclude=["task", "partner_feedback"])
            completion_details_data["uploaded_image"] = completion_details.uploaded_image.url if completion_details.uploaded_image else None
            completion_details_data["uploaded_file"] = completion_details.uploaded_file.url if completion_details.uploaded_file else None

            # Serialize partner feedback if it exists
            if completion_details.partner_feedback:
                partner_feedback = completion_details.partner_feedback
                completion_details_data["partner_feedback"] = {
                    "rating": partner_feedback.rating,
                    "comment": partner_feedback.comment,
                    "partner": {
                        "id": partner_feedback.partner.id,
                        "username": partner_feedback.partner.username,
                        "profile_picture": partner_feedback.partner.profile_picture.url if partner_feedback.partner.profile_picture else None,
                    },
                }

        # Fetch likes for the task
        likes = Like.objects.filter(task=task)
        likes_data = [
            {
                "user": {
                    "id": like.user.id,
                    "username": like.user.username,
                    "profile_picture": like.user.profile_picture.url if like.user.profile_picture else None,
                },
                "created_at": like.created_at.isoformat(),
            }
            for like in likes
        ]

        # Fetch comments for the task
        comments = Comment.objects.filter(task=task)
        comments_data = [
            {
                "id": comment.id,
                "text": comment.text,
                "user": {
                    "id": comment.user.id,
                    "username": comment.user.username,
                    "profile_picture": comment.user.profile_picture.url if comment.user.profile_picture else None,
                },
                "created_at": comment.created_at.isoformat(),
            }
            for comment in comments
        ]

        # Prepare the response data
        data = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
            "completion_details": completion_details_data,
            "likes": likes_data,
            "comments": comments_data,  # Include comments in the response
        }

        return JsonResponse(data)
    except Task.DoesNotExist:
        return JsonResponse({"error": "Task not found"}, status=404)


@csrf_exempt
def toggle_subtask(request, subtask_id):
    subtask = SubTask.objects.get(id=subtask_id)
    subtask.completed = not subtask.completed
    subtask.save()
    return JsonResponse({"id": subtask.id, "completed": subtask.completed})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import SubTask  # make sure SubTask is imported

@csrf_exempt
def edit_subtask(request, subtask_id):
    subtask = get_object_or_404(SubTask, id=subtask_id)
    
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            new_title = data.get('title')
            if new_title:
                subtask.title = new_title
                subtask.save()
                return JsonResponse({'success': True, 'id': subtask.id, 'title': subtask.title})
            else:
                return JsonResponse({'success': False, 'error': 'Title is required'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)




@csrf_exempt
def delete_subtask(request, subtask_id):
    subtask = get_object_or_404(SubTask, id=subtask_id)
    if request.method == 'DELETE':
        subtask.delete()
        return JsonResponse({'success': True, 'deleted_id': subtask_id})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)




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


import threading
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Task, TaskCompletionDetails, PartnerFeedback, ActivityLog

def log_activity_and_update_scores(task, user, completion=None, partner_feedback=None):
    """Thread function to log activity and update scores asynchronously."""
    # Log the task completion
    ActivityLog.objects.create(
        task=task,
        user=user,
        action='completed',
        details=f"Task '{task.title}' was completed with details shared."
    )

    # Increment user score
    task.user.score += 1
    task.user.save()

    # Award points to the task partner (if any)
    if task.task_partner:
        task.task_partner.score += 5  # Example: 5 points for helping
        task.task_partner.save()

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import threading

from .models import Task, TaskCompletionDetails, PartnerFeedback


@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        if task.can_be_completed():
            skip_sharing = request.POST.get('skip_sharing')

            if skip_sharing:
                task.status = 'completed'
                task.save()

                # Run logging and score updates in a separate thread
                thread = threading.Thread(target=log_activity_and_update_scores, args=(task, request.user))
                thread.start()

                messages.success(request, 'Task marked as completed without sharing completion details.')
                return redirect('task_detail', task_id=task.id)

            # Get form data
            completion_details = request.POST.get('completion_details')
            uploaded_image = request.FILES.get('uploaded_image')
            uploaded_file = request.FILES.get('uploaded_file')

            # Create completion instance
            completion = TaskCompletionDetails(
                task=task,
                completion_details=completion_details
            )

            # Attach only existing files to avoid Cloudinary errors
            if uploaded_image:
                completion._image_file = uploaded_image
            if uploaded_file:
                completion._file_file = uploaded_file

            completion.save()

            # Save partner feedback if provided
            partner_feedback = None
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

            # Run logging and score updates in a separate thread
            thread = threading.Thread(target=log_activity_and_update_scores, args=(task, request.user, completion, partner_feedback))
            thread.start()

            messages.success(request, 'Task completed and details shared successfully.')
            return redirect('task_detail', task_id=task.id)
        
        else:
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



import time
from concurrent.futures import ThreadPoolExecutor
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Team, Task
from .forms import AddMemberForm, TeamTaskForm, ReassignTaskForm, EscalateTaskForm

def process_tasks(tasks):
    """Process tasks to check if they are overdue or approaching due date."""
    tasks_with_due = []
    for task in tasks:
        tasks_with_due.append({
            'task': task,
            'is_overdue': task.is_overdue(),
            'is_approaching': task.is_approaching_due_date(),
        })
    return tasks_with_due
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Team, Task
from .forms import AddMemberForm, TeamTaskForm , ReassignTaskForm,EscalateTaskForm # Import the TaskForm

@login_required
@execution_time_logger
def view_team_tasks(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    tasks = Task.objects.filter(team=team)  # Fetch tasks for the team
    add_member_form = AddMemberForm()
    task_form = TeamTaskForm()  # Task creation form
    reassigned_task_form=ReassignTaskForm()
    escualeted_reason_form=EscalateTaskForm()

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

    tasks_with_due=[]    
    for task in tasks:
        
        # Check if the task is overdue or approaching due date
        is_overdue = task.is_overdue()
        is_approaching = task.is_approaching_due_date()
        
        # Add notification flags
        tasks_with_due.append({
            'task': task,
            'is_overdue': is_overdue,
            'is_approaching': is_approaching,
        })



    return render(request, 'teams/team_tasks.html', {
        'team': team,
        'tasks': tasks_with_due,
        'add_member_form': add_member_form,
        'task_form': task_form,
        'reassigned_task_form': reassigned_task_form,
        'escualeted_reason_form': escualeted_reason_form
      
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



from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, F, ExpressionWrapper, fields

from task.models import  Team, Task, TeamScoreboard  # Update with actual app name
from task.models import CustomUser




def member_analysis(request, team_id, member_id):
    """Fetch task analysis data for a specific team member, including daily, weekly, and monthly reports."""

    member = get_object_or_404(CustomUser, id=member_id)
    team = get_object_or_404(Team, id=team_id)

    # Get tasks assigned to the member in this team
    tasks = Task.objects.filter(team=team, assigned_to=member)

    # Calculate task statistics
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='completed')
    pending_tasks = tasks.filter(status='pending').count()
    in_progress_tasks = tasks.filter(status='in_progress').count()
    overdue_tasks = tasks.filter(status__in=['pending', 'in_progress'], due_date__lt=timezone.now()).count()

    # Average completion time for completed tasks
    if completed_tasks.exists():
        average_completion_time = completed_tasks.annotate(
            completion_time=ExpressionWrapper(F('updated_at') - F('created_at'), output_field=fields.DurationField())
        ).aggregate(avg_completion_time=Avg('completion_time'))['avg_completion_time']
        average_completion_time = str(average_completion_time)  # Convert to string for JSON
    else:
        average_completion_time = None

    # Get the member's score from the scoreboard
    scoreboard_entry = TeamScoreboard.objects.filter(team=team, member=member).first()
    score = scoreboard_entry.score if scoreboard_entry else 0

    # Define time periods
    now = timezone.now()
    last_24_hours = now - timedelta(days=1)
    last_7_days = now - timedelta(days=7)
    last_30_days = now - timedelta(days=30)

    # Daily, Weekly, Monthly Reports
    daily_completed = completed_tasks.filter(updated_at__gte=last_24_hours).count()
    weekly_completed = completed_tasks.filter(updated_at__gte=last_7_days).count()
    monthly_completed = completed_tasks.filter(updated_at__gte=last_30_days).count()

    # Filter tasks into daily, weekly, and monthly lists
    daily_tasks = tasks.filter(updated_at__gte=last_24_hours)
    weekly_tasks = tasks.filter(updated_at__gte=last_7_days)
    monthly_tasks = tasks.filter(updated_at__gte=last_30_days)

    # Serialize tasks
    def serialize_tasks(task_queryset):
        return [
            {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'due_date': task.due_date.strftime('%Y-%m-%d') if task.due_date else None,
                'created_at': task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': task.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for task in task_queryset
        ]

    # Serialize all tasks and filtered tasks
    task_list = serialize_tasks(tasks)
    daily_task_list = serialize_tasks(daily_tasks)
    weekly_task_list = serialize_tasks(weekly_tasks)
    monthly_task_list = serialize_tasks(monthly_tasks)

    return JsonResponse({
        'member': {'username': member.username},
        'task_summary': {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks.count(),
            'pending_tasks': pending_tasks,
            'in_progress_tasks': in_progress_tasks,
            'overdue_tasks': overdue_tasks,
            'average_completion_time': average_completion_time,
        },
        'performance': {
            'score': score,
            'daily_completed': daily_completed,
            'weekly_completed': weekly_completed,
            'monthly_completed': monthly_completed,
        },
        'tasks': {
            'all': task_list,  # All tasks
            'daily': daily_task_list,  # Tasks updated in the last 24 hours
            'weekly': weekly_task_list,  # Tasks updated in the last 7 days
            'monthly': monthly_task_list,  # Tasks updated in the last 30 days
        },
    })



from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Task
import logging
from django.conf import settings
import logging
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Task
from .forms import EscalateTaskForm  # Import the form


logger = logging.getLogger(__name__)

@login_required
def escalate_task(request, task_id):
    # Get the task and ensure it is assigned to the current user
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    print("Escalating task")

    # Get the team ID for redirection
    team_id = task.team.id

    # Check if the task is already escalated
    if task.escalated_to:
        messages.warning(request, "This task has already been escalated.")
        return redirect("view_team_tasks", team_id=team_id)

    if request.method == 'POST':
        # Process the form
        form = EscalateTaskForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data['escalation_reason']  # Get the escalation reason
            
            # Determine the user to escalate to
            if task.team.team_lead:
                escalated_user = task.team.team_lead
                escalation_message = f"Task '{task.title}' has been escalated to the team lead: {escalated_user.username}."
            elif task.assigned_to:
                escalated_user = task.assigned_to
                escalation_message = f"Task '{task.title}' has been escalated to the assigned user: {escalated_user.username}."
            else:
                # Handle edge case where neither team lead nor assigned user is available
                messages.error(request, "No team lead or assigned user found to escalate the task.")
                return redirect("view_team_tasks", team_id=team_id)

            # Update the task with escalation details
            task.status = 'escalated'
            task.escalated_to = escalated_user
            task.escalation_reason = reason  # Save the escalation reason
            print("task escualating")
            task.save()

            # Log the escalation
            logger.info(f"Task {task.id} escalated to {escalated_user.username} by {request.user.username}. Reason: {reason}")

            # Notify the user
            messages.success(request, escalation_message)

           

            # Redirect to the team tasks view
            return redirect("view_team_tasks", team_id=team_id)
    else:
        # Display the form
        form = EscalateTaskForm()

    # Render the escalation form
    return redirect("view_team_tasks", team_id=team_id)






from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Task
from .forms import ReassignTaskForm

@login_required
def reassign_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # Ensure the current user is the team lead
    if request.user != task.team.team_lead and request.user != task.user:
        messages.error(request, "You do not have permission to reassign this task.")
        return redirect("view_team_tasks", team_id=task.team.id)

    if request.method == 'POST':
        print("reassigning task")
        form = ReassignTaskForm(request.POST, instance=task, team=task.team)
        if form.is_valid():
            task = form.save()
            task.escalated_to=None
            task.save()
            messages.success(request, f"Task '{task.title}' has been reassigned to {task.assigned_to.username}.")
            return redirect("view_team_tasks", team_id=task.team.id)


from django.shortcuts import render
from .models import Task, TaskCompletionDetails

from django.shortcuts import render
from django.db.models import Count
from concurrent.futures import ThreadPoolExecutor
from .models import Task, TaskCompletionDetails, User

def fetch_completed_tasks():
    """Fetch all completed tasks with related completion details"""
    return Task.objects.filter(status='completed').select_related('completion_details')

def fetch_top_users():
    """Fetch top 5 users with the most followers"""
    return User.objects.annotate(follower_count=Count('followers')).order_by('-follower_count')[:5]

@execution_time_logger
def completed_tasks_feed(request):
    filter_type = request.GET.get('filter_type')

    # Use ThreadPoolExecutor to fetch tasks and top users concurrently
    with ThreadPoolExecutor() as executor:
        future_tasks = executor.submit(fetch_completed_tasks)
        future_users = executor.submit(fetch_top_users)

        completed_tasks = future_tasks.result()
        top_users = future_users.result()

    task_feed_data = []

    # Process tasks
    for task in completed_tasks:
        completion_details = getattr(task, 'completion_details', None)

        if not completion_details:
            continue  # Skip tasks without completion details

        # Apply filters
        if (
            (filter_type == 'detail' and completion_details.has_details()) or
            (filter_type == 'video' and completion_details.has_uploaded_file()) or
            (filter_type == 'post' and completion_details.has_files()) or
            (filter_type == 'image' and completion_details.has_uploaded_image()) or
            (filter_type == 'feedback' and completion_details.has_partner_feedback()) or
            (not filter_type)  # No filter applied
        ):
            task_feed_data.append({'task': task, 'completion_details': completion_details})

    return render(request, 'feed/completed_tasks_feed.html', {
        'task_feed_data': task_feed_data,
        'filter_type': filter_type,
        'top_users': top_users,
    })



from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Like, Task

@login_required
def like_task(request, task_id):
    task = Task.objects.get(id=task_id)
    like, created = Like.objects.get_or_create(user=request.user, task=task)
    
    if not created:
        like.delete()  # Unlike the task if it was already liked
        liked = False
    else:
        liked = True

    like_count = task.likes.count()
    return JsonResponse({'liked': liked, 'like_count': like_count})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Team, Appreciation
from .forms import AppreciationForm

@login_required
def team_appreciations(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    # Handle form submission
    if request.method == 'POST':
        form = AppreciationForm(request.POST)
        if form.is_valid():
            appreciation = form.save(commit=False)
            appreciation.from_user = request.user
            appreciation.team = team
            appreciation.save()
            return redirect('team_appreciations', team_id=team.id)
    else:
        form = AppreciationForm()

    # Render the template with the form and appreciations
    return render(request, 'teams/appreciations.html', {
        'team': team,
        'form': form,
    })



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Team, TeamPermission, Permission
from django.contrib.auth import get_user_model
import json

CustomUser = get_user_model()


def fetch_permissions(request, team_id):
    # Fetch the team or return a 404 if not found
    team = get_object_or_404(Team, id=team_id)

    # Check if the request user is the team owner
    is_team_owner = request.user == team.created_by

    # Fetch all team members
    members = team.members.all()
    permissions_data = []

    for member in members:
        # Fetch permissions for each member
        permissions = {
            "add_task": TeamPermission.objects.filter(team=team, user=member, permission__codename="add_task").exists(),
            "delete_task": TeamPermission.objects.filter(team=team, user=member, permission__codename="delete_task").exists(),
            "edit_team": TeamPermission.objects.filter(team=team, user=member, permission__codename="edit_team").exists(),
        }
        print(request.user ,team.created_by)
        # Add the "manage_permissions" option only for the team owner
        if request.user == team.created_by and request.user==member:
            permissions["manage_permissions"] = True
        
        permissions_data.append({
            "id": member.id,
            "username": member.username,
            "permissions": permissions,
        })

    return JsonResponse({"members": permissions_data})

@csrf_exempt
def update_permissions(request, team_id, user_id):
    if request.method == 'POST':
        team = Team.objects.get(id=team_id)
        user = CustomUser.objects.get(id=user_id)
        data = json.loads(request.body)

        # Update permissions
        for codename, has_permission in data.items():
            permission = Permission.objects.get(codename=codename)
            if has_permission:
                TeamPermission.objects.get_or_create(team=team, user=user, permission=permission)
            else:
                TeamPermission.objects.filter(team=team, user=user, permission=permission).delete()

        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)




from google import generativeai


# Configure Gemini API
generativeai.configure(api_key="AIzaSyDx3rr0MzUPaumvdII3WIffmtsZqAz7JIs")

# Initialize the Gemini model
model = generativeai.GenerativeModel('gemini-1.5-flash')



from django.contrib.auth import get_user_model

User = get_user_model()

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from user.forms import UserInterestGoalForm



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from user.forms import UserInterestGoalForm
from user.models import CustomUser


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
    - Provide exactly 20 tasks.
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
    return suggestions[:20]  # Return up to 20 suggestions
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
import json

@login_required
def task_suggestions_view(request):
    user = get_object_or_404(CustomUser, id=request.user.id)
    suggestions = []
    form = UserInterestGoalForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        # Save interests and goals
        user.interests = [i.strip() for i in form.cleaned_data['interests'].split(',')]
        user.goals = [g.strip() for g in form.cleaned_data['goals'].split(',')]
        user.save()
        suggestions = generate_task_suggestions(user)
        return JsonResponse({
            'status': 'success',
            'suggestions': suggestions,
        })
    elif request.method == 'GET':
        form = UserInterestGoalForm(initial={
            'interests': user.interests,
            'goals': user.goals
        })
        if user.interests and user.goals:
            suggestions = generate_task_suggestions(user)
        return JsonResponse({
            'status': 'success',
            'form_data': {
                'interests': form.initial['interests'],
                'goals': form.initial['goals'],
            },
            'suggestions': suggestions,
        })
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method or form data',
        }, status=400)





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
    - Provide exactly 20 tasks.
    - Each task should be a single sentence.
    - Start each task with a verb (e.g., "Develop", "Plan", "Research").

    **Task Suggestions:**
    """

    # Simulating AI model response
    response = model.generate_content(prompt)  # Replace with actual AI model call
    suggestions = response.text.strip().split('\n') if response and response.text else []
    suggestions = [s.strip() for s in suggestions if s.strip()]
    return suggestions[:20]

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied
import json

@login_required
@require_http_methods(["GET", "POST"])
def team_task_suggestions_view(request, team_id):
    # Fetch team and check user permissions
    team = get_object_or_404(Team, id=team_id)

    # Optional: Check if the user is part of the team
    if request.user not in team.members.all():
        return JsonResponse({'status': 'error', 'message': "You don't have access to this team."}, status=403)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            monthly_goal = data.get('monthly_goal', '').strip()
            yearly_goal = data.get('yearly_goal', '').strip()
            weekly_goal= data.get('weekly_goal', '').strip()
            vision = data.get('vision', '').strip()

            # Update the team fields
            team.monthly_goals = monthly_goal
            team.yearly_goals = yearly_goal
            team.weekly_goals= weekly_goal
            team.vision = vision
            team.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Team goals updated successfully.'
            })

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)
        
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    else:  # GET Request for suggestions and form data
        suggestions = generate_team_task_suggestions(team)

        form_data = {
            'monthly_goal': team.monthly_goals or '',
            'yearly_goal': team.yearly_goals  or '',
            'weekly_goal': team.weekly_goals  or '',
            'vision': team.vision or '',
        }

        return JsonResponse({
            'status': 'success',
            'form_data': form_data,
            'suggestions': suggestions,
        })



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Team

@csrf_exempt
def update_team_goals(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # Update the team goals here
        # For simplicity, assuming 'team' is fetched
        Team.monthly_goals = data.get('monthly_goals')
        Team.yearly_goals = data.get('yearly_goals')
        Team.vision = data.get('vision')
        Team.save()
        # Re-fetch suggestions
        suggestions = generate_team_task_suggestions(Team)
        return JsonResponse({'status': 'success', 'suggestions': suggestions})
    return JsonResponse({'status': 'error'}, status=400)




import google.generativeai as genai

from .models import Task

# Configure Gemini API
generativeai.configure(api_key="AIzaSyDx3rr0MzUPaumvdII3WIffmtsZqAz7JIs")
model = generativeai.GenerativeModel('gemini-1.5-flash')

# import requests

# def get_latest_news(query):
#     """
#     Fetch the latest news related to the task topic.
#     """
#     NEWS_API_KEY = settings.NEWS_API_KEY  # Add NewsAPI key in settings
#     url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
#     response = requests.get(url)
#     data = response.json()
#     articles = data.get("articles", [])[:3]  # Get top 3 latest news

#     if not articles:
#         return ["No recent news available."]
    
#     return [f"📰 {article['title']} - {article['source']['name']} ({article['url']})" for article in articles]







from django.shortcuts import render


from django.shortcuts import render



import json
from django.shortcuts import render



@login_required
def get_ai_posts(request):
    user = request.user
    tasks = Task.objects.filter(user=user).order_by("-created_at")[:10]
    task_titles = [task.title for task in tasks]

    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    User has recently planned or completed these tasks: {task_titles}.

    Generate **20 unique insights** based on these tasks. Each insight should be a complete post with a mix of and informative for user and encouraging motivating:
    - A short story 
    - Facts 
    - A productivity thought 
    - Practical knowledge 
    - Motivational elements 
    - Actionable tips 
    - Scientific/psychological facts 

  


    ### Response Format:
    Return a **valid JSON array** inside markdown triple backticks like this:
    ```
    [
        {{"post": "Your first post here..." }},
        {{"post": "Your second post here..." }},
        ...
        {{"post": "Your twentieth post here..." }}
    ]
    ```
    Ensure the response **only** contains the JSON inside backticks.
    """

    try:
        response = model.generate_content(prompt)
        ai_text = response.candidates[0].content.parts[0].text.strip()
        json_text = ai_text.split("```")[1].strip()
        posts = json.loads(json_text)  # Convert JSON string to Python list
    except (IndexError, json.JSONDecodeError, KeyError):
        posts = [{"post": "AI response is not valid JSON format. Please try again."}]

    return JsonResponse({"posts": posts})


# @login_required
# def get_ai_posts(request):
#     user = request.user
#     tasks = Task.objects.filter(user=user).order_by("-created_at")[:10]
#     task_titles = [task.title for task in tasks]

#     model = genai.GenerativeModel("gemini-1.5-flash")
    
#     prompt = f"""
#     Based on these recent tasks: {task_titles},
#     generate 20 unique, informative posts that blend:
#     - Practical knowledge (30%)
#     - Motivational elements (20%)
#     - Actionable tips (30%)
#     - Scientific/psychological facts (20%)

#     Each post should follow this structure:
#     1. Hook: Engaging opening sentence
#     2. Core Insight: Valuable information/fact
#     3. Task Connection: Relate to user's tasks
#     4. Actionable Tip: Specific advice
#     5. Motivational Close: Encouraging ending

#     Example Format (return as valid JSON):
#     ```
#     [
#         {{
#             "post": "Did you know? 15 minutes of planning saves 90 minutes of execution (Forbes). For your '{task_titles[0]}' task, try the 5-5-5 method: 5 mins planning, 5 mins organizing, 5 mins reviewing. Small investments in preparation yield massive productivity dividends!",
#             "category": "productivity"
#         }},
#         {{
#             "post": "The Zeigarnik Effect shows unfinished tasks stay on our minds. Your '{task_titles[1]}' is creating mental clutter. Here's the fix: Either complete it now, schedule it concretely, or delete it. Clarity brings peace of mind and focus!",
#             "category": "psychology"
#         }}
#     ]
#     ```

#     Include diverse categories: productivity, psychology, health, time-management, etc.
#     Ensure all facts are accurate and verifiable.
#     """

#     generation_config = {
#         "temperature": 0.7,
#         "max_output_tokens": 2000,
#         "top_p": 0.9
#     }

#     try:
#         response = model.generate_content(
#             prompt,
#             generation_config=generation_config
#         )
#         ai_text = response.candidates[0].content.parts[0].text.strip()
        
#         # Extract JSON from markdown code block
#         json_str = ai_text.split("```")[1].strip()
#         posts = json.loads(json_str)
        
#         # Add default category if missing and ensure proper formatting
#         for post in posts:
#             post['category'] = post.get('category', 'general')
#             post['post'] = post['post'].replace('"', "'")  # Ensure consistent quotes
            
#     except Exception as e:
#         print(f"AI Post Generation Error: {str(e)}")
#         posts = [{
#             "post": "Research shows writing down tasks increases completion by 42%. Keep using this app to harness that advantage!",
#             "category": "productivity"
#         }]
    
#     print(posts)

#     return JsonResponse({"posts": posts})




from django.shortcuts import render
import json  # Needed to parse the JsonResponse

def ai_stories(request):
    response = get_ai_posts(request)  # Get JSON response
    posts_data = json.loads(response.content)  # Convert JsonResponse to dict
    posts = posts_data.get("posts", [])  # Extract 'posts' list

    return render(request, "stories/ai_stories.html", {"posts": posts})



import json
import random
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import google.generativeai as genai
from .models import Task



from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import google.generativeai as genai

@login_required
def get_extended_insight(request):
    insight_text = request.GET.get("insight")
    if not insight_text:
        return JsonResponse({"error": "Missing insight text"}, status=400)

    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # Prompt designed to continue the existing insight naturally
    prompt = f"""
    You're expanding this insight to provide deeper value while maintaining its original voice:
    
    Original Insight: "{insight_text}"
    
    Continue this thought by:
    1. First building on the original statement (1-2 sentences)
    2. Then flowing into a relevant example that demonstrates it
    3. Finally extracting practical lessons
    
    Structure your response to:
    - Begin with "Building on this..." [continue the thought]
    - Transition with "Consider how..." [introduce example]
    - Conclude with "This shows us..." [practical takeaways]
    
    Keep the tone and style consistent with the original insight.
    Length: Approximately 3-4 paragraphs (300-400 words)
    """
    
    generation_config = {
        "temperature": 0.5,  # Balanced creativity/consistency
        "max_output_tokens": 500
    }

    try:
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )

        if response and response.candidates and response.candidates[0].content.parts:
            extension = response.candidates[0].content.parts[0].text.strip()
            
            # Create seamless transition
            extended_insight = f"{insight_text}\n\n{extension}"
            
            # Remove any duplicate phrases
            extended_insight = extended_insight.replace(
                insight_text + insight_text, 
                insight_text
            )
        else:
            extended_insight = insight_text  # Fallback to original

    except Exception as e:
        print(f"Extension error: {str(e)}")
        extended_insight = insight_text

    return JsonResponse({
        "detailed_post": extended_insight,
        "seamless": True  # Frontend can use this for styling
    })


import openai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json



@csrf_exempt
def ai_chat(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            question = data.get("question")
            story = data.get("story")
            previous_qa = data.get("previous_qa", "")

            if not question or not story:
                return JsonResponse({"error": "Missing question or story"}, status=400)

            # Create the prompt with context
            prompt = f"""
            Based on this context:
            {story}

            {previous_qa}

            Answer this question in a helpful, detailed way:
            {question}
            """

            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)

            # Safely extract the response
            if response and response.candidates and response.candidates[0].content.parts:
                answer = response.candidates[0].content.parts[0].text.strip()
            else:
                answer = "I couldn't generate a response. Please try again."

            return JsonResponse({"response": answer})

        except Exception as e:
            print(f"Error in ai_chat: {str(e)}")
            return JsonResponse({"error": "An error occurred while processing your request"}, status=500)
    
    return JsonResponse({"error": "Invalid request method"}, status=400)





import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import google.generativeai as genai

@login_required
def get_ai_memes(request):
    """Generate meme captions based on user tasks."""
    user = request.user
    tasks = Task.objects.filter(user=user).order_by("-created_at")[:10]
    task_titles = [task.title for task in tasks]

    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    User has recently planned or completed these tasks: {task_titles}.
    
    Generate **10 funny meme captions** based on these tasks. Captions should be:
    - Witty and humorous
    - Relatable to productivity, motivation, or daily struggles
    - Short (1-2 lines max)

    **Return ONLY a valid JSON array. No markdown. No explanations. Just JSON.**
    Example:
    [
        {{"meme_text": "When you finish a task and realize there's more waiting..." }},
        {{"meme_text": "That feeling when you check off a task but forget to save your progress..." }},
        {{"meme_text": "When the deadline is tomorrow, and you haven't even started..." }}
    ]
    """

    try:
        response = model.generate_content(prompt)
        ai_text = response.candidates[0].content.parts[0].text.strip()
        print("Raw AI Response:", ai_text)  # Debugging

        # Ensure AI returns only JSON (no markdown backticks)
        if ai_text.startswith("```json"):
            json_text = ai_text.split("```json")[1].strip("``` \n")
        else:
            json_text = ai_text  # Assume raw JSON

        memes = json.loads(json_text)  # Convert JSON string to Python list
    except (IndexError, json.JSONDecodeError, KeyError) as e:
        print("JSON Parsing Error:", str(e))  # Debugging
        memes = [{"meme_text": "AI response is not valid JSON format. Please try again."}]

    return JsonResponse({"memes": memes})




@login_required
def ai_memes(request):
    """Fetch AI-generated meme captions and display them in HTML."""
    response = get_ai_memes(request)
    memes_data = json.loads(response.content)  
    memes = memes_data.get("memes", [])  # Extract AI-generated captions
    print(memes)
    return render(request, "memes/ai_memes.html", {"memes": memes})



import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import google.generativeai as genai

@login_required
def get_ai_quotes(request):
    """Generate motivational quotes based on user tasks."""
    user = request.user
    tasks = Task.objects.filter(user=user).order_by("-created_at")[:10]
    task_titles = [task.title for task in tasks]

    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    User has recently planned or completed these tasks: {task_titles}.
    
    Generate **10 motivational quotes** based on these tasks. Quotes should be:
    - Inspiring and uplifting
    - Related to productivity, hard work, and success
    - Short (1-2 sentences max)

    **Return ONLY a valid JSON array. No markdown. No explanations. Just JSON.**
    Example:
    [
        {{"quote_text": "Success is not final, failure is not fatal: it is the courage to continue that counts."}},
        {{"quote_text": "Believe in yourself and all that you are. Know that there is something inside you greater than any obstacle."}},
        {{"quote_text": "Great things never come from comfort zones."}}
    ]
    """

    try:
        response = model.generate_content(prompt)
        ai_text = response.candidates[0].content.parts[0].text.strip()
        print("Raw AI Response:", ai_text)  # Debugging

        # Ensure AI returns only JSON (no markdown backticks)
        if ai_text.startswith("```json"):
            json_text = ai_text.split("```json")[1].strip("``` \n")
        else:
            json_text = ai_text  # Assume raw JSON

        quotes = json.loads(json_text)  # Convert JSON string to Python list
    except (IndexError, json.JSONDecodeError, KeyError) as e:
        print("JSON Parsing Error:", str(e))  # Debugging
        quotes = [{"quote_text": "AI response is not valid JSON format. Please try again."}]

    return JsonResponse({"quotes": quotes})


from django.shortcuts import render
import json
import google.generativeai as genai

@login_required
def ai_quotes(request):
    """Fetch AI-generated motivational quotes and render them in HTML."""
    response = get_ai_quotes(request)
    quotes_data = json.loads(response.content)  # Convert JSONResponse to Python dict
    quotes = quotes_data.get("quotes", [])

    return render(request, "motivation/ai_quotes.html", {"quotes": quotes})


from django.http import JsonResponse
from .models import Task
from user.views import generate_daily_schedule

def get_schedule(request):
    user = request.user
    tasks = Task.objects.filter(user=user)

    # Generate schedule
    schedule = generate_daily_schedule(user, tasks)

    return JsonResponse({
        'status': 'success',
        'message': 'Schedule generated successfully',
        'schedule': schedule  # This assumes your function returns a dict/serializable data
    })






from django.shortcuts import render, redirect
import google.generativeai as genai


model = genai.GenerativeModel("gemini-1.5-flash")


def parse_mcqs(text):
    import re
    pattern = re.compile(r"\*\*(\d+)\.\s(.+?)\*\*\s+a\)\s(.+?)\s+b\)\s(.+?)\s+c\)\s(.+?)\s+d\)\s(.+?)\s+\*\*Correct Answer: (\w)\)\*\*", re.DOTALL)
    questions = []
    for match in pattern.finditer(text):
        _, question, a, b, c, d, correct = match.groups()
        options = [('a', a.strip()), ('b', b.strip()), ('c', c.strip()), ('d', d.strip())]
        questions.append({
            'question': question.strip(),
            'options': options,
            'correct': correct.lower()
        })
    return questions
def quiz(request):
    if request.method == "POST":
        if "subject" in request.POST:
            # Quiz generation request
            subject = request.POST["subject"]
            level = request.POST.get("level", "beginner")  # default to beginner
            question_count = int(request.POST.get("question_count", 10))  # default to 10

            prompt = f"""
Generate {question_count} multiple-choice questions on the subject: "{subject}".
Difficulty level: {level.capitalize()}.

Use this exact format:

**1. Your question here**

a) Option A  
b) Option B  
c) Option C  
d) Option D  

**Correct Answer: b)**

Repeat the format for all {question_count} questions.
"""

            response = model.generate_content(prompt)
            text = response.candidates[0].content.parts[0].text.strip()
            questions = parse_mcqs(text)

            request.session["quiz"] = questions
            request.session["subject"] = subject
            request.session["level"] = level
            request.session["question_count"] = question_count

            return render(request, "quiz/ai_quiz.html", {
                "questions": questions,
                "subject": subject,
                "level": level,
                "question_count": question_count,
                "show_quiz": True,
                "show_results": False
            })

        elif any(key.startswith("q") for key in request.POST):
            # Quiz submission request
            questions = request.session.get("quiz", [])
            subject = request.session.get("subject", "Unknown")
            level = request.session.get("level", "Unknown")
            question_count = request.session.get("question_count", len(questions))

            score = 0
            results = []

            for i, q in enumerate(questions):
                selected = request.POST.get(f"q{i}")
                is_correct = selected == q["correct"]
                if is_correct:
                    score += 1
                results.append({
                    "question": q["question"],
                    "your_answer": dict(q["options"]).get(selected, ""),
                    "correct": dict(q["options"]).get(q["correct"], ""),
                    "is_correct": is_correct
                })

            return render(request, "quiz/ai_quiz.html", {
                "score": score,
                "results": results,
                "subject": subject,
                "level": level,
                "question_count": question_count,
                "show_quiz": False,
                "show_results": True
            })

    # Default (GET or invalid POST)
    return render(request, "quiz/ai_quiz.html", {
        "show_quiz": False,
        "show_results": False
    })


from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Task

@require_POST
def make_task_active(request, task_id):
    Task.objects.filter(user=request.user, is_active=True).update(is_active=False)
    Task.objects.filter(pk=task_id, user=request.user).update(is_active=True)
    return JsonResponse({'status': 'success'})

@require_POST
def toggle_task_pinned(request, task_id):
    task = Task.objects.get(pk=task_id, user=request.user)
    task.is_pinned = not task.is_pinned
    task.save()

    return JsonResponse({'status': 'success'})






# views.py
def get_active_task(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    # Get the currently active task with its subtasks
    active_task = Task.objects.filter(
        user=request.user,
        is_active=True
    ).prefetch_related('subtasks').first()
    
    if active_task:
        subtasks = []
        for subtask in active_task.subtasks.all():
            subtasks.append({
                'id': subtask.id,
                'title': subtask.title,
              
                'is_completed': subtask.completed,
               
            })
        
        return JsonResponse({
            'task': {
                'id': active_task.id,
                'title': active_task.title,
                'description': active_task.description,
                'priority': active_task.priority,
                'get_priority_display': active_task.get_priority_display(),
                'due_date': active_task.due_date.strftime('%Y-%m-%d %H:%M'),
                'subtasks': subtasks
            }
        })
    
    return JsonResponse({'message': 'No active task'})
