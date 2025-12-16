from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.http import HttpRequest, HttpResponse
from .models import Profile
from django.contrib import messages
from django.contrib.auth.models import User

# Create your views here.

def sign_up(request: HttpRequest):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('accounts:sign_up')
        
        user = User.objects.create_user(username=username, password=password, email=email)
        Profile.objects.create(user=user)
        login(request, user)
        return redirect('main:home_view')
    
    return render(request, 'accounts/signup.html')

def sign_in(request: HttpRequest):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('accounts:profile_view')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('accounts:sign_in')
    
    return render(request, 'accounts/signin.html')

def log_out(request: HttpRequest):

    logout(request)
    return redirect('accounts:sign_in')

def profile_view(request: HttpRequest):
    
    return render(request, 'accounts/profile.html')

def update_profile(request: HttpRequest):
   
    return render(request, 'accounts/update_profile.html')