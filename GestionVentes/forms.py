# forms.py
from django import forms
from .models import Vente, DetailVente

from .models import Ordonnance, LigneOrdonnance

class OrdonnanceForm(forms.ModelForm):
    class Meta:
        model = Ordonnance
        fields = ['numero', 'medecin', 'patient', 'date_prescription', 'notes']
        widgets = {
            'date_prescription': forms.DateInput(attrs={'type': 'date'}),
        }

class LigneOrdonnanceForm(forms.ModelForm):
    class Meta:
        model = LigneOrdonnance
        fields = ['medicament', 'posologie', 'duree', 'quantite']
class VenteForm(forms.ModelForm):
    class Meta:
        model = Vente
        fields = ['id_User', 'dateVente', 'totalVente']

class DetailVenteForm(forms.ModelForm):
    class Meta:
        model = DetailVente
        fields = ['id_Vente', 'id_Medicaments', 'quantiteVendu', 'sousTotal']
