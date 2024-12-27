from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.categories_index, name='categories_index'),
    path('categories/edit/<int:id>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:id>/', views.delete_category, name='delete_category'),
    path('medicaments/', views.medicaments_index, name='medicaments_index'),
    path('stocks_dashboard/', views.stocks_dashboard, name='stocks_dashboard'),
    # ajoutez d'autres URLs ici
] 