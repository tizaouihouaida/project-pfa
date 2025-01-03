from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from Utilisateurs.decorators import role_required
from django.utils import timezone
from .models import Stock, Notification, Medicament
from .models import CategorieMedicament
from .forms import CategorieForm, MedicamentForm
import os
from django.conf import settings

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
    categories = CategorieMedicament.objects.filter(est_cachee=False)  # Récupérer les catégories visibles
    return render(request, 'categories/index.html', {'categories': categories, 'username': username,})

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
    categories = CategorieMedicament.objects.all()  # Récupérer toutes les catégories
    username = request.user.username
    medicaments = Medicament.objects.all()  # Affiche uniquement les médicaments non vendus
    if request.method == 'POST':
        form = MedicamentForm(request.POST, request.FILES)
        if form.is_valid():
            medicament = form.save(commit=False)
            medicament.est_vendu = False  # Par défaut, le médicament n'est pas vendu
            medicament.save()
            return redirect('medicaments_index')  # Redirige vers la liste des médicaments
    else:
        form = MedicamentForm()

    return render(request, 'medicaments/index.html', {
        'medicaments': medicaments,
        'categories': categories,
        'username': username,
        'form': form,
    })

@login_required
@role_required('gestionnaire_stocks')
def stocks_index(request):
    username = request.user.username
    stocks = Stock.objects.all()
    notifications = []

    for stock in stocks:
        if stock.quantite < stock.seuil_alerte and not stock.medicament.est_vendu:
            notifications.append(Notification(message=f"Le médicament {stock.medicament.nom} a dépassé le seuil d'alerte."))
        if stock.date_preemption < timezone.now().date() and not stock.medicament.est_vendu:
            notifications.append(Notification(message=f"Le médicament {stock.medicament.nom} a dépassé la date de préemption."))

    return render(request, 'stocks/index.html', {'stocks': stocks, 'notifications': notifications, 'username': username,}) # Assurez-vous que ce template existe

@login_required
@role_required('gestionnaire_stocks')
def medicaments_index(request):
    medicaments = Medicament.objects.all()  # Récupérer les médicaments disponibles
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
        form = MedicamentForm()
    return render(request, 'medicaments/create.html', {'form': form})

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

@login_required
@role_required('gestionnaire_stocks')
def medicament_update(request, id_Medicament):
    medicament = get_object_or_404(Medicament, id_Medicament=id_Medicament)

    if request.method == 'POST':
        # Mettre à jour uniquement les champs qui ont été modifiés
        if 'nom' in request.POST:
            medicament.nom = request.POST.get('nom')
        if 'description' in request.POST:
            medicament.description = request.POST.get('description')
        if 'prixUnitaire' in request.POST:
            medicament.prixUnitaire = request.POST.get('prixUnitaire')
        if 'est_vendu' in request.POST:
            medicament.est_vendu = request.POST.get('est_vendu', False)
        
        # Mettre à jour la catégorie si elle est fournie
        if 'id_Categorie' in request.POST:
            medicament.id_Categorie_id = request.POST.get('id_Categorie')  # Mettre à jour la catégorie

        image = request.FILES.get('image')

        # Si une nouvelle image est téléchargée, mettez à jour le champ image
        if image:
            medicament.image = image  # Mettre à jour l'image

        medicament.save()  # Enregistrer les modifications
        return redirect('medicaments_index')  # Rediriger vers la liste des médicaments

    categories = CategorieMedicament.objects.all()  # Récupérer toutes les catégories pour le formulaire
    return render(request, 'medicaments/update.html', {'medicament': medicament, 'categories': categories})


# Ajoutez d'autres vues pour update et delete
