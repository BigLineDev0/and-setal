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
    email = models.EmailField()
    telephone = models.CharField(max_length=20, unique=True, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLES_CHOICES, default='citoyen')


    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"


class Otp(models.Model):
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    date_creation = models.DateTimeField(auto_now_add=True)
    est_utilise = models.BooleanField(default=False)
    tentative = models.PositiveSmallIntegerField(default=0)


    def est_expire(self):
        return timezone.now() > self.date_creation + timedelta(minutes=5)


    @staticmethod
    def generer_code():
        return str(random.randint(100000, 999999))
