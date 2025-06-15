
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Utilisateurs.urls')),  # Inclure les URLs de l'application Utilisateurs
    path('sales_dashboard/', include('GestionVentes.urls')),  # Inclure les URLs de l'application GestionVentes
    path('stocks/', include('GestionStocks.urls')),  # Inclure les URLs de l'application GestionStocks
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
