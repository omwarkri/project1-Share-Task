from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import SubTask
import json

@csrf_exempt
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
    try:
        subtask = SubTask.objects.get(id=subtask_id)
        subtask.completed = not subtask.completed
        subtask.save()
        microtasks = subtask.microtasks.all()
        microtasks.update(completed=subtask.completed)
        return JsonResponse({
            "status": "success",
            "id": subtask.id,
            "completed": subtask.completed,
            "updated_microtasks": list(microtasks.values_list('id', flat=True)),
        })
    except SubTask.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Subtask not found"}, status=404)

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