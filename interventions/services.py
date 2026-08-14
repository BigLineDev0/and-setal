# interventions/services.py
from django.utils import timezone
from .models import Intervention

def demarrer_intervention(incident, agent):
    
    intervention = Intervention.objects.create(signalement=incident, agent=agent)
    incident.statut = 'en_cours'
    incident.save()
    return intervention

def terminer_intervention(intervention, commentaire, photo=None):

    intervention.statut = 'resolu'
    intervention.date_fin = timezone.now()
    intervention.commentaire = commentaire
    if photo:
        intervention.photo = photo
    intervention.save()
    intervention.signalement.statut = 'resolu'
    intervention.signalement.save()

def annuler_intervention(intervention):
    
    intervention.statut = 'annulee'
    intervention.date_fin = timezone.now()
    intervention.save()
    intervention.signalement.statut = 'en_attente'
    intervention.signalement.save()