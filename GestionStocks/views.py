from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from Utilisateurs.decorators import role_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils import timezone
from .models import Stock, Notification, Medicament, Fournisseur, Commande
from .models import CategorieMedicament
from .forms import CategorieForm, MedicamentForm, FournisseurForm
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
    categories = CategorieMedicament.afficheLesCategories() # Récupérer les catégories visibles
    return render(request, 'categories/index.html', {'categories': categories, 'username': username,})

@login_required
@role_required('gestionnaire_stocks')
def categories_create(request):
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
def categories_edit(request, id):
    categorie = get_object_or_404(CategorieMedicament, id_Categorie=id)
    if request.method == 'POST':
        form = CategorieForm(request.POST, instance=categorie)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = CategorieForm(instance=categorie)
    return render(request, 'categories/index.html', {'form': form})

@login_required
@role_required('gestionnaire_stocks')
def categories_delete(request, id):
    categorie = get_object_or_404(CategorieMedicament, id_Categorie=id)
    if request.method == 'POST':
        categorie.cacherCategorie()
        return redirect('categories_index')
    return redirect('categories_index')  # Redirige vers la liste des catégories

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
    medicaments = Medicament.afficheLesMedicaments()  # Récupérer les médicaments disponibles
    categories = CategorieMedicament.afficheLesCategories()  # Récupérer toutes les catégories
    username = request.user.username
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
def medicament_create(request):
    if request.method == 'POST':
        form = MedicamentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('medicaments_index')  # Redirige vers la liste des médicaments
    else:
        form = MedicamentForm()
    return render(request, 'medicaments/create.html', {'form': form})

def medicament_list(request):
    medicaments = Medicament.objects.all()
    return render(request, 'medicament_list.html', {'medicaments': medicaments})

@login_required
@role_required('gestionnaire_stocks')
def medicament_hide(request, id):
    medicament = get_object_or_404(Medicament, id_Medicament=id)
    if request.method == 'POST':
        medicament.cacherMedicament()
        return redirect('medicaments_index')
    return redirect('medicaments_index')


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


@login_required
@role_required('gestionnaire_stocks')
def fournisseurs_index(request):
    username = request.user.username
    fournisseur_instance = Fournisseur()
    fournisseurs = fournisseur_instance.afficheLesFournisseurs()
    return render(request, 'fournisseurs/index.html', {'fournisseurs': fournisseurs, 'username': username,}) # Assurez-vous que ce template existe

@login_required
@role_required('gestionnaire_stocks')
@require_POST
def fournisseur_create(request):
    form = FournisseurForm(request.POST)
    if form.is_valid():
        fournisseur = form.save(commit=False)
        fournisseur.ajouterFournisseur()
        return redirect('fournisseurs_index')
    else:
        form = FournisseurForm()
    form = FournisseurForm()
    return render(request, 'fournisseurs/index.html', {'fournisseurs': fournisseurs, 'username': username, 'form': form})

@login_required
@role_required('gestionnaire_stocks')
def fournisseur_update(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        form = FournisseurForm(request.POST, instance=fournisseur)
        if form.is_valid():
            fournisseur = form.save(commit=False)
            fournisseur.modifierFournisseur(
                nom=form.cleaned_data['nom'],
                email=form.cleaned_data['email'],
                telephone=form.cleaned_data['telephone'],
                adresse=form.cleaned_data['adresse']
            )
            return redirect('fournisseurs_index')
    else:
        form = FournisseurForm(instance=fournisseur)
    form = FournisseurForm()
    return render(request, 'fournisseurs/index.html', {'fournisseurs': fournisseurs, 'username': username, 'form': form})



@login_required
@role_required('gestionnaire_stocks')
@require_POST
def fournisseur_delete(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        fournisseur.supprimerFournisseur()
        return redirect('fournisseurs_index')
    form = FournisseurForm()
    return render(request, 'fournisseurs/index.html', {'fournisseurs': fournisseurs, 'username': username, 'form': form})


@login_required
@role_required('gestionnaire_stocks')
def fournisseurs_search(request):
    query = request.GET.get('q', '')
    fournisseurs = Fournisseur.objects.filter(nom__icontains=query)
    return JsonResponse(list(fournisseurs.values()), safe=False)


@login_required
@role_required('gestionnaire_stocks')
def commandes_index(request):
    username = request.user.username
    commandes = Commande.objects.all()
    return render(request, 'commandes/index.html', {'commandes': commandes, 'username': username})


@login_required
@role_required('gestionnaire_stocks')
def livrer_commande(request, id):
    commande = get_object_or_404(Commande, id=id)
    if request.method == 'POST':
        commande.livrer_commande()
        return redirect('commandes_index')
    return redirect('commandes_index')