# Create your models here.

from django.db import models
from django.conf import settings

from incident.models import Incident


class Intervention(models.Model):

    STATUT_CHOICES = [
        ('en_cours', 'En cours'),
        ('resolu', 'Résolu'),
        ('annulee', 'Annulée')
    ]

    signalement = models.OneToOneField(
        Incident,
        on_delete=models.CASCADE,
        related_name="intervention"
    )

    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="interventions"
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_cours'
    )

    photo = models.ImageField(
        upload_to='interventions/',
        null=True,
        blank=True
    )

    commentaire = models.TextField(
    null=True,
    blank=True
    )

    date_creation = models.DateTimeField(auto_now_add=True)
    date_fin= models.DateTimeField(null=True, blank=True)