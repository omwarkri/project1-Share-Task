from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Team, TeamInvitation, TeamScoreboard
from .forms import TeamForm, AddMemberForm, TeamTaskForm, ReassignTaskForm, EscalateTaskForm
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models import Count, Q
import json

User = get_user_model()

@login_required
def create_team(request):
    if request.method == "POST":
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.created_by = request.user
            team.save()
            team.members.add(request.user)
            return redirect("team_list")
    else:
        form = TeamForm()
    return render(request, "teams/create_team.html", {"form": form})

@login_required
def teams_list(request):
    if request.method == "POST":
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.created_by = request.user
            team.save()
            team.members.add(request.user)
            return redirect('teams_list')

    teams = Team.objects.filter(
        Q(members=request.user) | Q(created_by=request.user)
    ).distinct()
    form = TeamForm()

    teams_data = [
        {
            'id': team.id,
            'name': team.name,
            'description': team.description,
            'created_by': team.created_by.username,
            'members': [member.username for member in team.members.all()],
        }
        for team in teams
    ]
    return JsonResponse({'teams': teams_data})

@login_required
def view_team_tasks(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    tasks = Task.objects.filter(team=team)
    add_member_form = AddMemberForm()
    task_form = TeamTaskForm()
    reassigned_task_form = ReassignTaskForm()
    escualeted_reason_form = EscalateTaskForm()

    if request.method == "POST":
        if "add_member" in request.POST:
            add_member_form = AddMemberForm(request.POST)
            if add_member_form.is_valid():
                user = add_member_form.cleaned_data['user']
                if user not in team.members.all():
                    team.members.add(user)
                    messages.success(request, f"{user.username} added to the team!")
                else:
                    messages.warning(request, f"{user.username} is already in the team!")
                return redirect('view_team_tasks', team_id=team.id)
        elif "add_task" in request.POST:
            task_form = TeamTaskForm(request.POST)
            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.team = team
                task.created_by = request.user
                task.save()
                messages.success(request, "Task added successfully!")
                return redirect('view_team_tasks', team_id=team.id)

    tasks_with_due = []    
    for task in tasks:
        tasks_with_due.append({
            'task': task,
            'is_overdue': task.is_overdue(),
            'is_approaching': task.is_approaching_due_date(),
        })

    return render(request, 'teams/team_tasks.html', {
        'team': team,
        'tasks': tasks_with_due,
        'add_member_form': add_member_form,
        'task_form': task_form,
        'reassigned_task_form': reassigned_task_form,
        'escualeted_reason_form': escualeted_reason_form
    })