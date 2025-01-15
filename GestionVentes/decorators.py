from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps
from django.contrib.auth.models import Group

def sales_manager_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
            
        # Vérifier si l'utilisateur est dans le groupe Gestionnaire_Vente
        if request.user.groups.filter(name='Gestionnaire_Vente').exists() or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            # Si non autorisé, renvoyer vers la page 403
            raise PermissionDenied()
            
    return _wrapped_view
