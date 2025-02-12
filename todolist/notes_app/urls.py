
from django.contrib import admin
from django.urls import path,include
from .views import add_task_note,get_task_notes,update_task_note

urlpatterns = [
     path('task/<int:task_id>/add_note/', add_task_note, name='add_task_note'),

    path('task/<int:task_id>/notes/', get_task_notes, name='get_task_notes'),
     path('update-task-note/<int:note_id>/', update_task_note, name='update_task_note'),
]