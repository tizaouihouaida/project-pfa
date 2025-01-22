from .models import Notification

def notification_count(request):
    """
    Ajoute le nombre de notifications non lues au context de tous les templates
    """
    if request.user.is_authenticated:
        count = Notification.objects.filter(lu=False).count()
        return {'notification_count': count}
    return {'notification_count': 0}
