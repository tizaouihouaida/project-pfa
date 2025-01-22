from django.core.management.base import BaseCommand
from GestionStocks.models import Notification

class Command(BaseCommand):
    help = 'Vérifie l\'état des notifications'

    def handle(self, *args, **options):
        # Afficher toutes les notifications
        self.stdout.write("=== Toutes les notifications ===")
        for notif in Notification.objects.all():
            self.stdout.write(f"ID: {notif.id}, Message: {notif.message}, Lu: {notif.lu}, Date: {notif.date}")

        # Afficher le nombre de notifications non lues
        unread_count = Notification.objects.filter(lu=False).count()
        self.stdout.write(f"\nNombre de notifications non lues: {unread_count}")

        # Afficher le nombre total de notifications
        total_count = Notification.objects.count()
        self.stdout.write(f"Nombre total de notifications: {total_count}")
