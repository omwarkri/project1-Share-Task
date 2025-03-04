from django.urls import path
from . import views

urlpatterns = [
    # Other URLs...
    path('chat/<int:task_id>/', views.chat_view, name='chat'),
    path('fetch-all-chats/', views.fetch_all_chats, name='fetch_all_chats'),
    path('team/<int:team_id>/send-message/', views.send_message, name="send_message"),
    path('team/<int:team_id>/chat/', views.team_chatroom, name="team_chat"),
    path('team/<int:team_id>/messages/', views.get_messages, name="get_messages"),
  
]
