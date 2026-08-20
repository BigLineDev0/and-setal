# interventions/services.py
from django.utils import timezone
from .models import Intervention

# L'endpoint permettant de démarrer une intervention
def demarrer_intervention(incident, agent):
    
    intervention = Intervention.objects.create(signalement=incident, agent=agent)
    incident.statut = 'en_cours'
    incident.save()
    return intervention
# l'endpoint permettant de terminer une intervention
def terminer_intervention(intervention, commentaire, photo=None):

    intervention.statut = 'resolu'
    intervention.date_fin = timezone.now()
    intervention.commentaire = commentaire
    if photo:
        intervention.photo = photo
    intervention.save()
    intervention.signalement.statut = 'resolu'
    intervention.signalement.save()
# L'endpoint permettant d'annuler une intervention
def annuler_intervention(intervention):
    
    intervention.statut = 'annulee'
    intervention.date_fin = timezone.now()
    intervention.save()
    intervention.signalement.statut = 'en_attente'
    intervention.signalement.save()