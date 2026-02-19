from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from .models import Task, ActivityLog
import json

@require_POST
@csrf_protect
@login_required
def mark_task_visited(request):
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        task = Task.objects.prefetch_related('subtasks__microtasks').get(id=task_id, user=request.user)
        task.last_visited_at = timezone.now()
        task.save()

        subtasks = []
        for subtask in task.subtasks.all():
            microtasks = []
            for microtask in subtask.microtasks.all():
                microtasks.append({
                    'id': microtask.id,
                    'title': microtask.title,
                    'is_completed': microtask.completed,
                })
            subtasks.append({
                'id': subtask.id,
                'title': subtask.title,
                'is_completed': subtask.completed,
                'microtasks': microtasks,
            })

        return JsonResponse({
            'status': 'success',
            'message': 'Task marked as visited',
            'task': {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'priority': task.priority,
                'get_priority_display': task.get_priority_display(),
                'due_date': task.due_date.strftime('%Y-%m-%d %H:%M'),
                'subtasks': subtasks,
            }
        })
    except Task.DoesNotExist:
        return JsonResponse({'message': 'No active task'}, status=404)

@login_required
@require_POST
def make_task_active(request, task_id):
    try:
        task = Task.objects.filter(pk=task_id, user=request.user).first()
        if not task:
            return JsonResponse({'status': 'failed', 'error': 'Task not found or unauthorized'}, status=400)

        with transaction.atomic():
            Task.objects.filter(user=request.user, is_active=True).update(is_active=False)
            task.is_active = True
            task.save()

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@require_POST
@login_required
def toggle_task_pinned(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    task.is_pinned = not task.is_pinned
    task.save()
    return JsonResponse({'status': 'success'})

@login_required
def change_task_status(request, task_id, new_status):
    task = get_object_or_404(Task, id=task_id)
    task.status = new_status
    UserActivity.objects.get_or_create(user=task.user, activity_date=date.today(), activity_type='Task updated')
    task.save()
    return redirect('home')