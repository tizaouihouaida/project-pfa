from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
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
                messages.error(request, "Identifiants invalides ou rôle incorrect ou mot de passe incorrect")
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
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def home_view(request):
    return redirect('login')

@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.save()

        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            return redirect('login')

    else:
        password_form = PasswordChangeForm(user)
    return render(request, 'profile.html', {'user': user, 'password_form': password_form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        return redirect('login')
    return render(request, 'confirm_delete.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password == confirm_password:
            user = request.user
            if user.check_password(current_password):
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                return redirect('profil')
            else:
                messages.error(request, "Mot de passe actuel incorrect.")

    return render(request, 'profile.html', {'user': request.user})

@login_required
def profile_vente(request):
    user = request.user
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.save()

        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            return redirect('login')

    else:
        password_form = PasswordChangeForm(user)
    return render(request, 'profile_vente.html', {'user': user, 'password_form': password_form})

@login_required
def change_password_ventes(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password == confirm_password:
            user = request.user
            if user.check_password(current_password):
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                return redirect('profil_vente')
            else:
                messages.error(request, "Mot de passe actuel incorrect.")

    return render(request, 'profile_vente.html', {'user': request.user})
