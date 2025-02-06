
from django.contrib import admin
from django.urls import path,include
from .views import search_tasks,update_task_dependencies,get_task_dependencies

urlpatterns = [

    path('search-tasks/', search_tasks, name='search_tasks'),
    path('update-task-dependencies/<int:task_id>/', update_task_dependencies, name='update_task_dependencies'),
    path('get-task-dependencies/<int:task_id>/', get_task_dependencies, name='get_task_dependencies'),
  
]
