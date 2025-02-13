
from django.contrib import admin
from django.urls import path,include
from .views import search_tasks,update_task_dependencies,get_task_dependencies,add_task_note,generate_ai_procedure
from .views import *
urlpatterns = [

    path('search-tasks/', search_tasks, name='search_tasks'),
    path('update-task-dependencies/<int:task_id>/', update_task_dependencies, name='update_task_dependencies'),
    path('get-task-dependencies/<int:task_id>/', get_task_dependencies, name='get_task_dependencies'),
   
    path('generate-ai-procedure/<int:task_id>/', generate_ai_procedure, name='generate_ai_procedure'),

    path("api/tasks/<int:task_id>/subtasks/", get_subtasks),
    path("api/tasks/<int:task_id>/subtasks/add/", add_subtask),
    path("api/subtasks/<int:subtask_id>/toggle/", toggle_subtask),
  
]
