from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Utilisateurs.decorators import role_required

@login_required
@role_required('gestionnaire_stocks')  # Vérifie que l'utilisateur est un gestionnaire de stocks
def stocks_dashboard(request):
    return render(request, 'stocks_dashboard.html')  # Assurez-vous que ce template existe
