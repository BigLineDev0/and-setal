from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import random


class Utilisateurs(AbstractUser):
    ROLES_CHOICES = [
        ('citoyen', 'Citoyen'),
        ('agent', 'Agent'),
        ('admin', 'Admin')
    ]
    
    # L'email doit impérativement être unique pour servir d'identifiant
    email = models.EmailField(unique=True)
    
    telephone = models.CharField(max_length=20, unique=True, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLES_CHOICES, default='citoyen')

    # Indique à Django et SimpleJWT d'utiliser l'email pour la connexion
    USERNAME_FIELD = 'email'
    
    # Champs obligatoires demandés dans le terminal lors du 'createsuperuser'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'telephone']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"

class Otp(models.Model):
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=4)
    date_creation = models.DateTimeField(auto_now_add=True)
    est_utilise = models.BooleanField(default=False)
    tentative = models.PositiveSmallIntegerField(default=0)


    def est_expire(self):
        return timezone.now() > self.date_creation + timedelta(minutes=5)


    @staticmethod
    def generer_code():
        return str(random.randint(1000, 9999))
