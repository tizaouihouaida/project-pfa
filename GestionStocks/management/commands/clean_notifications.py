from django.core.management.base import BaseCommand
from GestionStocks.models import Notification
from django.db.models import Count

class Command(BaseCommand):
    help = 'Nettoie les notifications en double en gardant seulement la plus récente pour chaque médicament et type'

    def handle(self, *args, **options):
        # Trouver les notifications en double
        duplicates = (
            Notification.objects.values('message', 'type')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
        )

        cleaned = 0
        for dup in duplicates:
            # Pour chaque groupe de doublons, garder seulement la notification la plus récente
            notifications = (
                Notification.objects.filter(
                    message=dup['message'],
                    type=dup['type']
                ).order_by('-date')
            )
            # Garder la première (la plus récente) et supprimer les autres
            to_keep = notifications.first()
            notifications.exclude(id=to_keep.id).delete()
            cleaned += notifications.count() - 1

        self.stdout.write(
            self.style.SUCCESS(f'Nettoyage terminé. {cleaned} notifications en double ont été supprimées.')
        )
