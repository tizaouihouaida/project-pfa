from django.contrib import admin
from .models import Medicament, CategorieMedicament, Stock

admin.site.register(Medicament)
admin.site.register(CategorieMedicament)
admin.site.register(Stock)
