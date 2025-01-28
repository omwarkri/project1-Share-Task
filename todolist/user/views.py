# views.py

from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

class ProtectedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({"message": "You have access to this protected view!"})


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from user.models import CustomUser



def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print(username)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Replace 'home' with your desired page
        else:
            return render(request, 'user/login.html', {'error': 'Invalid credentials'})
    return render(request, 'user/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if not CustomUser.objects.filter(username=username).exists():
            user = CustomUser.objects.create_user(username=username, email=email, password=password)
            return redirect('login')
        else:
            return render(request, 'user/register.html', {'error': 'Username already exists'})
    return render(request, 'user/register.html')
