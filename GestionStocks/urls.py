from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.categories_index, name='categories_index'),
    path('medicaments/', views.medicaments_index, name='medicaments_index'),
    path('stocks_dashboard/', views.stocks_dashboard, name='stocks_dashboard'),
    # ajoutez d'autres URLs ici
] 