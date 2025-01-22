from django.core.management.base import BaseCommand
from GestionStocks.models import Notification
from django.utils import timezone

class Command(BaseCommand):
    help = 'Analyse et corrige les notifications'

    def handle(self, *args, **options):
        # 1. Afficher toutes les notifications
        self.stdout.write("Liste de toutes les notifications:")
        for notif in Notification.objects.all().order_by('-date'):
            self.stdout.write(f"ID: {notif.id}, Message: {notif.message}, Lu: {notif.lu}, Type: {notif.type_notification}, Date: {notif.date}")
        
        # 2. Compter les notifications non lues
        unread_count = Notification.objects.filter(lu=False).count()
        self.stdout.write(f"\nNombre de notifications non lues: {unread_count}")
        
        # 3. Supprimer toutes les notifications
        Notification.objects.all().delete()
        self.stdout.write("Toutes les notifications ont été supprimées.")
        
        # 4. Recréer les deux notifications actuelles comme non lues
        Notification.objects.create(
            message="Le stock de Golgate a atteint le seuil d'alerte",
            type_notification='alerte_stock',
            lu=False,
            date=timezone.now()
        )
        
        Notification.objects.create(
            message="Le stock de EFFERALGAN a atteint le seuil d'alerte",
            type_notification='alerte_stock',
            lu=False,
            date=timezone.now()
        )
        
        self.stdout.write(self.style.SUCCESS("Notifications réinitialisées avec succès."))
