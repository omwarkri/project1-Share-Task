from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from .models import Like, Comment, Task
from .forms import CommentForm

@login_required
def like_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    like, created = Like.objects.get_or_create(user=request.user, task=task)
    
    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    like_count = task.likes.count()
    return JsonResponse({'liked': liked, 'like_count': like_count})

@require_POST
@login_required
def add_comment(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    form = CommentForm(request.POST)
    
    if form.is_valid():
        comment = form.save(commit=False)
        comment.task = task
        comment.user = request.user
        comment.save()
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
    return JsonResponse({
        'success': False,
        'error': 'Invalid form data.',
    }, status=400)

@login_required
def get_comments(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    comments = task.comments.all().values('id', 'text', 'user__username', 'created_at')
    return JsonResponse({
        'success': True,
        'comments': list(comments),
    })