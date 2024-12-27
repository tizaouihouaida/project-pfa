from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from Utilisateurs.decorators import role_required
from django.utils import timezone
from .models import Stock, Notification
from .models import CategorieMedicament
from .forms import CategorieForm 

@login_required
@role_required('gestionnaire_stocks')  # Vérifie que l'utilisateur est un gestionnaire de stocks
def stocks_dashboard(request):
    username = request.user.username  # Récupérer le nom d'utilisateur
    return render(request, 'stocks_dashboard.html', {'username': username}) 

 # Assurez-vous que ce template existe
@login_required
@role_required('gestionnaire_stocks')
def categories_index(request):
    username = request.user.username
    categories = CategorieMedicament.objects.all()

    if request.method == 'POST':
        form = CategorieForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categories_index')  # Redirige vers l'index après l'ajout
    else:
        form = CategorieForm()

    return render(request, 'categories/index.html', {'categories': categories, 'form': form}) # Assurez-vous que ce template existe
@login_required
@role_required('gestionnaire_stocks')
def medicaments_index(request):
    username = request.user.username
    return render(request, 'medicaments/index.html', {'username': username}) 

@login_required
@role_required('gestionnaire_stocks')
def stocks_index(request):
    stocks = Stock.objects.all()
    notifications = []

    for stock in stocks:
        if stock.quantite < stock.seuil_alerte and not stock.medicament.est_vendu:
            notifications.append(Notification(message=f"Le médicament {stock.medicament.nom} a dépassé le seuil d'alerte."))
        if stock.date_preemption < timezone.now().date() and not stock.medicament.est_vendu:
            notifications.append(Notification(message=f"Le médicament {stock.medicament.nom} a dépassé la date de préemption."))

    return render(request, 'stocks/index.html', {'stocks': stocks, 'notifications': notifications}) # Assurez-vous que ce template existe
