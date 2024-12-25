from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Utilisateurs.decorators import role_required

@login_required
@role_required('gestionnaire_ventes')  # Vérifie que l'utilisateur est un gestionnaire de ventes
def sales_dashboard(request):
    return render(request, 'sales_dashboard.html')  # Assurez-vous que ce template existe
