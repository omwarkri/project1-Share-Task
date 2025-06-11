from django.urls import path
from . import views

urlpatterns = [
    path('ai-task-management/<int:task_id>/', views.ai_taskmanagement_view, name='ai_task_management'),
    path('chat_ai_view/<int:task_id>/', views.chat_ai_view, name='chat_ai_view'),

    path("api/tasks/<int:task_id>/subtasks/ai_suggestions/", views.ai_subtask_suggestions, name="ai_subtask_suggestions"),



    path("api/tasks/<int:task_id>/microtasks/", views.get_microtasks),
    path("api/tasks/<int:task_id>/microtasks/add/", views.add_microtask),
    path("api/microtasks/<int:microtask_id>/toggle/", views.toggle_microtask),
    path("api/microtasks/<int:microtask_id>/delete/", views.delete_microtask),
    path("api/microtasks/<int:microtask_id>/update/", views.update_microtask),
    path("api/tasks/<int:subtask_id>/microtasks/ai_suggestions/", views.generate_microtasks_for_each_subtask),

    path('microtask/<int:microtask_id>/instructions/', views.get_microtask_instructions, name='microtask_instructions'),

   
  
  
]
    