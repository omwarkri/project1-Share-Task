from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Count, Avg, F, DurationField, ExpressionWrapper
from django.db.models.functions import Coalesce
from sentence_transformers import SentenceTransformer
from .models import Task
from user.models import UserTaskAnalytics

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))


# Load model once at startup
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
def preprocess_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)  # Remove special characters
    words = text.split()
    words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]
    
    # Ensure at least 3 words remain (to avoid over-filtering)
    if len(words) < 3:
        return text.lower()  # Return original text if preprocessing removes too much
    
    return " ".join(words)


@receiver([post_save, post_delete], sender=Task)
def update_user_task_analytics(sender, instance, **kwargs):
    """Updates analytics when a task is created, updated, or deleted."""
    user = instance.user
    tasks = Task.objects.filter(user=user)

    completed_tasks = tasks.filter(status="completed")
    overdue_tasks = tasks.filter(due_date__lt=timezone.now(), status__in=["pending", "in_progress"])

    # Calculate average task completion time
    avg_completion_time = completed_tasks.aggregate(
        avg_time=Coalesce(
            Avg(ExpressionWrapper(F("updated_at") - F("created_at"), output_field=DurationField())),
            timezone.timedelta(seconds=0),  # Default value instead of 0
        )
    )["avg_time"]

    # Find the most common category
    most_common_category = tasks.values("category").annotate(count=Count("category")).order_by("-count").first()

    # Ensure analytics entry exists, or create one
    UserTaskAnalytics.objects.update_or_create(
        user=user,
        defaults={
            "total_tasks": tasks.count(),
            "completed_tasks": completed_tasks.count(),
            "overdue_tasks": overdue_tasks.count(),
            "average_completion_time": avg_completion_time.total_seconds() / 3600 if avg_completion_time else 0,
            "most_common_category": most_common_category["category"] if most_common_category else None,
        },
    )


@receiver(post_save, sender=Task)
def handle_task_creation(sender, instance, created, **kwargs):
    """
    Handles various actions when a task is created or updated:
    - Generates a vector embedding for shareable tasks.
    - Sends an email when a task is assigned or escalated.
    """
    if created and instance.shareable:
        # Generate and store vector
        task_text = f"{instance.title} {instance.description or ''}"
        vector = model.encode(task_text).tolist()
        instance.vector = vector
        instance.save(update_fields=["vector"])

    # Send email notifications
    if created:
        if instance.assigned_to:
            send_assignment_email(instance, instance.assigned_to)
    else:
        if instance.escalated_to and instance.status == "escalated":
            send_escalation_email(instance, instance.escalated_to, instance.escalation_reason)
        elif instance.assigned_to:
            send_assignment_email(instance, instance.assigned_to)






# tasks/utils.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_assignment_email(task, assigned_user):
    """
    Send an email to the assigned user.
    """
    subject = f"Task Assigned: {task.title}"
    html_message = render_to_string('emails/task_assignment.html', {
        'task': task,
        'assigned_user': assigned_user,
    })
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    to_email = assigned_user.email

    send_mail(
        subject,
        plain_message,
        from_email,
        [to_email],
        html_message=html_message,
    )

def send_escalation_email(task, escalated_user, reason):
    """
    Send an email to the escalated user.
    """
    subject = f"Task Escalation: {task.title}"
    html_message = render_to_string('emails/task_escalation.html', {
        'task': task,
        'escalated_user': escalated_user,
        'reason': reason,
    })
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    to_email = escalated_user.email

    send_mail(
        subject,
        plain_message,
        from_email,
        [to_email],
        html_message=html_message,
    )