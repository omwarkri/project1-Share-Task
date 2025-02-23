from django.apps import AppConfig

class TaskConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "task"

    def ready(self):
        from .tasks import start_scheduler  # Move import here
        start_scheduler()
