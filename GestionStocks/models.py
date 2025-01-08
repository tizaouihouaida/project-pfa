from django.db import models
from django.utils import timezone


class CategorieMedicament(models.Model):
    id_Categorie = models.AutoField(primary_key=True)
    nom_Categorie = models.CharField(max_length=255)
    description = models.TextField()
    est_cachee = models.BooleanField(default=False)

    def ajouterCategorie(self):
        self.save()

    def modifierCategorie(self, nom_Categorie=None, description=None):
        if nom_Categorie:
            self.nom_Categorie = nom_Categorie
        if description:
            self.description = description
        self.save()

    def cacherCategorie(self):
        self.est_cachee = True
        self.save()
        Medicament.objects.filter(id_Categorie=self).update(est_cachee=True)

    @staticmethod
    def afficheLesCategories():
        return CategorieMedicament.objects.filter(est_cachee=False)

    def __str__(self):
        return self.nom_Categorie

class Medicament(models.Model):
    id_Medicament = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255)
    description = models.TextField() 
    prixUnitaire = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='medicament_images/', null=True, blank=True)
    id_Categorie = models.ForeignKey(CategorieMedicament, on_delete=models.CASCADE)
    est_vendu = models.BooleanField(default=False)
    est_cachee = models.BooleanField(default=False)

    def ajouterMedicament(self):
        self.save()

    def modifierMedicament(self, nom=None, description=None, id_Categorie=None, prixUnitaire=None):
        if nom:
            self.nom = nom
        if description:
            self.description = description
        if id_Categorie:
            self.id_Categorie = id_Categorie
        if prixUnitaire:
            self.prixUnitaire = prixUnitaire
        self.save()

    def cacherMedicament(self):
        self.est_cachee = True
        self.save()

    @staticmethod
    def afficheLesMedicaments():
        return Medicament.objects.filter(est_cachee=False)
    
    @staticmethod
    def afficheMedicamentStock():
        return Medicament.objects.filter(est_vendu=False)
    
    @staticmethod
    def MedicamentParCategorie(categorie_id):
        return Medicament.objects.filter(id_Categorie=categorie_id, est_cachee=False)

    @staticmethod
    def medicaments_disponibles_pour_stock():
        """Retourne les médicaments disponibles pour créer un nouveau stock"""
        return Medicament.objects.filter(
            est_cachee=False, 
            est_vendu=False
        ).exclude(
            id_Medicament__in=Stock.objects.values('medicament')
        )

    @staticmethod
    def medicaments_non_caches():
        """Retourne tous les médicaments non cachés"""
        return Medicament.objects.filter(est_cachee=False)

    def __str__(self):
        return self.nom

class Stock(models.Model):
    id_Stock = models.AutoField(primary_key=True)
    medicament = models.ForeignKey(Medicament, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    seuil_alerte = models.IntegerField(default=10)
    date_derniere_modification = models.DateTimeField(auto_now=True)

    def deduire_quantite(self, quantite_a_deduire):
        """Déduit une quantité du stock et retourne True si l'opération est réussie"""
        if self.quantite >= quantite_a_deduire:
            self.quantite -= quantite_a_deduire
            self.save()
            
            # Créer une notification si le seuil d'alerte est atteint
            if self.quantite <= self.seuil_alerte:
                Notification.objects.create(
                    message=f"Le stock de {self.medicament.nom} est bas ({self.quantite} restants)",
                    type_notification="alerte_stock"
                )
            return True
        return False

    def __str__(self):
        return f"Stock de {self.medicament.nom}: {self.quantite} unités"

class Notification(models.Model):
    message = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)
    type = models.CharField(
        max_length=20, 
        choices=[
            ('peremption', 'Péremption'),
            ('stock', 'Stock'),
        ],
        default='stock'
    )

    def __str__(self):
        return self.message

class Fournisseur(models.Model):
    nom = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    telephone = models.CharField(max_length=20, null=True, blank=True)
    adresse = models.TextField(null=True, blank=True)

    def ajouterFournisseur(self):
        self.save()

    def modifierFournisseur(self, nom=None, email=None, telephone=None, adresse=None):
        if nom:
            self.nom = nom
        if email:
            self.email = email
        if telephone:
            self.telephone = telephone
        if adresse:
            self.adresse = adresse
        self.save()
    def supprimerFournisseur(self):
        self.delete()
    def afficheLesFournisseurs(self):
        return Fournisseur.objects.all()
    
    def __str__(self):
        return self.nom

class Commande(models.Model):
    medicament = models.ForeignKey(Medicament, on_delete=models.CASCADE)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE)
    quantite_commande = models.FloatField(null=True, blank=True)
    date_commande = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=50, choices=[('en_attente', 'En attente'), ('livrée', 'Livrée')])

    def __str__(self):
        return f"Commande de {self.medicament.nom} auprès de {self.fournisseur.nom}"

    def livrer_commande(self):
        if self.statut == 'livrée':
            return
        
        # Chercher un stock existant pour ce médicament
        stock = Stock.objects.filter(medicament=self.medicament).first()
        
        if stock:
            # Si le stock existe, mettre à jour la quantité
            stock.quantite += self.quantite_commande
            stock.save()
        else:
            # Si le stock n'existe pas, en créer un nouveau
            stock = Stock.objects.create(
                medicament=self.medicament,
                quantite=self.quantite_commande,
                seuil_alerte=10  # Valeur par défaut
            )
        
        # Mettre à jour le statut de la commande
        self.statut = 'livrée'
        self.save()
        
        # Mettre à jour le statut du médicament
        self.medicament.est_vendu = True
        self.medicament.save()

