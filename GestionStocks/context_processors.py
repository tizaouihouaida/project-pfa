from .models import Notification

def notifications_count(request):
    """
    Ajoute le nombre total de notifications au contexte de tous les templates
    """
    if request.user.is_authenticated:
        total_notifications = Notification.objects.count()
        return {'total_notifications': total_notifications}
    return {'total_notifications': 0} 