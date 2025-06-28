from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Vente, DetailVente, Ordonnance, LigneOrdonnance
from GestionStocks.models import Medicament, CategorieMedicament, Stock, Notification
from .forms import VenteForm, DetailVenteForm, OrdonnanceForm, LigneOrdonnanceForm
from Utilisateurs.decorators import role_required
from django.db.models import Sum, DecimalField, IntegerField, Q
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta
from django.views.generic import DetailView, CreateView
from django.urls import reverse_lazy
import json
import logging
from django.db import transaction
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.forms import inlineformset_factory

logger = logging.getLogger(__name__)

@csrf_exempt
def send_receipt(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            sale_id = data.get('sale_id')
            client_email = data.get('client_email')
            
            send_mail(
                f'Reçu de votre achat #{sale_id}',
                'Merci pour votre achat chez PNAWKAST!',
                settings.DEFAULT_FROM_EMAIL,
                [client_email],
                fail_silently=False,
            )
            
            return JsonResponse({'status': 'success', 'message': 'Reçu envoyé avec succès'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée'}, status=405)

@login_required
@role_required('gestionnaire_ventes')
def pos_index(request):
    username = request.user.username
    categories = CategorieMedicament.afficheLesCategories()
    medicaments = Medicament.Medicament_disponible()
    return render(request, 'pos/index.html', {
        'categories': categories,
        'medicaments': medicaments,
        'username': username
    })

@login_required
@role_required('gestionnaire_ventes')
def pos_view(request):
    medicaments = Medicament.objects.all()
    for med in medicaments:
        med.low_stock = med.quantite <= 5
    return render(request, 'pos.html', {'medicaments': medicaments})

@login_required
@role_required('gestionnaire_ventes')
def sales_dashboard(request):
    username = request.user.username
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

    return render(request, 'sales_dashboard.html', {
        'ventes': ventes,
        'total_revenue': total_revenue,
        'top_medicament': top_medicament,
        'medicament_stats': json.dumps(list(medicament_stats), default=str),
        'top_sales': json.dumps(list(top_sales), default=str),
        'top_sale': top_sale,
        'username': username,
    })

@transaction.atomic
def finaliser_vente(request, pk):
    vente = get_object_or_404(Vente, pk=pk)
    
    if not vente.details.exists():
        messages.error(request, "Le panier est vide!")
        return redirect('panier')
    
    total = 0
    for detail in vente.details.all():
        medicament = detail.medicament
        if detail.quantite > medicament.quantite_stock:
            messages.error(request, f"Stock insuffisant pour {medicament.nom}")
            return redirect('panier')
        total += detail.prix_unitaire * detail.quantite
    
    for detail in vente.details.all():
        medicament = detail.medicament
        medicament.quantite_stock -= detail.quantite
        medicament.save()
    
    vente.montant_total = total
    vente.est_paye = True
    vente.save()
    
    messages.success(request, "Vente finalisée avec succès!")
    return redirect('recu', pk=vente.pk)

@login_required
@role_required('gestionnaire_ventes')
def ventes_index(request):
    username = request.user.username
    today = timezone.now().date()
    ventes = Vente.objects.filter(dateVente__date=today)
    return render(request, 'ventes/index.html', {
        'ventes': ventes,
        'username': username
    })

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
        vente = Vente.objects.get(id_Vente=id)
        details = DetailVente.objects.filter(id_Vente=vente).select_related('id_Medicaments')
        
        details_list = []
        total_html = 0
        for detail in details:
            prix_unitaire = float(detail.sousTotal) / detail.quantiteVendu if detail.quantiteVendu > 0 else 0
            details_list.append({
                'medicament': detail.id_Medicaments.nom,
                'quantite': detail.quantiteVendu,
                'prix_unitaire': prix_unitaire,
                'total': float(detail.sousTotal)
            })
            total_html += float(detail.sousTotal)
        
        modal_content = render_to_string('includes/vente_modal.html', {
            'vente': vente,
            'details': details_list,
            'total_html': total_html
        })
        
        return JsonResponse({
            'modal_content': modal_content,
            'vente_id': vente.id_Vente,
            'date_vente': vente.dateVente.strftime("%Y-%m-%d %H:%M:%S"),
            'total_vente': float(vente.totalVente),
            'details': details_list
        })
    except Vente.DoesNotExist:
        return JsonResponse({'error': 'Vente non trouvée'}, status=404)
    except Exception as e:
        logger.error(f"Erreur dans la vue vente_detail : {e}")
        return JsonResponse({
            'error': 'Une erreur est survenue lors de la récupération des détails de la vente.'
        }, status=500)

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
        return JsonResponse({
            'status': 'success',
            'name': medicament.nom,
            'price': str(medicament.prixUnitaire)
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

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
                    'stock': stock.quantite,
                    'can_sell': quantite
                })
            elif stock.quantite > 0:
                return JsonResponse({
                    'status': 'warning',
                    'available': True,
                    'message': f'Stock insuffisant. Seuls {stock.quantite} unités sont disponibles.',
                    'stock': stock.quantite,
                    'can_sell': stock.quantite
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'available': False,
                    'message': 'Stock épuisé pour ce médicament',
                    'stock': 0,
                    'can_sell': 0
                })
        except Stock.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'available': False,
                'message': 'Aucun stock disponible pour ce médicament',
                'stock': 0,
                'can_sell': 0
            })
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
@role_required('gestionnaire_ventes')
def finalize_sale(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée'})

    try:
        cart_data = json.loads(request.POST.get('cart', '[]'))
        
        if not cart_data:
            return JsonResponse({'status': 'error', 'message': 'Le panier est vide'})

        with transaction.atomic():
            total_vente = Decimal('0.00')
            vente = Vente.objects.create(
                totalVente=total_vente,
                dateVente=timezone.now(),
                id_User=request.user
            )
            
            for item in cart_data:
                medicament = Medicament.objects.select_for_update().get(id_Medicament=item['id'])
                stock = Stock.objects.select_for_update().get(medicament=medicament)
                
                if stock.quantite >= item['quantity']:
                    sous_total = Decimal(str(item['quantity'])) * Decimal(str(item['price']))
                    
                    DetailVente.objects.create(
                        id_Vente=vente,
                        id_Medicaments=medicament,
                        quantiteVendu=item['quantity'],
                        sousTotal=sous_total
                    )
                    
                    total_vente += sous_total
                    stock.quantite -= item['quantity']
                    stock.save()
                    
                    if stock.quantite <= stock.seuil_alerte:
                        if stock.quantite == 0:
                            medicament.est_vendu = False
                            medicament.save()
                        Notification.objects.create(
                            message=f"Stock bas pour {medicament.nom}: {stock.quantite} restants",
                            type_notification="alerte_stock"
                        )
                else:
                    raise ValidationError(f"Stock insuffisant pour {medicament.nom}")

            vente.totalVente = total_vente
            vente.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Vente finalisée avec succès',
                'vente_id': vente.id_Vente,
                'total': float(total_vente)
            })
            
    except ValidationError as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Format de panier invalide'})
    except Exception as e:
        logger.error(f"Erreur lors de la finalisation de la vente: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Une erreur est survenue lors de la finalisation de la vente'
        })

