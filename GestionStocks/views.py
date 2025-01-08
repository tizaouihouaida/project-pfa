from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.views.decorators.csrf import csrf_protect
from Utilisateurs.decorators import role_required
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone
from django.db.models import F
from .models import Stock, Notification, Medicament, Fournisseur, Commande
from .models import CategorieMedicament
from .forms import CategorieForm, MedicamentForm, FournisseurForm, StockForm
from django.core.exceptions import ValidationError
from .forms import CommandeForm
import os
from django.conf import settings
from django.contrib import messages
from datetime import timedelta

@login_required
@role_required('gestionnaire_stocks')  # Vérifie que l'utilisateur est un gestionnaire de stocks
def stocks_dashboard(request):
    today = timezone.now().date()
    
    # Statistiques générales
    total_medicaments = Medicament.objects.filter(est_cachee=False).count()
    total_categories = CategorieMedicament.objects.filter(est_cachee=False).count()
    total_fournisseurs = Fournisseur.objects.count()
    total_commandes = Commande.objects.count()
    ruptures_stock = Stock.objects.filter(quantite__lte=F('seuil_alerte')).count()
    medicaments_perimes = Stock.objects.filter(date_preemption__lte=today).count()
    total_notifications = Notification.objects.count()

    # Stocks critiques
    stocks_critiques = Stock.objects.filter(
        quantite__lte=F('seuil_alerte')
    ).select_related('medicament')[:5]

    # Médicaments proche de la péremption
    peremption_proche = []
    stocks = Stock.objects.filter(
        date_preemption__gt=today
    ).select_related('medicament')[:5]
    
    for stock in stocks:
        jours_restants = (stock.date_preemption - today).days
        stock.jours_restants = jours_restants
        if jours_restants <= 60:  # Afficher seulement si moins de 60 jours
            peremption_proche.append(stock)

    # Dernières notifications
    dernieres_notifications = Notification.objects.all().order_by('-date')[:5]

    context = {
        'username': request.user.username,
        'total_medicaments': total_medicaments,
        'total_categories': total_categories,
        'total_fournisseurs': total_fournisseurs,
        'total_commandes': total_commandes,
        'ruptures_stock': ruptures_stock,
        'medicaments_perimes': medicaments_perimes,
        'total_notifications': total_notifications,
        'stocks_critiques': stocks_critiques,
        'peremption_proche': peremption_proche,
        'dernieres_notifications': dernieres_notifications,
    }
    
    return render(request, 'stocks_dashboard.html', context)

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
    fournisseurs = Fournisseur.objects.all()
    form = FournisseurForm()
    return render(request, 'fournisseurs/index.html', {'fournisseurs': fournisseurs, 'username': username, 'form': form})

@login_required
@role_required('gestionnaire_stocks')
@require_POST
def fournisseur_create(request):
    form = FournisseurForm(request.POST)
    if form.is_valid():
        fournisseur = form.save(commit=False)
        fournisseur.ajouterFournisseur()
        return redirect('fournisseurs_index')
    # If form is invalid, get all fournisseurs and render the page again
    fournisseurs = Fournisseur.objects.all()
    return render(request, 'fournisseurs/index.html', {
        'fournisseurs': fournisseurs,
        'username': request.user.username,
        'form': form
    })

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
    
    fournisseurs = Fournisseur.objects.all()
    return render(request, 'fournisseurs/index.html', {
        'fournisseurs': fournisseurs,
        'username': request.user.username,
        'form': form
    })



