from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

from django.conf import settings  # Import settings to use AUTH_USER_MODEL

class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def is_subscription_valid(self):
        return self.is_active and (self.end_date is None or self.end_date > now())
