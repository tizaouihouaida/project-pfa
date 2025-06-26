from django.db import models
from django.core.validators import MinValueValidator
from Utilisateurs.models import Utilisateur
from django.utils import timezone

class Medicament(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    quantite_stock = models.PositiveIntegerField(default=0)
    code_barres = models.CharField(max_length=50, unique=True, blank=True, null=True)
    
    def __str__(self):
        return f"{self.nom} (Stock: {self.quantite_stock})"

    @property
    def disponible(self):
        """Check if medication is available"""
        return self.quantite_stock > 0

class Ordonnance(models.Model):
    numero = models.CharField(max_length=50, unique=True)
    medecin = models.CharField(max_length=100)
    patient = models.CharField(max_length=100)
    date_prescription = models.DateField()
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Ordonnance {self.numero} - {self.patient}"

class LigneOrdonnance(models.Model):
    ordonnance = models.ForeignKey(Ordonnance, on_delete=models.CASCADE)
    medicament = models.ForeignKey(Medicament, on_delete=models.CASCADE)
    posologie = models.CharField(max_length=100)
    duree = models.PositiveIntegerField()
    quantite = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.medicament.nom} - {self.posologie}"

class Vente(models.Model):
    id_Vente = models.AutoField(primary_key=True)
    id_User = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    dateVente = models.DateTimeField(default=timezone.now)
    totalVente = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Vente {self.id_Vente} - {self.dateVente}"

class DetailVente(models.Model):
    id_DetailVente = models.AutoField(primary_key=True)
    id_Vente = models.ForeignKey(Vente, on_delete=models.CASCADE)
    id_Medicaments = models.ForeignKey(Medicament, on_delete=models.CASCADE)
    quantiteVendu = models.PositiveIntegerField()
    sousTotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        """Calculate subtotal before saving"""
        if not self.sousTotal:
            self.sousTotal = self.id_Medicaments.prix * self.quantiteVendu
        super().save(*args, **kwargs)
        
        # Update stock
        self.id_Medicaments.quantite_stock -= self.quantiteVendu
        self.id_Medicaments.save()
    
    def __str__(self):
        return f"{self.quantiteVendu}x {self.id_Medicaments.nom}"