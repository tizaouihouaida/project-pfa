from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


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
    #   self.est_cachee = True
        self.delete()
# Medicament.objects.filter(id_Categorie=self).update(est_cachee=True)

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
        # self.est_cachee = True
        self.delete()

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
    def Medicament_disponible():
        return Medicament.objects.filter(
            est_vendu=True,  # Le médicament est marqué comme vendable
            est_cachee=False,  # Le médicament n'est pas caché
            stock__isnull=False,  # Le médicament a un stock
            stock__quantite__gt=0,  # La quantité en stock est supérieure à 0
            stock__date_preemption__gt=timezone.now().date()  # Le médicament n'est pas périmé
        ).distinct()
    
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
    medicament = models.OneToOneField(Medicament, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    date_preemption = models.DateField(null=True, blank=True)
    seuil_alerte = models.IntegerField()
    date_derniere_modification = models.DateTimeField(auto_now=True)

    def ajouterStock(self):
        self.save()

    def modifierStock(self, medicament=None, quantite=None, seuil_alerte=None):
        if medicament:
            self.medicament = medicament
        if quantite:
            self.quantite = quantite
        if seuil_alerte:
            self.seuil_alerte = seuil_alerte
        self.save()

    @staticmethod
    def afficheLesMedicaments():
        return Stock.medicament.afficheLesMedicaments()
    
    def supprimerStock(self):
        self.delete()

    @staticmethod
    def afficheLesStocks():
        return Stock.objects.all()

    def deduire_quantite(self, quantite):
        if self.quantite >= quantite:
            self.quantite -= quantite
            self.save()
            
            # Notification pour stock épuisé
            if self.quantite == 0:
                Notification.objects.create(
                    message=f"Le stock du médicament {self.medicament.nom} est totalement épuisé. Veuillez commander.",
                    type_notification="stock_epuise"
                )
            # Notification pour stock bas
            elif self.quantite <= self.seuil_alerte:
                Notification.objects.create(
                    message=f"Le stock de {self.medicament.nom} est bas ({self.quantite} restants)",
                    type_notification="alerte_stock"
                )
            return True
        return False

    def clean(self):
        # Valider que la quantité n'est pas négative
        if self.quantite < 0:
            raise ValidationError({
                'quantite': 'La quantité ne peut pas être négative'
            })

    def get_status(self):
        """Retourne le statut du stock"""
        if self.quantite <= 0:
            return "non_disponible"
        elif self.quantite <= self.seuil_alerte:
            return "rupture_stock"
        return "disponible"

    def verifier_disponibilite(self):
        """Vérifie si le médicament est disponible à la vente"""
        aujourd_hui = timezone.now().date()

        # Supprimer toutes les anciennes notifications pour ce médicament
        Notification.objects.filter(
            message__contains=self.medicament.nom
        ).delete()

        # Vérifier la date de péremption
        if self.date_preemption and self.date_preemption <= aujourd_hui:
            self.medicament.est_vendu = False
            self.medicament.save()
            Notification.objects.create(
                message=f"Le médicament {self.medicament.nom} a dépassé sa date de péremption",
                type_notification='peremption',
                lu=False
            )
            return False

        status = self.get_status()
        
        # Mettre à jour l'état de vente du médicament
        if status == "non_disponible":
            self.medicament.est_vendu = False
            self.medicament.save()
            Notification.objects.create(
                message=f"Le stock de {self.medicament.nom} est épuisé (quantité = 0)",
                type_notification='stock',
                lu=False
            )
            return False
        elif status == "rupture_stock":
            # Le médicament est toujours vendable mais avec un avertissement
            self.medicament.est_vendu = True
            self.medicament.save()
            Notification.objects.create(
                message=f"Le stock de {self.medicament.nom} a atteint le seuil d'alerte",
                type_notification='stock',
                lu=False
            )
            return True
        else:
            # Stock normal
            self.medicament.est_vendu = True
            self.medicament.save()
            return True

    def save(self, *args, **kwargs):
        # Si c'est une nouvelle instance (pas encore dans la base de données)
        if not self.pk:
            # Vérifier si un autre stock existe déjà pour ce médicament
            existing_stock = Stock.objects.filter(medicament=self.medicament).first()
            if existing_stock:
                raise ValidationError("Un stock existe déjà pour ce médicament.")
        
        # Si la date de péremption est définie et est dépassée
        if self.date_preemption and self.date_preemption <= timezone.now().date():
            # Créer une notification
            Notification.objects.create(
                message=f"Le médicament {self.medicament.nom} est périmé depuis le {self.date_preemption}",
                type_notification='peremption'
            )
            # Mettre le médicament comme non vendable
            self.medicament.est_vendu = False
            self.medicament.save()
        
        # Si la quantité est en dessous du seuil d'alerte
        if self.quantite <= self.seuil_alerte:
            Notification.objects.create(
                message=f"Le stock de {self.medicament.nom} est bas ({self.quantite} restants)",
                type_notification='alerte_stock'
            )
        
        # Si la quantité est à zéro
        if self.quantite == 0:
            Notification.objects.create(
                message=f"Le stock du médicament {self.medicament.nom} est totalement épuisé. Veuillez commander.",
                type_notification='stock_epuise'
            )
            # Mettre le médicament comme non vendable
            self.medicament.est_vendu = False
            self.medicament.save()
        
        self.full_clean()
        super().save(*args, **kwargs)
        self.verifier_disponibilite()

    @staticmethod
    def medicaments_vendables():
        """Retourne les médicaments qui peuvent être vendus (disponible ou en rupture de stock)"""
        return Stock.objects.filter(
            quantite__gt=0,  # Quantité supérieure à 0
            medicament__est_vendu=True,  # Médicament marqué comme vendable
            date_preemption__gt=timezone.now().date()  # Non périmé
        ).select_related('medicament')

    def __str__(self):
        return f"Stock {self.id_Stock} - {self.medicament.nom}"

class Notification(models.Model):
    message = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)
    type_notification = models.CharField(
        max_length=20, 
        choices=[
            ('peremption', 'Péremption'),
            ('stock', 'Stock'),
            ('stock_epuise', 'Stock épuisé'),
            ('alerte_stock', 'Alerte stock')
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
    def modifierCommande(self, medicament=None, fournisseur=None, quantite_commande=None, date_commande=None, statut=None):
        if medicament:
            self.medicament = medicament
        if fournisseur:
            self.fournisseur = fournisseur
        if quantite_commande:
            self.quantite_commande = quantite_commande
        if date_commande:
            self.date_commande = date_commande
        if statut:
            self.statut = statut
        self.save()
    def supprimerCommande(self):
        self.delete()
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
