from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('sales_dashboard/', views.sales_dashboard, name='sales_dashboard'),# Exemple de motif d'URL
    # Ajoutez d'autres motifs d'URL ici
]