@login_required
@role_required('gestionnaire_stocks')
@require_POST
def fournisseur_delete(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    fournisseur.supprimerFournisseur()
    return redirect('fournisseurs_index')


@login_required
@role_required('gestionnaire_stocks')
def fournisseurs_search(request):
    query = request.GET.get('q', '')
    fournisseurs = Fournisseur.objects.filter(nom__icontains=query)
    return JsonResponse(list(fournisseurs.values()), safe=False)

@login_required
@role_required('gestionnaire_stocks')
def livrer_commande(request, id):
    commande = get_object_or_404(Commande, id=id)
    if request.method == 'POST':
        commande.livrer_commande()
        return redirect('commandes_index')
    return redirect('commandes_index')


@login_required
@role_required('gestionnaire_stocks')
def stocks_index(request):
    stocks = Stock.afficheLesStocks()
    medicaments_disponibles = Medicament.medicaments_disponibles_pour_stock()
    tous_medicaments = Medicament.medicaments_non_caches()
    
    return render(request, 'stocks/index.html', {
        'stocks': stocks,
        'medicaments': medicaments_disponibles,
        'tous_medicaments': tous_medicaments,
        'username': request.user.username
    })


@login_required
@role_required('gestionnaire_stocks')
@require_POST
def stocks_create(request):
    try:
        form = StockForm(request.POST)
        if form.is_valid():
            medicament_id = form.cleaned_data['medicament'].id_Medicament
            
            # Vérifier si un stock existe déjà pour ce médicament
            existing_stock = Stock.objects.filter(medicament_id=medicament_id).first()
            if existing_stock:
                return JsonResponse({
                    'success': False,
                    'errors': {
                        'medicament': ['Un stock existe déjà pour ce médicament']
                    }
                })
            
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    except Exception as e:
        return JsonResponse({'success': False, 'errors': {'__all__': [str(e)]}})



@login_required
@role_required('gestionnaire_stocks')
@require_POST
def stocks_update(request, id):
    try:
        stock = get_object_or_404(Stock, id_Stock=id)
        form = StockForm(request.POST, instance=stock)
        
        if form.is_valid():
            medicament_id = form.cleaned_data['medicament'].id_Medicament
            
            # Vérifier si un autre stock existe déjà pour ce médicament
            existing_stock = Stock.objects.filter(medicament_id=medicament_id).exclude(id_Stock=id).first()
            if existing_stock:
                return JsonResponse({
                    'success': False,
                    'errors': {
                        'medicament': ['Un stock existe déjà pour ce médicament']
                    }
                })
            
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    except Exception as e:
        return JsonResponse({'success': False, 'errors': {'__all__': [str(e)]}})


@login_required
@role_required('gestionnaire_stocks')
@require_POST
def stocks_delete(request, id):
    try:
        stock = get_object_or_404(Stock, id_Stock=id)
        medicament = stock.medicament
        medicament.est_vendu = False
        medicament.save()
        stock.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'errors': str(e)})

@login_required
@role_required('gestionnaire_stocks')
@require_GET
def get_stock_for_update(request, id):
    try:
        stock = get_object_or_404(Stock, id_Stock=id)
        print(f"Medicament ID: {stock.medicament.id_Medicament}")  # Debug log
        response_data = {
            'success': True,
            'stock': {
                'id_Stock': stock.id_Stock,
                'medicament': int(stock.medicament.id_Medicament),  # Convertir en int pour être sûr
                'quantite': str(stock.quantite),
                'date_preemption': stock.date_preemption.strftime('%Y-%m-%d') if stock.date_preemption else '',
                'seuil_alerte': str(stock.seuil_alerte)
            }
        }
        print(f"Response data: {response_data}")  # Debug log
        return JsonResponse(response_data)
    except Exception as e:
        print(f"Error: {str(e)}")  # Debug log
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
@login_required
@role_required('gestionnaire_stocks')
def commandes_index(request):
    commandes = Commande.objects.all()
    medicaments = Medicament.objects.filter(est_cachee=False)
    fournisseurs = Fournisseur.objects.all()
    return render(request, 'commandes/index.html', {'commandes': commandes, 'medicaments': medicaments, 'fournisseurs': fournisseurs})


@csrf_protect
def commandes_create(request):
    if request.method == 'POST':
        form = CommandeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('commandes_index')
    medicaments = Medicament.objects.filter(est_cachee=False)
    fournisseurs = Fournisseur.objects.all()
    return render(request, 'commandes/index.html', {'medicaments': medicaments, 'fournisseurs': fournisseurs})


