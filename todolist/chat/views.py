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



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Team, TeamChat  # Import your Team and TeamChat models
import json

@login_required
@csrf_exempt
def send_message(request, team_id):
    if request.method == "POST":
        try:
            # Fetch the Team object using team_id
            try:
                team = Team.objects.get(id=team_id)
            except Team.DoesNotExist:
                return JsonResponse({"error": "Team does not exist"}, status=404)

            # Get the message and attachment from the request
            message_text = request.POST.get("message")
            attachment = request.FILES.get("attachment")  # Get the uploaded file

            if not message_text and not attachment:
                return JsonResponse({"error": "Message or attachment is required"}, status=400)

            # Create and save the TeamChat object
            message = TeamChat.objects.create(
                team=team,  # Associate the message with the team
                sender=request.user,
                message=message_text,
                attachment=attachment,  # Save the attachment (if any)
                created_at=timezone.now()  # Use Django's timezone handling
            )

            # Prepare the response data
            response_data = {
                "message": message.message,
                "sender": message.sender.username,
                "created_at": message.created_at.isoformat(),
            }

            # Include the attachment URL in the response (if an attachment was uploaded)
            if message.attachment:
                response_data["attachment_url"] = message.attachment.url

            return JsonResponse(response_data, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


from django.http import JsonResponse


@login_required
def get_messages(request, team_id):
    messages = TeamChat.objects.filter(team_id=team_id).order_by("created_at")

    return JsonResponse([
        {
            "id": msg.id,
            "sender": msg.sender.username,
            "message": msg.message,
            "attachment": msg.attachment.url if msg.attachment else None,  # Convert FieldFile to URL
            "created_at": msg.created_at,
        }
        for msg in messages
    ], safe=False)



@login_required
def team_chatroom(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    messages = TeamChat.objects.filter(team=team).order_by("created_at")

    return render(request, "chatroom.html", {"team": team, "messages": messages})

