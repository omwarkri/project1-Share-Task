
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
                'username': note.user.username if note.user else 'Anonymous',
                'note_text': note.note_text,
                'created_at': note.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for note in notes
        ]
        return JsonResponse({'status': 'success', 'notes': notes_list})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
