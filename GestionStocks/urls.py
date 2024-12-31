from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

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
    path('medicaments/', views.medicaments_index, name='medicament_index'),
    path('medicaments/create/', views.medicament_create, name='medicament_create'),
    path('medicaments/edit/<int:id>/', views.medicament_edit, name='medicament_edit'),
    path('medicaments/delete/<int:id>/', views.medicament_delete, name='medicament_delete'),
    # ajoutez d'autres URLs ici
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 