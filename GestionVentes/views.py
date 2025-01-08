from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string  # Importer render_to_string
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Vente, DetailVente
from GestionStocks.models import Medicament, CategorieMedicament, Stock, Notification  # Importez depuis GestionStocks
from .forms import VenteForm, DetailVenteForm
from Utilisateurs.decorators import role_required
from django.db.models import Sum, DecimalField, IntegerField
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
import json
import logging
from django.db import transaction
from decimal import Decimal
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

@login_required
@role_required('gestionnaire_ventes')
def pos_index(request):
    username = request.user.username
    categories = CategorieMedicament.afficheLesCategories()
    medicaments = Medicament.Medicament_disponible()
    return render(request, 'pos/index.html', {'categories': categories, 'medicaments': medicaments, 'username': username})

def sales_dashboard(request):
    today = timezone.now().date()
    ventes = Vente.objects.filter(dateVente__date=today)
    total_revenue = ventes.aggregate(
        total=Coalesce(Sum('totalVente', output_field=DecimalField()), Decimal('0.00'))
    )['total']

    top_medicament = (
        DetailVente.objects.values('id_Medicaments__nom')
        .annotate(total_quantity=Sum('quantiteVendu', output_field=IntegerField()))
        .order_by('-total_quantity')
        .first()
    )

    medicament_stats = (
        DetailVente.objects.values('id_Medicaments__nom')
        .annotate(total_quantity=Sum('quantiteVendu', output_field=IntegerField()))
        .order_by('-total_quantity')[:5]
    )

    top_sale = ventes.order_by('-totalVente').first()

    top_sales = ventes.values('dateVente', 'totalVente').order_by('dateVente')

    # Sérialiser les données en JSON
    top_sales_json = json.dumps(list(top_sales), default=str)
    medicament_stats_json = json.dumps(list(medicament_stats), default=str)

    return render(request, 'sales_dashboard.html', {
        'ventes': ventes,
        'total_revenue': total_revenue,
        'top_medicament': top_medicament,
        'medicament_stats': medicament_stats_json,  # Passer les données sérialisées
        'top_sales': top_sales_json,  # Passer les données sérialisées
        'top_sale': top_sale,
    })


@login_required
@role_required('gestionnaire_ventes')
def ventes_index(request):
    username = request.user.username
    today = timezone.now().date()
    ventes = Vente.objects.filter(dateVente__date=today)
    return render(request, 'ventes/index.html', {'ventes': ventes, 'username': username})


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
        medicaments = Medicament.objects.filter(
            id_Categorie=category_id,
            stock__quantite__gt=0,
            est_cachee=False
        ).distinct().values('id_Medicament', 'nom', 'description', 'prixUnitaire', 'image')
        return JsonResponse({'medicaments': list(medicaments)})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
@role_required('gestionnaire_ventes')
def search_medicaments(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        medicaments = Medicament.objects.filter(
            nom__icontains=query,
            stock__quantite__gt=0,
            est_cachee=False
        ).distinct().values('id_Medicament', 'nom', 'description', 'prixUnitaire', 'image')
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

        try:
            with transaction.atomic():  # Utiliser une transaction pour garantir l'intégrité des données
                vente = Vente.objects.create(id_User=request.user, totalVente=0)
                logger.info(f"Vente créée avec ID: {vente.id_Vente}")

                for item in json.loads(cart):
                    medicament = get_object_or_404(Medicament, id_Medicament=item['id'])
                    quantite = int(item['quantity'])
                    logger.info(f"Traitement de {medicament.nom}, quantité: {quantite}")

                    # Vérifier le stock disponible
                    stock = Stock.objects.select_for_update().get(medicament=medicament)
                    if not stock.deduire_quantite(quantite):
                        raise ValidationError(f"Stock insuffisant pour {medicament.nom}")

                    # Vérifier si le stock atteint le seuil d'alerte après la vente
                    if stock.quantite <= stock.seuil_alerte:
                        medicament.est_vendu = False
                        medicament.save()
                        Notification.objects.create(
                            message=f"Le stock de {medicament.nom} est bas ({stock.quantite} restants)",
                            type_notification="alerte_stock"
                        )
                        logger.info(f"Notification créée pour {medicament.nom}")
                        return JsonResponse({'status': 'error', 'message': f"Le stock de {medicament.nom} est épuisé et ne peut plus être vendu."})

                    # Créer le détail de vente
                    detail_vente = DetailVente.objects.create(
                        id_Vente=vente,
                        id_Medicaments=medicament,
                        quantiteVendu=quantite,
                        sousTotal=item['total']
                    )
                    logger.info(f"Détail de vente créé pour {medicament.nom}")

                    total += item['total']

                vente.totalVente = total
                vente.save()
                logger.info(f"Vente finalisée avec total: {total}")

                return JsonResponse({'status': 'success', 'total': total})

        except json.JSONDecodeError:
            logger.error("Erreur de décodage JSON")
            return JsonResponse({'status': 'error', 'message': 'Format de panier invalide'}, status=400)
        except ValidationError as e:
            logger.error(f"Erreur de validation: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        except Exception as e:
            logger.error(f"Erreur inattendue: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'Une erreur est survenue'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée'}, status=405)


@login_required
@role_required('gestionnaire_ventes')
def check_stock(request):
    if request.method == 'POST':
        medicament_id = request.POST.get('medicament_id')
        quantite = int(request.POST.get('quantite', 0))

        try:
            stock = Stock.objects.get(medicament_id=medicament_id)
            if stock.quantite >= quantite:
                return JsonResponse({
                    'status': 'success',
                    'available': True,
                    'stock': stock.quantite
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'available': False,
                    'message': f'Stock insuffisant. Quantité disponible: {stock.quantite}',
                    'stock': stock.quantite
                })
        except Stock.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'available': False,
                'message': 'Aucun stock disponible pour ce médicament'
            })
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
