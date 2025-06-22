from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.views.decorators.http import require_POST, require_GET
from .models import CategorieMedicament, Medicament, Stock, Fournisseur, Commande, Notification
from .forms import CategorieForm, MedicamentForm, StockForm, FournisseurForm, CommandeForm
from Utilisateurs.decorators import role_required
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from django.db.models import F
from django.core.exceptions import ValidationError
import os
from django.conf import settings
from datetime import timedelta
from django.core.paginator import Paginator  # Ajoutez cette ligne en haut du fichier
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

@login_required
@role_required('gestionnaire_stocks')
def categories_index(request):
    categories_list = CategorieMedicament.afficheLesCategories()  # Récupérer les médicaments disponibles
    categories = CategorieMedicament.afficheLesCategories()  # Récupérer toutes les catégories
    username = request.user.username
    
    # Pagination
    paginator = Paginator(categories_list, 10)  # 10 médicaments par page
    page_number = request.GET.get('page')
    categories = paginator.get_page(page_number)
    
    if request.method == 'POST':
        form = MedicamentForm(request.POST, request.FILES)
        if form.is_valid():
            medicament = form.save(commit=False)
            medicament.est_vendu = False  # Par défaut, le médicament n'est pas vendu
            medicament.save()
            return redirect('categories_index')  # Redirige vers la liste des médicaments
    else:
        form = MedicamentForm()

    return render(request, 'categories/index.html', {
        # 'categories': categories,
        'categories': categories,
        'username': username,
        'form': form,
    })

@login_required
@role_required('gestionnaire_stocks')
def categories_create(request):
    if request.method == 'POST':
        form = CategorieForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "La catégorie a été créée avec succès!")
            return redirect('categories_index')
        else:
            messages.error(request, "Erreur lors de la création de la catégorie. Veuillez corriger les erreurs.")
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
            messages.success(request, f"La catégorie {categorie.nom_Categorie} a été modifiée avec succès!")
            return redirect('categories_index')
        else:
            messages.error(request, "Erreur lors de la modification. Veuillez corriger les erreurs.")
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = CategorieForm(instance=categorie)
    return render(request, 'categories/update.html', {'form': form})


@login_required
@role_required('gestionnaire_stocks')
@require_POST
def categories_delete(request, id):
    categorie = get_object_or_404(CategorieMedicament, id_Categorie=id)
    try:
        categorie.cacherCategorie()
        messages.success(request, f"La catégorie {categorie.nom_Categorie} a été supprimée avec succès!")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression de la catégorie: {str(e)}")
    
    return redirect('categories_index')


@login_required
@role_required('gestionnaire_stocks')
def medicaments_index(request):
    """
    Displays the list of medicines with pagination and handles initial form display.
    Messages from other views will be displayed here.
    """
    medicaments_list = Medicament.objects.filter(est_cachee=False) # Only show active medicines
    categories = CategorieMedicament.objects.all()
    username = request.user.username
    
    paginator = Paginator(medicaments_list, 10)  # 10 medicines per page
    page_number = request.GET.get('page')
    medicaments = paginator.get_page(page_number)
    
    return render(request, 'medicaments/index.html', {
        'medicaments': medicaments,
        'categories': categories,
        'username': username,
    })


@login_required
@role_required('gestionnaire_stocks')
def medicament_create(request):
    """
    Handles the creation of a new medicine. Redirects to the index with a message.
    """
    if request.method == 'POST':
        form = MedicamentForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                medicament = form.save(commit=False)
                medicament.est_vendu = False  # Default value for new medicine
                medicament.est_cachee = False # Default value for new medicine
                medicament.save()
                messages.success(request, '**Succès !** Le médicament a été ajouté avec succès.')
            except Exception as e:
                messages.error(request, f"**Erreur !** Impossible d'ajouter le médicament : {e}")
            return redirect('medicaments_index')
        else:
            # Form is not valid, add errors to messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"**Erreur de champ ({field}) :** {error}")
            messages.error(request, "**Erreur !** Veuillez corriger les erreurs du formulaire pour ajouter le médicament.")
            return redirect('medicaments_index') # Redirect even on error to show messages
    else:
        # If it's a GET request, just redirect to the index page (form is in modal)
        return redirect('medicaments_index')


