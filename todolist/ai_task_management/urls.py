from django.urls import path
from . import views

urlpatterns = [
    path('ai-task-management/<int:task_id>/', views.ai_taskmanagement_view, name='ai_task_management'),
    path('chat_ai_view/<int:task_id>/', views.chat_ai_view, name='chat_ai_view'),
  
  
]
