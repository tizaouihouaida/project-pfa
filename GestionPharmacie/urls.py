"""
URL configuration for GestionPharmacie project.

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
# GestionPharmacie/urls.py
from django.contrib import admin
from django.urls import path
from Utilisateurs.views import login_view, registration_view, home_view, logout_view, profile_view
from GestionStocks.views import stocks_dashboard
from GestionVentes.views import sales_dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('register/', registration_view, name='register'),
    path('logout/', logout_view, name='logout'),  # URL pour la déconnexion
    path('profile/', profile_view, name='profile'),  # URL pour le profil
    path('stocks_dashboard/', stocks_dashboard, name='stocks_dashboard'),
    path('sales_dashboard/', sales_dashboard, name='sales_dashboard'),
]