@login_required
@role_required('gestionnaire_stocks')
def commandes_update(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    
    # Pour les requêtes AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = {
                'success': True,
                'commande': {
                    'id': commande.pk,
                    'medicament': commande.medicament.id_Medicament,
                    'fournisseur': commande.fournisseur.id,
                    'quantite_commande': float(commande.quantite_commande),
                    'statut': commande.statut
                }
            }
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    # Pour les requêtes POST normales
    if request.method == 'POST':
        form = CommandeForm(request.POST, instance=commande)
        if form.is_valid():
            form.save()
            return redirect('commandes_index')

    medicaments = Medicament.objects.filter(est_cachee=False)
    fournisseurs = Fournisseur.objects.all()
    return render(request, 'commandes/index.html', {
        'commande': commande,
        'medicaments': medicaments,
        'fournisseurs': fournisseurs
    })

    
@login_required
@role_required('gestionnaire_stocks')
@require_POST
def commandes_delete(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    commande.delete()
    return redirect('commandes_index')


@login_required
@role_required('gestionnaire_stocks')
@require_POST
def commandes_change_status(request, pk):
    try:
        commande = get_object_or_404(Commande, pk=pk)
        if commande.statut == 'en_attente':
            commande.livrer_commande()
        else:
            # Si on veut revenir à "en_attente", il faut retirer la quantité du stock
            stock = Stock.objects.filter(medicament=commande.medicament).first()
            if stock:
                if stock.quantite >= commande.quantite_commande:
                    stock.quantite -= commande.quantite_commande
                    stock.save()
                    commande.statut = 'en_attente'
                    commande.save()
                else:
                    messages.error(request, "Impossible de changer le statut : quantité insuffisante en stock")
                    return redirect('commandes_index')
            else:
                messages.error(request, "Impossible de changer le statut : aucun stock trouvé")
                return redirect('commandes_index')
        
        messages.success(request, "Le statut de la commande a été mis à jour avec succès")
        return redirect('commandes_index')
    
    except Exception as e:
        messages.error(request, f"Une erreur est survenue : {str(e)}")
        return redirect('commandes_index')

@login_required
@role_required('gestionnaire_stocks')
def notifications_index(request):
    now = timezone.now()
    today = now.date()
    yesterday = today - timedelta(days=1)
    last_week = today - timedelta(days=7)
    
    # Récupérer toutes les notifications triées par date
    notifications = Notification.objects.all().order_by('-date')
    
    # Grouper les notifications
    grouped_notifications = {
        'aujourdhui': [],
        'hier': [],
        'cette_semaine': [],
        'plus_ancien': []
    }
    
    for notif in notifications:
        notif_date = notif.date.date()
        if notif_date == today:
            grouped_notifications['aujourdhui'].append(notif)
        elif notif_date == yesterday:
            grouped_notifications['hier'].append(notif)
        elif notif_date > last_week:
            grouped_notifications['cette_semaine'].append(notif)
        else:
            grouped_notifications['plus_ancien'].append(notif)
    
    return render(request, 'notifications/index.html', {
        'grouped_notifications': grouped_notifications,
        'username': request.user.username
    })

@login_required
@role_required('gestionnaire_stocks')
def update_stock(request, id):
    if request.method == 'POST':
        try:
            stock = Stock.objects.get(id_Stock=id)
            nouvelle_quantite = int(request.POST.get('quantite', 0))
            
            if nouvelle_quantite >= 0:
                stock.quantite = nouvelle_quantite
                stock.save()
                
                # Vérifier si le seuil d'alerte est atteint
                if stock.quantite <= stock.seuil_alerte:
                    Notification.objects.create(
                        message=f"Le stock de {stock.medicament.nom} est bas ({stock.quantite} restants)",
                        type_notification="alerte_stock"
                    )
                
                return JsonResponse({'status': 'success', 'message': 'Stock mis à jour avec succès'})
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'La quantité doit être positive'
                }, status=400)
                
        except Stock.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Stock non trouvé'
            }, status=404)
        except ValueError:
            return JsonResponse({
                'status': 'error',
                'message': 'Quantité invalide'
            }, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

