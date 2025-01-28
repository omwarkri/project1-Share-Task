from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from user.models import CustomUser
from .models import Message

@login_required
def chat_view(request, user_id):
    # Fetch the receiver user or return a 404 if not found
    receiver = get_object_or_404(CustomUser, id=user_id)

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
        return redirect('chat', user_id=user_id)

    # Render the chat template with messages and receiver
    return render(request, "chat.html", {"receiver": receiver, "messages": messages})
