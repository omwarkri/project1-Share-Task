from django.urls import path
from . import views

urlpatterns = [
    # Other URLs...
    path('chat/<int:user_id>/', views.chat_view, name='chat'),
]
