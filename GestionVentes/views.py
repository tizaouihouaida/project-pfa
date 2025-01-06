from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string  # Importer render_to_string
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Vente, DetailVente
from GestionStocks.models import Medicament, CategorieMedicament  # Importez depuis GestionStocks
from .forms import VenteForm, DetailVenteForm
from Utilisateurs.decorators import role_required
from django.utils import timezone
from datetime import timedelta
import json
import logging

logger = logging.getLogger(__name__)

@login_required
@role_required('gestionnaire_ventes')
def pos_index(request):
    categories = CategorieMedicament.afficheLesCategories()
    medicaments = Medicament.afficheLesMedicaments()
    return render(request, 'pos/index.html', {'categories': categories, 'medicaments': medicaments})

@login_required
@role_required('gestionnaire_ventes')
def sales_dashboard(request):
    today = timezone.now().date()
    ventes = Vente.objects.filter(dateVente__date=today)
    return render(request, 'sales_dashboard.html', {'ventes': ventes})

@login_required
@role_required('gestionnaire_ventes')
def ventes_index(request):
    today = timezone.now().date()
    ventes = Vente.objects.filter(dateVente__date=today)
    return render(request, 'ventes/index.html', {'ventes': ventes})


@login_required
@role_required('gestionnaire_ventes')
def search_ventes(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        ventes = Vente.objects.filter(
            Q(id_User__username__icontains=query) |
            Q(dateVente__icontains=query) |
            Q(totalVente__icontains=query)
        ).values('id_Vente', 'id_User__username', 'dateVente', 'totalVente')
        return JsonResponse({'ventes': list(ventes)})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required
@role_required('gestionnaire_ventes')
def vente_detail(request, id):
    try:
        vente = get_object_or_404(Vente, id_Vente=id)
        details = DetailVente.objects.filter(id_Vente=vente).select_related('id_Medicaments')

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Vérifier la requête AJAX
            modal_content = render_to_string('ventes/vente_detail_modal_content.html', {'vente': vente, 'details': details})
            return JsonResponse({'modal_content': modal_content})

        return render(request, 'ventes/detail_ventes.html', {'vente': vente, 'details': details})

    except Exception as e:
        print(f"Erreur dans la vue vente_detail : {e}")
        return JsonResponse({'error': 'Une erreur est survenue lors de la récupération des détails de la vente.'}, status=500)

@login_required
@role_required('gestionnaire_ventes')
def filter_by_category(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        medicaments = Medicament.MedicamentParCategorie(category_id)
        return JsonResponse({'medicaments': list(medicaments.values('id_Medicament', 'nom', 'description', 'prixUnitaire', 'image'))})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
@role_required('gestionnaire_ventes')
def search_medicaments(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        medicaments = Medicament.objects.filter(nom__icontains=query, est_cachee=False).values('id_Medicament', 'nom', 'description', 'prixUnitaire', 'image')
        return JsonResponse({'medicaments': list(medicaments)})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
@role_required('gestionnaire_ventes')
def add_to_cart(request):
    if request.method == 'POST':
        medicament_id = request.POST.get('medicament_id')
        medicament = get_object_or_404(Medicament, id_Medicament=medicament_id)
        return JsonResponse({'status': 'success', 'name': medicament.nom, 'price': str(medicament.prixUnitaire)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
@role_required('gestionnaire_ventes')
def finalize_sale(request):
    if request.method == 'POST':
        cart = request.POST.get('cart')
        total = 0
        vente = Vente(id_User=request.user, totalVente=0)
        vente.save()

        logger.info(f"Vente créée avec dateVente: {vente.dateVente}")
        for item in json.loads(cart):
            medicament = get_object_or_404(Medicament, id_Medicament=item['id'])
            detail_vente = DetailVente(
                id_Vente=vente,
                id_Medicaments=medicament,
                quantiteVendu=item['quantity'],
                sousTotal=item['total']
            )
            detail_vente.save()
            total += item['total']
        vente.totalVente = total
        vente.save()

        logger.info(f"Vente mise à jour avec dateVente: {vente.dateVente}")
        return JsonResponse({'status': 'success', 'total': total})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
