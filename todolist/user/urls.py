from django.urls import path
from . import views
from .views import UserRegistrationView, CustomTokenObtainPairView, ProtectedView, get_user_analytics,download_task_report, download_task_report_pdf


urlpatterns = [
   
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/<int:user_id>/', views.profile_view_id, name='view_profile_id'),
    path('api/user-analytics/', get_user_analytics, name='user-analytics'),
    path('download-report/<str:report_type>/', download_task_report, name='download_task_report'),
    path('download-report/pdf/<str:report_type>/', download_task_report_pdf, name='download_task_report_pdf'),
    path('api/register/', UserRegistrationView.as_view(), name='user_register'),  # User registration
    path('api/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'), 
    path('api/protected/', ProtectedView.as_view(), name='protected_view'), 
]
