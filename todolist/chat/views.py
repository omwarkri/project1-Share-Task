from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from user.models import CustomUser
from task.models import Task
from .models import Message
from django.http import HttpResponseBadRequest



@login_required
def chat_view(request, receiver_id):
    # Validate the receiver ID
    if not receiver_id:
        return HttpResponseBadRequest("Receiver ID is missing or invalid.")

    # Fetch the receiver user or return 404 if not found
    receiver = get_object_or_404(CustomUser, id=receiver_id)

    # Get optional task parameters from query strings
    task_id = request.GET.get('task_id')
    task_title = request.GET.get('task_title')

    # Fetch the task if task_id is provided and valid
    task = Task.objects.filter(id=task_id).first() if task_id and task_id != 'None' else None

    # Fetch chat messages between the logged-in user and receiver
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=receiver)) |
        (Q(sender=receiver) & Q(receiver=request.user))
    ).order_by('timestamp')

    # Handle message sending
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        attachment = request.FILES.get("attachment")

        # Save message only if content or attachment is provided
        if content or attachment:
            Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content,
                attachment=attachment
            )
        # Redirect to maintain query params after sending a message
        if task_id :
            return redirect(f"{request.path}?task_id={task_id or ''}&task_title={task_title or ''}")
        return redirect(f"{request.path}")

    # Render the chat template
    return render(request, "chat.html", {
        "receiver": receiver,
        "messages": messages,
        "task": task,
        "task_title": task_title
    })



from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Message
from django.db.models import Q 

@login_required
def all_chats(request):
    user = request.user
    
    # Fetch distinct conversations by grouping messages
    conversations = Message.objects.filter(
        Q(sender=user) | Q(receiver=user)  # ✅ No need for models.Q, just Q
    ).order_by('-timestamp')

    # Group by unique chat participants
    grouped_chats = {}
    for message in conversations:
        contact = message.receiver if message.sender == user else message.sender
        if contact not in grouped_chats:
            grouped_chats[contact] = message

    context = grouped_chats.values()
    for i in context:
        print(i.receiver.id)

    return grouped_chats.values()
