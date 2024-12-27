from django import forms
from .models import CategorieMedicament

class CategorieForm(forms.ModelForm):
    class Meta:
        model = CategorieMedicament
        fields = ['nom_Categorie', 'description']
