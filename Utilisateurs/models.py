from django.contrib.auth.models import AbstractUser
from django.db import models

class Utilisateur(AbstractUser):
    ROLE_CHOICES = [
        ('gestionnaire_stocks', 'Gestionnaire de Stocks'),
        ('gestionnaire_ventes', 'Gestionnaire de Ventes'),
    ]

    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        permissions = [('can_view_user', 'Can view user')]
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        unique_together = (('username', 'email'),)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='utilisateur_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='utilisateur_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def __str__(self):
        return f"{self.username} - {self.role}"

