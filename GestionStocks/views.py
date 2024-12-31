from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from Utilisateurs.decorators import role_required
from django.utils import timezone
from .models import Stock, Notification, Medicament
from .models import CategorieMedicament
from .forms import CategorieForm, MedicamentForm

@login_required
@role_required('gestionnaire_stocks')  # Vérifie que l'utilisateur est un gestionnaire de stocks
def stocks_dashboard(request):
    username = request.user.username  # Récupérer le nom d'utilisateur
    return render(request, 'stocks_dashboard.html', {'username': username}) 

 # Assurez-vous que ce template existe
@login_required
@role_required('gestionnaire_stocks')
def categories_index(request):
    categories = CategorieMedicament.objects.filter(est_cachee=False)  # Récupérer les catégories visibles
    return render(request, 'categories/index.html', {'categories': categories})

@login_required
@role_required('gestionnaire_stocks')
def category_create(request):
    if request.method == 'POST':
        form = CategorieForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categories_index')  # Redirige vers la liste des catégories
    else:
        form = CategorieForm()
    return render(request, 'categories/create.html', {'form': form})

@login_required
@role_required('gestionnaire_stocks')
def category_edit(request, id):
    category = get_object_or_404(CategorieMedicament, id_Categorie=id)
    if request.method == 'POST':
        form = CategorieForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('categories_index')  # Redirige vers la liste des catégories
    else:
        form = CategorieForm(instance=category)
    return render(request, 'categories/update.html', {'form': form})

@login_required
@role_required('gestionnaire_stocks')
def category_delete(request, id):
    category = get_object_or_404(CategorieMedicament, id_Categorie=id)
    category.est_cachee = True  # Mettre à jour le champ est_cachee
    category.save()
    return redirect('categories_index')  # Redirige vers la liste des catégories

@login_required
@role_required('gestionnaire_stocks')
def medicaments_index(request):
    medicaments = Medicament.objects.filter(est_vendu=True)  # Récupérer les médicaments disponibles
    categories = CategorieMedicament.objects.all()  # Récupérer toutes les catégories
    username = request.user.username
    return render(request, 'medicaments/index.html', {
        'medicaments': medicaments,
        'categories': categories,
        'username': username
    })

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

@login_required
@role_required('gestionnaire_stocks')
def medicaments_index(request):
    medicaments = Medicament.objects.filter(est_vendu=True)  # Récupérer les médicaments disponibles
    categories = CategorieMedicament.objects.all()  # Récupérer toutes les catégories
    username = request.user.username
    return render(request, 'medicaments/index.html', {
        'medicaments': medicaments,
        'categories': categories,
        'username': username
    })



@login_required
@role_required('gestionnaire_stocks')
def medicament_create(request):
    if request.method == 'POST':
        form = MedicamentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('medicaments_index')  # Redirige vers la liste des médicaments
        else:
            print(form.errors)  # Affiche les erreurs du formulaire dans la console
    return redirect('medicaments_index')  # Redirige si la méthode n'est pas POST

@login_required
@role_required('gestionnaire_stocks')
def medicament_edit(request, id):
    medicament = get_object_or_404(Medicament, id_Medicament=id)
    if request.method == 'POST':
        form = MedicamentForm(request.POST, request.FILES, instance=medicament)
        if form.is_valid():
            form.save()
            return redirect('medicaments_index')
    return redirect('medicaments_index')  # Redirige si la méthode n'est pas POST

def medicament_list(request):
    medicaments = Medicament.objects.all()
    return render(request, 'medicament_list.html', {'medicaments': medicaments})

@login_required
@role_required('gestionnaire_stocks')
def medicament_delete(request, id):
    medicament = get_object_or_404(Medicament, id_Medicament=id)
    if request.method == 'POST':
        medicament.delete()
        return redirect('medicaments_index')
    return render(request, 'medicaments/confirm_delete.html', {'medicament': medicament})

# Ajoutez d'autres vues pour update et delete
