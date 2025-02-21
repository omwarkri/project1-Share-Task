from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from user.models import CustomUser
from task.models import Task
from .models import Message
from django.http import HttpResponseBadRequest
from django.http import JsonResponse


@login_required
def chat_view(request, task_id):
    # Validate the receiver ID
    if not task_id:
        return HttpResponseBadRequest("Receiver ID is missing or invalid.")
    receiver_id = request.GET.get('receiver_id')
    # Fetch the receiver user or return 404 if not found
    receiver = get_object_or_404(CustomUser, id=receiver_id)

    # Get optional task parameters from query strings
    
    print(task_id)
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
        message_text = request.POST.get("message")
        receiver = CustomUser.objects.get(id=receiver_id)
        attachment = request.FILES.get('attachment')


        if message_text.strip() or attachment:
            message = Message.objects.create(sender=request.user, task=task, receiver=receiver,  content=message_text,attachment=attachment)
            print(message,"these is message")
            return JsonResponse({"success": True, "message": message.content})

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
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Message

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from chat.models import Message

@login_required
def all_chats(request):
    user = request.user

    # Fetch messages where the user is either the sender or receiver
    conversations = Message.objects.filter(
        Q(sender=user) | Q(receiver=user)
    ).order_by('-timestamp')

    # Dictionary to store grouped conversations
    grouped_chats = {}

    for message in conversations:
        # Ensure the receiver is NOT the logged-in user
        contact = message.receiver if message.sender == user else message.sender
        if contact.id == user.id:  # This should never happen, but just in case
            continue

        task_id = message.task.id if message.task else None  # Handle messages with no task
        chat_key = (contact.id, task_id)  # Unique key: (User ID, Task ID)

        # Store only the latest message for each unique (contact, task_id) chat
        if chat_key not in grouped_chats:
            # Add receiver_id dynamically
            message.receiver_id = contact.id
            grouped_chats[chat_key] = message  

    # Get list of latest messages for each chat
    context = list(grouped_chats.values())

    # Debugging output (optional)
    for msg in context:
        print(f"Chat with User {msg.receiver_id}, Task ID: {msg.task.id if msg.task else 'No Task'}")

    return context









