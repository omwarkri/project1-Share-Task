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

from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Message

from django.db.models import Q
from django.http import JsonResponse





from django.db.models import Q, Max
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from django.db.models import Q, Max
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def fetch_all_chats(request):
    print("Fetching unique receiver-task pairs...")

    user = request.user

    # Get the latest message per (receiver, task) pair
    latest_messages = (
        Message.objects.filter(Q(sender=user) | Q(receiver=user), task__isnull=False)
        .values("receiver", "task")  # Get only receiver-task pairs
        .annotate(latest_timestamp=Max("timestamp"))  # Get the latest timestamp per pair
    )

    # Fetch actual messages using the latest timestamp
    unique_chats = Message.objects.filter(
        Q(sender=user) | Q(receiver=user),
        task__isnull=False,
        timestamp__in=[entry["latest_timestamp"] for entry in latest_messages],
    ).select_related("sender", "receiver", "task").order_by("-timestamp")

    # Format response
    context = {}
    
    for msg in unique_chats:
        # Ensure we always get the other user in the chat (not the logged-in user)
        chat_user = msg.receiver if msg.sender == user else msg.sender
        task_id = msg.task.id
        chat_key = (chat_user.id, task_id)  # Ensure unique (user, task) pairs

        if chat_key not in context:
            context[chat_key] = {
                "user": {
                    "id": chat_user.id,
                    "username": chat_user.username,
                },
                "task_id": task_id,
                "last_message": msg.content,
                "timestamp": msg.timestamp,
                "attachment_url": msg.attachment.url if msg.attachment else None,
            }

    return JsonResponse({'chats': list(context.values())})



from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import TeamChat 
from task.models import Team
from django.views.decorators.csrf import csrf_exempt
import json


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
import json

@login_required
@csrf_exempt
def send_message(request, team_id):
    if request.method == "POST":
        data = json.loads(request.body)
        message_text = data.get("message")
        sender = request.user  # Get the logged-in user

        if message_text:
            message = TeamChat.objects.create(
                team_id=team_id, sender=sender, message=message_text, created_at=now()
            )
            print(message)
            return JsonResponse({"message": message.message, "sender": sender.username}, status=201)
    return JsonResponse({"error": "Invalid request"}, status=400)



@login_required
def get_messages(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    messages = TeamChat.objects.filter(team=team).order_by("-created_at")[:50]  # Get last 50 messages

    return JsonResponse([
        {
            "id": msg.id,
            "message": msg.message,
            "sender": msg.sender.username,
            "created_at": msg.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for msg in messages
    ], safe=False)


@login_required
def team_chatroom(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    messages = TeamChat.objects.filter(team=team).order_by("created_at")

    return render(request, "chatroom.html", {"team": team, "messages": messages})

