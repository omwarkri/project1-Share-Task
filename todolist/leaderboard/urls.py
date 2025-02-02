from django.urls import path
from .views import leaderboard

urlpatterns = [
    # Other URL patterns
    path('leaderboard/', leaderboard, name='leaderboard'),
]