from django.contrib import admin
from .models import Utilisateurs

# Register your models here.
@admin.register(Utilisateurs)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'role', 'email', 'is_active')