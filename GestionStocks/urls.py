from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.categories_index, name='categories_index'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/edit/<int:id>/', views.category_edit, name='category_edit'),
    path('categories/delete/<int:id>/', views.category_delete, name='category_delete'),
    path('medicaments/', views.medicaments_index, name='medicaments_index'),
    path('medicaments/create/', views.medicament_create, name='medicament_create'),
    path('medicaments/edit/<int:id>/', views.medicament_edit, name='medicament_edit'),
    path('medicaments/delete/<int:id>/', views.medicament_delete, name='medicament_delete'),
    path('stocks_dashboard/', views.stocks_dashboard, name='stocks_dashboard'),
    path('stocks/', views.stocks_index, name='stocks_index'),
    path('medicaments/', views.medicaments_index, name='medicament_index'),
    path('medicaments/create/', views.medicament_create, name='medicament_create'),
    path('medicaments/update/<int:id_Medicament>/', views.medicament_update, name='medicament_update'),  # Mise à jour d'un médicament
    # ajoutez d'autres URLs ici
]
