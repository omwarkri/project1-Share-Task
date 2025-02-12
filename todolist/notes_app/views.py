
# views.py
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import TaskNotes

@csrf_exempt
def add_task_note(request, task_id):
    print(task_id)
    if request.method == 'POST':
        data = json.loads(request.body)
        note_text = data.get('note_text')
        print(note_text)
        # Save the note (example logic)
        note = TaskNotes.objects.create(
            task_id=task_id,
            note_text=note_text,
            user=request.user if request.user.is_authenticated else None
        )

        return JsonResponse({
            'status': 'success',
            'username': note.user.username if note.user else 'Anonymous',
            'note_text': note.note_text,
            'created_at': note.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


from django.http import JsonResponse
from .models import TaskNotes
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def get_task_notes(request, task_id):
    if request.method == 'GET':
        notes = TaskNotes.objects.filter(task_id=task_id).order_by('-created_at')  # Fetch latest notes first
        notes_list = [
            {
                'id':note.id,
                'username': note.user.username if note.user else 'Anonymous',
                'note_text': note.note_text,
                'created_at': note.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for note in notes
        ]
        print(notes_list)
        return JsonResponse({'status': 'success', 'notes': notes_list})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
import json
from .models import TaskNotes

@csrf_exempt
@require_http_methods(["POST"])
def update_task_note(request, note_id):
    """Update an existing task note."""
    try:
        data = json.loads(request.body)
        note_text = data.get('note_text', '').strip()

        if not note_text:
            return JsonResponse({'status': 'error', 'message': 'Note text cannot be empty'}, status=400)

        note = get_object_or_404(TaskNotes, id=note_id)

        note.note_text = note_text
        note.save()

        return JsonResponse({'status': 'success', 'message': 'Note updated successfully'})
    
    except TaskNotes.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Note not found'}, status=404)
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

