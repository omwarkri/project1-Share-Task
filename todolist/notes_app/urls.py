
from django.contrib import admin
from django.urls import path,include
from .views import add_task_note,get_task_notes

urlpatterns = [
     path('task/<int:task_id>/add_note/', add_task_note, name='add_task_note'),

    path('task/<int:task_id>/notes/', get_task_notes, name='get_task_notes'),
]