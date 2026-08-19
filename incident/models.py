from django.db import models

from django.conf import settings


class Incident(models.Model):


    STATUT_CHOISES = [

        ('en_attente', 'En Attente'),
        ('en_cours', 'En Cours'),
        ('resolu', 'Résolu'),
    ]

    citoyen = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,)
    statut = models.CharField(max_length=20, choices=STATUT_CHOISES, default='en_attente')
    description = models.TextField(null=True, blank=True)
    messageVocal = models.FileField(upload_to='audios/', null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    adresse = models.CharField(max_length=255, null=True, blank=True)
    dateCreation = models.DateTimeField(auto_now_add=True)
    dateModification = models.DateTimeField(auto_now=True)
    priorite = models.CharField(max_length=20, null=True, blank=True)
    urlImage = models.ImageField(upload_to='images/')

    def __str__(self):
        return f"Incident #{self.id}"



class AnalyseIA(models.Model):
    type_incident = models.CharField(max_length=64)
    score_confiance = models.FloatField()
    niveau_urgence = models.CharField(max_length=20)
    date_analyse = models.DateTimeField(auto_now_add=True)
    signalement = models.ForeignKey(Incident, on_delete=models.CASCADE)