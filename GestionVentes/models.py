from django.db import models
from Utilisateurs.models import Utilisateur
from GestionStocks.models import Medicament
from django.utils import timezone

class Vente(models.Model):
    id_Vente = models.AutoField(primary_key=True)
    id_User = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    dateVente = models.DateTimeField(default=timezone.now)
    totalVente = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Vente {self.id_Vente} - {self.dateVente}"

class DetailVente(models.Model):
    id_DetailVente = models.AutoField(primary_key=True)
    id_Vente = models.ForeignKey(Vente, on_delete=models.CASCADE, related_name='details')
    id_Medicaments = models.ForeignKey(Medicament, on_delete=models.CASCADE)
    quantiteVendu = models.IntegerField()
    sousTotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Détail vente {self.id_DetailVente} - {self.id_Vente}"
from django.db import models
from Utilisateurs.models import Utilisateur
from GestionStocks.models import Medicament
from django.utils import timezone

class Vente(models.Model):
    id_Vente = models.AutoField(primary_key=True)
    id_User = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    dateVente = models.DateTimeField(default=timezone.now)
    totalVente = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Vente {self.id_Vente} - {self.dateVente}"

class DetailVente(models.Model):
    id_DetailVente = models.AutoField(primary_key=True)
    id_Vente = models.ForeignKey(Vente, on_delete=models.CASCADE, related_name='details')
    id_Medicaments = models.ForeignKey(Medicament, on_delete=models.CASCADE)
    quantiteVendu = models.IntegerField()
    sousTotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Détail vente {self.id_DetailVente} - {self.id_Vente}"
