from django.db import models

from django.db import models

class Utilisateur(models.Model):
    ROLE_CHOICES = [
        ('gestionnaire_stocks', 'Gestionnaire de Stocks'),
        ('gestionnaire_ventes', 'Gestionnaire de Ventes'),
    ]

    id_User = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)

    def creerUser(self):
        self.save()

    def modifierUser(self, nom=None, prenom=None, email=None, phone=None, role=None):
        if nom:
            self.nom = nom
        if prenom:
            self.prenom = prenom
        if email:
            self.email = email
        if phone:
            self.phone = phone
        if role:
            self.role = role
        self.save()

    def supprimerUser(self):
        self.delete()

    def __str__(self):
        return f"{self.nom} {self.prenom} {self.role}"

