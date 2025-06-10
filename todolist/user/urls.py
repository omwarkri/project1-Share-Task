from django.urls import path
from . import views
from .views import UserRegistrationView, CustomTokenObtainPairView, ProtectedView, get_user_analytics,download_task_report, download_task_report_pdf
from .views import *


urlpatterns = [
   
    path('login/', views.login_view, name='login'),
    path('login/<str:token>/', views.login_view, name='login_with_token'),
    path('register/', views.register_view, name='register'),
    path('register/<str:token>/', views.register_view, name='register_with_token'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/<int:user_id>/', views.profile_view_id, name='view_profile_id'),
    path('followers/<int:user_id>/', followers_list, name='followers_list'),
    path('following/<int:user_id>/', following_list, name='following_list'),
    path('follow-user/<int:user_id>/', views.follow_user, name='follow_user'),
    path('api/user-analytics/', get_user_analytics, name='user-analytics'),
    path('download-report/<str:report_type>/', download_task_report, name='download_task_report'),
    path('download-report/pdf/<str:report_type>/', download_task_report_pdf, name='download_task_report_pdf'),
    path('api/register/', UserRegistrationView.as_view(), name='user_register'),  # User registration
    path('api/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'), 
    path('api/protected/', ProtectedView.as_view(), name='protected_view'),
    path('api/update-interests-goals/', update_user_interests_goals, name='update_interests_goals'), 
    path('increment-pomodoro/', views.increment_pomodoro_count, name='increment_pomodoro'),
    path('api/daily-challenges/', views.get_daily_challenges, name='daily-challenges'),
    path('api/accept-challenge/', views.accept_challenge, name='accept-challenge'),
    path('api/update-challenge-progress/', views.update_challenge_progress, name='update_challenge_progress'),
     path('api/schedule/', views.get_schedule, name='get_schedule'),
    path('api/schedule/save/', views.save_schedule, name='save_schedule'),
   
]
