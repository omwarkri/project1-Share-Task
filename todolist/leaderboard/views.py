from django.shortcuts import render
from user.models import CustomUser

def leaderboard(request):
    top_users = CustomUser.objects.order_by('-score')[:10]  # Top 10 users
    return render(request, 'leaderboard.html', {'top_users': top_users})