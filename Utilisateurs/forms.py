from django import forms
from .models import Utilisateur

class LoginForm(forms.Form):
    username = forms.CharField(label='Nom d’utilisateur')
    role = forms.ChoiceField(choices=[
        ('gestionnaire_stocks', 'Gestionnaire de Stocks'),
        ('gestionnaire_ventes', 'Gestionnaire de Ventes'),
    ], label='Rôle')
    password = forms.CharField(widget=forms.PasswordInput, label='Mot de passe')

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Mot de passe')
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Confirmer le mot de passe')

    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'role', 'phone', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.") 

