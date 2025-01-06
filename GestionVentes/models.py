from django.db import models
from Utilisateurs.models import Utilisateur
from GestionStocks.models import Medicament
from django.utils import timezone

class Vente(models.Model):
    id_Vente = models.AutoField(primary_key=True)
    id_User = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    dateVente = models.DateTimeField(default=timezone.now)  # Utiliser DateTimeField pour inclure l'heure
    totalVente = models.DecimalField(max_digits=10, decimal_places=2)

    def enregistrerVente(self):
        self.save()

    def modifierVente(self, id_User=None, dateVente=None, totalVente=None):
        if id_User:
            self.id_User = id_User
        if dateVente:
            self.dateVente = dateVente
        if totalVente:
            self.totalVente = totalVente
        self.save()

    @staticmethod
    def afficherVenteJournaliere(date):
        return Vente.objects.filter(dateVente__date=date)  # Filtrer par date sans l'heure

    def __str__(self):
        return f"Vente {self.id_Vente} - {self.dateVente} - {self.totalVente}"

class DetailVente(models.Model):
    id_DetailVente = models.AutoField(primary_key=True)
    id_Vente = models.ForeignKey(Vente, related_name='details', on_delete=models.CASCADE)
    id_Medicaments = models.ForeignKey(Medicament, on_delete=models.CASCADE)  # Utiliser ForeignKey
    quantiteVendu = models.IntegerField()
    sousTotal = models.DecimalField(max_digits=10, decimal_places=2)

    def enregistrerDetailVente(self):
        self.save()

    def modifierDetailVente(self, id_Vente=None, id_Medicaments=None, quantiteVendu=None, sousTotal=None):
        if id_Vente:
            self.id_Vente = id_Vente
        if id_Medicaments:
            self.id_Medicaments = id_Medicaments
        if quantiteVendu:
            self.quantiteVendu = quantiteVendu
        if sousTotal:
            self.sousTotal = sousTotal
        self.save()

    def __str__(self):
        return f"DetailVente {self.id_DetailVente} - {self.id_Vente}"
