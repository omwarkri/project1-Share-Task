from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Badge, UserBadge

@receiver(post_save, sender=CustomUser)
def check_score_for_badges(sender, instance, **kwargs):
    eligible_badges = Badge.objects.filter(min_score__lte=instance.score)
    for badge in eligible_badges:
        UserBadge.objects.get_or_create(user=instance, badge=badge)




# @receiver(pre_delete, sender=CustomUser)
# def delete_analytics_on_user_delete(sender, instance, **kwargs):
#     """Ensure UserTaskAnalytics is deleted before the user is removed."""
#     try:
#         if hasattr(instance, "task_analytics"):
#             instance.task_analytics.delete()
#     except UserTaskAnalytics.DoesNotExist:
#         pass

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, UserTaskAnalytics

@receiver(post_save, sender=CustomUser)
def create_user_analytics(sender, instance, created, **kwargs):
    if created:
        UserTaskAnalytics.objects.get_or_create(user=instance)

