from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Badge, UserBadge

@receiver(post_save, sender=CustomUser)
def check_score_for_badges(sender, instance, **kwargs):
    eligible_badges = Badge.objects.filter(min_score__lte=instance.score)
    for badge in eligible_badges:
        UserBadge.objects.get_or_create(user=instance, badge=badge)