@login_required
@role_required('gestionnaire_stocks')
def medicament_hide(request, id):
    """
    Sets a medicine as 'hidden' (soft delete). Redirects to the index with a message.
    """
    try:
        medicament = get_object_or_404(Medicament, id_Medicament=id)
        if request.method == 'POST': # It's good practice to handle deletions via POST
            medicament.est_cachee = True # Update the flag to hide
            medicament.save()
            messages.success(request, f'**Succès !** Le médicament "{medicament.nom}" a été masqué.')
        else:
            messages.warning(request, 'Méthode non autorisée pour cette action.')
    except Medicament.DoesNotExist:
        messages.error(request, "**Erreur !** Médicament introuvable.")
    except Exception as e:
        messages.error(request, f"**Erreur !** Impossible de masquer le médicament : {e}")
    return redirect('medicaments_index')


@login_required
@role_required('gestionnaire_stocks')
def medicament_update(request, id_Medicament):
    """
    Handles updating an existing medicine. Redirects to the index with a message.
    """
    medicament = get_object_or_404(Medicament, id_Medicament=id_Medicament)

    if request.method == 'POST':
        # Using the form to handle update for cleaner code and validation
        form = MedicamentForm(request.POST, request.FILES, instance=medicament)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'**Succès !** Le médicament "{medicament.nom}" a été mis à jour.')
            except Exception as e:
                messages.error(request, f"**Erreur !** Impossible de mettre à jour le médicament : {e}")
            return redirect('medicaments_index')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"**Erreur de champ ({field}) :** {error}")
            messages.error(request, "**Erreur !** Veuillez corriger les erreurs du formulaire pour mettre à jour le médicament.")
            return redirect('medicaments_index')
    else:
        # For GET request to update, if you have a separate update page, you'd render it.
        # But since we're using a modal, we redirect to the index.
        return redirect('medicaments_index')


def medicament_list(request):
    """
    This view seems redundant if medicaments_index is the main list display.
    Consider removing it if not explicitly used for another purpose.
    """
    medicaments = Medicament.objects.all()
    return render(request, 'medicament_list.html', {'medicaments': medicaments})

