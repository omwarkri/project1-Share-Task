from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Message

@receiver(post_save, sender=Message)
def send_message_notification(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        channel_layer = get_channel_layer()
        if channel_layer is None:
            print("❌ Channel layer not found!")  # ✅ Debugging statement
            return
        print("✅ Channel layer is available.")
        print(instance)
        receiver= instance.receiver.username
        sender = instance.sender.username
        task_id=instance.task.id
        print("sending through signal" , receiver, sender)
        # Define the unique room name for the sender and receiver
        room_name = f"chat_{task_id}"
        print(room_name,"sending to receiver")
        async_to_sync(channel_layer.group_send)(
            room_name,
            {
                "type": "chat_message",
                "message": instance.content,
                "sender": sender,
                "receiver": receiver,
                "timestamp": instance.timestamp.isoformat(),
                "attachment": instance.attachment.url if instance.attachment else None
            }
        )
