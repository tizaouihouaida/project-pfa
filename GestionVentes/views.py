from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Vente, DetailVente
from GestionStocks.models import Medicament, CategorieMedicament, Stock, Notification
from Utilisateurs.decorators import role_required
from django.utils import timezone
import json
import logging

logger = logging.getLogger(__name__)

@login_required
@role_required('gestionnaire_ventes')
def pos_index(request):
    categories = CategorieMedicament.afficheLesCategories()
    medicaments = Medicament.objects.filter(
        stock__quantite__gt=0,
        est_cachee=False
    ).distinct()
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
        try:
            cart_data = json.loads(request.POST.get('cart', '[]'))
            if not cart_data:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Le panier est vide'
                }, status=400)

            total = 0
            with transaction.atomic():
                # Créer la vente
                vente = Vente.objects.create(
                    id_User=request.user,
                    totalVente=0  # Sera mis à jour après
                )

                # Traiter chaque article du panier
                for item in cart_data:
                    try:
                        medicament = Medicament.objects.get(id_Medicament=item['id'])
                        quantite = int(item['quantity'])
                        
                        # Vérifier et mettre à jour le stock
                        stock = Stock.objects.select_for_update().get(medicament=medicament)
                        if not stock.deduire_quantite(quantite):
                            raise ValidationError(f"Stock insuffisant pour {medicament.nom}")

                        # Créer le détail de vente
                        sous_total = float(item['total'])
                        DetailVente.objects.create(
                            id_Vente=vente,
                            id_Medicaments=medicament,
                            quantiteVendu=quantite,
                            sousTotal=sous_total
                        )
                        total += sous_total

                    except Medicament.DoesNotExist:
                        raise ValidationError(f"Médicament introuvable: ID {item['id']}")
                    except Stock.DoesNotExist:
                        raise ValidationError(f"Stock introuvable pour {medicament.nom}")

                # Mettre à jour le total de la vente
                vente.totalVente = total
                vente.save()

                return JsonResponse({
                    'status': 'success',
                    'total': total,
                    'vente_id': vente.id_Vente
                })

        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Format de panier invalide'
            }, status=400)
        except ValidationError as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
        except Exception as e:
            logger.error(f"Erreur lors de la finalisation de la vente: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Une erreur est survenue lors de la vente'
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Méthode non autorisée'
    }, status=405)

@login_required
@role_required('gestionnaire_ventes')
def check_stock(request):
    if request.method == 'POST':
        medicament_id = request.POST.get('medicament_id')
        quantite = int(request.POST.get('quantite', 1))
        
        try:
            stock = Stock.objects.get(medicament_id=medicament_id)
            return JsonResponse({
                'status': 'success',
                'available': stock.quantite >= quantite,
                'stock': stock.quantite,
                'message': f'Stock disponible: {stock.quantite}'
            })
        except Stock.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Stock non trouvé pour ce médicament'
            }, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
