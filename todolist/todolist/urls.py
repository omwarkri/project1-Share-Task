"""
URL configuration for todolist project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from task.views import home,add_task, change_task_status,delete_task,task_detail,edit_task,complete_task,suggested_users,add_subtask,toggle_subtask,add_allowed_user,remove_allowed_user,add_task_partner,remove_task_partner
from rest_framework_simplejwt import views as jwt_views
from user.views import ProtectedView 
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.core.management import call_command

from django.contrib.auth import get_user_model
from django.http import HttpResponse

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

def create_superuser(request):
    User = get_user_model()
    username = "admin"
    email = "admin@example.com"
    password = "adminpass"

    if not User.objects.filter(username=username).exists():
        user = User.objects.create_superuser(username=username, email=email, password=password)
        return HttpResponse("Superuser created successfully.")
    else:
        return HttpResponse("Superuser already exists.")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('create-superuser/', create_superuser),  # Temporary endpoint
    path('user/',include('user.urls')),
    path('user/logout/', LogoutView.as_view(), name='logout'),
    path('', home,name='home'),
    path('add-task/', add_task, name='add_task'),
    path('change-status/<int:task_id>/<str:new_status>/', change_task_status, name='change_task_status'),
    path('delete/<int:task_id>/', delete_task, name='delete_task'),
    path('task/<int:task_id>/', task_detail, name='task_detail'),
    path('edit/<int:task_id>/', edit_task, name='edit_task'),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('',include('subscription.urls')),
    path('',include('chat.urls')),
    path('',include('leaderboard.urls')),
    path('',include('task.urls')),
    path('share-task/<int:task_id>/', complete_task, name='complete_task'),
    path('task/<int:task_id>/suggested_users/', suggested_users, name='suggested_users'),
    path('task/<int:task_id>/add_subtask/', add_subtask, name='add_subtask'),
    path('subtask/<int:subtask_id>/toggle/', toggle_subtask, name='toggle_subtask'),
    path('task/<int:task_id>/add-allowed-user/<int:user_id>/', add_allowed_user, name='add_allowed_user'),
    path('task/<int:task_id>/remove-allowed-user/<int:user_id>/', remove_allowed_user, name='remove_allowed_user'),
    path('task/<int:task_id>/add_task_partner/<int:user_id>/', add_task_partner, name='add_task_partner'),
    path('task/<int:task_id>/remove_task_partner/', remove_task_partner, name='remove_task_partner'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Obtain JWT token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