@login_required
@role_required('gestionnaire_stocks')
def fournisseurs_index(request):
    fournisseurs_list = Fournisseur.objects.all()  # Récupérer tous les fournisseurs
    username = request.user.username
    
    # Pagination
    paginator = Paginator(fournisseurs_list, 10)  # 10 fournisseurs par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'fournisseurs/index.html', {
        'fournisseurs': page_obj,
        'username': username
    })

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
    # Récupération des données
    stocks_list = Stock.afficheLesStocks()  # Convertir en liste pour la pagination
    medicaments_disponibles = Medicament.medicaments_disponibles_pour_stock()
    tous_medicaments = Medicament.medicaments_non_caches()
    
    # Pagination des stocks - 10 éléments par page
    paginator = Paginator(stocks_list, 10)
    page_number = request.GET.get('page')
    stocks = paginator.get_page(page_number)
    
    return render(request, 'stocks/index.html', {
        'stocks': stocks,  # Utilisez l'objet paginé
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
            # Assurez-vous que tous les champs requis sont remplis
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
            nouvelle_quantite = form.cleaned_data['quantite']
            
            # Vérifier si un autre stock existe déjà pour ce médicament
            existing_stock = Stock.objects.filter(medicament_id=medicament_id).exclude(id_Stock=id).first()
            if existing_stock:
                return JsonResponse({
                    'success': False,
                    'errors': {
                        'medicament': ['Un stock existe déjà pour ce médicament']
                    }
                })
            
            # Sauvegarder le stock
            stock = form.save()
            
            # Créer les notifications appropriées
            if nouvelle_quantite == 0:
                Notification.objects.create(
                    message=f"Le stock du médicament {stock.medicament.nom} est totalement épuisé. Veuillez commander.",
                    type_notification="stock_epuise"
                )
            elif nouvelle_quantite <= stock.seuil_alerte:
                Notification.objects.create(
                    message=f"Le stock de {stock.medicament.nom} est bas ({nouvelle_quantite} restants)",
                    type_notification="alerte_stock"
                )
            
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
    commandes_list = Commande.objects.all()
    username = request.user.username
    
    paginator = Paginator(commandes_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    medicaments = Medicament.objects.filter(est_cachee=False)
    fournisseurs = Fournisseur.objects.all()
    
    return render(request, 'commandes/index.html', {
        'commandes': page_obj,
        'medicaments': medicaments,
        'fournisseurs': fournisseurs,
        'username': username
    })
@login_required
@role_required('gestionnaire_stocks')
@csrf_protect
def commandes_create(request):
    if request.method == 'POST':
        form = CommandeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('commandes_index')
    else:
        form = CommandeForm()

    medicaments = Medicament.objects.filter(est_cachee=False)
    fournisseurs = Fournisseur.objects.all()
    return render(request, 'commandes/create.html', {
        'form': form,
        'medicaments': medicaments,
        'fournisseurs': fournisseurs
    })
from django.shortcuts import render, get_object_or_404, redirect
from .models import Commande, Medicament, Fournisseur

def commandes_update(request, pk):
    commande = get_object_or_404(Commande, pk=pk)

    if request.method == 'POST':
        medicament_id = request.POST.get('medicament')
        fournisseur_id = request.POST.get('fournisseur')
        quantite = request.POST.get('quantite_commande')

        commande.medicament_id = medicament_id
        commande.fournisseur_id = fournisseur_id
        commande.quantite_commande = quantite
        commande.save()
        return redirect('commandes_index')  # ou l'URL de ta liste de commandes

    medicaments = Medicament.objects.all()
    fournisseurs = Fournisseur.objects.all()

    return render(request, 'commande_update.html', {
        'commande': commande,
        'medicaments': medicaments,
        'fournisseurs': fournisseurs
    })

@login_required
@role_required('gestionnaire_stocks')
@require_POST
def commandes_delete(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    commande.supprimerCommande()
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
                    messages.error(request, "Impossible de changer le statut : quantité insuffisante en stock.")
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
    all_notifications = Notification.objects.all().order_by('-date')
    
    # Pagination
    paginator = Paginator(all_notifications, 10)  # 10 notifications par page
    page_number = request.GET.get('page')
    notifications = paginator.get_page(page_number)
    
    # Grouper les notifications de la page courante
    grouped_notifications = {
        'aujourdhui': [],
        'hier': [],
        'cette_semaine': [],
        'plus_ancien': []
    }
    
    for notif in notifications.object_list:  # Notez l'utilisation de object_list ici
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
        'notifications': notifications,  # Objet de pagination pour le template
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
                ancienne_quantite = stock.quantite
                stock.quantite = nouvelle_quantite
                stock.save()
                
                # Notification pour stock épuisé
                if nouvelle_quantite == 0:
                    Notification.objects.create(
                        message=f"Le stock du médicament {stock.medicament.nom} est totalement épuisé. Veuillez commander.",
                        type_notification="stock_epuise"
                    )
                # Notification pour stock bas
                elif nouvelle_quantite <= stock.seuil_alerte and nouvelle_quantite > 0:
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

@login_required
@role_required('vendeur')
def ventes_index(request):
    # Récupérer uniquement les médicaments vendables
    stocks = Stock.medicaments_vendables()
    
    # Préparer les données pour l'affichage
    medicaments = []
    for stock in stocks:
        status = stock.get_status()
        medicaments.append({
            'id': stock.medicament.id_Medicament,
            'nom': stock.medicament.nom,
            'prix': stock.medicament.prixUnitaire,
            'quantite': stock.quantite,
            'status': status,
            'image': stock.medicament.image.url if stock.medicament.image else None,
            'description': stock.medicament.description,
            'categorie': stock.medicament.id_Categorie.nom_Categorie,
        })
    
    return render(request, 'ventes/index.html', {
        'medicaments': medicaments,
        'username': request.user.username,
    })
