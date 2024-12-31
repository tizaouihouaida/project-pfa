from django import forms
from .models import Medicament
from .models import CategorieMedicament
class MedicamentForm(forms.ModelForm):
    class Meta:
        model = Medicament
        fields = ['nom', 'description', 'id_Categorie', 'prixUnitaire', 'image']
class CategorieForm(forms.ModelForm):
    class Meta:
        model = CategorieMedicament
        fields = ['nom_Categorie', 'description']