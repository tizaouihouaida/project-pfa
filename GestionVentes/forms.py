# forms.py
from django import forms
from .models import Vente, DetailVente

class VenteForm(forms.ModelForm):
    class Meta:
        model = Vente
        fields = ['id_User', 'dateVente', 'totalVente']

class DetailVenteForm(forms.ModelForm):
    class Meta:
        model = DetailVente
        fields = ['id_Vente', 'id_Medicaments', 'quantiteVendu', 'sousTotal']
