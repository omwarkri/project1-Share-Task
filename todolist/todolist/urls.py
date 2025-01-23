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
from task.views import home,add_task, change_task_status,delete_task,task_detail,edit_task
from rest_framework_simplejwt import views as jwt_views
from user.views import ProtectedView 
from django.contrib.auth.views import LogoutView
urlpatterns = [
    path('admin/', admin.site.urls),
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
]


