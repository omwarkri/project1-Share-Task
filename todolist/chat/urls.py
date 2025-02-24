from django.urls import path
from . import views

urlpatterns = [
    # Other URLs...
    path('chat/<int:task_id>/', views.chat_view, name='chat'),
    path('fetch-all-chats/', views.fetch_all_chats, name='fetch_all_chats'),
]
