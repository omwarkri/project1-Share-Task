from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Task, Team
from user.models import CustomUser
import google.generativeai as genai
from user.forms import UserInterestGoalForm

# Configure Gemini API
genai.configure(api_key="AIzaSyDx3rr0MzUPaumvdII3WIffmtsZqAz7JIs")
model = genai.GenerativeModel('gemini-1.5-flash')

@login_required
def generate_task_suggestions(user, task_model=Task):
    all_tasks = [task.title for task in task_model.objects.filter(user=user)]
    interests = user.interests
    goals = user.goals

    prompt = f"""
    You are a task recommendation system. Based on the user's completed tasks, interests, and goals, suggest 20 specific, actionable, and relevant tasks for the user.

    **User Context:**
    - Completed Tasks: {all_tasks}
    - Interests: {interests}
    - Goals: {goals}

    **Task Attributes:**
    - Specific: Each task should be clear and well-defined.
    - Actionable: Each task should be something the user can start working on immediately.
    - Relevant: Each task should align with the user's interests and goals.

    **Output Format:**
    - Provide exactly 20 tasks.
    - Each task should be a single sentence.
    - Start each task with a verb (e.g., "Learn", "Build", "Read").
    - Avoid vague or generic tasks.

    **Example Tasks:**
    1. Learn advanced Python concepts like decorators and generators.
    2. Build a personal portfolio website to showcase your projects.
    3. Read a book on software development best practices.

    **Task Suggestions:**
    """

    response = model.generate_content(prompt)
    suggestions = response.text.strip().split('\n') if response and response.text else []
    suggestions = [s.strip() for s in suggestions if s.strip()]
    return suggestions[:20]

@login_required
def task_suggestions_view(request):
    user = get_object_or_404(CustomUser, id=request.user.id)
    suggestions = []
    form = UserInterestGoalForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user.interests = [i.strip() for i in form.cleaned_data['interests'].split(',')]
        user.goals = [g.strip() for g in form.cleaned_data['goals'].split(',')]
        user.save()
        suggestions = generate_task_suggestions(user)
        return JsonResponse({
            'status': 'success',
            'suggestions': suggestions,
        })
    elif request.method == 'GET':
        form = UserInterestGoalForm(initial={
            'interests': user.interests,
            'goals': user.goals
        })
        if user.interests and user.goals:
            suggestions = generate_task_suggestions(user)
        return JsonResponse({
            'status': 'success',
            'form_data': {
                'interests': form.initial['interests'],
                'goals': form.initial['goals'],
            },
            'suggestions': suggestions,
        })
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method or form data',
    }, status=400)

@login_required
def generate_team_task_suggestions(team):
    completed_tasks = [task.title for task in Task.objects.filter(team=team)]
    monthly_goals = team.monthly_goals or []
    yearly_goals = team.yearly_goals or []
    vision = team.vision or ""

    prompt = f"""
    You are a task recommendation system. Based on the team's completed tasks, monthly goals, yearly goals, and vision, suggest 20 specific, actionable, and relevant tasks for the team.

    **Team Context:**
    - Completed Tasks: {completed_tasks}
    - Monthly Goals: {monthly_goals}
    - Yearly Goals: {yearly_goals}
    - Vision: {vision}

    **Task Attributes:**
    - Specific: Each task should be clear and well-defined.
    - Actionable: Each task should be something the team can start working on immediately.
    - Relevant: Each task should align with the team's goals and vision.

    **Output Format:**
    - Provide exactly 20 tasks.
    - Each task should be a single sentence.
    - Start each task with a verb (e.g., "Develop", "Plan", "Research").
    """

    response = model.generate_content(prompt)
    suggestions = response.text.strip().split('\n') if response and response.text else []
    suggestions = [s.strip() for s in suggestions if s.strip()]
    return suggestions[:20]

@login_required
def team_task_suggestions_view(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    if request.user not in team.members.all():
        return JsonResponse({'status': 'error', 'message': "You don't have access to this team."}, status=403)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            team.monthly_goals = data.get('monthly_goal', '').strip()
            team.yearly_goals = data.get('yearly_goal', '').strip()
            team.weekly_goals = data.get('weekly_goal', '').strip()
            team.vision = data.get('vision', '').strip()
            team.save()
            return JsonResponse({'status': 'success', 'message': 'Team goals updated successfully.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        suggestions = generate_team_task_suggestions(team)
        form_data = {
            'monthly_goal': team.monthly_goals or '',
            'yearly_goal': team.yearly_goals or '',
            'weekly_goal': team.weekly_goals or '',
            'vision': team.vision or '',
        }
        return JsonResponse({
            'status': 'success',
            'form_data': form_data,
            'suggestions': suggestions,
        })