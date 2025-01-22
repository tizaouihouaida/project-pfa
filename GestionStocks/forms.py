from django import forms
from .models import CategorieMedicament, Medicament, Fournisseur, Stock, Commande

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

class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['nom', 'email', 'telephone', 'adresse']

class StockForm(forms.ModelForm):
    quantite = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'type': 'number',
            'min': '0',
            'step': '1'
        })
    )
    seuil_alerte = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'type': 'number',
            'min': '0',
            'step': '1'
        })
    )
    
    class Meta:
        model = Stock
        fields = ['medicament', 'quantite', 'date_preemption', 'seuil_alerte']
        widgets = {
            'medicament': forms.Select(attrs={'class': 'form-control'}),
            'date_preemption': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ['medicament', 'fournisseur', 'quantite_commande', 'statut']