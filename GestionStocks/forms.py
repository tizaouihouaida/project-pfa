from django import forms
from .models import CategorieMedicament, Medicament

class CategorieForm(forms.ModelForm):
    class Meta:
        model = CategorieMedicament
        fields = ['nom_Categorie', 'description']

    def clean_nom_Categorie(self):
        nom_Categorie = self.cleaned_data.get('nom_Categorie')
        if self.instance.pk:
            if CategorieMedicament.objects.filter(nom_Categorie=nom_Categorie).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError(f"Une catégorie avec le nom '{nom_Categorie}' existe déjà.")
        else:
            if CategorieMedicament.objects.filter(nom_Categorie=nom_Categorie).exists():
                raise forms.ValidationError(f"Une catégorie avec le nom '{nom_Categorie}' existe déjà.")
        return nom_Categorie

class MedicamentForm(forms.ModelForm):
    class Meta:
        model = Medicament
        fields = ['nom', 'description', 'prixUnitaire', 'image', 'id_Categorie']
