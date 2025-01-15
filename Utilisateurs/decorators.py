from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps

def role_required(role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
                
            if request.user.is_superuser or request.user.role == role:
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied  # Lève une erreur 403
        return _wrapped_view
    return decorator