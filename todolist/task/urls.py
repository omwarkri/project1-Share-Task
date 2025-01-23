
from django.contrib import admin
from django.urls import path,include
from .views import home,add_task

urlpatterns = [
    path('',home),
    
  
]
