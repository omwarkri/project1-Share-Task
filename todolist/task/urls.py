
from django.contrib import admin
from django.urls import path,include
from .views import search_tasks,update_task_dependencies,get_task_dependencies,add_task_note,generate_ai_procedure
from .views import *
from .views import team_leaderboard
urlpatterns = [

     

    path('search-tasks/', search_tasks, name='search_tasks'),
    path('update-task-dependencies/<int:task_id>/', update_task_dependencies, name='update_task_dependencies'),
    path('get-task-dependencies/<int:task_id>/', get_task_dependencies, name='get_task_dependencies'),
   
    path('generate-ai-procedure/<int:task_id>/', generate_ai_procedure, name='generate_ai_procedure'),

    path("api/tasks/<int:task_id>/subtasks/", get_subtasks),
    path("api/tasks/<int:task_id>/subtasks/add/", add_subtask),
    path("api/subtasks/<int:subtask_id>/toggle/", toggle_subtask),


    path('teams/', teams_list, name='teams_list'),  # Show all teams
    path('teams/<int:team_id>/', view_team_tasks, name='view_team_tasks'),  # Show tasks for a team
    path("accept-invite/<str:token>/", accept_invite, name="accept_invite"),
    path('teams/create/', create_team, name='create_team'),
    path('teams/<int:team_id>/leaderboard/', team_leaderboard, name='team_leaderboard'),
    path("teams/<int:team_id>/invite/", send_team_invite, name="send_team_invite"),
    path('team/<int:team_id>/member-analysis/<int:member_id>/', member_analysis, name='member_analysis'),
    path("tasks/escalate/<int:task_id>/", escalate_task, name="escalate_task"),
    path("tasks/<int:task_id>/reassign/", reassign_task, name="reassigned_task"),
    
    
  
]
