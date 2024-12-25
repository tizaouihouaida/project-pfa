from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm, RegistrationForm
from .models import Utilisateur
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            role = form.cleaned_data['role']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and user.role == role:
                login(request, user)
                return redirect('stocks_dashboard' if role == 'gestionnaire_stocks' else 'sales_dashboard')
            else:
                messages.error(request, "Identifiants invalides ou rôle incorrect.")
        else:
            messages.error(request, "Le formulaire est invalide.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def registration_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hachage du mot de passe
            user.save()
            return redirect('login')  # Redirige vers la page de connexion
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def home_view(request):
    return redirect('login')  # Redirige vers la page de connexion
@login_required
def profile_view(request):
    user = request.user  # Récupère l'utilisateur connecté
    return render(request, 'profile.html', {'user': user})  # Passe l'utilisateur au template

def logout_view(request):
    logout(request)  # Déconnexion de l'utilisateur
    return redirect('login')  # Redirige vers la page de connexion
