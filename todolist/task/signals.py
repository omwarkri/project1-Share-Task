from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Count, Avg, F, DurationField, ExpressionWrapper
from django.db.models.functions import Coalesce
from .models import Task    
from user.models import UserTaskAnalytics

@receiver([post_save, post_delete], sender=Task)
def update_user_task_analytics(sender, instance, **kwargs):
    """Updates analytics when a task is created, updated, or deleted."""
    user = instance.user
    tasks = Task.objects.filter(user=user)

    completed_tasks = tasks.filter(status='completed')
    overdue_tasks = tasks.filter(due_date__lt=timezone.now(), status__in=['pending', 'in_progress'])

    # Calculate average task completion time
    avg_completion_time = completed_tasks.aggregate(
        avg_time=Coalesce(
            Avg(ExpressionWrapper(F('updated_at') - F('created_at'), output_field=DurationField())),
            timezone.timedelta(seconds=0)  # Default value instead of 0
        )
    )['avg_time']

    # Find the most common category
    most_common_category = tasks.values('category').annotate(count=Count('category')).order_by('-count').first()
    
    # Ensure analytics entry exists, or create one
    analytics, created = UserTaskAnalytics.objects.update_or_create(
        user=user,
        defaults={
            'total_tasks': tasks.count(),
            'completed_tasks': completed_tasks.count(),
            'overdue_tasks': overdue_tasks.count(),
            'average_completion_time': avg_completion_time.total_seconds() / 3600 if avg_completion_time else 0,
            'most_common_category': most_common_category['category'] if most_common_category else None
        }
    )
