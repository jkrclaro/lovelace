from django.shortcuts import render, redirect
from django.contrib.auth import (
    login as auth_login, 
    authenticate, 
    logout as auth_logout
)
from django.contrib import messages

from src.pxdcast.forms import SignupForm, LoginForm


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            auth_login(request, user)
            return redirect('pxdcast:home')
    else:
        form = SignupForm()

    return render(request, 'registration/signup.html', {'form': form})


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('pxdcast:home')
        else:
            messages.error(request, 'The email and password does not match')
            return redirect('pxdcast:login')
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})


def logout(request):
    auth_logout(request)
    return redirect('pxdcast:home')