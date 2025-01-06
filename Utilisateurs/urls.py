from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.registration_view, name='register'),
    path('logout/', views.logout_view, name='logout'),  
    path('profil/', views.profile, name='profil'),
    path('profil_vente/', views.profile_vente, name='profil_vente'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('change_password/', views.change_password, name='change_password'),
    path('change_password_ventes/', views.change_password_ventes, name='change_password_ventes'),
]
