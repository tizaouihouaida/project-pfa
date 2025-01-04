from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Utilisateurs.decorators import role_required

@login_required
@role_required('gestionnaire_ventes')  # Vérifie que l'utilisateur est un gestionnaire de ventes
def sales_dashboard(request):
    username = request.user.username
    return render(request, 'sales_dashboard.html', {'username': username})  # Assurez-vous que ce template existe
