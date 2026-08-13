from django.contrib import admin

from incident.models import AnalyseIA, Incident

# Register your models here.
@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ['id', 'priorite']
@admin.register(AnalyseIA)
class AnalyseIAAdmin(admin.ModelAdmin):
    list_display = ['type_incident', 'score_confiance', 'niveau_urgence']
