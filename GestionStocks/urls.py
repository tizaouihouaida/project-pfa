from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.categories_index, name='categories_index'),
    path('categories/create/', views.categories_create, name='categories_create'),
    path('categories/edit/<int:id>/', views.categories_edit, name='categories_edit'),
    path('categories/delete/<int:id>/', views.categories_delete, name='categories_delete'),
    path('medicaments/', views.medicaments_index, name='medicaments_index'),
    path('medicaments/create/', views.medicament_create, name='medicament_create'),
    path('medicaments/edit/<int:id>/', views.medicament_edit, name='medicament_edit'),
    path('medicaments/hide/<int:id>/', views.medicament_hide, name='medicament_hide'),
    path('stocks_dashboard/', views.stocks_dashboard, name='stocks_dashboard'),
    path('stocks/', views.stocks_index, name='stocks_index'),
    path('medicaments/', views.medicaments_index, name='medicament_index'),
    path('medicaments/create/', views.medicament_create, name='medicament_create'),
    path('medicaments/update/<int:id_Medicament>/', views.medicament_update, name='medicament_update'),  # Mise à jour d'un médicament
    path('fournisseurs/', views.fournisseurs_index, name='fournisseurs_index'),
    path('commandes/', views.commandes_index, name='commandes_index'),
    # ajoutez d'autres URLs ici
]
