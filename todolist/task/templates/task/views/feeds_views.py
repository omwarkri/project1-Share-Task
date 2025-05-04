from django.shortcuts import render
from django.db.models import Count
from concurrent.futures import ThreadPoolExecutor
from .models import Task, TaskCompletionDetails, User
from .decorators import execution_time_logger

def fetch_completed_tasks():
    return Task.objects.filter(status='completed').select_related('completion_details')

def fetch_top_users():
    return User.objects.annotate(follower_count=Count('followers')).order_by('-follower_count')[:5]

@execution_time_logger
def completed_tasks_feed(request):
    filter_type = request.GET.get('filter_type')

    with ThreadPoolExecutor() as executor:
        future_tasks = executor.submit(fetch_completed_tasks)
        future_users = executor.submit(fetch_top_users)

        completed_tasks = future_tasks.result()
        top_users = future_users.result()

    task_feed_data = []

    for task in completed_tasks:
        completion_details = getattr(task, 'completion_details', None)
        if not completion_details:
            continue

        if (
            (filter_type == 'detail' and completion_details.has_details()) or
            (filter_type == 'video' and completion_details.has_uploaded_file()) or
            (filter_type == 'post' and completion_details.has_files()) or
            (filter_type == 'image' and completion_details.has_uploaded_image()) or
            (filter_type == 'feedback' and completion_details.has_partner_feedback()) or
            (not filter_type)
        ):
            task_feed_data.append({'task': task, 'completion_details': completion_details})

    return render(request, 'feed/completed_tasks_feed.html', {
        'task_feed_data': task_feed_data,
        'filter_type': filter_type,
        'top_users': top_users,
    })