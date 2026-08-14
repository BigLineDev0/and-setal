from django.contrib import admin

from interventions.models import Intervention

# Register your models here.
@admin.register(Intervention)
class InterventionAdmin(admin.ModelAdmin):
    list_display = ['id', 'signalement', 'agent', 'statut']
