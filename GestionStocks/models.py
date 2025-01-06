from django.db import models


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
    def MedicamentParCategorie(categorie_id):
        return Medicament.objects.filter(id_Categorie=categorie_id, est_cachee=False)

    def __str__(self):
        return self.nom

class Stock(models.Model):
    id_Stock = models.AutoField(primary_key=True)
    medicament = models.ForeignKey(Medicament, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    date_preemption = models.DateField(null=True, blank=True)
    seuil_alerte = models.IntegerField()

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

    def supprimerStock(self):
        self.delete()

    @staticmethod
    def afficheLesStocks():
        return Stock.objects.all()

    def __str__(self):
        return f"Stock {self.id_Stock} - {self.medicament.nom}"

class Notification(models.Model):
    message = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)

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
    medicament = models.ForeignKey('Medicament', on_delete=models.CASCADE)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE)
    quantite_commande = models.FloatField(null=True, blank=True)
    date_commande = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=50, choices=[('en_attente', 'En attente'), ('livrée', 'Livrée')])

    def __str__(self):
        return f"Commande de {self.medicament.nom} auprès de {self.fournisseur.nom}"

    def livrer_commande(self):
        if self.statut == 'livrée':
            return
        self.medicament.est_vendu = False
        self.medicament.save()
        stock, created = Stock.objects.get_or_create(medicament=self.medicament)
        stock.quantite += self.quantite_commande
        stock.save()
        self.statut = 'livrée'
        self.save()
