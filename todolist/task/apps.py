from django.apps import AppConfig
import sys

class TaskConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "task"

    def ready(self):
        """Run only if not in migrations or management commands"""
        if "runserver" in sys.argv or "celery" in sys.argv:
            from .tasks import start_scheduler  # Import only when necessary
            start_scheduler()

        import task.signals  # Import signals to register them