@login_required
def check_auth(request):
    return JsonResponse({
        'authenticated': request.user.is_authenticated,
        'username': request.user.username if request.user.is_authenticated else None
    })

# Ordonnance Views
LigneOrdonnanceFormSet = inlineformset_factory(
    Ordonnance,
    LigneOrdonnance,
    form=LigneOrdonnanceForm,
    extra=1,
    can_delete=False,
    fields=['medicament', 'posologie', 'duree', 'quantite']
)

class CreateOrdonnanceView(CreateView):
    model = Ordonnance
    form_class = OrdonnanceForm
    template_name = 'ventes/ordonnance/create.html'
    success_url = reverse_lazy('liste_ordonnances')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['ligne_ordonnance_formset'] = LigneOrdonnanceFormSet(self.request.POST)
        else:
            context['ligne_ordonnance_formset'] = LigneOrdonnanceFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['ligne_ordonnance_formset']
        form.instance.created_by = self.request.user
        
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class OrdonnanceDetailView(DetailView):
    model = Ordonnance
    template_name = 'ventes/ordonnance/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lignes'] = self.object.ligneordonnance_set.all()
        return context

def liste_ordonnances(request):
    ordonnances = Ordonnance.objects.all().order_by('-date_prescription')
    return render(request, 'ventes/ordonnance/list.html', {'ordonnances': ordonnances})