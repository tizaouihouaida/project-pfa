from django.urls import path
from .views import profile, delete_account, change_password  # Importez la vue de changement de mot de passe

urlpatterns = [
    path('profil/', profile, name='profil'),  # Assurez-vous que cette ligne est présente
    path('delete_account/', delete_account, name='delete_account'),  # Assurez-vous que cette ligne est présente
    path('change_password/', change_password, name='change_password'),  # Ajoutez cette ligne
]
