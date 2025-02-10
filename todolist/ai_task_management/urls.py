from django.urls import path
from . import views

urlpatterns = [
    path('ai-task-management/<int:task_id>/', views.chat_ai_view, name='ai_task_management'),
]
