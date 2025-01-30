from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from user.models import CustomUser
from task.models import Task
from .models import Message

@login_required
def chat_view(request, user_id):
    # Fetch the receiver user or return a 404 if not found
    receiver = get_object_or_404(CustomUser, id=user_id)

    # Get task-related details (optional task_id and task_title query parameters)
    task_id = request.GET.get("task_id")
    task_title = request.GET.get("task_title")
    task = Task.objects.filter(id=task_id).first() if task_id else None

    print(task_id)

    # Retrieve messages between the sender (logged-in user) and receiver
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=receiver)) |
        (Q(sender=receiver) & Q(receiver=request.user))
    ).order_by('timestamp')

    # Handle message sending
    if request.method == "POST":
        content = request.POST.get("content", "")
        attachment = request.FILES.get("attachment")  # Handle file attachment
        if content or attachment:  # Ensure at least one field is provided
            Message.objects.create(sender=request.user, receiver=receiver, content=content, attachment=attachment)
        return redirect(f"{request.path}?task_id={task_id}&task_title={task_title}")
    print(task,task_title)
    # Render the chat template with messages, receiver, and task
    return render(request, "chat.html", {
        "receiver": receiver,
        "messages": messages,
        "task": task,
        "task_title": task_title  # Add task_title to the context for use in the template
    })
